#!/usr/bin/env python

import os, sys, pdb, json

chromium_path = os.path.abspath(
    os.path.join(os.environ['HOME'], 'chromium', 'src'))
blink_bindings_path = os.path.join(
    chromium_path, 'third_party', 'WebKit', 'Source', 'bindings', 'scripts')
sys.path.insert(0, blink_bindings_path)

from blink_idl_parser import parse_file, BlinkIDLParser

def getIDLFiles(dir):
    file_type='.idl'
    non_idl_set = (
        'InspectorInstrumentation.idl',
    )
    for dir_path, dir_names, file_names in os.walk(dir):
        for file_name in file_names:
            if file_name.endswith(file_type) and file_name not in non_idl_set:
                yield os.path.join(dir_path, file_name)


def getInterfaceNodes(dir_path):
    parser = BlinkIDLParser(debug=False)
    class_name = 'Interface' 
    for file in getIDLFiles(dir_path):
        definitions = parse_file(parser, file)
        for definition in definitions.GetChildren():
            if definition.GetClass() == class_name:
                yield definition


def get_filepath(interface_node):
    filename = interface_node.GetProperty('FILENAME')
    filepath = os.path.realpath(filename)
    return filepath


def partial(interface_node_list):
    for interface_node in interface_node_list:
        if interface_node.GetProperty('Partial', default=False):
            yield interface_node  


def non_partial(interface_node_list):
    for interface_node in interface_node_list:
        if not interface_node.GetProperty('Partial', default=False):
            yield interface_node


def getAttribute(interface_node):
    for attribute in interface_node.GetListOf('Attribute'):
        yield attribute


def get_type(node):
    return node.GetListOf('Type')[0].GetName()


def get_primitivetype(node):
    under_type = node.GetListOf('Type')[0].GetChildren()[0]
    if under_type.GetClass() == 'PrimitiveType':
        return under_type.GetName()


def get_typeref(node):
    under_type = node.GetListOf('Type')[0].GetChildren()[0]
    if under_type.GetClass() == 'Typeref':
        return under_type.GetName()


def get_extattirbute(interface_node):
    for extattributes in interface_node.GetListOf('ExtAttributes'):
        for extattribute_list in extattributes.GetChildren():
            yield extattribute_list


def extattr_dict(extattribute_list):
    for extattribute in extattribute_list:
        extattribute_dict = {}
        extattribute_dict['Extattribute Name'] = extattribute.GetName()
        return extattribute_dict


def attribute_dict(interface_node):
    for attribute in getAttribute(interface_node):
        attr_dict = {}
        attr_dict['Name'] = attribute.GetName()
        attr_dict['Typeref'] = get_typeref(attribute)
        attr_dict['ExtAttributes'] = extattr_dict(get_extattirbute(attribute))
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
            arg_dict['Argument Name'] = arg_name.GetName()
            arg_dict['Type'] = get_type(arg_name)
            arg_dict['PrimitiveType'] = get_primitivetype(arg_name)
            yield arg_dict


def operation_dict(interface_node):
    for operation in get_operation(interface_node):
        operate_dict = {}
        operate_dict['Name'] = operation.GetName()
        operate_dict['Arguments'] =[argument for argument in argument_dict(operation)]
        operate_dict['Type'] = get_type(operation)
        operate_dict['ExtAttributes'] = extattr_dict(get_extattirbute(operation))
        yield operate_dict


def get_const(interface_node):
    for const in interface_node.GetListOf('Const'):
        yield const

def format_interface_dict(interface_node):
        interface_dict = {}
        interface_dict['Interface Name'] = interface_node.GetName()
        interface_dict['FilePath'] = get_filepath(interface_node)
        interface_dict['Attribute'] = [attr_name for attr_name in attribute_dict(interface_node)]
        interface_dict['Operation'] = [operation for operation in operation_dict(interface_node)]
        interface_dict['ExtAttributes'] = extattr_dict(get_extattirbute(interface_node))
        return interface_dict


def export_jsonfile(dictionary):
    filename = 'sample.json'
    indent_size = 4
    f = open(filename, 'a')
    json.dump(dictionary, f, sort_keys = True, indent = indent_size)
    f.close()



def main(args):
    path = args[0]
    partial_or_nonpartial = non_partial
    for interface_node in partial_or_nonpartial(getInterfaceNodes(path)):
        dictionary = format_interface_dict(interface_node)
        export_jsonfile(dictionary)
        #print format_interface_dict(interface_node)
        #print [con.GetName() for con in get_const(interface_node)]


if __name__ == '__main__':
    main(sys.argv[1:])
   
