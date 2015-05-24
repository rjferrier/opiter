import sys
sys.path.append('..')

import unittest
from unit_tree_elements import UnitOptionsNode
from tree_elements import OptionsNodeException


class TestOptionsNodeCreation(unittest.TestCase):

    def test_create_node_from_non_string(self):
        """
        When I create a node using something other than a string, an
        error should be raised.
        """
        create_node = lambda: UnitOptionsNode({'foo': 'bar'})
        self.assertRaises(OptionsNodeException, create_node)

    def test_create_node_with_bad_child(self):
        """
        When I create a node with a child that is not another
        OptionsTreeElement, an error should be raised.
        """
        create_node = lambda: UnitOptionsNode('foo', child='bar')
        self.assertRaises(OptionsNodeException, create_node)
        
        
class TestOptionsNodeBasics(unittest.TestCase):

    def setUp(self):
        self.node = UnitOptionsNode('foo', {'bar': 1})

    def test_equal_names_and_dicts(self):
        self.assertEqual(self.node, UnitOptionsNode('foo', {'bar': 1}))

    def test_equal_names_but_unequal_dicts(self):
        self.assertNotEqual(self.node, UnitOptionsNode('foo', {'bar': 2}))

    def test_unequal_names_but_equal_dicts(self):
        self.assertNotEqual(self.node, UnitOptionsNode('baz', {'bar': 1}))

    def test_copy(self):
        other = self.node.copy()
        # test for equivalence and non-identity
        self.assertEqual(other, self.node)
        self.assertFalse(other is self.node)

    def test_str(self):
        self.assertEqual(str(self.node), 'foo')
        
    
if __name__ == '__main__':
    unittest.main()
        
