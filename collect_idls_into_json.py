#!/usr/bin/env python
# Copyright 2015 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Usage: collect_idls_into_json.py path_file.txt json_file.json

path_file.txt: output of interface_node_path.py #path
"""

import os
import sys
import json

from blink_idl_parser import parse_file, BlinkIDLParser

_class_name = 'Interface'
_partial = 'Partial'


def get_interfaces(path_file):
    """Returns a generator which yields interface IDL nodes.
    Args:
      path_file: text file path
    Returns:
      a generator which yields interface node objects
    """
    def load_filepaths():
        with open(path_file, 'r') as f:
            for line in f:
                path = line.strip()
                yield path
    parser = BlinkIDLParser(debug=False)
    for idl_path in load_filepaths():
        definitions = parse_file(parser, idl_path)
        for definition in definitions.GetChildren():
            if definition.GetClass() == _class_name:
                yield definition


def get_filepath(interface_node):
    """Returns relative path to the IDL file in which the |interface_node| is defined.
    Args:
      interface_node: interface node class object
    Returns:
      str which is interface_node's file path
    """
    filename = interface_node.GetProperty('FILENAME')
    return os.path.relpath(filename)


def get_partial(interface_node_list):
    """Returns a generator which yields partial interface node.
    Args:
      interface_node_list: a generator which is interface IDL node
    Return:
      a generator which yields partial interface node
    """
    for interface_node in interface_node_list:
        if interface_node.GetProperty(_partial):
            yield interface_node


def get_non_partial(interface_node_list):
    """Returns a generator which yields interface node.
    Args:
      interface_node_list: a generator which is interface IDL node
    Returns:
      a generator which yields interface node
    """
    for interface_node in interface_node_list:
        if not interface_node.GetProperty(_partial):
            yield interface_node


def get_attributes(interface_node):
    """Returns list of Attribute that interface_node have.
    Args:
      interface_node: interface node object
    Returns:
      a list of attribute
    """
    return interface_node.GetListOf('Attribute')


def get_attribute_type(attribute):
    """Returns type of attribute or operation's argument.
    Args:
      node: attribute node object
    Returns:
      str which is Attribute object type
    """
    return attribute.GetListOf('Type')[0].GetChildren()[0].GetName()

get_operation_type = get_attribute_type
get_argument_type = get_attribute_type


def get_extattributes(node):
    """Returns a generator which yields Extattribute's object dictionary
    Args:
      node: interface, attribute or operation node object#node which has extattr object
    Returns:
      a generator which yields extattribute dictionary
    """
    def get_extattr_nodes():
        for extattributes in node.GetListOf('ExtAttributes'):
            for extattribute_list in extattributes.GetChildren():
                yield extattribute_list
    for extattr_node in get_extattr_nodes():
        yield {
            'Name': extattr_node.GetName()
        }


def attributes_dict(interface_node):
    """Returns a generator which yields dictioary of Extattribute object information.
    Args:
      interface_node: interface node object
    Returns:
      a generator which yields dictionary of attribite information
    """
    for attribute in get_attributes(interface_node):
        yield {
            'Name': attribute.GetName(),
            'Type': get_attribute_type(attribute),
            'ExtAttributes': [extattr for extattr in get_extattributes(attribute)],
        }


def get_operations(interface_node):
    """Returns list of Operations object under the interface_node.
    Args:
      interface_node: interface node object
    Returns:
      list which is list of oparation object
    """
    return interface_node.GetListOf('Operation')


def get_arguments(operation):
    """Returns list of Arguments object under the operation object.
    Args:
      operation: interface node object
    Returns:
      list which is list of argument object
    """
    argument_node = operation.GetListOf('Arguments')[0]
    return argument_node.GetListOf('Argument')


def argument_dict(argument):
    """Returns generator which yields dictionary of Argument object information.
    Args:
      argument: interface node object
    Returns:
      a generator which yields dictionary of argument information
    """
    for arg_name in get_arguments(argument):
        yield {
            'Name': arg_name.GetName(),
            'Type': get_argument_type(arg_name),
        }


def get_operation_name(operation):
    """Returns openration object name.
    Args:
      operation: operation object in interface node object
    Returns:
      str which is operation's name
    """
    if operation.GetProperty('GETTER', default=None):
        return '__getter__'
    elif operation.GetProperty('SETTER', default=None):
        return '__setter__'
    elif operation.GetProperty('DELETER', default=None):
        return '__deleter__'
    else:
        return operation.GetName()


def operation_dict(interface_node):
    """Returns a generator which yields dictionary of Operation object information.
    Args:
    interface_node: interface node object
    Returns:
      a generator which yields dictionary of operation's informantion
    """
    for operation in get_operations(interface_node):
        yield {
            'Name': get_operation_name(operation),
            'Argument': [args for args in argument_dict(operation)],
            'Type': get_operation_type(operation),
            'ExtAttributes': [extattr for extattr in get_extattributes(operation)],
        }


def get_consts(interface_node):
    """Returns list of Constant object.
    Args:
      interface_node: interface node object
    Returns:
      list which is list of constant object
    """
    return interface_node.GetListOf('Const')


def get_const_type(node):
    """Returns constant's type.
    Args:
      node: interface node's attribute or operation object
    Returns:
      node.GetChildren()[0].GetName(): str, constant object's name
    """
    return node.GetChildren()[0].GetName()


def get_const_value(node):
    """Returns constant's value.
    Args:
      node: interface node's attribute or operation object
    Returns:
      node.GetChildren()[1].GetName(): list, list of oparation object
    """
    return node.GetChildren()[1].GetName()


def const_dict(interface_node):
    """Returns generator which yields dictionary of constant object information.
    Args:
      interface_node: interface node object
    Returns:
      a generator which yields dictionary of constant object information
    """
    for const in get_consts(interface_node):
        yield {
            'Name': const.GetName(),
            'Type': get_const_type(const),
            'Value': get_const_value(const),
        }


def format_interface_dict(interface_node):
    """Returns dictioanry of each interface_node information.
    Args:
      interface_node: interface node object
    Returns:
      dictionary which has interface node information
    """
    return {
        'Name': interface_node.GetName(),
        'FilePath': get_filepath(interface_node),
        'Attribute': [attr for attr in attributes_dict(interface_node)],
        'Operation': [operation for operation in operation_dict(interface_node)],
        'ExtAttributes': [extattr for extattr in get_extattributes(interface_node)],
        'Constant': [const for const in const_dict(interface_node) if const],
    }


def merge_partial_interface(interface_dict_list, partial_dict_list):
    """Returns list of interface_node information dictioary.
    Args:
      interface_dict_list: list of interface node dictionary
      partial_dict_list: list of partial interface node dictionary
    Returns:
      list which is list of interface node's dictionry merged with partial interface node
    """
    for partial in partial_dict_list:
        for interface in interface_dict_list:
            if interface['Name'] == partial['Name']:
                interface['Attribute'].append(partial['Attribute'])
                interface['Operation'].append(partial['Operation'])
                interface['ExtAttributes'].append(partial['ExtAttributes'])
                interface.setdefault('Partial_FilePath', []).append(partial['FilePath'])
                interface.setdefault('Constant', []).append(partial['Constant'])
    return interface_dict_list


def format_interface_to_dict(dictionary_list):
    """Returns dictioary which is changed structure of interface_dict_list.
    Args:
      dictirary_list: list, list of interface node dictionary
    Returns:
      dictionary, {interface_node name: interface node dictionary}
    """
    dictionary = {}
    for interface_dict in dictionary_list:
        dictionary.setdefault(interface_dict['Name'], interface_dict)
    return dictionary


# export_to_jsonfile(), + indent command line argument
def export_to_jsonfile(dictionary, json_file):
    """Returns jsonfile which is dumped each interface_node information dictionary to json.
    Args:
      dictioary: dict, output of format_dictinatry
      json_file: json file for output
    Returns:
      json file which is contained each interface node dictionary
    """
    indent_size = 4
    with open(json_file, 'w') as f:
        json.dump(dictionary, f, sort_keys=True, indent=indent_size)


def main(args):
    path_file = args[0]
    json_file = args[1]
    interface_dict_list = [format_interface_dict(interface_node) for interface_node in get_non_partial(get_interfaces(path_file))]
    partial_dict_list = [format_interface_dict(interface_node) for interface_node in get_partial(get_interfaces(path_file))]
    dictionary_list = merge_partial_interface(interface_dict_list, partial_dict_list)
    dictionary = format_interface_to_dict(dictionary_list)
    export_to_jsonfile(dictionary, json_file)


if __name__ == '__main__':
    main(sys.argv[1:])
