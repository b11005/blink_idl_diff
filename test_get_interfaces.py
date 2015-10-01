#/usr/bin/env python

import unittest
import collect_idls_into_json
import utilities

key_set = set(['Operations', 'Name', 'FilePath', 'Inherit', 'Consts', 'ExtAttributes', 'Attributes'])

class TestFunctions(unittest.TestCase):
    def setup(self):
        print 'setup'
        #for acrual in collect_idls_into_json.get_interfaces(utilities.read_file_to_list('sample.txt')):

    def test_interfaces(self):
       for actual in collect_idls_into_json.get_interfaces(utilities.read_file_to_list('sample0.txt')):
           self.assertEqual(actual.GetClass(), "Interface")


    def test_get_filepaths(self):
        for actual in collect_idls_into_json.get_interfaces(utilities.read_file_to_list('sample0.txt')):
            path = collect_idls_into_json.get_filepath(actual)
            self.assertTrue(path.startswith('Source'))
            self.assertTrue(path.endswith('.idl'))

    #def test_get_attributes(self):
        #for actual in collect_idls_into_json.get_interfaces(utilities.read_file_to_list('sample0.txt')):
            #self.assertEqual()



    def test_interface_to_dict(self):
        for actual in collect_idls_into_json.get_interfaces(utilities.read_file_to_list('sample0.txt')):
            self.assertTrue(key_set.issuperset(collect_idls_into_json.interface_to_dict(actual)))


if __name__ == '__main__':
    unittest.main()
