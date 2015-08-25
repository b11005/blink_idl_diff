#/usr/bin/env python

import unittest, os
import interface_export_json

path = os.path.abspath(
    os.path.join(os.environ['HOME'], 'blink_idl_diff'))

class TestFunctions(unittest.TestCase):

    def setUp(self):
        print 'SetUp'

    def test_idlfile(self):
        for i in interface_export_json.get_idl_files(path):
            actual = i
            self.assertEqual(actual, os.path.join(path, "test_interface.idl"))


if __name__ == '__main__':
    unittest.main()
