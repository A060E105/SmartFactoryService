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
from typing import Union
from PySide6.QtCore import QObject, Signal

from Logger import get_logger
from config import Configuration
from FactoryControl import IOCtrl, VirtualIO
from database import create_session, AIResult

log = get_logger()
CONFIG = Configuration()
STATUS_MSG = CONFIG.status_message


class UIController(QObject):
    change_text = Signal(str, str)
    change_style = Signal(str, str)
    table_updated = Signal(pd.DataFrame)

    def __init__(self):
        super().__init__()
        virtual_io = VirtualIO()
        virtual_io.set_callback(self.start_analysis)
        self.io_ctrl = IOCtrl(virtual_io)
        self.session = create_session()

    def __del__(self):
        self.io_ctrl.cleanup()

    def calibration(self):
        pass

    def start_analysis(self):
        self.io_ctrl.disable()
        self.__clear_result()
        filename = f"{int(time.time())}_{CONFIG.device_name}"
        self.__set_status(STATUS_MSG['recording'])
        response = self.__send_socket(filename=filename)
        log.debug(f"response: {response}")

        try:
            if response.get('status'):
                raise Exception

            result = response.get('result')[0]
            KDE_score = response.get('KDE_score')[0]
            MSE_score = response.get('MSE_score')[0]

            # updated table
            self.__updated_table()

            # TODO(): show result text
            # TODO(): record to the CSV

        except Exception as e:
            # TODO(): show error message
            print(e)
            threading.Thread(target=self.check_server_start, args=(True,)).start()
        finally:
            self.__set_status(STATUS_MSG['wait_for_press'])
            self.io_ctrl.enable()

    def restart_server(self):
        execute_path = os.path.join(os.path.expanduser('~'), '.conda', 'envs', 'SmartFactory', 'pythonw.exe')
        os.system('taskkill /im pythonw.exe /f')  # kill pythonw execute
        os.system(f'start {execute_path} thread_server.py')
        log.info('restart system')
        threading.Thread(target=self.check_server_start).start()

    def check_server_start(self, reconnected=False):
        # TODO(): server status show initialized message
        self.__set_server_status('initial')
        for i in range(5):
            if reconnected:
                self.__set_server_status('reconnected', i + 1)
            result = self.__send_socket('check', 'check')
            if result.get('status') == 'OK':
                # TODO(): server status show success message
                self.__set_server_status('success')
                return
            time.sleep(6)
        self.__set_server_status('fail')
        # TODO(): server status show fail message

    def __updated_table(self):
        df = pd.read_sql_query(self.session.query(AIResult).statement, self.session.bind)
        df = df[['file_name', 'result', 'kde', 'mse', 'create_at']]
        self.table_updated.emit(df)

    def __set_server_status(self, status, count=None):
        mapping = {
            'initial': {'text': '系統初始化中', 'style': 'yellow'},
            'success': {'text': '系統已啟動', 'style': 'green'},
            'fail': {'text': '系統未啟動', 'style': 'red'},
            'reconnected': {'text': '重新連接中...', 'style': 'yellow'},
        }
        text = mapping.get(status).get('text')
        style = f"border: 3px solid {mapping.get(status).get('style')}"
        if count is not None:
            text += str(count)
        self.__set_view_text('server_status', text)
        self.__set_view_style('server_status', style)

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
        self.__set_view_text('predict_status', text)

    def __set_view_text(self, label: str, text: Union[str, int]):
        """
        設定畫面上的文字，label 為物件名稱
        """
        self.change_text.emit(label, str(text))

    def __set_view_style(self, label: str, style: str):
        """
         設定畫面上的樣式
        """
        self.change_style.emit(label, style)

    @staticmethod
    def __send_socket(action='all', filename='', config_name='mic_default') -> dict:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
                client.connect(('127.0.0.1', CONFIG.port))

                while True:
                    try:
                        request = json.dumps([action, filename, 'default', config_name])
                        client.send(request.encode())

                        read_data = json.loads(client.recv(4096).decode('utf-8'))
                        print('response: ', read_data)
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
