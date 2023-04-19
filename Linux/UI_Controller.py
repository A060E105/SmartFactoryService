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
from PySide6.QtWidgets import QMessageBox

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
    show_error_msg = Signal(str, str)
    table_updated = Signal(pd.DataFrame)
    clear_result = Signal()

    def __init__(self):
        super().__init__()
        # virtual_io = VirtualIO()
        # virtual_io.set_callback(self.start_analysis)
        # self.io_ctrl = IOCtrl(virtual_io)
        self.session = create_session()

    def __del__(self):
        # self.io_ctrl.cleanup()
        pass

    def calibration(self):
        pass

    def start_analysis(self, event=None):
        # self.io_ctrl.disable()
        self.__clear_result()
        filename = f"{int(time.time())}_{CONFIG.device_name}"
        self.__set_status(STATUS_MSG['recording'])
        response = self.__send_socket(filename=filename)
        log.debug(f"response: {response}")

        try:
            if response.get('status'):
                raise Exception

            # updated table
            self.updated_table()

            # TODO(): record to the CSV

        except Exception as e:
            self.__show_error(response.get('status'))
            threading.Thread(target=self.check_server_start, args=(True,)).start()
        finally:
            self.__set_status(STATUS_MSG['wait_for_press'])
            # self.io_ctrl.enable()

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

    def check_server_recording(self) -> None:
        response = self.__send_socket(action='check_recording', filename='check')
        print(response)
        if response.get('status') == 5:
            self.__clear_result()
            self.__set_status(STATUS_MSG['recording'])

    def updated_table(self):
        df = pd.read_sql_query(self.session.query(AIResult).statement, self.session.bind)
        df = df[['file_name', 'decibel', 'ai_score1', 'ai_score2', 'freq_result', 'ai_result', 'final_result',
                 'created_at']]
        self.table_updated.emit(df)

    def __show_error(self, code):
        parser_error_code = {
            0: '程式有其他異常錯誤。',
            1: '系統沒有回應，重新連接中。',
            2: '請檢查麥克風裝置是否連接。',
            3: '無效的動作指令。',
            4: '檔案名稱不可為空。',
            5: '麥克風正在使用中，請稍後再進行操作。'
        }
        error_code = f"Error code[{code}]"
        error_msg = parser_error_code.get(code) + error_code
        self.show_error_msg.emit('Error', error_msg)
        # threading.Thread(target=QMessageBox.critical, args=(None, 'Error', error_msg)).start()

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
        self.clear_result.emit()

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
                        # print('response: ', read_data)
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
