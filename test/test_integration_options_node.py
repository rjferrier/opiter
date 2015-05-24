import sys
sys.path.append('..')

import unittest
from tree_elements import OptionsNode
from options_dict import OptionsDict, OptionsDictException
    

class TestOptionsNodeCreationOptions(unittest.TestCase):

    def test_create_with_bad_common_entries(self):
        """
        I create an OptionsNode using something that is not a dictionary
        for the entries argument.  An error should be raised.
        """
        create_array = lambda: OptionsNode('A', 'foo')
        self.assertRaises(OptionsDictException, create_array)


class TestOptionsNodeBasics(unittest.TestCase):

    def setUp(self):
        self.node = OptionsNode('A', {'foo': 'bar'})

    def test_collapse(self):
        self.assertEqual(len(self.node.collapse()), 1)


class TestOptionsNodeAfterCollapse(unittest.TestCase):

    def setUp(self):
        node = OptionsNode('A', {'foo': 'bar'})
        self.od = node.collapse()[0]

    def test_type(self):
        self.assertIsInstance(self.od, OptionsDict)

    def test_name(self):
        self.assertEqual(str(self.od), 'A')

    def test_contents(self):
        self.assertEqual(self.od['foo'], 'bar')


class TestOptionsNodeOperations(unittest.TestCase):

    def setUp(self):
        self.A = OptionsNode('A')
        self.B = OptionsNode('B')

    def test_multiplication(self):
        product = self.A * self.B
        self.assertIsInstance(product, OptionsNode)
        # the collapsed product should be a one-element list
        ods = product.collapse()
        self.assertEqual(len(ods), 1)
        # inspect this element 
        self.assertIsInstance(ods[0], OptionsDict)
        self.assertEqual(str(ods[0]), 'A_B')
