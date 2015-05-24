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


class TestOptionsArrayBasics(unittest.TestCase):

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

    def test_element_types_after_collapse(self):
        for el in self.array.collapse():
            self.assertIsInstance(el, OptionsDict)

    def test_element_contents_after_collapse(self):
        """
        Getting the options dictionaries and querying 'random' should
        return the various values; alternatively, the OptionsNode
        dictionary we started with should now be queryable.
        """
        for i, el in enumerate(self.array.collapse()):
            if i==3:
                self.assertEqual(el['foo'], 'bar')
            else:
                self.assertEqual(el['random'], self.values[i])


class TestOptionsArrayOperations(unittest.TestCase):

    def setUp(self):
        self.letters = OptionsArray('letter', ['A', 'B'])
        self.numbers = OptionsArray('number', range(2))

    # def test_multiplication(self):
    #     tree = self.letters * self.numbers
    #     expected_names = ['A_0', 'A_1', 'B_0', 'B_1']
    #     for el, expected in zip(tree.collapse(), expected_names):
    #         self.assertEqual(str(el), expected)
