import sys
sys.path.append('..')

import unittest
from unit_tree_elements import UnitOptionsArray, UnitOptionsNode
from tree_elements import OptionsArrayException


class TestOptionsArrayCreationOptions(unittest.TestCase):

    def test_format_names_with_string(self):
        """
        I create an OptionsArray 'A' using integers 2, 5, 10.
        Format the element names as A02, A05, A10.
        """
        array = UnitOptionsArray('A', [2, 5, 10], name_format='A{:02g}')
        expected_names = ['A02', 'A05', 'A10']
        for el, expected in zip(array, expected_names):
            self.assertEqual(str(el), expected)

    def test_format_names_with_function(self):
        """
        I create an OptionsArray 'A' using floats 1, 2.5,
        6.25.  Format the element names as 1p00, 2p50, 6p25.
        """
        fmt = lambda x: '{:.2f}'.format(x).replace('.', 'p')
        array = UnitOptionsArray('A', [1., 2.5, 6.25], name_format=fmt)
        expected_names = ['1p00', '2p50', '6p25']
        for el, expected in zip(array, expected_names):
            self.assertEqual(str(el), expected)

    def test_format_names_with_bad_formatter(self):
        """
        I create an OptionsArray with an inappropriate object
        as name_format.  An error should be raised.
        """
        create_array = lambda: UnitOptionsArray('A', [1., 2.5, 6.25],
                                                name_format=None)
        self.assertRaises(OptionsArrayException, create_array)


class TestOptionsDictArrayBasics(unittest.TestCase):

    def setUp(self):
        """
        I create an OptionsArray from a list of different-typed
        values, one of which is already an OptionsNode.
        """
        od = UnitOptionsNode('some_dict', {'foo': 'bar'})
        self.values = ['A', od, 2, 3.14]
        self.array = UnitOptionsArray('random_things', self.values)

    def test_element_names(self):
        """
        The name of each element, given by its string representation,
        should be identical to the string representation of the
        corresponding initial value.
        """
        for el, v in zip(self.array, self.values):
            self.assertEqual(str(el), str(v))
        
        
if __name__ == '__main__':
    unittest.main()
        
