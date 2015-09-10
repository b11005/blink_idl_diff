#/usr/bin/env python

import unittest, os
import collect_idls_into_json

path = os.path.abspath(
    os.path.join(os.environ['HOME'], 'blink_idl_diff', 'sample1.txt'))

class TestFunctions(unittest.TestCase):
    def setup(self):
        print 'setup'


    def test_interfaces(self):
        for actual in collect_idls_into_json.get_interfaces(collect_idls_into_json.load_filepaths('sample1.txt')):
            #self.assertEqual(actual.GetName(), "GarbageCollectedScriptWrappable")
            #print actual.GetName()
            const = collect_idls_into_json.const_dict(actual)
            if const:
                print const['ExtAttributes'], const['Name']


if __name__ == '__main__':
    unittest.main()
