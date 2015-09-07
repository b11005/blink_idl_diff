#!/usr/bin/env python

"""Usage: interface_to_json.py path_file.txt json_file.json

path_file.txt: output of interface_node_path.py#path

# This script is to integrate and dump interface node information to json file.
"""

import os
import sys
import json

from blink_idl_parser import parse_file, BlinkIDLParser


def load_filepaths(path_file):
    """Returns a generator which yields absolute path of IDL files written in the |path_file|.
    Args:
      path_file: text file, #\n
    Returns:
      a generator which yileds absolute file path
    """
    with open(path_file, 'r') as f:
        for line in f:
            path = line.strip()
            yield path


def get_interfaces(idl_paths):
    """Return a generator which yields interface IDL nodes.
    Args:
      path_file: text file
    Returns:
      definition: generator, interface node objects
    """
    parser = BlinkIDLParser(debug=False)
    _class_name = 'Interface'
    for idl_path in load_filepaths(idl_paths):
        definitions = parse_file(parser, idl_path)
        for definition in definitions.GetChildren():
            if definition.GetClass() == _class_name:
                yield definition


def get_filepath(interface_node):
    """Returns relative path which is contained in interface_node.
    Args:
      interface_node: interface node class object
    Returns:
      os.path.relpath(filename): str, interface_node's file path
    """
    filename = interface_node.GetProperty('FILENAME')
    return os.path.relpath(filename)


def get_partial(interface_node_list):
    """Returns generator which yields partial interface node.
    Args:
      interface_node_list: generator, interface node class object
    Return:
      interface_node: generator, interface node class object
    """
    for interface_node in interface_node_list:
        if interface_node.GetProperty('Partial'):
            yield interface_node


def get_non_partial(interface_node_list):
    """Returns generator which yields interface node.
    Args:
      interface_node_list: generator interface node class object
    Returns:
      interface_node: generator, interface node class object
    """
    for interface_node in interface_node_list:
        if not interface_node.GetProperty('Partial'):
            yield interface_node


def get_attributes(interface_node):
    """Returns list of Attribute object.
    Args:
      interface_node: interface node object
    Returns:
      list, Attribute object list
    """
    return interface_node.GetListOf('Attribute')


def get_type(node):
    """Returns type of attribute or operation's type.
    Args:
      node: attribute or operation node object
    Returns:
      str, 
    """
    return node.GetListOf('Type')[0].GetChildren()[0].GetName()


def get_extattributes(node):
    """Returns generator which yields list of Extattribute object.
    Args:
      node: interface, attribute or operation node object#node which has extattr object
    Returns:
      extattribute_list: generator, extattribute object list
    """
    for extattributes in node.GetListOf('ExtAttributes'):
        for extattribute_list in extattributes.GetChildren():
            yield extattribute_list

### converter or translater  ==> @@_to_!!
def extattr_dict(node):
    """Returns a generator which yields Extattribute's information dictionary.
    Args:
      node: interface node object
    Returns:
      generator, extattribute dictionary
    """
    for extattribute in get_extattributes(node):
        yield {
            'Name': extattribute.GetName(),
        }
### ==>dicts =  map(extattr_dict, get_extattributes), dicts = [conv(extattr) for extattr in get_extattrs(node)]

def attributes_dict(interface_node):
    """Returns generator which yields dictioary of Extattribute object information.
    Args:
      interface_node: interface node object
    Returns:
      attr_dict: generator, dictionary of attribite information
    """
    for attribute in get_attributes(interface_node):
        attr_dict = {}
        attr_dict['Name'] = attribute.GetName()
        attr_dict['Type'] = get_type(attribute)
        attr_dict['ExtAttributes'] = [extattr for extattr in extattr_dict(attribute)]
        yield attr_dict


def get_operations(interface_node):
    """Returns list of Operations object under the interface_node.
    Args:
      interface_node: interface node object
    Returns:
      interface_node.GetListOf('Operation'): list, list of oparation object
    """
    return interface_node.GetListOf('Operation')


def get_arguments(operation):
    """Returns list of Arguments object under the operation object.
    Args:
      operation: interface node object
    Returns:
      argument_node.GetListOf('Argument'): list, list of argument object
    """
    argument_node = operation.GetListOf('Arguments')[0]
    return argument_node.GetListOf('Argument')


def argument_dict(argument):
    """Returns generator which yields dictionary of Argument object information.
    Args:
      argument: interface node object
    Returns:
      arg_dict: dict, generator of argument information's dictionary
    """
    for arg_name in get_arguments(argument):
        arg_dict = {}
        arg_dict['Name'] = arg_name.GetName()
        arg_dict['Type'] = get_type(arg_name)
        yield arg_dict


def get_operation_name(operation):
    """Returns openration object name.
    Args:
      operation: operation object in interface node object
    Returns:
      str, operation's name
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
    """Returns generator which yields dictionary of Operation object information.
    Args:
    interface_node: interface node object
    Returns:
      operate_dict: generator of operation dictionary
    """
    for operation in get_operations(interface_node):
        operate_dict = {}
        operate_dict['Name'] = get_operation_name(operation)
        operate_dict['Argument'] = [args for args in argument_dict(operation)]
        operate_dict['Type'] = get_type(operation)
        operate_dict['ExtAttributes'] = [extattr for extattr in extattr_dict(operation)]
        yield operate_dict


def get_consts(interface_node):
    """Returns list of Constant object.
    Args:
      interface_node: interface node object
    Returns:
      interface_node.GetListOf('Const'): list, list of constant object
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
      {}: generator, dict of constant object information
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
      interface_dict: dict, dictionary of interface node information
    """
    interface_dict = {}
    interface_dict['Name'] = interface_node.GetName()
    interface_dict['FilePath'] = get_filepath(interface_node)
    interface_dict['Attribute'] = [attr for attr in attributes_dict(interface_node)]
    interface_dict['Operation'] = [operation for operation in operation_dict(interface_node)]
    interface_dict['ExtAttributes'] = [extattr for extattr in extattr_dict(interface_node)]
    interface_dict['Constant'] = [const for const in const_dict(interface_node) if const]
    return interface_dict


def merge_partial_interface(interface_dict_list, partial_dict_list):
    """Returns list of interface_node information dictioary.
    Args:
      interface_dict_list: list
      partial_dict_list: list
    Returns:
      interface_dict_list: list, list of interface node's dictionry merged with partial interface node
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
    """Returns dictioary which is changed structure of interface_dict_list.
    Args:
      dictirary_list: list, list of interface node dictionary
    Returns:
      dictionary: dict, {interface_node name: interface node dictionary}
    """
    dictionary = {}
    for interface_dict in dictionary_list:
        dictionary.setdefault(interface_dict['Name'], interface_dict)
    return dictionary

### export_to_jsonfile(), + indent command line argument
def export_jsonfile(dictionary, json_file):
    """Returns jsonfile which is dumped each interface_node information dictionary to json.
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
    path_file = args[0]
    json_file = args[1]
    interface_dict_list = [format_interface_dict(interface_node) for interface_node in get_non_partial(get_interfaces(path_file))]
    partial_dict_list = [format_interface_dict(interface_node) for interface_node in get_partial(get_interfaces(path_file))]
    dictionary_list = merge_partial_interface(interface_dict_list, partial_dict_list)
    dictionary = format_dictionary(dictionary_list)
    export_jsonfile(dictionary, json_file)


if __name__ == '__main__':
    main(sys.argv[1:])
