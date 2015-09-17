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


def get_filepath(interface):
    """Returns relative path to the IDL file in which the |interface| is defined.
    Args:
      interface: IDL interface
    Returns:
      str which is |interface| file path under WebKit directory
    """
    filename = interface.GetProperty('FILENAME')
    return os.path.relpath(filename).strip('../chromium/src/third_party/WebKit')


def filter_partial(interfaces):
    """Returns a generator which yields partial interface.
    Args:
      interfaces: a generator which is interface IDL
    Return:
      a generator which yields partial interface node
    """
    for interface in interfaces:
        if interface.GetProperty(_partial):
            yield interface


def filter_non_partial(interfaces):
    """Returns a generator which yields interface node.
    Args:
      interfaces: a generator which is interface IDL node
    Returns:
      a generator which yields interface node
    """
    for interface in interfaces:
        if not interface.GetProperty(_partial):
            yield interface


def get_attributes(interface):
    """Returns list of Attribute if the interface have one.
    Args:
      interface: interface node object
    Returns:
      a list of attribute
    """
    return interface.GetListOf('Attribute')


def get_attribute_type(attribute):
    """Returns type of attribute or operation's argument.
    Args:
      attribute: attribute node object
    Returns:
      str which is Attribute object type
    """
    return attribute.GetOneOf('Type').GetChildren()[0].GetName()

get_operation_type = get_attribute_type
get_argument_type = get_attribute_type


def get_extattributes(node):
    
    extattributes = node.GetOneOf('ExtAttributes')
    if extattributes:
        for extattribute in extattributes.GetChildren():
            yield extattribute


def extattr_to_dict(extattributes):
    """Returns a generator which yields Extattribute's object dictionary
    Args:
      extattributes: interface, attribute or operation node which has extattribute
    Returns:
      a generator which yields extattribute dictionary
    """
    for extattribute in extattributes:
        yield {
            'Name': extattribute.GetName(),
        }


def attributes_to_dict(attributes):
    """Returns a generator which yields dictioary of Extattribute object information.
    Args:
      attributes: interface node object
    Returns:
      a generator which yields dictionary of attribite information
    """
    for attribute in attributes:
        yield {
            'Name': attribute.GetName(),
            'Type': get_attribute_type(attribute),
            'ExtAttributes': list(extattr_to_dict(get_attributes(attribute))),
            'Readonly': attribute.GetProperty('READONLY', default=False),
            'Static': attribute.GetProperty('STATIC', default=False),
        }


def get_operations(interface):
    """Returns list of Operations object under the interface.
    Args:
      interface: interface node object
    Returns:
      list which is list of oparation object
    """
    return interface.GetListOf('Operation')


def get_arguments(operation):
    """Returns list of Arguments object under the operation object.
    Args:
      operation: interface node object
    Returns:
      list of argument object
    """
    argument_node = operation.GetOneOf('Arguments')
    return argument_node.GetListOf('Argument')


def argument_dict(arguments):
    """Returns generator which yields dictionary of Argument object information.
    Args:
      arguments: interface node object
    Returns:
      a generator which yields dictionary of argument information
    """
    for argument in arguments:
        yield {
            'Name': argument.GetName(),
            'Type': get_argument_type(argument),
        }


def get_operation_name(operation):
    """Returns openration object name.
    Args:
      operation: operation object in interface node object
    Returns:
      str which is operation's name
    """
    if operation.GetProperty('GETTER'):
        return '__getter__'
    elif operation.GetProperty('SETTER'):
        return '__setter__'
    elif operation.GetProperty('DELETER'):
        return '__deleter__'
    else:
        return operation.GetName()


def operation_dict(operations):
    """Returns a generator which yields dictionary of Operation object information.
    Args:
      operations: interface node object
    Returns:
      a generator which yields dictionary of operation's informantion
    """
    for operation in operations:
        yield {
            'Name': get_operation_name(operation),
            'Arguments': list(argument_dict(get_arguments(operation))),
            'Type': get_operation_type(operation),
            'ExtAttributes': list(extattr_to_dict(get_attributes(operation))),
            'Static': operation.GetProperty('STATIC', default=False),
        }


def inherit_to_dict(interface):
    if interface.GetOneOf('Inherit'):
        yield {'Name': interface.GetOneOf('Inherit').GetName()}


def get_consts(interface):
    """Returns list of Constant object.
    Args:
      interface: interface node object
    Returns:
      list which is list of constant object
    """
    return interface.GetListOf('Const')


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


def const_dict(consts):
    """Returns generator which yields dictionary of constant object information.
    Args:
      consts: interface node object
    Returns:
      a generator which yields dictionary of constant object information
    """
    for const in consts:
        yield {
            'Name': const.GetName(),
            'Type': get_const_type(const),
            'Value': get_const_value(const),
            'ExtAttributes': list(extattr_to_dict(get_attributes(const))),
        }


def interface_to_dict(interface):
    """Returns dictioary whose key is interface name and value is interface dictioary.
    Args:
      interface: list, list of interface node dictionary
    Returns:
      dictionary, {interface name: interface node dictionary}
    """
    return {
        'Attributes': list(attributes_to_dict(get_attributes(interface))),
        'Operations': list(operation_dict(get_operations(interface))),
        'ExtAttributes': list(extattr_to_dict(get_attributes(interface))),
        'Consts': list(const_dict(get_consts(interface))),
        'Inherit': list(inherit_to_dict(interface)),
        'FilePath': get_filepath(interface),
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
        json.dump(dictionary, f, sort_keys=True)


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
