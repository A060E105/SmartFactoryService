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
from storage import Storage

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
config = Configuration()
storage = Storage()
button_lock = False
qr_code_text = ''
result = ''
status_message = config.status_message
# ==============================================================================
#   UI
# ==============================================================================

primary_color = 'gray'
success_color = 'green'
error_color = 'red'


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


def create_layout(div):
    global window
    global QR_code_switch
    global save_switch
    global tv_QR_Code
    global tv_status
    window.update()
    wh = window.winfo_height()
    ww = window.winfo_width()
    div_w = div.winfo_width()
    div_h = div.winfo_height()

    # control div
    control_div = tk.Frame(div, bg=primary_color)
    control_div.place(relx=0.1, rely=0.05)

    radio_font = tkFont.Font(size=30)
    # switch using QR code
    QR_code_switch = tk.StringVar(value='on')
    use_QR_code = tk.Radiobutton(control_div, text='使用QR Code', variable=QR_code_switch, bg=primary_color,
                                 indicatoron=False, value='on', width=15, font=radio_font)
    non_use_QR_code = tk.Radiobutton(control_div, text='不使用QR Code', variable=QR_code_switch, bg=primary_color,
                                     indicatoron=False, value='off', width=15, font=radio_font)
    use_QR_code.pack(side='left')
    non_use_QR_code.pack(side='left')

    control_save_div = tk.Frame(div, bg=primary_color)
    control_save_div.place(relx=0.1, rely=0.15)
    # switch save methods
    save_switch = tk.StringVar(value='local')
    btn_local = tk.Radiobutton(control_save_div, text='本地儲存', variable=save_switch, bg=primary_color,
                               indicatoron=False, value='local', width=10, font=radio_font)
    btn_remote = tk.Radiobutton(control_save_div, text='遠端儲存', variable=save_switch, bg=primary_color,
                                indicatoron=False, value='remote', width=10, font=radio_font)
    btn_local.pack(side='left')
    btn_remote.pack(side='left')

    # title div
    title_div = tk.Frame(div, bg=primary_color)
    title_div.place(relx=0.1, rely=0.3)

    # in title div
    title = tk.Label(title_div)
    title.config(text='編號:', font=font, bg=primary_color)
    title.grid(column=0, row=0)
    tv_QR_Code = tk.Label(title_div, width=20)
    tv_QR_Code.config(text='', font=font, relief='sunken', borderwidth=3)
    tv_QR_Code.grid(column=1, row=0)

    # status
    tv_status = tk.Label(div)
    tv_status.config(text=status_message['wait_for_press'], bg=primary_color, font=font)
    tv_status.place(relx=0.1, rely=0.45)

    # progress bar div
    progress_bar_div = tk.Frame(div, bg=primary_color)
    progress_bar_div.place(relx=0.1, rely=0.6)
    defined_layout_weight(progress_bar_div)

    # in process bar div
    progress_bar = Progressbar(progress_bar_div, length=int(div_w*0.8), mode='determinate')
    # progress_bar = Progressbar(progress_bar_div, length=int(ww*0.35), mode='indeterminate')
    progress_bar.config(value=20)
    progress_bar.grid(column=0, row=0)

    # result div
    result = tk.Label(div)
    result.config(text='OK', font=font, bg=success_color)
    # result.config(text='NG', font=font, bg=error_color)
    result.place(relx=0.45, rely=0.8)


# ==============================================================================
#   UI window
# ==============================================================================
window = tk.Tk()

font = tkFont.Font(size=50)
align_mode = 'nswe'
pad = 10

window.title(f'Smart Factory-{config.version}')

defined_layout_weight(window, cols=1, rows=1)

div_size = 900
div1 = tk.Frame(window, width=div_size, height=div_size, bg=primary_color)
# div2 = tk.Frame(window, width=div_size, height=div_size, bg=primary_color)

div1.grid(padx=pad, pady=pad, sticky=align_mode, column=0, row=0)
# div2.grid(padx=pad, pady=pad, sticky=align_mode, column=1, row=0)

for div in [div1]:
    create_layout(div)


# ==============================================================================
#  show / clear QR Code
# ==============================================================================

def changeText(txt):
    global tv_QR_Code
    print(f'change txt={txt}')
    tv_QR_Code.config(text=txt)


def clearText():
    global tv_QR_Code
    global qr_code_text
    tv_QR_Code.config(text='')
    qr_code_text = ''


def set_status(txt):
    global tv_status
    tv_status.config(text=txt)


# ==============================================================================
#   Menu
# ==============================================================================
menu = Menu(window)
new_item = Menu(menu, tearoff=0)

menu.add_cascade(label='選項', menu=new_item)


new_item.add_command(label='初始化', command=lambda: messagebox.showinfo('初始化', '初始化'))
new_item.add_separator()
new_item.add_command(label='麥克風校正', command=lambda: messagebox.showinfo('麥克風校正', '麥克風校正'))
new_item.add_separator()
new_item.add_command(label='建立新CSV檔', command=lambda: storage.create())

window.config(menu=menu)


# ==============================================================================
#   bar code
# ==============================================================================
def barcode():
    global qr_code_text
    # ser = serial.Serial('COM3', 115200, timeout=1)  # windows
    ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)  # linux
    set_status('掃描中')
    while True:
        try:
            read_data = ser.readline().decode('ascii')
            time.sleep(1)
            if read_data == '':
                ser.flush()
                continue
            else:
                changeText(read_data)
                qr_code_text = read_data
                print(f'read_data: {read_data}')
                ser.flush()
                set_status('掃描完成')
                break
        except KeyboardInterrupt:
            ser.close()


# ==============================================================================
#   Smart Factory main methods
# ==============================================================================
def send_socket() -> str:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect(('127.0.0.1', config.port))

        while True:
            try:
                request = json.dumps(['all', get_file_name(), 'default'])
                client.send(request.encode())

                read_data = json.loads(client.recv(4096).decode('utf-8'))
                print(f'result: {read_data}')
                ok_count = 0
                for item in read_data:
                    if item == 'OK':
                        ok_count += 1

                if ok_count > len(read_data)/2:
                    result_str = 'OK'
                else:
                    result_str = 'NG'

                return result_str
            except KeyboardInterrupt:
                client.close()

            client.close()


def get_file_name() -> str:
    global QR_code_switch
    timestamp = int(time.time())
    device_name = config.device_name

    if QR_code_switch.get() == 'off':
        filename = f"{timestamp}_{device_name}"
    else:
        filename = f"{qr_code_text}_{timestamp}_{device_name}"

    return filename


def start_analysis(event):
    global QR_code_switch
    global button_lock

    print('press button')

    if button_lock:
        return
    button_lock = True

    if QR_code_switch.get() == 'on':
        print('running barcode scanner')
        barcode()
    else:
        print('running analysis')

    print(f"file name: {get_file_name()}")
    print(f"device: {config.mic_default_name}")

    set_status('等待汽缸下壓')
    while GPIO.input(machine_pin):
        pass

    set_status('下壓完成')
    time.sleep(1)
    set_status('開始錄音')
    result = send_socket()       # send data to server

    storage.write(time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
                  filename=get_file_name(), code=qr_code_text,
                  device=config.device_name, model=config.model_name,
                  result=result)

    set_status('等待中')
    clearText()
    button_lock = False


# ==============================================================================
#   GPIO
# ==============================================================================
input_pin = 18      # BCM model with GPIO 18, BOARD model with Pin 12. start button
machine_pin = 4

GPIO.setmode(GPIO.BCM)

GPIO.setup(input_pin, GPIO.IN)
GPIO.add_event_detect(input_pin, GPIO.FALLING, callback=start_analysis, bouncetime=2000)

GPIO.setup(machine_pin, GPIO.IN)        # 汽缸回傳訊號

# ==============================================================================
#   window main loop
# ==============================================================================
window.mainloop()
GPIO.cleanup()
print('end program')

