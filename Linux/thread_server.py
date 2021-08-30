#!/usr/bin/env python3
import re
import socket
import threading
import json
import sounddevice as sd
from multiprocessing import Queue
from SmartFactoryService import Audio
import SmartFactoryService as SFS

microphones = {'1': Audio.DEVICE_1, '2': Audio.DEVICE_2, 'test': 'test'}

action_list = ["all", 'rec_only', 'spec_only', 'spec_ai']

microphones_status = {}


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
        print("New connection added: ", clientAddress)

    def run(self):
        print("Connection from : ", clientAddress)
        while True:
            queue = Queue()
            request = json.loads(self.csocket.recv(2048).decode('utf-8'))
            action = request[0]
            filename = request[1]
            device_name = request[2]
            device = ''

            if action not in action_list:       # check action has or hasn't been defined
                self.csocket.send(json.dumps(['Error', 'invalid action']).encode())
                break

            if not filename:        # check filename is empty
                self.csocket.send(json.dumps(['Waring', 'filename can\'t empty']))
                break

            if device_name in microphones:       # check microphone has or hasn't been defined
                if microphones_status[device_name].isLock:
                    if action in action_list[:2]:
                        self.csocket.send(json.dumps(['please wait.', 'this device on using.']).encode())
                        break
                device = microphones[device_name]
                microphones_status[device_name].lock()  # lock microphone device

            print(f'client action: {action}, filename: {filename}, device: {device}')

            sfs = SFS.SmartFactoryService(filename=filename, device=device, queue=queue, gpu_lock=gpu_lock)

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

            result_list = queue.get()
            result = json.dumps(result_list)
            microphones_status[device_name].unlock()   # unlock microphone device
            self.csocket.send(result.encode())
            self.csocket.close()
            break
        print("Client at ", clientAddress, " disconnected...")


def boot_init() -> None:
    boot_device = ''
    queue = Queue()
    os_devices = sd.query_devices()
    for device in os_devices:
        if re.search(Audio.DEVICE_1, device['name']) is not None:
            boot_device = Audio.DEVICE_1
        elif re.search(Audio.DEVICE_2, device['name']) is not None:
            boot_device = Audio.DEVICE_2

    print('boot initiation device', boot_device)

    if boot_device:
        sfs = SFS.SmartFactoryService(filename='boot_init', device=boot_device, queue=queue, gpu_lock=gpu_lock)
        sfs.boot_init()
        queue.get()


boot_init()     # boot initiation

LOCALHOST = ""
PORT = 8080
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((LOCALHOST, PORT))

print("Server started")
print("Waiting for client request..")

while True:
    server.listen(1)
    clientsock, clientAddress = server.accept()
    newthread = ClientThread(clientAddress, clientsock)
    newthread.start()
