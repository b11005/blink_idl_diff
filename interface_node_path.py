#!/usr/bin/env python

import os, sys

chromium_path = os.path.abspath(
    os.path.join(os.environ['HOME'], 'chromium', 'src'))
blink_bindings_path = os.path.join(
    chromium_path, 'third_party', 'WebKit', 'Source', 'bindings', 'scripts')
sys.path.insert(0, blink_bindings_path)

from blink_idl_parser import parse_file, BlinkIDLParser

def get_idl_files(dir):
    file_type='.idl'
    non_idl_set = (
        'InspectorInstrumentation.idl',
    )
    for dir_path, dir_names, file_names in os.walk(dir):
        for file_name in file_names:
            if file_name.endswith(file_type) and file_name not in non_idl_set:
                yield os.path.join(dir_path, file_name)


def get_interface_nodes(dir_path):
    parser = BlinkIDLParser(debug=False)
    class_name = 'Interface' 
    for idl_node in get_idl_files(dir_path):
        node_path = idl_node
        definitions = parse_file(parser, idl_node)
        for definition in definitions.GetChildren():
            if definition.GetClass() == class_name:
                yield node_path


def main(args):
    path = args[0]
    filename = args[1]
    interface_path_list = [node_path for node_path in get_interface_nodes(path)]
    #print interface_path
    #with open(filename) as f:
    f = open(filename, 'w')
    for interface_path in interface_path_list:
        f.write(interface_path + '\t')
    f.close()


if __name__ == '__main__':
    main(sys.argv[1:])
