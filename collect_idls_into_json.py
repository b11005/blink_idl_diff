#!/usr/bin/env python
# Copyright 2015 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Usage: interface_to_json.py path_file.txt json_file.json

path_file.txt: output of interface_node_path.py #path
"""

import os
import sys
import json

from blink_idl_parser import parse_file, BlinkIDLParser

_class_name = 'Interface'
_partial = 'Partial'


def get_interfaces(idl_paths):
    """Return a generator which yields interface IDL nodes.
    Args:
      path_file: text file
    Returns:
      a generator which yields interface node objects
    """
    def load_filepaths(path_file):
        with open(path_file, 'r') as f:
            for line in f:
                path = line.strip()
                yield path
    parser = BlinkIDLParser(debug=False)
    for idl_path in load_filepaths(idl_paths):
        definitions = parse_file(parser, idl_path)
        for definition in definitions.GetChildren():
            if definition.GetClass() == _class_name:
                yield definition


def get_filepath(interface_node):
    """Return relative path which is contained in interface_node.
    Args:
      interface_node: interface node class object
    Returns:
      str which is interface_node's file path
    """
    filename = interface_node.GetProperty('FILENAME')
    return os.path.relpath(filename)


def get_partial(interface_node_list):
    """Return a generator which yields partial interface node.
    Args:
      interface_node_list: generator, interface node class object
    Return:
      a generator which yields interface node class object
    """
    for interface_node in interface_node_list:
        if interface_node.GetProperty(_partial):
            yield interface_node


def get_non_partial(interface_node_list):
    """Return a generator which yields interface node.
    Args:
      interface_node_list: generator interface node class object
    Returns:
      a generator which yields interface node class object
    """
    for interface_node in interface_node_list:
        if not interface_node.GetProperty(_partial):
            yield interface_node


def get_attributes(interface_node):
    """Return list of Attribute object.
    Args:
      interface_node: interface node object
    Returns:
      list which is Attribute object list
    """
    return interface_node.GetListOf('Attribute')


def get_attribute_type(attribute):
    """Return type of attribute or operation's type.
    Args:
      node: attribute node object
    Returns:
      str which is Attribute object type
    """
    return attribute.GetListOf('Type')[0].GetChildren()[0].GetName()

get_operation_type = get_attribute_type
get_argument_type = get_attribute_type


def get_extattributes(node):
    """Return a generator which yields Extattribute's object dictionary
    Args:
      node: interface, attribute or operation node object#node which has extattr object
    Returns:
      a generator which yields extattribute dictionary
    """
    def get_extattr_nodes(node):
        for extattributes in node.GetListOf('ExtAttributes'):
            for extattribute_list in extattributes.GetChildren():
                yield extattribute_list
    for extattr_node in get_extattr_nodes(node):
        yield {
            'Name': extattr_node.GetName()
        }


def attributes_dict(interface_node):
    """Return a generator which yields dictioary of Extattribute object information.
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
    """Return list of Operations object under the interface_node.
    Args:
      interface_node: interface node object
    Returns:
      list which is list of oparation object
    """
    return interface_node.GetListOf('Operation')


def get_arguments(operation):
    """Return list of Arguments object under the operation object.
    Args:
      operation: interface node object
    Returns:
      list which is list of argument object
    """
    argument_node = operation.GetListOf('Arguments')[0]
    return argument_node.GetListOf('Argument')


def argument_dict(argument):
    """Return generator which yields dictionary of Argument object information.
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
    """Return openration object name.
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
    """Return a generator which yields dictionary of Operation object information.
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
    """Return list of Constant object.
    Args:
      interface_node: interface node object
    Returns:
      list which is list of constant object
    """
    return interface_node.GetListOf('Const')


def get_const_type(node):
    """Return constant's type.
    Args:
      node: interface node's attribute or operation object
    Returns:
      node.GetChildren()[0].GetName(): str, constant object's name
    """
    return node.GetChildren()[0].GetName()


def get_const_value(node):
    """Return constant's value.
    Args:
      node: interface node's attribute or operation object
    Returns:
      node.GetChildren()[1].GetName(): list, list of oparation object
    """
    return node.GetChildren()[1].GetName()


def const_dict(interface_node):
    """Return generator which yields dictionary of constant object information.
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
    """Return dictioanry of each interface_node information.
    Args:
      interface_node: interface node object
    Returns:
      dictionary which has interface node information
    """
    interface_dict = {}
    interface_dict['Name'] = interface_node.GetName()
    interface_dict['FilePath'] = get_filepath(interface_node)
    interface_dict['Attribute'] = [attr for attr in attributes_dict(interface_node)]
    interface_dict['Operation'] = [operation for operation in operation_dict(interface_node)]
    interface_dict['ExtAttributes'] = [extattr for extattr in get_extattributes(interface_node)]
    interface_dict['Constant'] = [const for const in const_dict(interface_node) if const]
    return interface_dict


def merge_partial_interface(interface_dict_list, partial_dict_list):
    """Returns list of interface_node information dictioary.
    Args:
      interface_dict_list: list
      partial_dict_list: list
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
                if interface['Constant']:
                    interface.setdefault('Constant', []).append(partial['Constant'])
    return interface_dict_list


def format_dictionary(dictionary_list):
    """Return dictioary which is changed structure of interface_dict_list.
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
    """Return jsonfile which is dumped each interface_node information dictionary to json.
    Args:
      dictioary: dict, output of format_dictinatry
      json_file: json file for output
    Returns:
      json file which is contained each interface node dictionary
    """
    filename = json_file
    indent_size = 4
    with open(filename, 'w') as f:
        json.dump(dictionary, f, sort_keys=True, indent=indent_size)


def main(args):
    path_filename = args[0]
    json_file = args[1]
    interface_dict_list = [format_interface_dict(interface_node) for interface_node in get_non_partial(get_interfaces(path_filename))]
    partial_dict_list = [format_interface_dict(interface_node) for interface_node in get_partial(get_interfaces(path_filename))]
    dictionary_list = merge_partial_interface(interface_dict_list, partial_dict_list)
    dictionary = format_dictionary(dictionary_list)
    export_to_jsonfile(dictionary, json_file)


if __name__ == '__main__':
    main(sys.argv[1:])
