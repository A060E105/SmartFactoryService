#!/usr/bin/env python3
import re
import socket
import threading
import json
import sounddevice as sd
from multiprocessing import Queue
from SmartFactoryService import Audio
import SmartFactoryService as SFS
from config import Configuration
from Logger import get_logger

import os
import sys

if sys.executable.endswith("pythonw.exe"):
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')


log = get_logger()

CONFIG = Configuration()

microphones = {'1': Audio.DEVICE_1, '2': Audio.DEVICE_2, 'default': Audio.DEVICE_DEFAULT, 'test': 'test'}

action_list = ["all", 'rec_only', 'spec_only', 'spec_ai', 'cali', 'check']

microphones_status = {}

log.info(f'========================================')


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
                self.csocket.send(json.dumps({'status': 3, 'result': ['invalid action']}).encode())
                break

            if action == 'check':       # check server has start
                self.csocket.send(json.dumps({'status': 'OK'}).encode())
                break

            if not filename:        # check filename is empty
                self.csocket.send(json.dumps({'status': 4, 'result': ['filename can\'t empty']}))
                break

            if device_name in microphones:       # check microphone has or hasn't been defined
                if microphones_status[device_name].isLock:
                    if action in action_list[:2]:
                        self.csocket.send(json.dumps({'status': 5, 'result': ['this device on using.']}).encode())
                        break
                device = microphones[device_name]
                microphones_status[device_name].lock()  # lock microphone device

            log.info(f'client action: {action}, filename: {filename}, device: {device}')

            sfs = SFS.SmartFactoryService(filename=filename, device=device, queue=queue,
                                          gpu_lock=gpu_lock, config=config_name)

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
            elif action == action_list[4]:
                sfs.cali()

            result_list = queue.get()
            result = json.dumps(result_list)
            result += '\r\n'
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
