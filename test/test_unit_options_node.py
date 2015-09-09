import unittest
from unit_tree_elements import UnitOptionsNode
from tree_elements import OptionsNodeException
from copy import deepcopy


class TestOptionsNodeCreation(unittest.TestCase):

    def check_name_and_entries(self, node, expected_name, expected_entries={}):
        self.assertEqual(str(node), expected_name)
        self.assertEqual(node.collapse()[0], expected_entries)
    
    def test_create_node_from_name(self):
        node = UnitOptionsNode('a_node')
        self.check_name_and_entries(node, 'a_node', {})
        
    def test_create_node_from_name_and_array(self):
        node = UnitOptionsNode('a_node', array_name='an_array')
        self.check_name_and_entries(node, 'a_node', {'an_array': 'a_node'})
        
    def test_create_node_from_name_and_format_function_and_array(self):
        name_format = lambda s: '<'+s+'>'
        node = UnitOptionsNode('a_node', array_name='an_array',
                               name_format=name_format)
        self.check_name_and_entries(node, '<a_node>', {'an_array': 'a_node'})
        
    def test_create_node_from_value_and_format_string(self):
        name_format = '{:.2f}'
        node = UnitOptionsNode(1./7, name_format=name_format)
        self.check_name_and_entries(node, '0.14')
        
    def test_create_node_from_value_and_format_function_and_array(self):
        name_format = lambda x: str(x + 1)
        node = UnitOptionsNode(1, name_format=name_format, array_name='num')
        self.check_name_and_entries(node, '2', {'num': 1})
        
    def test_create_node_from_name_and_value_and_array(self):
        node = UnitOptionsNode('a_node', 3, array_name='an_array')
        self.check_name_and_entries(node, 'a_node', {'an_array': 3})
        
    def test_create_node_from_entries(self):
        node = UnitOptionsNode({'foo': 'bar'}, array_name='num')
        self.check_name_and_entries(node, '', {'foo': 'bar'})
        
    def test_create_node_from_node_and_format_function_and_array(self):
        name_format = lambda s: '<'+s+'>'
        src = UnitOptionsNode('a_node')
        node = UnitOptionsNode(src, array_name='an_array',
                               name_format=name_format)
        self.check_name_and_entries(node, '<a_node>', {'an_array': 'a_node'})

    def test_create_node_with_bad_child(self):
        """
        When I create a node with a child that is not another
        OptionsTreeElement, an error should be raised.
        """
        create_node = lambda: UnitOptionsNode('foo', child='bar')
        self.assertRaises(OptionsNodeException, create_node)
        
        
class TestOptionsNodeBasics(unittest.TestCase):

    @staticmethod
    def make_node(name='foo', entries={'bar': 1},
                  child=UnitOptionsNode('qux')):
        return UnitOptionsNode(name, entries, child)
    
    def setUp(self):
        self.node = self.make_node()

    def test_equal(self):
        self.assertEqual(self.node, self.make_node())

    def test_unequal_names(self):
        self.assertNotEqual(self.node,
                            self.make_node(name='baz'))

    def test_unequal_dicts(self):
        self.assertNotEqual(self.node, 
                            self.make_node(entries={'bar': 2}))

    def test_unequal_dicts(self):
        self.assertNotEqual(self.node, 
                            self.make_node(child=UnitOptionsNode('baz')))

    def test_donate_copy(self):
        node_init = deepcopy(self.node)
        acceptor = UnitOptionsNode('baz')
        acceptor, remainder = self.node.donate_copy(acceptor)
        self.assertEqual(acceptor.child, node_init)
        self.assertEqual(len(remainder), 0)        

    def test_count_leaves(self):
        self.assertEqual(self.node.count_leaves(), 1)        

    def test_getitem(self):
        """
        There are no iterable children, so an IndexError should be raised.
        """
        getter = lambda: self.node[0]
        self.assertRaises(IndexError, getter)

    def test_setitem(self):
        """
        There are no iterable children, so an IndexError should be raised.
        """
        getter = lambda: self.node[0]
        self.assertRaises(IndexError, getter)

        
if __name__ == '__main__':
    unittest.main()
        
