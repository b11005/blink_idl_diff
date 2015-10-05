#/usr/bin/env python

import unittest
import collect_idls_into_json
import utilities

_KEY_SET = set(['Operations', 'Name', 'FilePath', 'Inherit', 'Consts', 'ExtAttributes', 'Attributes'])
_FILE = 'sample0.txt'

class TestFunctions(unittest.TestCase):
    def setUp(self):
        pass


    def test_definitions(self):
       for actual in collect_idls_into_json.get_definitions(utilities.read_file_to_list(_FILE)):
           self.assertEqual(str(type(actual)), "<class 'idl_parser.idl_node.IDLNode'>")


    def test_interfaces(self):
        interface_nodes = [collect_idls_into_json.is_interface_node(actual) for actual in collect_idls_into_json.get_definitions(utilities.read_file_to_list(_FILE))]
        for interface in interface_nodes:
            if interface:
                self.assertEqual(collect_idls_into_json.get_interface_node(actual).GetClass(), 'Interface')


    def test_implements(self):
        implements = [collect_idls_into_json.is_implements(actual) for actual in collect_idls_into_json.get_definitions(utilities.read_file_to_list(_FILE))]
        for implement in implements:
            if implement:
                self.assertEqual(collect_idls_into_json.get_interface_node(actual).GetClass(), 'Implement')
            else:
                self.assertFalse(implement)


    def test_fileter_partial(self):
        for actual in collect_idls_into_json.filter_partial(collect_idls_into_json.get_definitions(utilities.read_file_to_list(_FILE))):
            self.assertTrue(actual.GetProperty('Partial'))


    def test_fileter_non_partial(self):
        for actual in collect_idls_into_json.filter_non_partial(collect_idls_into_json.get_definitions(utilities.read_file_to_list(_FILE))):
            self.assertFalse(actual.GetProperty('Partial'))


    def test_get_filepaths(self):
        for actual in collect_idls_into_json.get_definitions(utilities.read_file_to_list(_FILE)):
            path = collect_idls_into_json.get_filepath(actual)
            self.assertTrue(path.startswith('Source'))
            self.assertTrue(path.endswith('.idl'))


    def test_get_const_node(self):
        for actual in collect_idls_into_json.get_definitions(utilities.read_file_to_list(_FILE)):
            for const in collect_idls_into_json.get_const_node(actual):
                if const:
                    self.assertEqual(const.GetClass(), 'Const')


    def test_const_type(self):
        for actual in collect_idls_into_json.get_definitions(utilities.read_file_to_list(_FILE)):
            pass
            #print collect_idls_into_json.get_const_type(actual)
                    #self.assertEqual(const.GetClass(), 'Const')


    def test_get_const_value(self):
        for actual in collect_idls_into_json.get_definitions(utilities.read_file_to_list(_FILE)):
            pass
            #print collect_idls_into_json.get_const_value(actual)


    def test_get_attribute_node(self):
        for actual in collect_idls_into_json.get_definitions(utilities.read_file_to_list(_FILE)):
            for attribute in collect_idls_into_json.get_attribute_node(actual):
                if attribute:
                    self.assertEqual(attribute.GetClass(), 'Attribute')


    def test_get_operation_node(self):
        for actual in collect_idls_into_json.get_definitions(utilities.read_file_to_list(_FILE)):
            for operation in collect_idls_into_json.get_operation_node(actual):
                if operation:
                    self.assertEqual(operation.GetClass(), 'Operation')


    '''def test_interface_to_dict(self):
        for actual in collect_idls_into_json.get_interfaces(utilities.read_file_to_list('sample0.txt')):
            self.assertTrue(key_set.issuperset(collect_idls_into_json.interface_to_dict(actual)))'''


if __name__ == '__main__':
    unittest.main()
