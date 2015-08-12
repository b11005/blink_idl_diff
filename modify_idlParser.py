#!/usr/bin/env python                                                           

import os, sys, pdb

chromium_path = os.path.abspath(
    os.path.join(os.environ['HOME'], 'chromium', 'src'))
blink_bindings_path = os.path.join(
    chromium_path, 'third_party', 'WebKit', 'Source', 'bindings', 'scripts')
sys.path.insert(0, blink_bindings_path)

from blink_idl_parser import parse_file, BlinkIDLParser

def getIDLFiles(dir):
    file_type='.idl'
    ignore_set = (
        'InspectorInstrumentation.idl',
    )
    for dir_path, dir_names, file_names in os.walk(dir):
        for file_name in file_names:
            if file_name.endswith(file_type) and file_name not in ignore_set:
                yield os.path.join(dir_path, file_name)


def getInterfaceNodes(dir_path):
    parser = BlinkIDLParser(debug=False)
    class_name = 'Interface' 
    for file in getIDLFiles(dir_path):
        definitions = parse_file(parser, file)
        for definition in definitions.GetChildren():
            if definition.GetClass() == class_name:
                yield definition


def partial(interfaceNode):
    is_partial = interfaceNode.GetProperty('Partial', default = False)
    if is_partial:
        yield interfaceNode


def none_partial(interfaceNode):
    is_partial = interfaceNode.GetProperty('Partial', default = False)
    if not is_partial:
        yield interfaceNode


def getAttributes(interfaceNode):
    for node in interfaceNode:
        for attribute in node.GetListOf('Attribute'):
            yield attribute.GetName()


def getOperations(interfaceNode):
    for node in interfaceNode:
        for operation in node.GetListOf('Operation'):
            yield operation.GetName()


def main(args):
    parser = BlinkIDLParser(debug=False)
    path = args[0]
    count = 0
    partialFilter = none_partial
    for interfaceNode in getInterfaceNodes(path):
        print interfaceNode.GetName()
        filtered_nodes = partialFilter(interfaceNode)
        #print [name.GetName() for name in filtered_nodes]
        #for filteredNode in partialFilter(interfaceNode):
        #getAttributes(filtered_nodes)
        #print 'interfaceName: ', [node_name.GetName() for node_name in filtered_nodes] 
        print 'Attributes',[attributeNames for attributeNames in getAttributes(filtered_nodes)]
        print 'Operations',[operationNames for operationNames in getOperations(filtered_nodes)]
    #print 'count: ', count


if __name__ == '__main__':
    main(sys.argv[1:])
   
