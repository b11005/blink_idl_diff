#!/usr/bin/env python

import subprocess
import sys
import os

python = 'python'


def get_filepath(dir_path, path_file):
    imput1 = 'Source/bindings/scripts/interface_node_path.py'
    subprocess.check_output([python, imput1, dir_path, path_file])
    return path_file


def create_json(path_file, json):
    imput2 = 'Source/bindings/scripts/collect_idls_into_json.py'
    subprocess.check_output([python, imput2, path_file, json])
    return json


def make_diff(json1, json2):
    imput3 = 'Source/bindings/scripts/generate_idl_diff.py'
    diff = '/usr/local/google/home/natsukoa/trial/chromium_diff.json'
    subprocess.check_output([python, imput3, json1, json2, diff])
    return diff


def print_result(diff):
    imput4 = 'Source/bindings/scripts/print_idl_diff.py'
    order = "ALPHABET"
    return subprocess.call([python, imput4, diff, order])


def main(argv):
    dir_path1 = os.path.abspath('Source/')
    path_file1 = '/usr/local/google/home/natsukoa/trial/test1.txt'
    file_path1 = get_filepath(dir_path1, path_file1)
    json_file1 = '/usr/local/google/home/natsukoa/trial/test_sample1.json'
    file_path1 = ('/usr/local/google/home/natsukoa/trial/test1.txt')
    json1 = create_json(file_path1, json_file1)
    dir_path2 = '/usr/local/google/home/natsukoa/chromium1/src/third_party/WebKit/Source'
    path_file2 = '/usr/local/google/home/natsukoa/trial/test2.txt'
    file_path2 = get_filepath(dir_path2, path_file2)
    json_file2 = '/usr/local/google/home/natsukoa/trial/test_sample2.json'
    json2 = create_json(file_path2, json_file2)
    diff = make_diff(json1, json2)
    call = print_result(diff)


if __name__ == '__main__':
    main(sys.argv[1:])
