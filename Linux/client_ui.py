"""
    author: Jin-Mo,Lin
    email: s106003041@g.ksu.edu.tw
    description:
"""

from os import path
import tkinter as tk
from tkinter import Menu
from tkinter import messagebox
from tkinter.ttk import Progressbar
from tkinter import ttk
from tkinter import filedialog
import tkinter.font as tkFont
import time

# thread
import threading
# barcode
import serial


# ==============================================================================
#   UI
# ==============================================================================

primary_color = 'gray'
success_color = 'green'
error_color = 'red'
progressbar_list = []


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
    window.update()
    wh = window.winfo_height()
    ww = window.winfo_width()
    div_w = div.winfo_width()
    div_h = div.winfo_height()

    # title div
    title_div = tk.Frame(div, bg=primary_color)
    title_div.place(relx=0.1, rely=0.1)

    # in title div
    title = tk.Label(title_div)
    title.config(text='編號:', font=font, bg=primary_color)
    title.grid(column=0, row=0)
    QR_Code = tk.Label(title_div)
    QR_Code.config(text='ABC', font=font, relief='sunken', borderwidth=3)
    QR_Code.grid(column=1, row=0)

    # progress bar div
    progress_bar_div = tk.Frame(div, bg=primary_color)
    progress_bar_div.place(relx=0.1, rely=0.5)
    defined_layout_weight(progress_bar_div)

    # in process bar div
    progress_bar = Progressbar(progress_bar_div, length=int(ww*0.35), mode='determinate')
    # progress_bar = Progressbar(progress_bar_div, length=int(ww*0.35), mode='indeterminate')
    progress_bar.config(value=20)
    progress_bar.grid(column=0, row=0)
    progressbar_list.append(progress_bar)

    # result div
    result = tk.Label(div)
    result.config(text='OK', font=font, bg=success_color)
    # result.config(text='NG', font=font, bg=error_color)
    result.place(relx=0.4, rely=0.8)


# ==============================================================================
#   UI window
# ==============================================================================
window = tk.Tk()

font = tkFont.Font(size=50)
align_mode = 'nswe'
pad = 10

window.title('Smart Factory')

defined_layout_weight(window, cols=2, rows=1)

div_size = 900
div1 = tk.Frame(window, width=div_size, height=div_size, bg=primary_color)
div2 = tk.Frame(window, width=div_size, height=div_size, bg=primary_color)

div1.grid(padx=pad, pady=pad, sticky=align_mode, column=0, row=0)
# div2.grid(padx=pad, pady=pad, sticky=align_mode, column=1, row=0)

for div in [div1]:
    create_layout(div)


# ==============================================================================
#  show / hide QR Code
# ==============================================================================
def show_QRCode() -> None:
    global window
    global QR_Code_center
    fontStyle = tkFont.Font(size=int(60))
    QR_Code_center = tk.Label(window, font=fontStyle)
    txt = 'abcde'
    QR_Code_center.config(text=txt)
    QR_Code_center.place(x=0, y=0)
    center_QRCode()


def hide_QRCode():
    global QR_Code_center
    QR_Code_center.destroy()


def center_QRCode():
    global window
    global QR_Code_center
    window.update()
    h = window.winfo_height()
    w = window.winfo_width()
    mw = QR_Code_center.winfo_width()
    QR_Code_center.place(x=w/2-mw/2, rely=0.7)


def changeText(txt):
    global QR_Code_center
    QR_Code_center.config(text=txt)
    center_QRCode()

def cleanText():
    global QR_Code_center
    QR_Code_center.config(text='')
    center_QRCode()


# ==============================================================================
#   change progressbar value
# ==============================================================================
def step():
    progressbar_list[0]['value'] += 20


def clean_progressbar():
    progressbar_list[0]['value'] = 0


# ==============================================================================
#   Menu
# ==============================================================================
menu = Menu(window)
new_item = Menu(menu, tearoff=0)

menu.add_cascade(label='選項', menu=new_item)


new_item.add_command(label='初始化', command=lambda: messagebox.showinfo('初始化', '初始化'))
new_item.add_separator()
new_item.add_command(label='麥克風校正', command=lambda: messagebox.showinfo('麥克風校正', '麥克風校正'))
new_item.add_command(label='show QR Code', command=show_QRCode)
new_item.add_command(label='hide QR Code', command=hide_QRCode)
new_item.add_command(label='clear QR Code', command=cleanText)
new_item.add_command(label='setp progressbar', command=step)
new_item.add_command(label='clean progressbar', command=clean_progressbar)
new_item.add_command(label='start grogressbar', command=lambda: progressbar_list[0].start())
new_item.add_command(label='stop progressbar', command=lambda: progressbar_list[0].stop())

window.config(menu=menu)


# ==============================================================================
#   bar code
# ==============================================================================
read_barcode = threading.Event()
read_barcode.set()

def borcode():
    ser = serial.Serial('COM3', 115200, timeout=1)
    while True:
        try:
            if read_barcode.is_set():
                readData = ser.readline().decode('ascii')
                time.sleep(1)
                if readData == '':
                    ser.flush()
                    continue
                changeText(readData)
                ser.flush()
            else:
                break
        except KeyboardInterrupt:
            ser.close()


code = threading.Thread(target=borcode)
code.start()


# ==============================================================================
#   window main loop
# ==============================================================================
window.mainloop()
read_barcode.clear()
print('end program')



"""


class UI(Thread):
    LEFT = 0
    RIGHT = 1
    primary_color = 'gray'
    div_size = 900
    pad = 10

    def __init__(self):
        Thread.__init__(self)
        self.wh = 1
        self.ww = 1
        self.qr_code_list = []      # left QR code save in index 0, right save in index 1
        self.progressbar_list = []  # left progressbar object save in index 0, right save in index 1
        self.result_list = []       # left result save in index 0, right save in index 1
        self.window = tk.Tk()
        self.window.title("Class")
        self.font = tkFont.Font(size=50)
        self.__defined_layout_weight(self.window, cols=2, rows=1)
        self.div1 = tk.Frame(self.window, width=self.div_size, height=self.div_size, bg=self.primary_color)
        self.div2 = tk.Frame(self.window, width=self.div_size, height=self.div_size, bg=self.primary_color)
        self.div1.grid(column=0, row=0, padx=self.pad, pady=self.pad, sticky="WSNE")
        self.div2.grid(column=1, row=0, padx=self.pad, pady=self.pad, sticky="WSNE")

        # create left and right layout
        for div in [self.div1, self.div2]:
            self.__create_layout(div)

    def __defined_layout_weight(self, obj, cols=1, rows=1) -> None:
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

    def __create_layout(self, div) -> None:
        self.refresh()
        # title div
        title_div = tk.Frame(div, bg=self.primary_color)
        title_div.place(relx=0.1, rely=0.1)

        # in title div
        title = tk.Label(title_div)
        title.config(text='編號:', font=self.font, bg=self.primary_color)
        title.grid(column=0, row=0)
        qr_code = tk.Label(title_div)
        qr_code.config(text='ABC', font=self.font, relief='sunken', borderwidth=3)
        qr_code.grid(column=1, row=0)
        self.qr_code_list.append(qr_code)


        progress_bar_div = tk.Frame(div, bg=self.primary_color)
        progress_bar_div.place(relx=0.1, rely=0.5)

        # in process bar div
        progress_bar = Progressbar(progress_bar_div, length=int(self.ww*0.35), mode='determinate')
        # progress_bar = Progressbar(progress_bar_div, length=int(self.ww*0.35), mode='indeterminate')
        progress_bar.config(value=20)
        progress_bar.grid(column=0, row=0)
        self.progressbar_list.append(progress_bar)

    def addStep(self):
        self.progressbar_list[0]['value'] += 10
        pass

    def refresh(self) -> None:
        self.window.update()
        self.wh = self.window.winfo_height()
        self.ww = self.window.winfo_width()

    def run(self) -> None:
        self.window.mainloop()


ui = UI()
ui.run()

"""