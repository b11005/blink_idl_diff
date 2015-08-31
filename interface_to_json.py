#!/usr/bin/env python

"""Usage: interface_to_json.py [text file which has idl file pathes] [json file name]
"""

import os
import sys
import json

from blink_idl_parser import parse_file, BlinkIDLParser


def load_filepath(path_file):
    for line in open(path_file, 'r'):
        path = line[:-1].split('\t')
        yield ','.join(map(str, path))


def get_interface_nodes(path):
    parser = BlinkIDLParser(debug=False)
    class_name = 'Interface'
    for node_path in load_filepath(path):
        definitions = parse_file(parser, node_path)
        for definition in definitions.GetChildren():
            if definition.GetClass() == class_name:
                yield definition


def get_filepath(interface_node):
    filename = interface_node.GetProperty('FILENAME')
    return os.path.relpath(filename)


def get_partial(interface_node_list):
    for interface_node in interface_node_list:
        if interface_node.GetProperty('Partial', default=False):
            yield interface_node


def get_non_partial(interface_node_list):
    for interface_node in interface_node_list:
        if not interface_node.GetProperty('Partial', default=False):
            yield interface_node


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
        attr_dict = {}
        attr_dict['Name'] = attribute.GetName()
        attr_dict['Type'] = get_type(attribute)
        attr_dict['ExtAttributes'] = [extattr for extattr in extattr_dict(attribute) if extattr]
        yield attr_dict


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
        yield arg_dict


def get_operation_name(operation):
    if operation.GetProperty('GETTER', default=None):
        return '__getter__'
    elif operation.GetProperty('SETTER', default=None):
        return '__setter__'
    elif operation.GetProperty('DELETER', default=None):
        return '__deleter__'
    else:
        return operation.GetName()


def operation_dict(interface_node):
    for operation in get_operations(interface_node):
        operate_dict = {}
        operate_dict['Name'] = get_operation_name(operation)
        operate_dict['Argument'] = [args for args in argument_dict(operation) if is args]
        operate_dict['Type'] = get_type(operation)
        operate_dict['ExtAttributes'] = [extattr for extattr in extattr_dict(operation) if extattr]
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
    interface_dict['Attribute'] = [attr for attr in attributes_dict(interface_node) if attr]
    interface_dict['Operation'] = [operation for operation in operation_dict(interface_node) if operation]
    interface_dict['ExtAttributes'] = [extattr for extattr in extattr_dict(interface_node) if extattr]
    interface_dict['Constant'] = [const for const in const_dict(interface_node) if const]
    return interface_dict


def merge_partial_interface(interface_dict_list, partial_dict_list):
    for partial in partial_dict_list:
        for interface in interface_dict_list:
            if interface['Name'] == partial['Name']:
                interface['Attribute'].append(partial['Attribute'])
                interface['Operation'].append(partial['Operation'])
                interface['ExtAttributes'].append(partial['ExtAttributes'])
                interface.setdefault('Partial_FilePath', []).extend(partial['FilePath'])
                if interface['Constant']:
                    interface.setdefault('Constant', []).extend(partial['Constant'])
    return interface_dict_list


def format_dictionary(dictionary_list):
    dictionary = {}
    for interface_dict in dictionary_list:
        dictionary.setdefault(interface_dict['Name'], interface_dict)
    return dictionary


def export_jsonfile(dictionary, json_file):
    filename = json_file
    indent_size = 4
    f = open(filename, 'w')
    json.dump(dictionary, f, sort_keys=True, indent=indent_size)
    f.close()


def main(args):
    path_file = args[0]
    json_file = args[1]
    interface_dict_list = [format_interface_dict(interface_node) for interface_node in get_non_partial(get_interface_nodes(path_file))]
    partial_dict_list = [format_interface_dict(interface_node) for interface_node in get_partial(get_interface_nodes(path_file))]
    dictionary_list = merge_partial_interface(interface_dict_list, partial_dict_list)
    dictionary = format_dictionary(dictionary_list)
    export_jsonfile(dictionary, json_file)


if __name__ == '__main__':
    main(sys.argv[1:])
