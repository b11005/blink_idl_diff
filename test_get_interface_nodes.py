#/usr/bin/env python

import unittest, os
import interface_to_json

path = os.path.abspath(
    os.path.join(os.environ['HOME'], 'blink_idl_diff', 'test_interface.txt'))

class TestFunctions(unittest.TestCase):
    def setup(self):
        print 'setup'


    def test_interfaces(self):
        for actual in interface_to_json.get_interfaces('test_interface.txt'):
            self.assertEqual(actual.GetName(), "GarbageCollectedScriptWrappable")

if __name__ == '__main__':
    unittest.main()
