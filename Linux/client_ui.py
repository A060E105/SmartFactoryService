"""
    author: Jin-Mo,Lin
    email: s106003041@g.ksu.edu.tw
    description:
"""
import json
from os import path
import tkinter as tk
from tkinter import Menu
from tkinter import messagebox
from tkinter.ttk import Progressbar
import tkinter.font as tkFont
import time
import datetime

# config
from config import Configuration

# write data to csv
from storage import storage as STORAGE

# from database import AI

# GPIO
import RPi.GPIO as GPIO

import socket

# thread
import threading
from multiprocessing import Queue
# barcode
import serial

# ==============================================================================
#   Global variable
# ==============================================================================
CONFIG = Configuration()
# STORAGE = Storage()
STATUS_MESSAGE = CONFIG.status_message
QR_CODE_SWITCH: tk.StringVar = None
SAVE_SWITCH: tk.StringVar = None
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
    global QR_CODE_SWITCH
    global SAVE_SWITCH
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

    # control div
    control_div = tk.Frame(div, bg=UI.get('color').get('primary_color'))
    control_div.place(relx=0.1, rely=0.05)

    radio_font = tkFont.Font(size=30)
    # switch using QR code
    QR_CODE_SWITCH = tk.StringVar(value='on')

    use_QR_code = tk.Radiobutton(control_div, text='使用QR Code', variable=QR_CODE_SWITCH,
                                 bg=UI.get('color').get('primary_color'),
                                 indicatoron=False, value='on', width=15, font=radio_font)
    non_use_QR_code = tk.Radiobutton(control_div, text='不使用QR Code', variable=QR_CODE_SWITCH,
                                     bg=UI.get('color').get('primary_color'),
                                     indicatoron=False, value='off', width=15, font=radio_font)
    use_QR_code.pack(side='left')
    non_use_QR_code.pack(side='left')

    control_save_div = tk.Frame(div, bg=UI.get('color').get('primary_color'))
    control_save_div.place(relx=0.1, rely=0.15)
    # switch save methods
    SAVE_SWITCH = tk.StringVar(value='local')
    btn_local = tk.Radiobutton(control_save_div, text='本地儲存', variable=SAVE_SWITCH,
                               bg=UI.get('color').get('primary_color'),
                               indicatoron=False, value='local', width=10, font=radio_font)
    # btn_remote = tk.Radiobutton(control_save_div, text='遠端儲存', variable=SAVE_SWITCH, bg=primary_color,
    #                             indicatoron=False, value='remote', width=10, font=radio_font)
    btn_local.pack(side='left')
    # btn_remote.pack(side='left')

    # title div
    title_div = tk.Frame(div, bg=UI.get('color').get('primary_color'))
    title_div.place(relx=0.1, rely=0.3)

    # in title div
    title = tk.Label(title_div)
    title.config(text='編號:', font=FONT, bg=UI.get('color').get('primary_color'))
    title.grid(column=0, row=0)
    TV_QR_CODE = tk.Label(title_div, width=20)
    TV_QR_CODE.config(text='', font=FONT, relief='sunken', borderwidth=3)
    TV_QR_CODE.grid(column=1, row=0)

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
    column = ['時間', '序號', '檔案名稱', '結果']
    text_size = 20
    column_width = [0.15, 0.2, 0.3, 0.2]
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

def set_serial_code(txt):
    global TV_QR_CODE
    TV_QR_CODE.config(text=txt)


def clean_serial_code():
    global TV_QR_CODE
    TV_QR_CODE.config(text='')
    UI['qr_code'] = ''


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
    set_status(STATUS_MESSAGE['wait_for_down'])
    machine_down()
    wait_machine_response()

    set_status(STATUS_MESSAGE['calibration'])
    response = send_socket(action='cali', filename='cali', config_name='mic_default')
    try:
        if response.get('status'):
            raise BaseException

        result = response.get('result')
        messagebox.showinfo(title='success', message=result[0])
    except BaseException:
        show_error(response.get('status'))
    finally:
        set_status(STATUS_MESSAGE['wait_for_press'])
        machine_up()
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


# ==============================================================================
#   Menu
# ==============================================================================
def init_menu():
    menu = Menu(WINDOW)
    new_item = Menu(menu, tearoff=0)

    menu.add_cascade(label='選項', menu=new_item)
    new_item.add_command(label='麥克風校正', command=calibration)
    new_item.add_separator()
    new_item.add_command(label='建立新CSV檔', command=create_new_csv)

    WINDOW.config(menu=menu)


# ==============================================================================
#   bar code
# ==============================================================================
def barcode():
    # ser = serial.Serial('COM3', 115200, timeout=1)  # windows
    try:
        ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)  # linux
        set_status(STATUS_MESSAGE['wait_for_scanner'])
    except serial.serialutil.SerialException:
        messagebox.showerror(title='Error', message='無法連線Barcode Scanner\n1.確認Barcode Scanner正常連接\n2.更換Barcode Scanner')
        return 1

    while True:
        try:
            read_data = ser.readline().decode('ascii')
            time.sleep(1)
            if read_data == '':
                ser.flush()
                continue
            else:
                set_serial_code(read_data)
                UI['qr_code'] = read_data
                # print(f'read_data: {read_data}')
                ser.flush()
                break
        except KeyboardInterrupt:
            ser.close()


# ==============================================================================
#   Smart Factory main methods
# ==============================================================================
def show_error(code):
    parser_error_code = {
        1: '系統正在初始化中，請稍後一分鐘再進行操作。',
        2: '請檢查麥克風裝置是否連接。'
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
        print('connection fail')
        return {'status': 1, 'result': ['']}


def get_file_name() -> str:
    global QR_CODE_SWITCH
    timestamp = int(time.time())
    device_name = CONFIG.device_name

    if QR_CODE_SWITCH.get() == 'off':
        filename = f"{timestamp}_{device_name}"
    else:
        filename = f"{UI['qr_code']}_{timestamp}_{device_name}"

    return filename


def start_analysis(event):
    global QR_CODE_SWITCH
    global SAVE_SWITCH

    disable_start_btn()
    hide_result()

    if QR_CODE_SWITCH.get() == 'on':
        bar_result = barcode()
        if bar_result:  # true 表示有錯誤
            enable_start_btn()
            return

    current_file_name = get_file_name()
    print(f"file name: {current_file_name}")
    print(f"device: {CONFIG.mic_default_name}")

    set_status(STATUS_MESSAGE.get('wait_for_down'))
    machine_down()
    wait_machine_response()     # 等待汽缸下壓

    set_status(STATUS_MESSAGE['recording'])
    response = send_socket(filename=current_file_name, config_name='mic_default')       # send data to server

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
        table_insert([timestr, UI['qr_code'], current_file_name, result])
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
    finally:
        set_status(STATUS_MESSAGE['wait_for_press'])
        clean_serial_code()
        machine_up()        # 汽缸歸位
        enable_start_btn()  # enable start button


# ==============================================================================
#   GPIO
# ==============================================================================
START_INPUT_PIN = 18      # BCM model with GPIO 18, BOARD model with Pin 12. start button
MACHINE_INPUT_PIN = 4
MACHINE_OUTPUT_PIN = 23

GPIO.setmode(GPIO.BCM)

GPIO.setup(START_INPUT_PIN, GPIO.IN)
GPIO.add_event_detect(START_INPUT_PIN, GPIO.FALLING, callback=start_analysis, bouncetime=5000)

GPIO.setup(MACHINE_INPUT_PIN, GPIO.IN)        # 汽缸回傳訊號
GPIO.setup(MACHINE_OUTPUT_PIN, GPIO.OUT, initial=GPIO.LOW)        # 汽缸控制訊號，高電位觸發


def disable_start_btn() -> None:
    GPIO.cleanup(START_INPUT_PIN)


def enable_start_btn() -> None:
    """
        監聽啟動按鈕
    """
    GPIO.setup(START_INPUT_PIN, GPIO.IN)
    GPIO.add_event_detect(START_INPUT_PIN, GPIO.FALLING, callback=start_analysis, bouncetime=5000)


def wait_machine_response() -> None:
    """
        等待汽缸回傳
    """
    while GPIO.input(MACHINE_INPUT_PIN):
        pass
    time.sleep(2)


def machine_up() -> None:
    """
        汽缸上升
    """
    GPIO.output(MACHINE_OUTPUT_PIN, GPIO.LOW)


def machine_down() -> None:
    """
        汽缸下壓
    """
    GPIO.output(MACHINE_OUTPUT_PIN, GPIO.HIGH)


# ==============================================================================
#   window main loop
# ==============================================================================
init_layout()
init_menu()
WINDOW.mainloop()
GPIO.cleanup()
print('end program')

