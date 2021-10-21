#!/usr/bin/python3

import os
import glob
import shutil
import tarfile
from config import Configuration

CONFIG = Configuration()

home = os.path.expanduser("~")

with tarfile.open('new_version.tar.gz', 'r:gz') as tf:
    tf.extractall()

if os.path.exists('./dist/version.txt'):
    with open('./dist/version.txt', 'r') as file:
        txt = file.readline()
        txt = txt.splitlines()[0]
        print('==========')
        print(f'update to {txt} version')
        print('==========')
        CONFIG.version = txt
        CONFIG.save()

    os.remove('./dist/version.txt')

files = glob.glob('./dist/*.*')

for file in files:
    shutil.copy(file, home)


os.remove('new_version.tar.gz')
shutil.rmtree('dist')
