#/usr/bin/env python

import unittest
import collect_idls_into_json
import utilities

from blink_idl_parser import parse_file, BlinkIDLParser

_FILE = 'test.txt'
_KEY_SET = set(['Operations', 'Name', 'FilePath', 'Inherit', 'Consts', 'ExtAttributes', 'Attributes'])


class TestFunctions(unittest.TestCase):
    def setUp(self):
        parser = BlinkIDLParser()
        path = utilities.read_file_to_list(_FILE)[0]
        definitions = parse_file(parser, path)
        self.definition = definitions.GetChildren()[0]


    def test_definitions(self):
        for actual in collect_idls_into_json.get_definitions(utilities.read_file_to_list(_FILE)):
            self.assertEqual(actual.GetName(), self.definition.GetName())


    '''def test_get_implements(self):
        implement = self.definition.GetClass()
        if implement == 'Implements':
            self.assertTrue(collect_idls_into_json.is_implements())
        else:
            self.assertFalse(collect_idls_into_json.is_implements(node))'''


    def test_is_non_partial(self):
        if self.definition.GetClass() == 'Interface' and not self.definition.GetProperty('Partial'):
            self.assertTrue(collect_idls_into_json.is_non_partial(self.definition))
        else:
            self.assertFalse(collect_idls_into_json.is_non_partial(self.definition))
                

    '''def test_is_partial(self):
        if self.definition.GetClass() == 'Interface' and self.definition.GetProperty('Partial'):
            self.assertTrue(collect_idls_into_json.is_partial(self.definition))
        else:
            self.assertFalse(collect_idls_into_json.is_partial(self.definition))'''


    def test_get_filepaths(self):
        filepath = collect_idls_into_json.get_filepath(self.definition)
        self.assertTrue(filepath.startswith('Source'))
        self.assertTrue(filepath.endswith('.idl'))


    def test_const_node_to_dict(self):
        const_member = set(['Name', 'Type', 'Value', 'ExtAttributes'])
        for const in collect_idls_into_json.get_const_node_list(self.definition):
            if const:
                self.assertEqual(const.GetClass(), 'Const')
                self.assertTrue(const_member.issuperset(collect_idls_into_json.const_node_to_dict(const).keys()))
            else:
                self.assertEqual(const, None)


    '''def test_const_type(self):
        pass
        #for actual in collect_idls_into_json.get_definitions(utilities.read_file_to_list(_FILE)):
            #self.assertEqual(collect_idls_into_json.get_const_type(actual))
            #collect_idls_into_json.get_const_type(actual)


    def test_get_const_value(self):
        for actual in collect_idls_into_json.get_definitions(utilities.read_file_to_list(_FILE)):
            pass'''


    def test_attribute_node_to_dict(self):
        attribute_member = set(['Name', 'Type', 'ExtAttributes', 'Readonly', 'Static'])
        for attribute in collect_idls_into_json.get_attribute_node_list(self.definition):
            if attribute:
                self.assertEqual(attribute.GetClass(), 'Attribute')
                self.assertTrue(attribute_member.issuperset(collect_idls_into_json.attribute_node_to_dict(attribute).keys()))
            else:
                self.assertEqual(attribute, None)


    def test_operation_node_to_dict(self):
        operate_member = set(['Static', 'ExtAttributes', 'Type', 'Name', 'Arguments'])
        argument_member = set(['Name', 'Type'])
        for operation in collect_idls_into_json.get_operation_node_list(self.definition):
            if operation:
                self.assertEqual(operation.GetClass(), 'Operation')
                self.assertTrue(operate_member.issuperset(collect_idls_into_json.operation_node_to_dict(operation).keys()))
                for argument in collect_idls_into_json.get_argument_node_list(operation):
                    if argument:
                        self.assertEqual(argument.GetClass(), 'Argument')
                        self.assertTrue(argument_member.issuperset(collect_idls_into_json.argument_node_to_dict(argument).keys()))
                    else:
                        self.assertEqual(argument, None)
            else:
                self.assertEqual(operation, None)


    def test_extattribute_node_to_dict(self):
        for extattr in collect_idls_into_json.get_extattribute_node_list(self.definition):
            if extattr:
                self.assertEqual(extattr.GetClass(), 'ExtAttribute')
            else:
                self.assertEqual(extattr, None)


    def test_inherit_node_to_dict(self):
        for inherit in collect_idls_into_json.inherit_node_to_dict(self.definition):
            if inherit:
                self.assertEqual(inherit.keys(), 'Parent')
            else:
                self.assertEqual(inherit, [])


    def test_interface_node_to_dict(self):
        self.assertTrue(_KEY_SET.issuperset(collect_idls_into_json.interface_node_to_dict(self.definition)))


    '''def test_merge_partial_dicts(self):
        #for actual in collect_idls_into_json.get_definitions(utilities.read_file_to_list('sample0.txt')):
            #self.assertTrue(_KEY_SET.issuperset(collect_idls_into_json.merge_partial_dicts(actual)))
        pass

    def test_merge_implement_node(self):
        pass

    def test_export_to_jsonfile(self):
        pass'''


if __name__ == '__main__':
    unittest.main()
