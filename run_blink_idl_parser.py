#!/usr/bin/env python                                                           

import os
import sys

chromium_path = os.path.abspath(
    os.path.join(os.environ['HOME'], 'chromium', 'src'))
blink_bindings_path = os.path.join(
    chromium_path, 'third_party', 'WebKit', 'Source', 'bindings', 'scripts')
sys.path.insert(0, blink_bindings_path)

from blink_idl_parser import parse_file, BlinkIDLParser


def _dump_tree(node, depth=0):
    print '  ' * depth + str(node)
    for child in node.GetChildren():
        _dump_tree(child, depth + 1)


def main(args):
    parser = BlinkIDLParser(debug=True)
    definitions = parse_file(parser, args[0])
    print '=== Tree ==='
    _dump_tree(definitions)


if __name__ == '__main__':
    main(sys.argv[1:])
