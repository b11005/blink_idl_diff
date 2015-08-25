#/usr/bin/env python

import unittest, os
import interface_export_json

path = os.path.abspath(
    os.path.join(os.environ['HOME'], 'blink_idl_diff'))

class TestFunctions(unittest.TestCase):
    def setup(self):
        print 'setup'


    def test_interface_node(self):
        for actual in interface_export_json.get_interface_nodes(path):
            self.assertEqual(actual, "GCObservation")

if __name__ == '__main__':
    unittest.main()
        
