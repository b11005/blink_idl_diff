#!/usr/bin/env python

import os, sys

def get_idl_files(dir):
    file_type='.idl'
    non_idl_set = (
        'InspectorInstrumentation.idl',
    )
    for dir_path, dir_names, file_names in os.walk(dir):
        for file_name in file_names:
            if file_name.endswith(file_type) and file_name not in non_idl_set:
                yield os.path.join(dir_path, file_name)


def main(args):
    path = args[0]
    for filepath  in get_idl_files(path):
        print filepath


if __name__ == '__main__':
    main(sys.argv[1:])
