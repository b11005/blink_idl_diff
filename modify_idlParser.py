#!/usr/bin/env python

import os, sys, pdb

chromium_path = os.path.abspath(
    os.path.join(os.environ['HOME'], 'chromium', 'src'))
blink_bindings_path = os.path.join(
    chromium_path, 'third_party', 'WebKit', 'Source', 'bindings', 'scripts')
sys.path.insert(0, blink_bindings_path)

from blink_idl_parser import parse_file, BlinkIDLParser

def getIDLFiles(dir):
    file_type='.idl'
    non_idl_set = (
        'InspectorInstrumentation.idl',
    )
    for dir_path, dir_names, file_names in os.walk(dir):
        for file_name in file_names:
            if file_name.endswith(file_type) and file_name not in non_idl_set:
                yield os.path.join(dir_path, file_name)


def getInterfaceNodes(dir_path):
    parser = BlinkIDLParser(debug=False)
    class_name = 'Interface' 
    for file in getIDLFiles(dir_path):
        definitions = parse_file(parser, file)
        for definition in definitions.GetChildren():
            if definition.GetClass() == class_name:
                yield definition


def partial(interface_node_list):
    for interface_node in interface_node_list:
        if interface_node.GetProperty('Partial', default=False):
            yield interface_node  

def non_partial(interface_node_list):
    for interface_node in interface_node_list:
        if not interface_node.GetProperty('Partial', default=False):
            yield interface_node

def getAttributes(interface_node):
    for attribute in interface_node.GetListOf('Attribute'):
        yield attribute


def getOperations(interfaceNode):
    for node in interfaceNode:
        for operation in node.GetListOf('Operation'):
            yield operation


def main(args):
    parser = BlinkIDLParser(debug=False)
    path = args[0]
    partial_or_nonpartial = non_partial
    print 'interface node', [node.GetName() for node in partial_or_nonpartial(getInterfaceNodes(path))]
    print [attr.GetName() for node_list in partial_or_nonpartial(getInterfaceNodes(path)) for attr in getAttributes(node_list)]

if __name__ == '__main__':
    main(sys.argv[1:])
   
