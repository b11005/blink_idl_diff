#!/usr/bin/env python

import os, sys, json

chromium_path = os.path.abspath(
    os.path.join(os.environ['HOME'], 'chromium', 'src'))
blink_bindings_path = os.path.join(
    chromium_path, 'third_party', 'WebKit', 'Source', 'bindings', 'scripts')
sys.path.insert(0, blink_bindings_path)

from blink_idl_parser import parse_file, BlinkIDLParser

def load_filepath(path_file):
    with open(path_file, 'r') as f:
        return f.read()


def get_interfaces(file_path):
    parser = BlinkIDLParser(debug=False)
    class_name = 'Interface' 
    definitions = parse_file(parser, file_path)
    for definition in definitions.GetChildren():
            if definition.GetClass() == class_name:
                return definition


def get_filepath(interface_node):
    filename = interface_node.GetProperty('FILENAME')
    filepath = os.path.relpath(filename)
    return filepath


def get_partial(interface_node):
    if interface_node.GetProperty('Partial', default=False):
        return interface_node


def get_non_partial(interface_node):
    if not interface_node.GetProperty('Partial', default=False):
        return interface_node


def get_attributes(interface_node):
    return interface_node.GetListOf('Attribute')


def get_type(node):
    return node.GetListOf('Type')[0].GetChildren()[0].GetName()


def get_extattirbutes(node):
    for extattributes in node.GetListOf('ExtAttributes'):
        for extattribute_list in extattributes.GetChildren():
            yield extattribute_list

def extattr_dict(node):
    for extattribute in get_extattirbutes(node):
        yield {
            'Name': extattribute.GetName()
        }

def attributes_dict(interface_node):
    for attribute in get_attributes(interface_node):
        yield {
            'Name': attribute.GetName(),
            'Type': get_type(attribute),
            'ExtAttribute': [extattr for extattr in extattr_dict(attribute)]
        }


def get_operations(interface_node):
    return interface_node.GetListOf('Operation')


def get_arguments(operation):
    argument_node = operation.GetListOf('Arguments')[0]
    return argument_node.GetListOf('Argument')


def argument_dict(argument):
    for arg_name in get_arguments(argument):
        arg_dict = {}
        arg_dict['Name'] = arg_name.GetName()
        arg_dict['Type'] = get_type(arg_name)
        return arg_dict


def get_operation_name(operation):
    if operation.GetProperty('GETTER',default=None):
        return '__getter__'
    elif operation.GetProperty('SETTER',default=None):
        return '__setter__'
    elif operation.GetProperty('DELETER',default=None):
        return '__deleter__'
    else:
        return operation.GetName()


def operation_dict(interface_node):
    operate_dict = {}
    for operation in get_operations(interface_node):
        operate_dict['Name'] = get_operation_name(operation)
        operate_dict['Argument'] = argument_dict(operation)
        operate_dict['Type'] = get_type(operation)
        operate_dict['ExtAttributes'] = [extattr for extattr in extattr_dict(operation)]
        yield operate_dict


def get_consts(interface_node):
    return interface_node.GetListOf('Const')


def get_const_type(node):
    return node.GetChildren()[0].GetName()


def get_const_value(node):
    return node.GetChildren()[1].GetName()


def const_dict(interface_node):
    for const in get_consts(interface_node):
        yield {
            'Name': const.GetName(),
            'Type': get_const_type(const),
            'Value': get_const_value(const)
        }        


def format_interface_dict(interface_node):
    interface_dict = {}
    interface_dict['Name'] = interface_node.GetName()
    interface_dict['FilePath'] = get_filepath(interface_node)
    interface_dict['Attribute'] = [attr for attr in attributes_dict(interface_node)]
    interface_dict['Operation'] = [operation for operation in operation_dict(interface_node)]
    interface_dict['ExtAttributes'] = [extattr for extattr in extattr_dict(interface_node)]
    interface_dict['Constant'] = [const for const in const_dict(interface_node)]
    return interface_dict


def merge_partial_interface(interface_dict, partial_dict_list):
    for partial in partial_dict_list:
        if interface_dict['Name'] == partial['Name']:
            interface_dict['Attribute'].append(partial['Attribute'])
            interface_dict['Operation'].append(partial['Operation'])
            interface_dict['ExtAttributes'].append(partial['ExtAttributes'])
            interface_dict.setdefault('Partial_FilePath', []).append(partial['FilePath'])
            if interface_dict['Constant']:
                interface_dict.setdefault('Constant', []).append(partial['Constant'])
    return interface_dict


def export_jsonfile(dictionary, json_file):
    filename = json_file
    indent_size = 4
    f = open(filename, 'w')
    json.dump(dictionary, f, sort_keys = True, indent = indent_size)
    f.close()


def main(args):
    path_file = args[0]
    jsonfile_name = args[1]
    d = {}
    partial_dict_list = []
    for filepath in load_filepath(path_file).split():
        interface_node = get_interfaces(filepath)
        if not interface_node:
            pass
        elif get_partial(interface_node):
            name = interface_node.GetName()
            if get_non_partial(interface_node):
                d[name] = format_interface_dict(interface_node)
        else:
            name = interface_node.GetName()
            d[name] = format_interface_dict(interface_node)
    export_jsonfile(d, jsonfile_name)
    #for k,v in d.items():
        #print k, v

if __name__ == '__main__':
    main(sys.argv[1:])
