#!/usr/bin/env python

import os, sys, pdb, json

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

def getAttribute(interface_node):
    for attribute in interface_node.GetListOf('Attribute'):
        yield attribute.GetName()


def getAttributeType(interface_node):
    for attribute in interface_node.GetListOf('Attribute'):
        yield attribute.GetListOf('Type')[0].GetChildren()[0].GetName()
    

def getOperation(interface_node):
    for operation in interface_node.GetListOf('Operation'):
        yield operation


def getArgument(interface_node):
    for operation in getOperation(interface_node):
        argument_node = operation.GetListOf('Arguments')[0]
        yield argument_node.GetListOf('Argument')


def make_interface_dict(interface_node):

        #argument_list = [argument.GetName() for arguments in getArgument(interface_node) for argument in arguments]
        #print argument_list
        interface_dict = {}
        interface_dict['Interface Name'] = interface_node.GetName()
        #'FilePath':,
        interface_dict['Attribute'] = {'Name':attr_name for attr_name in getAttribute(interface_node)}
        interface_dict['Attribute'].update({'Type':attr_type for attr_type in getAttributeType(interface_node)})
        interface_dict['Operation'] = {'Name': operation.GetName() for operation in getOperation(interface_node)}
        interface_dict['Operation'].update({'Argument':[argument.GetName() for arguments in getArgument(interface_node) for argument in arguments]})
        return interface_dict
        #print interface_dict

def make_jsonfile(dictionary):
    filename = 'sample.json'
    indent_size = 4
    f = open(filename, 'a')
    json.dump(dictionary, f, sort_keys = True, indent = indent_size)
    f.close()



def main(args):
    path = args[0]
    #make_jsonfile([dictronary for dictronary in make_interface_dict(path)])
    partial_or_nonpartial = non_partial
    for interface_node in partial_or_nonpartial(getInterfaceNodes(path)):
        dictionary = make_interface_dict(interface_node)
        make_jsonfile(dictionary)
        #make_interface_dict(interface_node)

if __name__ == '__main__':
    main(sys.argv[1:])
   
