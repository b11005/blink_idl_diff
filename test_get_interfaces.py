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


    def test_implements(self):
        implements = [collect_idls_into_json.is_implements(actual) for actual in collect_idls_into_json.get_definitions(utilities.read_file_to_list(_FILE))]
        for implement in implements:
            if implement:
                self.assertEqual(collect_idls_into_json.get_interface_node(actual).GetClass(), 'Implement')
            else:
                self.assertFalse(implement)


    def test_fileter_non_partial(self):
        for node in collect_idls_into_json.get_definitions(utilities.read_file_to_list(_FILE)):
            if node.GetClass() == 'Interface' and not node.GetProperty('Partial'):
                self.assertTrue(collect_idls_into_json.filter_non_partial(node))
            else:
                self.assertFalse(collect_idls_into_json.filter_non_partial(node))


    def test_fileter_partial(self):
        for node in collect_idls_into_json.get_definitions(utilities.read_file_to_list(_FILE)):
            if node.GetClass() == 'Interface' and node.GetProperty('Partial'):
                self.assertTrue(collect_idls_into_json.filter_partial(node))
            else:
                self.assertFalse(collect_idls_into_json.filter_partial(node))


    def test_get_filepaths(self):
        for actual in collect_idls_into_json.get_definitions(utilities.read_file_to_list(_FILE)):
            path = collect_idls_into_json.get_filepath(actual)
            self.assertTrue(path.startswith('Source'))
            self.assertTrue(path.endswith('.idl'))


    def test_get_const_node_list(self):
        for actual in collect_idls_into_json.get_definitions(utilities.read_file_to_list(_FILE)):
            for const in collect_idls_into_json.get_const_node_list(actual):
                if const:
                    self.assertEqual(const.GetClass(), 'Const')


    '''def test_const_type(self):
        for actual in collect_idls_into_json.get_definitions(utilities.read_file_to_list(_FILE)):
            pass


    def test_get_const_value(self):
        for actual in collect_idls_into_json.get_definitions(utilities.read_file_to_list(_FILE)):
            pass


    def test_const_node_to_dict(self):
    '''


    def test_get_attribute_node_list(self):
        for actual in collect_idls_into_json.get_definitions(utilities.read_file_to_list(_FILE)):
            for attribute in collect_idls_into_json.get_attribute_node_list(actual):
                if attribute:
                    self.assertEqual(attribute.GetClass(), 'Attribute')

    '''def test_get_attribute_type(self):
        pass


    def test_attribute_node_to_dict(self):
        pass'''


    def test_get_operation_node_list(self):
        for actual in collect_idls_into_json.get_definitions(utilities.read_file_to_list(_FILE)):
            for operation in collect_idls_into_json.get_operation_node_list(actual):
                if operation:
                    self.assertEqual(operation.GetClass(), 'Operation')


    def test_get_argument_node_list(self):
        pass

    def test_argument_node_to_dict(self):
        pass

    def test_get_operation_name(self):
        pass


    def test_operation_node_to_dict(self):
        pass


    def test_get_extattribute_node_list(self):
        for actual in collect_idls_into_json.get_definitions(utilities.read_file_to_list(_FILE)):
            for extattr in collect_idls_into_json.get_extattribute_node_list(actual):
                if extattr:
                    self.assertEqual(extattr.GetClass(), 'ExtAttribute')

    def test_extattr_node_to_dict(self):
        pass

    def test_get_inherit_node(self):
        pass

    def test_inherit_node_to_dict(self):
        pass


    def test_interface_to_dict(self):
        for actual in collect_idls_into_json.get_definitions(utilities.read_file_to_list('sample0.txt')):
            self.assertTrue(_KEY_SET.issuperset(collect_idls_into_json.interface_node_to_dict(actual)))


    def test_merge_partial_dict(self):
        pass


    def test_merge_implement_node(self):
        pass

    def test_export_to_jsonfile(self):
        pass

if __name__ == '__main__':
    unittest.main()
