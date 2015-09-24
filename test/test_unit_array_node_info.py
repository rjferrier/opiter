import unittest
from unit_options_array import UnitArrayNodeInfo
    

class TestArrayNodeInfoBasics(unittest.TestCase):

    def setUp(self):
        """
        With a sequence of nodes named 'A', 'B' and 'C', I create an
        ArrayNodeInfo object for the second node.
        """
        self.node_info = UnitArrayNodeInfo('seq', ['A', 'B', 'C'], 1)

    def test_belongs_to(self):
        """
        The node should test positive for belonging to 'seq', and negative
        for anything else.
        """
        self.assertTrue(self.node_info.belongs_to('seq'))
        self.assertFalse(self.node_info.belongs_to('B'))

    def test_belongs_to_any(self):
        """
        Similar to belongs_to test.
        """
        self.assertTrue(self.node_info.belongs_to_any(['seq', 'B']))
        self.assertFalse(self.node_info.belongs_to_any(['A', 'B']))
        
    def test_node_name(self):
        """
        I should be able to recover the name of the node from both 
        __str__ and get_string() methods.
        """
        self.assertEqual(self.node_info.get_string(), 'B')
        self.assertEqual(str(self.node_info), 'B')

    def test_other_node_name_from_absolute_index(self):
        """
        I should be able to recover the name of another node using an
        absolute index.  This will follow the usual Python indexing
        convention where a minus sign denotes position from the end.
        If the index runs past the end, an IndexError should be
        raised.
        """
        self.assertEqual(self.node_info.get_string(0), 'A')
        self.assertEqual(self.node_info.get_string(-1), 'C')
        self.assertRaises(IndexError, lambda: self.node_info.get_string(3))

    def test_other_node_name_from_relative_index(self):
        """
        I should be able to recover the name of another node using a
        relative index.  If it runs past the beginning, an IndexError
        should be raised.
        """
        self.assertEqual(self.node_info.get_string(relative=-1), 'A')
        self.assertRaises(IndexError,
                          lambda: self.node_info.get_string(relative=-2))

    def test_other_node_name_from_relative_and_absolute_index(self):
        """
        Using both a relative and absolute index should also work.
        A resulting negative index raises an IndexError.
        """
        self.assertEqual(self.node_info.get_string(relative=-1, absolute=2),
                         'B')
        self.assertRaises(IndexError, lambda: \
                          self.node_info.get_string(relative=-2, absolute=1))

    def test_other_node_name_from_absolute_index_in_dict(self):
        """
        The absolute index might be supplied via a dictionary of entries
        in the form {array_name: index}.  A deficient dictionary will
        cause the node name to default.
        """
        self.assertEqual(self.node_info.get_string({'seq': -1, 'foo': -1}),
                         'C')
        self.assertEqual(self.node_info.get_string({'foo': -1}), 'B')

    def test_other_node_name_from_relative_index_in_dict(self):
        """
        The relative index might be supplied via a dictionary of entries
        in the form {array_name: index}.  A deficient dictionary will
        cause the node name to default.
        """
        self.assertEqual(
            self.node_info.get_string(relative={'seq': -1, 'foo': -1}), 'A')
        self.assertEqual(
            self.node_info.get_string(relative={'foo': -1}), 'B')
        
    def test_array_and_node_name(self):
        self.assertEqual(self.node_info.get_string(collection_separator=': '),
                         'seq: B')
        
    def test_array_and_node_name_no_separation(self):
        self.assertEqual(self.node_info.get_string(collection_separator=''),
                         'seqB')

        
if __name__ == '__main__':
    unittest.main()
        
