#!/usr/bin/env python
#coding:utf-8

import os, sys, json

def load_jsonfile(json_file):
    file_name = json_file
    print file_name
    with open(file_name, 'r') as f:
        #data = json.load(f)
        print f
        for path in f:
            print path
            
            #print data
        #print data.dumps(data, sort_keys = True, indent = 4)
    f.close()

def main(args):
    json_file = args[0]
    load_jsonfile(json_file)


if __name__ == '__main__':
    main(sys.argv[1:])
