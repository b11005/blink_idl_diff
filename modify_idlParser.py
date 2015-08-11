#!/usr/bin/env python                                                           

import os
import sys,pdb

chromium_path = os.path.abspath(
    os.path.join(os.environ['HOME'], 'chromium', 'src'))
blink_bindings_path = os.path.join(
    chromium_path, 'third_party', 'WebKit', 'Source', 'bindings', 'scripts')
sys.path.insert(0, blink_bindings_path)

from blink_idl_parser import parse_file, BlinkIDLParser

def getIDLFiles(dir):
    for dpath, dnames, fnames in os.walk(dir):
        for fname in fnames:
            if fname.endswith('.idl') and fname!='InspectorInstrumentation.idl':
                yield os.path.join(dpath, fname)


def getInterfaceNodes(dir_path):
    parser = BlinkIDLParser(debug=False)
    for file in getIDLFiles(dir_path):
        definitions = parse_file(parser, file)
        for definition in definitions.GetChildren():
            if definition.GetClass() == 'Interface':
                yield definition


def partial(interfaceNode):
    isPartial = interfaceNode.GetProperty('Partial', default = False)
    if isPartial:
        yield interfaceNode


def nonePartial(interfaceNode):
    isPartial = interfaceNode.GetProperty('Partial', default = False)
    if not isPartial:
        yield interfaceNode


def getAttributes(interfaceNode):
    for attribute in interfaceNode.GetListOf('Attribute'):
        yield attribute.GetName()


def getOperations(interfaceNode):
    for operation in interfaceNode.GetListOf('Operation'):
        yield operation.GetName()


def main(args):
    parser = BlinkIDLParser(debug=False)
    path = args[0]
    count = 0
    partialFilter = nonePartial
    for interfaceNode in getInterfaceNodes(path):
        for filteredNode in partialFilter(interfaceNode):
            getAttributes(filteredNode)
            print 'interfaceName ', filteredNode.GetName()
            #print 'Attributes',[attributeNames for attributeNames in getAttributes(filteredNode) if getAttributes(filteredNode) != None]
            print 'Operations',[operationNames for operationNames in getOperations(filteredNode) if getOperations(filteredNode) != None]
    #print 'count: ', count


if __name__ == '__main__':
    main(sys.argv[1:])
   
