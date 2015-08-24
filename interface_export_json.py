#!/usr/bin/env python

import os, sys, json

chromium_path = os.path.abspath(
    os.path.join(os.environ['HOME'], 'chromium', 'src'))
blink_bindings_path = os.path.join(
    chromium_path, 'third_party', 'WebKit', 'Source', 'bindings', 'scripts')
sys.path.insert(0, blink_bindings_path)

from blink_idl_parser import parse_file, BlinkIDLParser

def get_idl_files(dir):
    file_type='.idl'
    non_idl_set = (
        'InspectorInstrumentation.idl',
    )
    for dir_path, dir_names, file_names in os.walk(dir):
        for file_name in file_names:
            if file_name.endswith(file_type) and file_name not in non_idl_set:
                yield os.path.join(dir_path, file_name)


def get_interface_nodes(dir_path):
    parser = BlinkIDLParser(debug=False)
    class_name = 'Interface' 
    for node_path in get_idl_files(dir_path):
        definitions = parse_file(parser, node_path)
        for definition in definitions.GetChildren():
            if definition.GetClass() == class_name:
                yield definition


def get_filepath(interface_node):
    filename = interface_node.GetProperty('FILENAME')
    filepath = os.path.relpath(filename)
    return filepath


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
        return extattributes.GetChildren()

def extattr_dict(extattribute_list):
    for extattribute in get_extattirbutes(extattribute_list):
        extattributes_dict = {}
        extattributes_dict['Name'] = extattribute.GetName()
        yield extattributes_dict


def attributes_dict(interface_node):
    for attribute in get_attributes(interface_node):
        attr_dict = {}
        attr_dict['Name'] = attribute.GetName()
        attr_dict['Type'] = get_type(attribute)
        attr_dict['ExtAttribute'] = [extattr for extattr in extattr_dict(attribute)]
        yield attr_dict


def get_operation(interface_node):
    for operation in interface_node.GetListOf('Operation'):
        yield operation


def get_argument(operation):
    argument_node = operation.GetListOf('Arguments')[0]
    yield argument_node.GetListOf('Argument')


def argument_dict(argument):
    for arg_list in get_argument(argument):
        for arg_name in arg_list:
            arg_dict = {}
            arg_dict['Name'] = arg_name.GetName()
            arg_dict['Type'] = get_type(arg_name)
            yield arg_dict


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
    for operation in get_operation(interface_node):
        operate_dict = {}
        operate_dict['Name'] = get_operation_name(operation)
        operate_dict['Argument'] = [argument for argument in argument_dict(operation)]
        operate_dict['Type'] = get_type(operation)
        operate_dict['ExtAttributes'] = [extattr for extattr in extattr_dict(get_extattirbutes(operation))]
        yield operate_dict


def get_const(interface_node):
    for const in interface_node.GetListOf('Const'):
        yield const


def get_const_type(node):
    return node.GetChildren()[0].GetName()


def get_const_value(node):
    return node.GetChildren()[1].GetName()


def const_dict(const):
    return {
    'Name': const.GetName(),
    'Type': get_const_type(const),
    'Value': get_const_value(const)
    }


def format_const(interface_node):
    for const in get_const(interface_node):
        yield const_dict(const)


def format_interface_dict(interface_node):
    interface_dict = {}
    interface_dict['Name'] = interface_node.GetName()
    interface_dict['FilePath'] = get_filepath(interface_node)
    interface_dict['Attribute'] = [attr_name for attr_name in attributes_dict(interface_node)]
    interface_dict['Operation'] = [operation for operation in operation_dict(interface_node)]
    interface_dict['ExtAttributes'] = [extattr for extattr in extattr_dict(get_extattirbutes(interface_node))]
    interface_dict['Const'] = [const for const in format_const(interface_node)]
    return interface_dict


def merge_partial_interface(interface_dict_list, partial_dict_list):
    for partial in partial_dict_list:
        for interface in interface_dict_list:
            if interface['Name'] == partial['Name']:
                interface['Attribute'].append(partial['Attribute'])
                interface['Operation'].append(partial['Operation'])
                interface['ExtAttributes'].append(partial['ExtAttributes'])
                interface['Const'].append(partial['Const'])
                interface.setdefault('Partial_FilePath',[]).append(partial['FilePath'])
    return interface_dict_list

def format_dictionary(dictionary_list):
    dictionary = {}
    for interface_dict in dictionary_list:
        dictionary.setdefault(interface_dict['Name'],interface_dict)
    return dictionary


def export_jsonfile(dictionary, json_file):
    filename = json_file
    indent_size = 4
    f = open(filename, 'w')
    json.dump(dictionary, f, sort_keys = True, indent = indent_size)
    f.close()


def main(args):
    path = args[0]
    json_file = args[1]
    interface_dict_list = [format_interface_dict(interface_node) for interface_node in get_non_partial(get_interface_nodes(path))]
    partial_dict_list = [format_interface_dict(interface_node) for interface_node in get_partial(get_interface_nodes(path))]
    dictionary_list = merge_partial_interface(interface_dict_list, partial_dict_list)
    dictionary = format_dictionary(dictionary_list)
    export_jsonfile(dictionary, json_file)


if __name__ == '__main__':
    main(sys.argv[1:])
   
