#!/usr/bin/python3

import os
import glob
import shutil
import tarfile
from config import Configuration

CONFIG = Configuration()

home = os.path.expanduser("~")

with tarfile.open('new_version.tar.gz', 'r:gz') as tf:
    def is_within_directory(directory, target):
        
        abs_directory = os.path.abspath(directory)
        abs_target = os.path.abspath(target)
    
        prefix = os.path.commonprefix([abs_directory, abs_target])
        
        return prefix == abs_directory
    
    def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
    
        for member in tar.getmembers():
            member_path = os.path.join(path, member.name)
            if not is_within_directory(path, member_path):
                raise Exception("Attempted Path Traversal in Tar File")
    
        tar.extractall(path, members, numeric_owner=numeric_owner) 
        
    
    safe_extract(tf)

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
