#/usr/bin/env python

import unittest
import collect_idls_into_json
import utilities

_FILE = 'sample1.txt'
_KEY_SET = set(['Operations', 'Name', 'FilePath', 'Inherit', 'Consts', 'ExtAttributes', 'Attributes'])

class TestFunctions(unittest.TestCase):
    def setUp(self):
        pass


    def test_definitions(self):
       for actual in collect_idls_into_json.get_definitions(utilities.read_file_to_list(_FILE)):
           self.assertEqual(str(type(actual)), "<class 'idl_parser.idl_node.IDLNode'>")


    def test_get_implements(self):
        for node in collect_idls_into_json.get_definitions(utilities.read_file_to_list(_FILE)):
            implement = node.GetClass()
            if implement == 'Implements':
                self.assertTrue(collect_idls_into_json.is_implements(node))
            else:
                self.assertFalse(collect_idls_into_json.is_implements(node))


    def test_is_non_partial(self):
        for node in collect_idls_into_json.get_definitions(utilities.read_file_to_list(_FILE)):
            if node.GetClass() == 'Interface' and not node.GetProperty('Partial'):
                self.assertTrue(collect_idls_into_json.is_non_partial(node))
            else:
                self.assertFalse(collect_idls_into_json.is_non_partial(node))


    def test_is_partial(self):
        for node in collect_idls_into_json.get_definitions(utilities.read_file_to_list(_FILE)):
            if node.GetClass() == 'Interface' and node.GetProperty('Partial'):
                self.assertTrue(collect_idls_into_json.is_partial(node))
            else:
                self.assertFalse(collect_idls_into_json.is_partial(node))


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
                else:
                    self.assertEqual(const, None)


    def test_const_type(self):
        pass
        #for actual in collect_idls_into_json.get_definitions(utilities.read_file_to_list(_FILE)):
            #self.assertEqual(collect_idls_into_json.get_const_type(actual))
            #print collect_idls_into_json.get_const_type(actual)


    def test_get_const_value(self):
        for actual in collect_idls_into_json.get_definitions(utilities.read_file_to_list(_FILE)):
            pass


    def test_const_node_to_dict(self):
        const_member = set(['Name', 'Type', 'Value', 'ExtAttributes'])
        for node in collect_idls_into_json.get_definitions(utilities.read_file_to_list(_FILE)):
            consts = node.GetListOf('Const')
            for const in consts:
                if const:
                    self.assertTrue(const_member.issuperset(collect_idls_into_json.const_node_to_dict(const).keys()))


    def test_get_attribute_node_list(self):
        for actual in collect_idls_into_json.get_definitions(utilities.read_file_to_list(_FILE)):
            for attribute in collect_idls_into_json.get_attribute_node_list(actual):
                if attribute:
                    self.assertEqual(attribute.GetClass(), 'Attribute')


    def test_get_attribute_type(self):
        pass


    def test_attribute_node_to_dict(self):
        attribute_member = set(['Name', 'Type', 'ExtAttributes', 'Readonly', 'Static'])
        for node in collect_idls_into_json.get_definitions(utilities.read_file_to_list(_FILE)):
            attrs = node.GetListOf('Attribute')
            for attr in attrs:
                if attr:
                    self.assertTrue(attribute_member.issuperset(collect_idls_into_json.attribute_node_to_dict(attr).keys()))


    def test_get_operation_node_list(self):
        for actual in collect_idls_into_json.get_definitions(utilities.read_file_to_list(_FILE)):
            for operation in collect_idls_into_json.get_operation_node_list(actual):
                if operation:
                    self.assertEqual(operation.GetClass(), 'Operation')


    def test_get_argument_node_list(self):
        for actual in collect_idls_into_json.get_definitions(utilities.read_file_to_list(_FILE)):
            for child in actual.GetChildren():
                if child.GetClass() == 'Operation':
                    for argument in collect_idls_into_json.get_argument_node_list(child):
                        if argument:
                            self.assertEqual(argument.GetClass(), 'Argument')


    def test_argument_node_to_dict(self):
        argument_member = set(['Name', 'Type'])
        for node in collect_idls_into_json.get_definitions(utilities.read_file_to_list(_FILE)):
            if node.GetOneOf('Arguments'):
                args = node.GetOneOf('Arguments').GetListOf('Argument')
                for arg in args:
                    if arg:
                        self.assertTrue(argument_member.issuperset(collect_idls_into_json.argument_node_to_dict(arg).keys()))


    def test_get_operation_name(self):
        pass


    def test_operation_node_to_dict(self):
        operate_member = set(['Static', 'ExtAttributes', 'Type', 'Name', 'Arguments'])
        for node in collect_idls_into_json.get_definitions(utilities.read_file_to_list(_FILE)):
            operations = node.GetListOf('Operation')
            for operation in operations:
                if operation:
                    self.assertTrue(operate_member.issuperset(collect_idls_into_json.operation_node_to_dict(operation).keys()))


    def test_get_extattribute_node_list(self):
        for actual in collect_idls_into_json.get_definitions(utilities.read_file_to_list(_FILE)):
            for extattr in collect_idls_into_json.get_extattribute_node_list(actual):
                if extattr:
                    self.assertEqual(extattr.GetClass(), 'ExtAttribute')


    def test_extattr_node_to_dict(self):
        pass


    '''def test_get_inherit_node(self):
        for actual in collect_idls_into_json.get_definitions(utilities.read_file_to_list(_FILE)):
            for inherit in collect_idls_into_json.get_inherit_node(actual):
                if inherit:
                    self.assertEqual(inherit.GetClass(), 'Inherit')'''

    def test_inherit_node_to_dict(self):
        pass


    def test_interface_to_dict(self):
        for actual in collect_idls_into_json.get_definitions(utilities.read_file_to_list('sample0.txt')):
            self.assertTrue(_KEY_SET.issuperset(collect_idls_into_json.interface_node_to_dict(actual)))


    def test_merge_partial_dicts(self):
        #for actual in collect_idls_into_json.get_definitions(utilities.read_file_to_list('sample0.txt')):
            #self.assertTrue(_KEY_SET.issuperset(collect_idls_into_json.merge_partial_dicts(actual)))
        pass

    def test_merge_implement_node(self):
        pass

    def test_export_to_jsonfile(self):
        pass

if __name__ == '__main__':
    unittest.main()
