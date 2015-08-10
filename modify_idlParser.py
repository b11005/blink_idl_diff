#!/usr/bin/env python                                                           

import os
import sys,pdb

chromium_path = os.path.abspath(
    os.path.join(os.environ['HOME'], 'chromium', 'src'))
blink_bindings_path = os.path.join(
    chromium_path, 'third_party', 'WebKit', 'Source', 'bindings', 'scripts')
sys.path.insert(0, blink_bindings_path)

from blink_idl_parser import parse_file, BlinkIDLParser

def GetPath(arg):
    for dpath, dnames, fnames in os.walk(arg):    
        path=[]
        for fname in fnames:
            if fname.endswith('.idl') and not fname=='InspectorInstrumentation.idl':
                path.append(dpath+'/'+fname)
        if path:
            yield path

def name_interface_list(child):
    name_interface=[]
    if child.GetLogLine('partial'):
        pass
    elif child.GetClass()=='Interface':
        name_interface.append(child.GetName())
    if name_interface:
        print  name_interface

def _dump_tree(node,args, depth=0):
    #print '  ' * depth + str(node)
    name_interface=[]
    for child in node.GetChildren():
        #name_interface_list(child)
        #pdb.set_trace()
        #print child.Traverse('partical',child.GetName())#I don't know how to find 'partical' object? node? attribute?
        if child.GetClass()=='Interface':# and child.GetLogLine('partial'):
            child.GetLogLine('partical')
            name_interface.append(child.GetName())
        #_dump_tree(child, depth + 1)
    #if len(name_interface)>=2:
    if name_interface:
       print name_interface

def main(args):
    parser = BlinkIDLParser(debug=False)
    definitions = parse_file(parser, args[0])
    #print '=== Tree ==='
    _dump_tree(definitions,args[0])
    

if __name__ == '__main__':
    fnames=GetPath(sys.argv[1])
    for files in fnames:
        main(files)
