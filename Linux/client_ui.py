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
import time


def defined_layout(obj, cols=1, rows=1):
    def method(trg, col, row):
        for c in range(col):
            trg.columnconfigure(c, weight=1)
        for r in range(row):
            trg.columnconfigure(r, weight=1)

    if type(obj) == list:
        [method(trg, cols, rows) for trg in obj]
    else:
        trg = obj
        method(trg, cols, rows)


window = tk.Tk()

align_mode = 'nswe'
pad = 10

window.title('Smart Factory')

div_size = 200
img_size = div_size * 2
div1 = tk.Frame(window, width=div_size, height=div_size, bg='blue')
div2 = tk.Frame(window, width=div_size, height=div_size, bg='green')

div1.grid(padx=pad, pady=pad, sticky=align_mode, column=0, row=0)
div2.grid(padx=pad, pady=pad, sticky=align_mode, column=1, row=0)

defined_layout(window, cols=2, rows=2)
defined_layout([div1, div2])


menu = Menu(window)
new_item = Menu(menu, tearoff=0)

new_item.add_command(label='New', command=lambda: messagebox.showinfo('New', 'new'))
new_item.add_separator()
new_item.add_command(label='Edit', command=lambda: messagebox.showinfo('Edit', 'edit'))

menu.add_cascade(label='File', menu=new_item)
window.config(menu=menu)

window.mainloop()

