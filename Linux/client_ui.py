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
qr_code_text = ''
current_file_name = ''
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


def create_layout(div: tk.Frame):
    global window
    global QR_code_switch
    global save_switch
    global tv_QR_Code
    global tv_status
    global table
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
    status_div = tk.Frame(div)
    status_div.config(bg=primary_color)
    status_div.place(relx=0.1, rely=0.5)

    tv_status_label = tk.Label(status_div)
    tv_status_label.config(text='狀態：', bg=primary_color, font=font)
    tv_status_label.grid(column=0, row=0)

    tv_status = tk.Label(status_div)
    tv_status.config(text=status_message['wait_for_press'], bg=primary_color, font=font)
    tv_status.grid(column=1, row=0)
    # tv_status.place(relx=0.1, rely=0.5)

    column = ['時間', '序號', '檔案名稱', '結果']
    text_size = 20
    column_width = [0.15, 0.2, 0.3, 0.2]
    heading_style = tk.ttk.Style()
    column_style = tk.ttk.Style()
    heading_style.configure('Treeview.Heading', font=(None, text_size))
    column_style.configure('Treeview', rowheight=35, font=(None, text_size))
    table = tk.ttk.Treeview(div, height=5, column=column, show='headings')
    for col, width in zip(column, column_width):
        table.heading(col, text=col)
        table.column(col, anchor='center', width=int(screen_width*width))

    # for col in column:
    #     table.heading(col, text=col)
    #     table.column(col, anchor='center', width=int(screen_width*0.2))

    table.place(relx=0.05, rely=0.7)

    # result div
    # result = tk.Label(div)
    # result.config(text='OK', font=tkFont.Font(size=70), bg=success_color)
    # # result.config(text='NG', font=font, bg=error_color)
    # result.place(relx=0.8, rely=0.5)


# ==============================================================================
#   UI window
# ==============================================================================
window = tk.Tk()

font = tkFont.Font(size=50)
align_mode = 'nswe'
pad = 10

screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

window.title(f'Smart Factory-{config.version}')

defined_layout_weight(window, cols=1, rows=1)

div_size = 1200
div1 = tk.Frame(window, width=screen_width, height=screen_height, bg=primary_color)
# div2 = tk.Frame(window, width=div_size, height=div_size, bg=primary_color)

div1.grid(padx=pad, pady=pad, sticky=align_mode, column=0, row=0)
# div2.grid(padx=pad, pady=pad, sticky=align_mode, column=1, row=0)

for div in [div1]:
    create_layout(div)


# ==============================================================================
#  show / clear QR Code
# ==============================================================================

def set_serial_code(txt):
    global tv_QR_Code
    tv_QR_Code.config(text=txt)


def clean_serial_code():
    global tv_QR_Code
    global qr_code_text
    tv_QR_Code.config(text='')
    qr_code_text = ''


def set_status(txt):
    global window
    global tv_status
    tv_status.config(text=txt)
    window.update()


def table_insert(value):
    global table
    table.insert('', 0, value=value)


def table_clean():
    global table

    for item in table.get_children():
        table.delete(item)


def create_new_csv():
    storage.create()
    table_clean()


def calibration():
    disable_input_btn()
    set_status(status_message['wait_for_down'])
    machine_down()
    # wait_machine_response()
    while GPIO.input(machine_input_pin):
        pass

    set_status(status_message['calibration'])
    result = send_socket(action='cali', filename='cali', config_name='mic_default')
    if result[0] == 'ok':
        messagebox.showinfo(title='success', message=result[1])
    elif result[0] == 'error':
        messagebox.showerror(title='Error', message=result[1])

    set_status(status_message['wait_for_press'])
    enable_input_btn()

# ==============================================================================
#   Menu
# ==============================================================================
menu = Menu(window)
new_item = Menu(menu, tearoff=0)

menu.add_cascade(label='選項', menu=new_item)


new_item.add_command(label='麥克風校正', command=calibration)
new_item.add_separator()
new_item.add_command(label='建立新CSV檔', command=create_new_csv)

window.config(menu=menu)


# ==============================================================================
#   bar code
# ==============================================================================
def barcode():
    global qr_code_text
    # ser = serial.Serial('COM3', 115200, timeout=1)  # windows
    ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)  # linux
    set_status(status_message['wait_for_scanner'])
    while True:
        try:
            read_data = ser.readline().decode('ascii')
            time.sleep(1)
            if read_data == '':
                ser.flush()
                continue
            else:
                set_serial_code(read_data)
                qr_code_text = read_data
                print(f'read_data: {read_data}')
                ser.flush()
                break
        except KeyboardInterrupt:
            ser.close()


# ==============================================================================
#   Smart Factory main methods
# ==============================================================================
def send_socket(action='all', filename=current_file_name, config_name=None) -> str:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect(('127.0.0.1', config.port))

        while True:
            try:
                request = json.dumps([action, filename, 'default', config_name])
                client.send(request.encode())

                read_data = json.loads(client.recv(4096).decode('utf-8'))
                print(f'result: {read_data}')
                if action == 'cali':
                    return read_data

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
    global current_file_name

    disable_input_btn()

    if QR_code_switch.get() == 'on':
        barcode()

    current_file_name = get_file_name()
    print(f"file name: {current_file_name}")
    print(f"device: {config.mic_default_name}")

    set_status(status_message['wait_for_down'])
    machine_down()
    wait_machine_response()     # 等待汽缸下壓

    set_status(status_message['recording'])
    result = send_socket(filename=current_file_name, config_name='mic_default')       # send data to server

    timestr = datetime.datetime.now().strftime('%Y-%m-%m %H:%M')
    table_insert([timestr, qr_code_text, current_file_name, result])
    storage.write(time=timestr,
                  filename=current_file_name, code=qr_code_text,
                  device=config.device_name, model=config.model_name,
                  result=result)

    set_status(status_message['wait_for_press'])
    clean_serial_code()
    machine_up()        # 汽缸歸位

    # enable input button
    enable_input_btn()


# ==============================================================================
#   GPIO
# ==============================================================================
input_pin = 18      # BCM model with GPIO 18, BOARD model with Pin 12. start button
machine_input_pin = 4
machine_output_pin = 23

GPIO.setmode(GPIO.BCM)

GPIO.setup(input_pin, GPIO.IN)
GPIO.add_event_detect(input_pin, GPIO.FALLING, callback=start_analysis, bouncetime=5000)

GPIO.setup(machine_input_pin, GPIO.IN)        # 汽缸回傳訊號
GPIO.setup(machine_output_pin, GPIO.OUT, initial=GPIO.LOW)        # 汽缸控制訊號，高電位觸發


def disable_input_btn() -> None:
    GPIO.cleanup(input_pin)


def enable_input_btn() -> None:
    GPIO.setup(input_pin, GPIO.IN)
    GPIO.add_event_detect(input_pin, GPIO.FALLING, callback=start_analysis, bouncetime=5000)


def wait_machine_response() -> None:
    """
        等待汽缸回傳
    """
    while GPIO.input(machine_input_pin):
        pass


def machine_up() -> None:
    """
        汽缸上升
    """
    GPIO.output(machine_output_pin, GPIO.HIGH)


def machine_down() -> None:
    """
        汽缸下壓
    """
    GPIO.output(machine_output_pin, GPIO.LOW)


# ==============================================================================
#   window main loop
# ==============================================================================
window.mainloop()
GPIO.cleanup()
print('end program')

