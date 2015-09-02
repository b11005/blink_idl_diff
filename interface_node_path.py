#!/usr/bin/env python

"""Usage: interface_node_path.py directory-path text_file

The goal of this script is to integrate IDL file path under the directory to text file.
"""
import os
import sys

_IDL_SUFFIX = '.idl'
_NON_IDL_FILES = frozenset([
    'InspectorInstrumentation.idl',
])


def get_idl_files(path):
    """Return a generator which has absolute path of IDL files.
    Args:
      path: directory path
    Return:
      generator, absolute IDL file path
    """
    for dir_path, dir_names, file_names in os.walk(path):
        for file_name in file_names:
            if file_name.endswith(_IDL_SUFFIX) and file_name not in _NON_IDL_FILES:
                yield os.path.join(dir_path, file_name)


def main(args):
    path = args[0]
    filename = args[1]
    with open(filename, 'w') as f:
        for filepath in get_idl_files(path):
            f.write(filepath + '\n')


if __name__ == '__main__':
    main(sys.argv[1:])
