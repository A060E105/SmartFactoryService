"""
    author: Jin-Mo,Lin
    email: s106003041@g.ksu.edu.tw
    Version: 2.0.0
    description: Windows platform client UI
"""
import datetime
import json
import re
import socket
import platform
# check device mount
import subprocess
import threading
from subprocess import PIPE
import time
import tkinter as tk
import tkinter.font as tkFont
from tkinter import Menu
from tkinter import messagebox
from tkinter.ttk import Progressbar

import os
import sys
sys.path.append('')

# I/O Control
if platform.system() == 'Linux':
    from FactoryControl import IOCtrl, MyGPIO, VirtualIO
else:
    from FactoryControl import IOCtrl, VirtualIO

# config
from config import Configuration
# write data to csv
from storage import storage as STORAGE
# logger
from Logger import get_logger

# from database import AI

# ==============================================================================
#   Global variable
# ==============================================================================
log = get_logger()
CONFIG = Configuration()
STATUS_MESSAGE = CONFIG.status_message
SAVE_SWITCH: tk.StringVar = None
SERVER_STATUS_DIV: tk.Frame = None
SERVER_STATUS_TEXT: tk.Label = None
TV_QR_CODE: tk.Label = None
TV_STATUS: tk.Label = None
TABLE: tk.ttk.Treeview = None
RESULT: tk.Label = None
WINDOW: tk.Tk = None
FONT: tkFont.Font = None
# ==============================================================================
#   UI
# ==============================================================================
UI = {
    'color': {
        "primary_color": 'gray',
        "success_color": 'green',
        "error_color": 'red'
    },
    'qr_code': ''
}


def defined_layout_weight(obj, cols=1, rows=1):
    def method(trg, col, row):
        for c in range(col):
            trg.columnconfigure(c, weight=1)
        for r in range(row):
            trg.rowconfigure(r, weight=1)

    if type(obj) == list:
        [method(trg, cols, rows) for trg in obj]
    else:
        trg = obj
        method(trg, cols, rows)


def create_layout(div: tk.Frame):
    global WINDOW
    global SAVE_SWITCH
    global SERVER_STATUS_DIV
    global SERVER_STATUS_TEXT
    global TV_QR_CODE
    global TV_STATUS
    global RESULT
    global TABLE

    WINDOW.update()
    screen_width = WINDOW.winfo_screenwidth()
    wh = WINDOW.winfo_height()
    ww = WINDOW.winfo_width()
    div_w = div.winfo_width()
    div_h = div.winfo_height()

    radio_font = tkFont.Font(size=30)

    control_save_div = tk.Frame(div, bg=UI.get('color').get('primary_color'))
    control_save_div.place(relx=0.1, rely=0.05)
    # switch save methods
    SAVE_SWITCH = tk.StringVar(value='local')
    btn_local = tk.Radiobutton(control_save_div, text='本地儲存', variable=SAVE_SWITCH,
                               bg=UI.get('color').get('primary_color'),
                               indicatoron=False, value='local', width=10, font=radio_font)
    btn_local.pack(side='left')

    # server status div
    SERVER_STATUS_DIV = tk.Frame(div, bg='yellow', padx=5, pady=5)
    SERVER_STATUS_DIV.place(relx=0.7, rely=0.05)

    SERVER_STATUS_TEXT = tk.Label(SERVER_STATUS_DIV)
    SERVER_STATUS_TEXT.config(text='系統初始化中', bg=UI.get('color').get('primary_color'), font=FONT)
    SERVER_STATUS_TEXT.pack(side='left')

    # control div
    control_div = tk.Frame(div, bg=UI.get('color').get('primary_color'))
    control_div.place(relx=0.1, rely=0.15)

    # 麥克風校正、啟動異音檢測 按鈕
    clib_btn_bg = tk.Frame(control_div, highlightbackground='black', highlightthickness=2, bd=0)
    start_btn_bg = tk.Frame(control_div, highlightbackground='black', highlightthickness=2, bd=0)
    clib_btn = tk.Button(clib_btn_bg, text='麥克風校正',
                          bg=UI.get('color').get('primary_color'),
                          font=radio_font, width=15, command=calibration)
    start_btn = tk.Button(start_btn_bg, text='開始異音檢測',
                          bg=UI.get('color').get('primary_color'), font=radio_font, width=15,
                          command=btn_start_analysis)
    clib_btn_bg.pack(side='left')
    start_btn_bg.pack(side='left', padx=100)
    start_btn.pack(side='left')
    clib_btn.pack(side='left')

    # title div
    title_div = tk.Frame(div, bg=UI.get('color').get('primary_color'))
    title_div.place(relx=0.1, rely=0.3)

    # in title div
    title = tk.Label(title_div, anchor='e', justify='left')
    discription = '麥克風校正： 錄音後計算校正值。\n' \
                  '異音檢測： 錄音後進行分析，快捷鍵為：空白鍵。\n'
    title.config(text=discription, font=('Times', 20, 'italic'), bg=UI.get('color').get('primary_color'))
    title.grid(column=0, row=0)

    # status
    status_div = tk.Frame(div)
    status_div.config(bg=UI.get('color').get('primary_color'))
    status_div.place(relx=0.1, rely=0.5)

    tv_status_label = tk.Label(status_div)
    tv_status_label.config(text='狀態：', bg=UI.get('color').get('primary_color'), font=FONT)
    tv_status_label.grid(column=0, row=0)

    TV_STATUS = tk.Label(status_div)
    TV_STATUS.config(text=STATUS_MESSAGE['wait_for_press'], bg=UI.get('color').get('primary_color'), font=FONT)
    TV_STATUS.grid(column=1, row=0)
    # TV_STATUS.place(relx=0.1, rely=0.5)

    # result table
    column = ['時間', '檔案名稱', '結果']
    text_size = 20
    column_width = [0.25, 0.4, 0.2]
    heading_style = tk.ttk.Style()
    column_style = tk.ttk.Style()
    heading_style.configure('Treeview.Heading', font=(None, text_size))
    column_style.configure('Treeview', rowheight=35, font=(None, text_size))
    TABLE = tk.ttk.Treeview(div, height=5, column=column, show='headings')
    for col, width in zip(column, column_width):
        TABLE.heading(col, text=col)
        TABLE.column(col, anchor='center', width=int(screen_width*width))

    TABLE.place(relx=0.05, rely=0.7)

    # result div
    RESULT = tk.Label(div, width=10)
    RESULT.config(text='', font=tkFont.Font(size=70), bg=UI['color']['primary_color'])
    # RESULT.config(text='NG', font=FONT, bg=UI['color']['error_color'])
    RESULT.place(relx=0.6, rely=0.5)


# ==============================================================================
#   UI window
# ==============================================================================
def init_layout():
    global WINDOW
    global FONT
    WINDOW = tk.Tk()
    FONT = tkFont.Font(size=50)
    align_mode = 'nswe'
    pad = 10

    screen_width = WINDOW.winfo_screenwidth()
    screen_height = WINDOW.winfo_screenheight()

    WINDOW.title(f'Smart Factory-{CONFIG.version}')

    defined_layout_weight(WINDOW, cols=1, rows=1)

    # div_size = 1200
    div1 = tk.Frame(WINDOW, width=screen_width, height=screen_height, bg=UI.get('color').get('primary_color'))
    # div2 = tk.Frame(WINDOW, width=div_size, height=div_size, bg=primary_color)

    div1.grid(padx=pad, pady=pad, sticky=align_mode, column=0, row=0)
    # div2.grid(padx=pad, pady=pad, sticky=align_mode, column=1, row=0)

    for div in [div1]:
        create_layout(div)


# ==============================================================================
#  show / clear QR Code
# ==============================================================================
def set_status(txt):
    global WINDOW
    global TV_STATUS
    TV_STATUS.config(text=txt)
    WINDOW.update()


def table_insert(value):
    global TABLE
    TABLE.insert('', 0, value=value)


def table_clean():
    global TABLE

    for item in TABLE.get_children():
        TABLE.delete(item)


def create_new_csv():
    STORAGE.create()
    table_clean()


def calibration() -> None:
    hide_result()
    disable_start_btn()

    set_status(STATUS_MESSAGE['calibration'])
    response = send_socket(action='get_cali', filename='cali', config_name='mic_default')
    try:
        if response.get('status'):
            raise BaseException

        result = response.get('result')
        messagebox.showinfo(title='Success', message=f"Calibration Success")
        msg_response = messagebox.askquestion(title='Do you want to save?', message=f'Cali: {result[0]}')
        if msg_response == 'yes':
            set_response = send_socket(action='set_cali', filename=result[0], config_name='mic_default')
            set_result = set_response.get('result')
            messagebox.showinfo(title='Success', message=set_result[0])
    except BaseException:
        show_error(response.get('status'))
        threading.Thread(target=check_server_start, args=(True,)).start()
    finally:
        set_status(STATUS_MESSAGE['wait_for_press'])
        enable_start_btn()


def show_result(result: str) -> None:
    global WINDOW
    global RESULT
    if result == 'OK':
        RESULT.config(text='OK', bg=UI['color']['success_color'])
    else:
        RESULT.config(text='NG', bg=UI['color']['error_color'])
    WINDOW.update()


def hide_result() -> None:
    global WINDOW
    global RESULT
    RESULT.config(text='', bg=UI['color']['primary_color'])
    WINDOW.update()


def restart_server() -> None:
    """
    重新啟動系統伺服器

    :return: None
    """
    execute_path = os.path.join(os.path.expanduser('~'), '.conda', 'envs', 'SmartFactory', 'pythonw.exe')
    os.system('taskkill /im pythonw.exe /f')    # kill pythonw execute
    os.system(f'start {execute_path} thread_server.py')
    log.info('restart system')
    threading.Thread(target=check_server_start).start()


# ==============================================================================
#   Menu
# ==============================================================================
def init_menu():
    menu = Menu(WINDOW)
    new_item = Menu(menu, tearoff=0)
    server_item = Menu(menu, tearoff=0)

    menu.add_cascade(label='選項', menu=new_item)
    # new_item.add_command(label='麥克風校正', command=calibration)
    # new_item.add_separator()
    new_item.add_command(label='建立新CSV檔', command=create_new_csv)

    menu.add_cascade(label='系統', menu=server_item)
    server_item.add_command(label='重新啟動', command=restart_server)

    WINDOW.config(menu=menu)


# ==============================================================================
#   Smart Factory main methods
# ==============================================================================
def show_error(code):
    parser_error_code = {
        1: '系統沒有回應，重新連接中。',
        2: '請檢查麥克風裝置是否連接。',
        3: '無效的動作指令。',
        4: '檔案名稱不可為空。',
        5: '麥克風正在使用中，請稍後再進行操作。'
    }
    # msg = '請重新啟動程式，或重新開機。'
    error_code = f'Error code[{code}]'
    error_msg = parser_error_code[code] + error_code
    messagebox.showerror(title='Error', message=error_msg)


def send_socket(action='all', filename='', config_name=None) -> dict:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect(('127.0.0.1', CONFIG.port))

            while True:
                try:
                    request = json.dumps([action, filename, 'default', config_name])
                    client.send(request.encode())

                    read_data = json.loads(client.recv(4096).decode('utf-8'))
                    # print(f'result: {read_data}')
                    return read_data
                except KeyboardInterrupt:
                    pass
                finally:
                    client.close()
    except Exception:
        log.info('connection fail')
        return {'status': 1, 'result': ['']}


def get_file_name() -> str:
    timestamp = int(time.time())
    device_name = CONFIG.device_name

    filename = f"{timestamp}_{device_name}"
    return filename


def start_analysis(event):
    global SAVE_SWITCH

    disable_start_btn()
    hide_result()

    current_file_name = get_file_name()
    print(f"file name: {current_file_name}")
    print(f"device: {CONFIG.mic_default_name}")

    set_status(STATUS_MESSAGE['recording'])
    response = send_socket(filename=current_file_name, config_name='mic_default')       # send data to server
    log.debug(f'response: {response}')

    try:
        if response.get('status'):
            raise BaseException

        ok_count = 0
        for item in response.get('result'):
            # 計算 OK 的數量
            if item == 'OK':
                ok_count += 1

        # OK 的數量必須大於一半
        if ok_count > len(response.get('result'))/2:
            result = 'OK'
        else:
            result = 'NG'

        show_result(result)
        timestr = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        table_insert([timestr, current_file_name, result])
        STORAGE.write(time=timestr,
                      filename=current_file_name, code=UI['qr_code'],
                      device=CONFIG.device_name, model=CONFIG.model_name,
                      result=result)

        # remote
        # if SAVE_SWITCH.get() == 'remote':
        #     AI.create(pro_serial=UI['qr_code'], device_name=config.device_name, file_name=current_file_name,
        #               test_time=timestr, model_name=config.model_name, result=result)
    except BaseException:
        show_error(response.get('status'))
        threading.Thread(target=check_server_start, args=(True,)).start()
    finally:
        set_status(STATUS_MESSAGE['wait_for_press'])
        enable_start_btn()  # enable start button


def btn_start_analysis():
    start_analysis('')


def check_remote_backup_path() -> None:
    """
    檢查遠端備份的路徑是否存在

    :return: None
    """
    backup_path = CONFIG.remote_backup_path.replace('\\', '/')
    if not os.path.exists(backup_path):
        log.warning(f'not found remote backup path')
        messagebox.showwarning('警告', '找不到遠端備份路徑')


def check_server_start(reconnected: bool = False) -> None:
    """
    檢查伺服器是否啟動，需與 threading.Thread 配合

    :param reconnected:
    :return: None
    """
    server_initialized()    # UI show initialized message
    for i in range(5):
        if reconnected:
            reconnected_server(i + 1)
        result = send_socket('check', 'check')
        if result.get('status') == 'OK':
            server_start_success()      # UI show success message
            log.info('server has start')
            return
        time.sleep(6)

    server_start_fail()     # UI show fail message
    log.info('server has not start')


def server_start_success() -> None:
    """
    伺服器正常啟動

    :return: None
    """
    global SERVER_STATUS_DIV
    global SERVER_STATUS_TEXT
    SERVER_STATUS_DIV.config(bg=UI.get('color').get('success_color'))
    SERVER_STATUS_TEXT.config(text='系統已啟動')


def server_start_fail() -> None:
    """
    伺服器未啟動

    :return: None
    """
    global SERVER_STATUS_DIV
    global SERVER_STATUS_TEXT
    SERVER_STATUS_DIV.config(bg=UI.get('color').get('error_color'))
    SERVER_STATUS_TEXT.config(text='系統未啟動')


def server_initialized() -> None:
    """
    伺服器初始化中

    :return: None
    """
    global SERVER_STATUS_DIV
    global SERVER_STATUS_TEXT
    SERVER_STATUS_DIV.config(bg='yellow')
    SERVER_STATUS_TEXT.config(text='系統初始化中')


def reconnected_server(count: int) -> None:
    global SERVER_STATUS_DIV
    global SERVER_STATUS_TEXT
    SERVER_STATUS_DIV.config(bg='yellow')
    SERVER_STATUS_TEXT.config(text=f'重新連接中...{count}')


# ==============================================================================
#   I/O Control
# ==============================================================================

virtual_io = VirtualIO()
virtual_io.set_callback(start_analysis)
io_ctrl = IOCtrl(virtual_io)


def disable_start_btn() -> None:
    """
        取消監聽啟動按鈕
    """
    io_ctrl.disable()


def enable_start_btn() -> None:
    """
        監聽啟動按鈕
    """
    io_ctrl.enable()


# ==============================================================================
#   window main loop
# ==============================================================================
init_layout()
init_menu()
# TODO(): check server has start method
threading.Thread(target=check_server_start).start()
threading.Thread(target=check_remote_backup_path).start()
WINDOW.mainloop()
io_ctrl.cleanup()
print('end program')

