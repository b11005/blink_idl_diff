#!/usr/bin/env python                                                           

import os
import sys,pdb

chromium_path = os.path.abspath(
    os.path.join(os.environ['HOME'], 'chromium', 'src'))
blink_bindings_path = os.path.join(
    chromium_path, 'third_party', 'WebKit', 'Source', 'bindings', 'scripts')
sys.path.insert(0, blink_bindings_path)

from blink_idl_parser import parse_file, BlinkIDLParser

def GetIDLFiles(dir):
    for dpath, dnames, fnames in os.walk(dir):
        for fname in fnames:
            if fname.endswith('.idl') and fname!='InspectorInstrumentation.idl':
                yield os.path.join(dpath, fname)


def GetInterfaceNodes(dir_path):
    parser = BlinkIDLParser(debug=False)
    for file in GetIDLFiles(dir_path):
        definitions = parse_file(parser, file)
        for definition in definitions.GetChildren():
            if definition.GetClass() == 'Interface':
                yield definition


def IsPartial(interfaceNode):
    isPartial = interfaceNode.GetProperty('Partial', default = False)
    if isPartial:
        yield interfaceNode


def NotPartial(interfaceNode):
    isPartial = interfaceNode.GetProperty('Partial', default = False)
    if not isPartial:
        yield interfaceNode


def GetAttributes(interfaceNode):
    for attribute in interfaceNode.GetListOf('Attribute'):
        yield attribute.GetName()
    #for element in interfaceNode.Tree():
        #print element


def main(args):
    parser = BlinkIDLParser(debug=False)
    path = args[0]
    count = 0
    partialFilter = NotPartial
    for interfaceNode in GetInterfaceNodes(path):
        for filteredNode in partialFilter(interfaceNode):
            print filteredNode.GetName()
            print [attributeNames for attributeNames in GetAttributes(filteredNode) if attributeNames]
    #print 'count: ', count


if __name__ == '__main__':
    main(sys.argv[1:])
   
