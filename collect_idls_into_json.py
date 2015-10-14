#!/usr/bin/env python
# Copyright 2015 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Usage: collect_idls_into_json.py path_file.txt json_file.json

This script collects and organizes interface information and that information dumps into json file.
"""

import json
import os
import sys
import utilities


from blink_idl_parser import parse_file, BlinkIDLParser

_INTERFACE = 'Interface'
_IMPLEMENT = 'Implements'
_PARTIAL = 'Partial'
_NAME = 'Name'
_TYPE = 'Type'
_VALUE = 'Value'
_PARENT = 'Parent'
_FILEPATH = 'FilePath'
_FILENAME = 'FILENAME'
_PROP_READONLY = 'READONLY'
_READONLY = 'Readonly'
_PROP_STATIC = 'STATIC'
_STATIC = 'Static'
_CONSTS = 'Consts'
_CONST = 'Const'
_ATTRIBUTES = 'Attributes'
_ATTRIBUTE = 'Attribute'
_OPERATIONS = 'Operations'
_OPERATION = 'Operation'
_PROP_GETTER = 'GETTER'
_NAMED_GETTER = '__getter__'
_PROP_SETTER = 'SETTER'
_NAMED_SETTER = '__setter__'
_PROP_DELETER = 'DELETER'
_NAMED_DELETER = '__deleter__'
_ARGUMENTS = 'Arguments'
_ARGUMENT = 'Argument'
_EXTATTRIBUTES = 'ExtAttributes'
_EXTATTRIBUTE = 'ExtAttribute'
_INHERIT = 'Inherit'
_REFERENCE = 'REFERENCE'
_PARTIAL_FILEPATH = 'Partial_FilePaths'
_MEMBERS = ['Consts', 'Attributes', 'Operations']


def get_definitions(paths):
    """Returns IDL node.
    Args:
      paths: list of IDL file path
    Returns:
      a generator which yields IDL node objects
    """
    parser = BlinkIDLParser()
    for path in paths:
        definitions = parse_file(parser, path)
        for definition in definitions.GetChildren():
            yield definition


def is_implements(definition):
    """Returns True if class of |definition| is Implement, otherwise False.
    Args:
      definition: IDL node
    Returns:
      boolean
    """
    return definition.GetClass() == _IMPLEMENT


def is_non_partial(definition):
    """Returns True if class of |definition| is 'interface' class and not 'partial' interface, otherwise False.
    Args:
      definition: IDL node
    Returns:
      boolean
    """
    return definition.GetClass() == _INTERFACE and not definition.GetProperty(_PARTIAL)


def is_partial(definition):
    """Returns True if |definition| is 'partial interface' class, otherwise False.
    Args:
      definition: IDL node
    Return:
      boolean
    """
    return definition.GetClass() == _INTERFACE and definition.GetProperty(_PARTIAL)


def get_filepath(interface_node):
    """Returns relative path to the IDL in which "interface_node| is defined.
    Args:
      interface_node: IDL interface
    Returns:
      str which is |interface_node|'s file path
    """
    filename = interface_node.GetProperty(_FILENAME)
    return os.path.relpath(filename)


def get_const_node_list(interface_node):
    """Returns Const node.
    Args:
      interface_node: interface node
    Returns:
      list of const node
    """
    return interface_node.GetListOf(_CONST)


def get_const_type(const_node):
    """Returns const's type.
    Args:
      const_node: const node
    Returns:
      node.GetChildren()[0].GetName(): str which is constant type
    """
    return const_node.GetChildren()[0].GetName()


def get_const_value(const_node):
    """Returns const's value.
    Args:
      const_node: const node
    Returns:
      node.GetChildren()[1].GetName(): name of oparation's value
    """
    return const_node.GetChildren()[1].GetName()


def const_node_to_dict(const_node):
    """Returns dictionary of const's information.
    Args:
      const_node: const node
    Returns:
      dictionary of const's information
    """
    return {
        _NAME: const_node.GetName(),
        _TYPE: get_const_type(const_node),
        _VALUE: get_const_value(const_node),
        _EXTATTRIBUTES: [extattr_node_to_dict(extattr) for extattr in get_extattribute_node_list(const_node)],
    }


def get_attribute_node_list(interface_node):
    """Returns list of Attribute if the interface have one.
    Args:
      interface_node: interface node
    Returns:
      list of attribute node
    """
    return interface_node.GetListOf(_ATTRIBUTE)


def get_attribute_type(attribute_node):
    """Returns type of attribute.
    Args:
      attribute_node: attribute node
    Returns:
      name of attribute's type
    """
    return attribute_node.GetOneOf(_TYPE).GetChildren()[0].GetName()


get_operation_type = get_attribute_type
get_argument_type = get_attribute_type


def attribute_node_to_dict(attribute_node):
    """Returns dictioary of attribute's information.
    Args:
      attribute_node: attribute node
    Returns:
      dictionary of attribute's information
    """
    return {
        _NAME: attribute_node.GetName(),
        _TYPE: get_attribute_type(attribute_node),
        _EXTATTRIBUTES: [extattr_node_to_dict(extattr) for extattr in get_extattribute_node_list(attribute_node)],
        _READONLY: attribute_node.GetProperty(_PROP_READONLY, default=False),
        _STATIC: attribute_node.GetProperty(_PROP_STATIC, default=False),
    }


def get_operation_node_list(interface_node):
    """Returns operations node list.
    Args:
      interface_node: interface node
    Returns:
      list of oparation node
    """
    return interface_node.GetListOf(_OPERATION)


def get_argument_node_list(operation_node):
    """Returns list of argument.
    Args:
      operation_node: operation node
    Returns:
      list of argument node
    """
    return operation_node.GetOneOf(_ARGUMENTS).GetListOf(_ARGUMENT)


def argument_node_to_dict(argument_node):
    """Returns dictionary of argument's information.
    Args:
      argument_node: argument node
    Returns:
      dictionary of argument's information
    """
    return {
        _NAME: argument_node.GetName(),
        _TYPE: get_argument_type(argument_node),
    }


def get_operation_name(operation_node):
    """Returns openration's name.
    Args:
      operation_node: operation node
    Returns:
      name of operation
    """
    if operation_node.GetProperty(_PROP_GETTER):
        return _NAMED_GETTER
    elif operation_node.GetProperty(_PROP_SETTER):
        return _NAMED_SETTER
    elif operation_node.GetProperty(_PROP_DELETER):
        return _NAMED_DELETER
    else:
        return operation_node.GetName()


def operation_node_to_dict(operation_node):
    """Returns dictionary of operation's information.
    Args:
      operation_node: operation node
    Returns:
      dictionary of operation's informantion
    """
    return {
        _NAME: get_operation_name(operation_node),
        _ARGUMENTS: [argument_node_to_dict(argument) for argument in get_argument_node_list(operation_node) if argument_node_to_dict(argument)],
        _TYPE: get_operation_type(operation_node),
        _EXTATTRIBUTES: [extattr_node_to_dict(extattr) for extattr in get_extattribute_node_list(operation_node)],
        _STATIC: operation_node.GetProperty(_PROP_STATIC, default=False),
    }


def get_extattribute_node_list(node):
    """Returns list of ExtAttribute.
    Args:
      node: IDL node
    Returns:
      list of ExtAttrbute
    """
    if node.GetOneOf(_EXTATTRIBUTES):
        return node.GetOneOf(_EXTATTRIBUTES).GetListOf(_EXTATTRIBUTE)
    else:
        return []


def extattr_node_to_dict(extattr):
    """Returns dictionary of ExtAttribute's information.
    Args:
      extattr: ExtAttribute node
    Returns:
      dictionary of ExtAttribute's information
    """
    return {
        _NAME: extattr.GetName(),
    }


def inherit_node_to_dict(interface_node):
    """Returns dictionary of inherit if |interface_node| has inherit node, otherwise return empty list.
    Args:
      interface_node: interface node
    Returns:
      dictioanry of inherit's information
    """
    inherit = interface_node.GetOneOf(_INHERIT)
    if inherit:
        return {_PARENT: inherit.GetName()}
    else:
        return []


def interface_node_to_dict(interface_node):
    """Returns dictioary whose key is interface name and value is dictioary of interface's information.
    Args:
      interface_node: interface node
    Returns:
      dictionary, {interface name: interface information dictionary}
    """
    return {
        _NAME: interface_node.GetName(),
        _FILEPATH: get_filepath(interface_node),
        _CONSTS: [const_node_to_dict(const) for const in get_const_node_list(interface_node)],
        _ATTRIBUTES: [attribute_node_to_dict(attr) for attr in get_attribute_node_list(interface_node) if attr],
        _OPERATIONS: [operation_node_to_dict(operation) for operation in get_operation_node_list(interface_node) if operation],
        _EXTATTRIBUTES: [extattr_node_to_dict(extattr) for extattr in get_extattribute_node_list(interface_node)],
        _INHERIT: inherit_node_to_dict(interface_node)
    }


def merge_partial_dicts(interfaces_dict, partials_dict):
    """Returns interface information dictioary.
    Args:
      interfaces_dict: interface node dictionary
      partial_dict: partial interface node dictionary
    Returns:
      a dictronary merged with interfaces_dict and partial_dict
    """
    for interface_name, partial in partials_dict.iteritems():
        interface = interfaces_dict.get(interface_name)
        if not interface:
            raise Exception('These is a partial interface, but the corresponding non-partial interface was not found.')
        else:
            for member in _MEMBERS:
                interface[member].extend(partial.get(member))
            interface.setdefault(_PARTIAL_FILEPATH, []).append(partial[_FILEPATH])
    return interfaces_dict


def merge_implement_nodes(interfaces_dict, implement_node_list):
    """Returns dict of interface information combined with referenced interface information
    Args:
      interfaces_dict: dict of interface information
      implement_nodes: list of implemented interface node
    Returns:
      interfaces_dict: dict of interface information combine into implements node
    """
    for implement in implement_node_list:
        reference = implement.GetProperty(_REFERENCE)
        implement = implement.GetName()
        if reference not in interfaces_dict.keys() or implement not in interfaces_dict.keys():
            raise Exception('There is not corresponding implement or reference interface.')
        else:
            for member in _MEMBERS:
                interfaces_dict[implement][member].extend(interfaces_dict[reference].get(member))
    return interfaces_dict


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
    path_list = utilities.read_file_to_list(path_file)
    implement_node_list = [definition
                           for definition in get_definitions(path_list)
                           if is_implements(definition)]
    interfaces_dict = {definition.GetName(): interface_node_to_dict(definition)
                       for definition in get_definitions(path_list)
                       if is_non_partial(definition)}
    partials_dict = {definition.GetName(): interface_node_to_dict(definition)
                     for definition in get_definitions(path_list)
                     if is_partial(definition)}
    dictionary = merge_partial_dicts(interfaces_dict, partials_dict)
    interfaces_dict = merge_implement_nodes(interfaces_dict, implement_node_list)
    export_to_jsonfile(dictionary, json_file)


if __name__ == '__main__':
    main(sys.argv[1:])
