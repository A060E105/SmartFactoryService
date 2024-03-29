#!/usr/bin/env python3
import re
import os
import sys
import json
import socket
import threading
import subprocess
import sounddevice as sd
from datetime import datetime
from multiprocessing import Queue
from Audio import Audio

import SmartFactoryService as SFS
from config import Configuration
from Logger import get_logger
from storage import CSVAgent
from database import create_session, AIResult, create_table


expire = datetime(2024, 2, 1)   # 過期時間

if sys.executable.endswith("pythonw.exe"):
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')


log = get_logger()

CONFIG = Configuration()

microphones = {'1': Audio.DEVICE_1, '2': Audio.DEVICE_2, 'default': Audio.DEVICE_DEFAULT, 'test': 'test'}

action_list = ["all", 'rec_only', 'spec_only', 'spec_ai', 'get_cali', 'set_cali', 'check', 'check_recording']

microphones_status = {}

log.info(f'========================================')


def set_input_volume_max() -> None:
    """
    麥克風輸入音量
    100%為65536，50%為32768
    20230215 change to 100%, the previous is 80%
    """
    volume = 65536 * (100 / 100)
    try:
        cmd = f"nircmdc.exe loop 144000 250 setsysvolume {volume} default_record"
        subprocess.run(cmd, timeout=1)
    except Exception:
        pass


class Status:
    def __init__(self) -> None:
        self.flag = False

    def lock(self):
        self.flag = True

    def unlock(self) -> None:
        self.flag = False

    @property
    def isLock(self) -> bool:
        return self.flag


for i in microphones.keys():
    microphones_status[i] = Status()


gpu_lock = threading.Lock()


class ClientThread(threading.Thread):
    def __init__(self, clientAddress, clientsocket):
        threading.Thread.__init__(self)
        self.csocket = clientsocket
        log.info(f'New connection added: {clientAddress}')

    def run(self):
        log.info(f'Connection from: {clientAddress}')
        while True:
            device = ''
            queue = Queue()
            request = json.loads(self.csocket.recv(2048).decode('utf-8'))
            print(f"request: {request}")
            action = request[0]
            filename = request[1]

            try:
                device_name = request[2]
            except IndexError:
                device_name = 'default'

            try:
                config_name = request[3]
            except IndexError:
                config_name = 'mic_default'

            if action not in action_list:       # check action has or hasn't been defined
                self.csocket.send((json.dumps({'status': 3, 'result': ['invalid action']}) + '\r\n').encode())
                break

            if action == 'check':       # check server has start
                self.csocket.send((json.dumps({'status': 'OK'}) + '\r\n').encode())
                break

            if action == 'check_recording':
                if microphones_status[device_name].isLock:
                    self.csocket.send((json.dumps({'status': 5, 'result': ['this device on using.']}) + '\r\n')
                                      .encode())
                else:
                    self.csocket.send((json.dumps({'status': 'OK'}) + '\r\n').encode())
                break

            if not filename:        # check filename is empty
                self.csocket.send((json.dumps({'status': 4, 'result': ["filename can't empty"]}) + '\r\n').encode())
                break

            if device_name in microphones:       # check microphone has or hasn't been defined
                if microphones_status[device_name].isLock:
                    if action in action_list[:2]:
                        self.csocket.send((json.dumps({'status': 5, 'result': ['this device on using.']}) + '\r\n')
                                          .encode())
                        break
                device = microphones[device_name]
                microphones_status[device_name].lock()  # lock microphone device

            log.info(f'client action: {action}, filename: {filename}, device: {device}')

            current_datetime = datetime.now()

            sfs = SFS.SmartFactoryService(filename=filename, device=device, queue=queue,
                                          gpu_lock=gpu_lock, config=config_name, current_datetime=current_datetime)

            today = datetime.today()
            if expire > today:      # 是否過期
                if action == action_list[0]:
                    sfs.all()
                elif action == action_list[1]:
                    sfs.rec_only()
                elif action == action_list[2]:
                    microphones_status[device_name].unlock()  # unlock microphone device
                    sfs.spec_only()
                elif action == action_list[3]:
                    microphones_status[device_name].unlock()  # unlock microphone device
                    sfs.spec_ai()
                elif action == action_list[4]:  # get calibration
                    sfs.get_cali()
                elif action == action_list[5]:  # set calibration
                    cali_value = float(request[1])
                    sfs.set_cali(cali_value)

                result_list = queue.get()
                result = json.dumps(result_list)
                result += '\r\n'
                if action == action_list[0]:
                    tmp_result = result_list.get('result')[0]
                    kde_score = result_list.get('KDE_score')[0]
                    mse_score = result_list.get('MSE_score')[0]
                    decibel = result_list.get('dB')
                    ai_score1 = result_list.get('ai_score1')
                    ai_score2 = result_list.get('ai_score2')
                    freq_result = result_list.get('freq_result')
                    final_result = result_list.get('final_result')
                    ai_result = AIResult(file_name=filename, kde=kde_score, mse=mse_score, decibel=decibel,
                                         ai_score1=ai_score1, ai_score2=ai_score2, freq_result=freq_result,
                                         ai_result=tmp_result, final_result=final_result,
                                         model_use_id=CONFIG.model_id, model_version=CONFIG.model_version)
                    session = create_session()
                    session.add(ai_result)
                    session.commit()
                    session.close()

                    # TODO(): save result to csv
                    csv_agent = CSVAgent(CONFIG.model_name, CONFIG.model_version, current_datetime)
                    csv_agent.write_csv(file_name=filename, ai_score1=ai_score1, ai_score2=ai_score2,
                                        freq_result=freq_result, ai_result=tmp_result, final_result=final_result,
                                        created_at=current_datetime.strftime('%Y-%m-%d %H:%M:%S'))
            else:
                result = json.dumps({'status': 0, 'result': ['???']})

            microphones_status[device_name].unlock()   # unlock microphone device
            self.csocket.send(result.encode())
            self.csocket.close()
            break
        log.info(f"Client at {clientAddress} disconnected...")


def boot_init() -> None:
    boot_device = ''
    queue = Queue()
    os_devices = sd.query_devices()
    for device in os_devices:
        if re.search(Audio.DEVICE_DEFAULT, device['name']) is not None:
            boot_device = Audio.DEVICE_DEFAULT
        elif re.search(Audio.DEVICE_1, device['name']) is not None:
            boot_device = Audio.DEVICE_1
        elif re.search(Audio.DEVICE_2, device['name']) is not None:
            boot_device = Audio.DEVICE_2

    log.info(f'boot initiation device {boot_device}')

    if boot_device:
        sfs = SFS.SmartFactoryService(filename='boot_init', device=boot_device, queue=queue, gpu_lock=gpu_lock)
        sfs.boot_init()
        queue.get()


set_input_volume_max()      # set microphone input volume max
create_table()  # sqlite initialize

boot_init()     # boot initiation

LOCALHOST = ""
PORT = CONFIG.port
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((LOCALHOST, PORT))

log.info("Server started")
log.info("Waiting for client request..")

while True:
    server.listen(1)
    clientsock, clientAddress = server.accept()
    newthread = ClientThread(clientAddress, clientsock)
    newthread.start()
