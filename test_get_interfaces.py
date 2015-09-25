#/usr/bin/env python

import unittest
import collect_idls_into_json
import utilities


class TestFunctions(unittest.TestCase):
    def setup(self):
        print 'setup'
        #for acrual in collect_idls_into_json.get_interfaces(utilities.read_file_to_list('sample.txt')):

    def test_interfaces(self):
       for actual in collect_idls_into_json.get_interfaces(utilities.read_file_to_list('sample0.txt')):
           self.assertEqual(actual.GetClass(), "Interface")

# not good
    def test_get_filepaths(self):
        for actual in collect_idls_into_json.get_interfaces(utilities.read_file_to_list('sample0.txt')):
            path = collect_idls_into_json.get_filepath(actual)
            self.assertTrue(path.startswith('Source'))
            self.assertTrue(path.endswith('.idl'))

    #def test_get_attributes(self):
    



    def test_interface_to_dict(self):
        for actual in collect_idls_into_json.get_interfaces(utilities.read_file_to_list('sample0.txt')):
            self.assertEqual(len(collect_idls_into_json.interface_to_dict(actual).keys()), 7)
            #print collect_idls_into_json.interface_to_dict(actual).items()


if __name__ == '__main__':
    unittest.main()
