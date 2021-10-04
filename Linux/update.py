#!/usr/bin/python3

import os
import glob
import shutil
import tarfile

home = os.path.expanduser("~")

with tarfile.open('new_version.tar.gz', 'r:gz') as tf:
    tf.extractall()

files = glob.glob('./dist/*.*')

for file in files:
    shutil.copy(file, home)


os.remove('new_version.tar.gz')
shutil.rmtree('dist')
