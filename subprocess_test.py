#!/usr/bin/env python


import subprocess

imput1 = './interface_node_path.py'
dir_path = '/usr/local/google/home/natsukoa/chromium/src/third_party/WebKit/Source'
path_file = './sample1.txt'

subprocess.check_output(['python',imput1, dir_path, path_file])

imput2 = './collect_idls_into_json.py'
json = 'sample1.json'

subprocess.check_output(['python', imput2, path_file, json])
