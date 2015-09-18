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
    """Returns a generator which yields interface IDL.
    Args:
      paths: IDL file path list
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
    """Returns relative path to the IDL file in which the |interface_node| is defined.
    Args:
      interface_node: IDL interface
    Returns:
      str which is |interface_node| file path under WebKit directory
    """
    filename = interface_node.GetProperty('FILENAME')
    return os.path.relpath(filename).strip('../chromium/src/third_party/WebKit')


def filter_partial(interface_nodes):
    """Returns a generator which yields partial interface.
    Args:
      interface_nodes: a generator which is interface IDL
    Return:
      a generator which yields partial interface node
    """
    for interface_node in interface_nodes:
        if interface_node.GetProperty(_partial):
            yield interface_node


def filter_non_partial(interface_nodes):
    """Returns a generator which yields interface node.
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
    """Returns type of attribute or operation's argument.
    Args:
      attribute_node: attribute node object
    Returns:
      str which is Attribute object type
    """
    return attribute_node.GetOneOf('Type').GetChildren()[0].GetName()

get_operation_type = get_attribute_type
get_argument_type = get_attribute_type


def get_extattributes(node):
    """Returns agenerator which yields list of ExtAttribute.
    Args:
      IDL node object
    Returns:
      a generator which yields list of ExtAttrbute
    """
    extattribute_nodes = node.GetOneOf('ExtAttributes')
    if extattributes_nodes:
        yield extattributes_nodes.GetChildren()


def extattr_to_dict(extattribute_nodes):
    """Returns a generator which yields Extattribute's object dictionary
    Args:
      extattribute_nodes: interface, attribute or operation node which has extattribute
    Returns:
      a generator which yields extattribute dictionary
    """
    for extattribute_node in extattribute_nodes:
        yield {
            'Name': extattribute_node.GetName(),
        }


def attributes_to_dict(attribute_nodes):
    """Returns a generator which yields dictioary of Extattribute object information.
    Args:
      attribute_nodes: list of interface node object
    Returns:
      a generator which yields dictionary of attribite information
    """
    for attribute_node in attribute_nodes:
        yield {
            'Name': attribute_node.GetName(),
            'Type': get_attribute_type(attribute_node),
            'ExtAttributes': list(extattr_to_dict(get_attributes(attribute_node))),
            'Readonly': attribute_node.GetProperty('READONLY', default=False),
            'Static': attribute_node.GetProperty('STATIC', default=False),
        }


def get_operations(interface_node):
    """Returns list of Operations object under the interface.
    Args:
      interface: interface node object
    Returns:
      list which is list of oparation object
    """
    return interface_node.GetListOf('Operation')


def get_arguments(operation_node):
    """Returns list of Arguments object under the operation object.
    Args:
      operation_node: interface node object
    Returns:
      list of argument object
    """
    argument_node = operation_node.GetOneOf('Arguments')
    return argument_node.GetListOf('Argument')


def argument_dict(argument_nodes):
    """Returns generator which yields dictionary of Argument object information.
    Args:
      arguments: interface node object
    Returns:
      a generator which yields dictionary of argument information
    """
    for argument_node in argument_nodes:
        yield {
            'Name': argument_node.GetName(),
            'Type': get_argument_type(argument_node),
        }


def get_operation_name(operation_node):
    """Returns openration object name.
    Args:
      operation_node: operation object in interface node object
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


def operation_dict(operation_nodes):
    """Returns a generator which yields dictionary of Operation object information.
    Args:
      operation_nodes: interface node object
    Returns:
      a generator which yields dictionary of operation's informantion
    """
    for operation_node in operation_nodes:
        yield {
            'Name': get_operation_name(operation_node),
            'Arguments': list(argument_dict(get_arguments(operation_node))),
            'Type': get_operation_type(operation_node),
            'ExtAttributes': list(extattr_to_dict(get_attributes(operation_node))),
            'Static': operation_node.GetProperty('STATIC', default=False),
        }


def inherit_to_dict(interface_node):
    if interface_node.GetOneOf('Inherit'):
        yield {'Name': interface_node.GetOneOf('Inherit').GetName()}


def get_consts(interface_node):
    """Returns list of Constant object.
    Args:
      interface_node: interface node object
    Returns:
      list which is list of constant object
    """
    return interface_node.GetListOf('Const')


def get_const_type(const_node):
    """Returns constant's type.
    Args:
      const_node: interface node's attribute or operation object
    Returns:
      node.GetChildren()[0].GetName(): str, constant object's name
    """
    return const_node.GetChildren()[0].GetName()


def get_const_value(node):
    """Returns constant's value.
    Args:
      node: interface node's attribute or operation object
    Returns:
      node.GetChildren()[1].GetName(): list, list of oparation object
    """
    return node.GetChildren()[1].GetName()


def const_dict(const_nodes):
    """Returns generator which yields dictionary of constant object information.
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
            'ExtAttributes': list(extattr_to_dict(get_attributes(const_node))),
        }


def interface_to_dict(interface_node):
    """Returns dictioary whose key is interface name and value is interface dictioary.
    Args:
      interface_node: interface node
    Returns:
      dictionary, {interface name: interface node dictionary}
    """
    return {
        'Attributes': list(attributes_to_dict(get_attributes(interface_node))),
        'Operations': list(operation_dict(get_operations(interface_node))),
        'ExtAttributes': list(extattr_to_dict(get_attributes(interface_node))),
        'Consts': list(const_dict(get_consts(interface_node))),
        'Inherit': list(inherit_to_dict(interface_node)),
        'FilePath': get_filepath(interface_node),
    }


def merge_dict(interface_dict, partial_dict):
    """Returns list of interface information dictioary.
    Args:
      interface_dict: interface node dictionary
      partial_dict: partial interface node dictionary
    Returns:
      list which is list of interface node's dictionry merged with partial interface node
    """
    for key in partial_dict.keys():
        if key in interface_dict:
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
