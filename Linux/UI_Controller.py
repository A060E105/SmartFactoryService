"""
UI controller
"""
import os
import sys
import json
import time
import socket
import threading
import pandas as pd
from PySide6.QtCore import QObject, Signal

from Logger import get_logger
from config import Configuration
from FactoryControl import IOCtrl, VirtualIO
from database import create_session, AIResult

log = get_logger()
CONFIG = Configuration()


class UIController(QObject):
    change_text = Signal(str, str)

    def __init__(self):
        super().__init__()
        virtual_io = VirtualIO()
        virtual_io.set_callback(self.start_analysis)
        self.io_ctrl = IOCtrl(virtual_io)

    def __del__(self):
        self.io_ctrl.cleanup()

    def calibration(self):
        pass

    def start_analysis(self):
        self.io_ctrl.disable()
        # TODO(): hide result text
        self.__clear_result()
        filename = f"{int(time.time())}_{CONFIG.device_name}"
        # TODO(): set status text as recording
        self.__set_status('recording...')
        response = self.__send_socket(filename=filename)
        log.debug(f"response: {response}")

        try:
            if response.get('status'):
                raise Exception

            result = response.get('result')[0]
            KDE_score = response.get('KDE_score')[0]
            MSE_score = response.get('MSE_score')[0]
            # TODO(): show result text
            # TODO(): table insert
            # TODO(): record to the CSV

        except Exception as e:
            # TODO(): show error message
            threading.Thread(target=self.check_server_start, args=(True,))
        finally:
            # TODO(): set status text as wait_for_press
            self.io_ctrl.enable()

    def restart_server(self):
        execute_path = os.path.join(os.path.expanduser('~'), '.conda', 'envs', 'SmartFactory', 'pythonw.exe')
        os.system('taskkill /im pythonw.exe /f')  # kill pythonw execute
        os.system(f'start {execute_path} thread_server.py')
        log.info('restart system')
        threading.Thread(target=self.check_server_start).start()

    def check_server_start(self, reconnected=False):
        pass

    def __clear_result(self) -> None:
        """
        清除結果文字
        """
        self.__set_view_text('result', '')

    def __set_result(self, text) -> None:
        """
        設定結果文字
        """
        self.__set_view_text('result', text)

    def __set_status(self, text):
        self.__set_view_text('status', text)

    def __set_view_text(self, label, text):
        """
        設定畫面上的文字，label 為物件名稱
        """
        self.change_text.emit(label, str(text))

    @staticmethod
    def __send_socket(action='all', filename='', config_name=None) -> dict:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
                client.connect(('127.0.0.1', CONFIG.port))

                while True:
                    try:
                        request = json.dumps([action, filename, 'default', config_name])
                        client.send(request.encode())

                        read_data = json.loads(client.recv(4096).decode('utf-8'))
                        return read_data
                    except Exception:
                        pass
                    finally:
                        client.close()
        except Exception as e:
            log.exception('connection fail')
            return {'status': 1, 'result': []}
# ==============================================================================
# ------------------------------------ END -------------------------------------
# ==============================================================================
