import unittest
from unit_options_node import UnitOrphanNodeInfo


class TestOrphanNodeInfoString(unittest.TestCase):

    def setUp(self):
        """
        I create an OrphanNodeInfo object.
        """
        self.node_info = UnitOrphanNodeInfo('A')

    def test_belongs_to(self):
        """
        The node should test negative for belonging to anything.
        """
        self.assertFalse(self.node_info.belongs_to('A'))

    def test_belongs_to_any(self):
        """
        Similar to belongs_to test.
        """
        self.assertFalse(self.node_info.belongs_to_any(['A', 'B']))

    def test_node_name(self):
        """
        I should be able to recover the name of the node from both the
        __str__ and get_string() methods.
        """
        self.assertEqual(self.node_info.get_string(), 'A')
        self.assertEqual(str(self.node_info), 'A')

    def test_other_node_name_from_relative_index(self):
        """
        Only a relative index of 0 should be valid.
        """
        self.assertEqual(self.node_info.get_string(relative=0), 'A')
        self.assertRaises(IndexError,
                          lambda: self.node_info.get_string(relative=-1))

    def test_other_node_name_from_relative_and_absolute_index(self):
        """
        Strictly speaking, using both a relative and absolute index
        should work, but a resulting negative index will raise an
        IndexError.
        """
        self.assertEqual(self.node_info.get_string(relative=-1, absolute=1),
                         'A')
        self.assertRaises(
            IndexError, lambda: \
            self.node_info.get_string(relative=-2, absolute=1))

    def test_other_node_name_from_absolute_index_in_dict(self):
        """
        The absolute index might be supplied via a dictionary of items
        in the form {collection_name: index}.  Here the node name will
        default.
        """
        self.assertEqual(self.node_info.get_string({'foo': -1}), 'A')

    def test_other_node_name_from_relative_index_in_dict(self):
        """
        The relative index might be supplied via a dictionary of items
        in the form {collection_name: index}.  Here the node name will
        default.
        """
        self.assertEqual(self.node_info.get_string(relative={'foo': 1}), 'A')
        

if __name__ == '__main__':
    unittest.main()
        
