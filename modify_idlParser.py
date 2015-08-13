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
    yield [node_list for node_list in interface_node_list if node_list.GetProperty('Partial', default=False)]


def none_partial(interface_node_list):
    yield [node_list for node_list in interface_node_list if not node_list.GetProperty('Partial', default=False)]


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
    partial_filter = none_partial
    print 'interface node list ', [node.GetName() for nodes in partial_filter(getInterfaceNodes(path)) for node in nodes]
    print [attr.GetName() for nodes_list in partial_filter(getInterfaceNodes(path)) for nodes in nodes_list for attr in getAttributes(nodes)]

if __name__ == '__main__':
    main(sys.argv[1:])
   
