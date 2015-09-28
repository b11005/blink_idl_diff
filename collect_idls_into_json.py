#!/usr/bin/env python
# Copyright 2015 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Usage: collect_idls_into_json.py path_file.txt json_file.json
"""

import os
import sys
import json
import utilities

from blink_idl_parser import parse_file, BlinkIDLParser

_class_name = 'Interface'
_partial = 'Partial'


def get_interfaces(paths):
    """Returns interface IDL node.
    Args:
      paths: list of IDL file path
    Returns:
      a generator which yields interface node objects
    """
    parser = BlinkIDLParser(debug=False)
    for path in paths:
        definitions = parse_file(parser, path)
        for definition in definitions.GetChildren():
            if definition.GetClass() == _class_name:
                yield definition


def get_filepath(interface_node):
    """Returns relative path under the WebKit directory which |interface_node| is defined.
    Args:
      interface_node: IDL interface
    Returns:
      str which is |interface_node| file path
    """
    filename = interface_node.GetProperty('FILENAME')
    return os.path.relpath(filename).strip('../chromium/src/third_party/WebKit')


def filter_partial(interface_nodes):
    """Returns partial interface node.
    Args:
      interface_nodes: a generator which is interface IDL
    Return:
      a generator which yields partial interface node
    """
    for interface_node in interface_nodes:
        if interface_node.GetProperty(_partial):
            yield interface_node


def filter_non_partial(interface_nodes):
    """Returns interface node.
    Args:
      interface_nodes: a generator which is interface IDL node
    Returns:
      a generator which yields interface node
    """
    for interface_node in interface_nodes:
        if not interface_node.GetProperty(_partial):
            yield interface_node


def get_attributes(interface_node):
    """Returns list of Attribute if the interface have one.
    Args:
      interface_node: interface node object
    Returns:
      a list of attribute
    """
    return interface_node.GetListOf('Attribute')


def get_attribute_type(attribute_node):
    """Returns type of attribute.
    Args:
      attribute_node: attribute node object
    Returns:
      str which is type of Attribute
    """
    return attribute_node.GetOneOf('Type').GetChildren()[0].GetName()


get_operation_type = get_attribute_type
get_argument_type = get_attribute_type


def get_extattributes(node):
    """Returns list of ExtAttribute.
    Args:
      IDL node object
    Returns:
      a list of ExtAttrbute
    """
    if node.GetOneOf('ExtAttributes'):
        return node.GetOneOf('ExtAttributes').GetListOf('ExtAttribute')
    else:
        return []


def extattr_node_to_dict(extattr):
    """Returns a generator which yields Extattribute's object dictionary
    Args:
      extattribute_nodes: list of extended attribute
    Returns:
      a generator which yields extattribute dictionary
    """
    return {
        'Name': extattr.GetName(),
        }


def attribute_node_to_dict(attribute_node):
     """Returns dictioary of attribute object information.
    Args:
      attribute_nodes: list of attribute node object
    Returns:
      a generator which yields dictionary of attribite information
    """
     return {
        'Name': attribute_node.GetName(),
        'Type': get_attribute_type(attribute_node),
        'ExtAttributes': [extattr_node_to_dict(extattr) for extattr in get_extattributes(attribute_node)],
        'Readonly': attribute_node.GetProperty('READONLY', default=False),
        'Static': attribute_node.GetProperty('STATIC', default=False),
    }

def get_operations(interface_node):
    """Returns Operations object under the interface.
    Args:
      interface: interface node object
    Returns:
      list which is list of oparation object
    """
    return interface_node.GetListOf('Operation')


def get_arguments(operation_node):
    """Returns Argument object under the operation object.
    Args:
      operation_node: operation node object
    Returns:
      list of argument object
    """
    return operation_node.GetOneOf('Arguments').GetListOf('Argument')


def argument_node_to_dict(argument_node):
    """Returns generator which yields dictionary of Argument object information.
    Args:
      arguments: list of argument node object
    Returns:
      a generator which yields dictionary of argument information
    """
    return {
        'Name': argument_node.GetName(),
        'Type': get_argument_type(argument_node),
    }


def get_operation_name(operation_node):
    """Returns openration object name.
    Args:
      operation_node: operation node object
    Returns:
      str which is operation's name
    """
    if operation_node.GetProperty('GETTER'):
        return '__getter__'
    elif operation_node.GetProperty('SETTER'):
        return '__setter__'
    elif operation_node.GetProperty('DELETER'):
        return '__deleter__'
    else:
        return operation_node.GetName()


def operation_node_to_dict(operation_node):
    """Returns  dictionary of Operation object information.
    Args:
      operation_nodes: list of operation node object
    Returns:
      dictionary of operation's informantion
    """
    return {
        'Name': get_operation_name(operation_node),
        'Arguments': [argument_node_to_dict(argument) for argument in get_arguments(operation_node)],
        'Type': get_operation_type(operation_node),
        'ExtAttributes': [extattr_node_to_dict(extattr) for extattr in get_extattributes(operation_node)],
        'Static': operation_node.GetProperty('STATIC', default=False),
    }


def inherit_to_dict(interface_node):
    if interface_node.GetOneOf('Inherit'):
        return {'Name': interface_node.GetOneOf('Inherit').GetName()}


def get_consts(interface_node):
    """Returns Constant object.
    Args:
      interface_node: interface node object
    Returns:
      list which is list of constant object
    """
    return interface_node.GetListOf('Const')


def get_const_type(const_node):
    """Returns constant's type.
    Args:
      const_node: constant node object
    Returns:
      node.GetChildren()[0].GetName(): str, constant object's name
    """
    return const_node.GetChildren()[0].GetName()


def get_const_value(const_node):
    """Returns constant's value.
    Args:
      const_node: constant node object
    Returns:
      node.GetChildren()[1].GetName(): list, list of oparation object
    """
    return const_node.GetChildren()[1].GetName()


'''def const_to_dict(const_nodes):
    """Returns dictionary of constant object information.
    Args:
      const_nodes: list of interface node object which has constant
    Returns:
      a generator which yields dictionary of constant object information
    """
    for const_node in const_nodes:
        yield {
            'Name': const_node.GetName(),
            'Type': get_const_type(const_node),
            'Value': get_const_value(const_node),
            'ExtAttributes': [extattr_node_to_dict(extattr) for extattr in get_extattributes(const_node)],
        }'''


def const_node_to_dict(const_node):
    """Returns dictionary of constant object information.
    Args:
      const_nodes: list of interface node object which has constant
    Returns:
      a generator which yields dictionary of constant object information
    """
    return {
        'Name': const_node.GetName(),
        'Type': get_const_type(const_node),
        'Value': get_const_value(const_node),
        'ExtAttributes': [extattr_node_to_dict(extattr) for extattr in get_extattributes(const_node)],
    }


def interface_to_dict(interface_node):
    """Returns dictioary whose key is interface name and value is interface dictioary.
    Args:
      interface_node: interface node
    Returns:
      dictionary, {interface name: interface node dictionary}
    """
    return {
        'Name': interface_node.GetName(),
        'Attributes': [attribute_node_to_dict(attr)  for attr in get_attributes(interface_node)],
        'Operations': [operation_node_to_dict(operation) for operation in get_operations(interface_node)],
        'ExtAttributes': [extattr_node_to_dict(extattr) for extattr in get_extattributes(interface_node)],
        'Consts': [const_node_to_dict(const) for const in get_consts(interface_node)],
        #'Consts': list(const_to_dict(get_consts(interface_node))),
        'Inherit': inherit_to_dict(interface_node),
        'FilePath': get_filepath(interface_node),
    }


def merge_dict(interface_dict, partial_dict):
    """Returns interface information dictioary.
    Args:
      interface_dict: interface node dictionary
      partial_dict: partial interface node dictionary
    Returns:
      a dictronary merged with interface_dict and  partial_dict
    """
    for key in partial_dict.keys():
        interface_dict[key]['Attributes'].append(partial_dict[key]['Attributes'])
        interface_dict[key]['Operations'].append(partial_dict[key]['Operations'])
        interface_dict[key]['Consts'].append(partial_dict[key]['Consts'])
        interface_dict[key].setdefault('Partial_FilePaths', []).append(partial_dict[key]['FilePath'])
    return interface_dict


def export_to_jsonfile(dictionary, json_file):
    """Returns jsonfile which is dumped each interface information dictionary to json.
    Args:
      dictioary: interface dictionary
      json_file: json file for output
    Returns:
      json file which is contained each interface node dictionary
    """
    with open(json_file, 'w') as f:
        json.dump(dictionary, f, sort_keys=True, indent=4)


def main(args):
    path_file = args[0]
    json_file = args[1]
    file_to_list = utilities.read_file_to_list(path_file)
    interface_dict = {interface.GetName(): interface_to_dict(interface) for interface in filter_non_partial(get_interfaces(file_to_list))}
    partial_dict = {interface.GetName(): interface_to_dict(interface) for interface in filter_partial(get_interfaces(file_to_list))}
    dictionary = merge_dict(interface_dict, partial_dict)
    export_to_jsonfile(dictionary, json_file)


if __name__ == '__main__':
    main(sys.argv[1:])
