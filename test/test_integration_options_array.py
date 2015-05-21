import sys
sys.path.append('..')

import unittest
from tree_elements import OptionsArray, OptionsNode
from options_dict import OptionsDict, OptionsDictException
    

class TestOptionsArrayCreationOptions(unittest.TestCase):

    def test_create_with_bad_common_entries(self):
        """
        I create an OptionsArray 'A' using three integers and
        something that is not a dictionary for the common_entries
        argument.  An error should be raised.
        """
        create_array = lambda: OptionsArray('A', range(3), 'foo')
        self.assertRaises(OptionsDictException, create_array)


class TestOptionsDictArrayBasics(unittest.TestCase):

    def setUp(self):
        """
        I create an OptionsArray from a list of assorted objects, one of
        which is an OptionsNode.
        """
        node = OptionsNode('some_dict', {'foo': 'bar'})
        self.values = ['A', 2, 3.14, node]
        self.array = OptionsArray('random', self.values)

    def test_element_types(self):
        for el in self.array:
            self.assertIsInstance(el, OptionsNode)

    def test_element_contents(self):
        """
        Getting the node's options_dict and querying 'random' should
        return the various values; additionally, the various
        dictionary entries we started with should now be queryable.
        """
        for i, el in enumerate(self.array):
            if i==3:
                self.assertEqual(el.options_dict['foo'], 'bar')
            else:
                self.assertEqual(el.options_dict['random'], self.values[i])
                

