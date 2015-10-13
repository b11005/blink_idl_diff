#!/usr/bin/env python

import subprocess
import sys

python = 'python'

def get_filepath():
    imput1 = './interface_node_path.py'
    dir_path = '/usr/local/google/home/natsukoa/chromium/src/third_party/WebKit/Source/core/testing'
    path_file = './sample1.txt'
    subprocess.check_output([python,imput1, dir_path, path_file])
    return path_file


def create_json(path_file):
    imput2 = './collect_idls_into_json.py'
    json = 'sample1.json'

    subprocess.check_output([python, imput2, path_file, json])
    return json


def make_diff(json1):
    imput3 = '/usr/local/google/home/natsukoa/chromium/src/third_party/WebKit/Source/bindings/scripts/generate_idl_diff.py'
    json2 = './test1.json'
    diff = 'diff.json'
    subprocess.check_output([python, imput3, json1, json2, diff]) 
    return diff

def print_result(diff):
    imput4 = '/usr/local/google/home/natsukoa/chromium/src/third_party/WebKit/Source/bindings/scripts/print_idl_diff.py'
    order = "TAG"
    return subprocess.check_output([python, imput4, diff, order] )


def main(argv):
    #args = argv[0]
    file_path = get_filepath()
    json1 = create_json(file_path)
    diff = make_diff(json1)
    print_result(diff)


if __name__ == '__main__':
    main(sys.argv[1:])

