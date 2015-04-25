import sys
sys.path.append('..')

import unittest
from options import Context


class TestContext(unittest.TestCase):

    def setUp(self):
        """
        With a array of nodes named 'A', 'B' and 'C', I create a
        Context for the second node.
        """
        self.ct = Context(['A', 'B', 'C'], 1)

    def test_repr(self):
        self.assertEqual(repr(self.ct),
                         "Context(['A', 'B', 'C'], 1)")

    def test_node_name(self):
        """
        I should be able to recover the name of the node from both 
        __str__ and str() methods.
        """
        self.assertEqual(self.ct.str(), 'B')
        self.assertEqual(str(self.ct), 'B')

    def test_other_node_name_from_absolute_index(self):
        """
        I should be able to recover the name of another node using an
        absolute index.  This will follow the usual Python indexing
        convention where a minus sign denotes position from the end.
        If the index runs past the end, an IndexError should be
        raised.
        """
        self.assertEqual(self.ct.str(0), 'A')
        self.assertEqual(self.ct.str(-1), 'C')
        self.assertRaises(IndexError, lambda: self.ct.str(3))

    def test_other_node_name_from_relative_index(self):
        """
        I should be able to recover the name of another node using a
        relative index.  If it runs past the beginning, an IndexError
        should be raised.
        """
        self.assertEqual(self.ct.str(relative=-1), 'A')
        self.assertRaises(IndexError,
                          lambda: self.ct.str(relative=-2))

    def test_other_node_name_from_relative_and_absolute_index(self):
        """
        Using both a relative and absolute index should also work.
        A resulting negative index raises an IndexError.
        """
        self.assertEqual(self.ct.str(relative=-1, absolute=2), 'B')
        self.assertRaises(
            IndexError, lambda: self.ct.str(relative=-2, absolute=1))

        
if __name__ == '__main__':
    unittest.main()
        
