import sys
sys.path.append('..')

import unittest
from unit_tree_elements import UnitOptionsArray, UnitOptionsNode
from tree_elements import OptionsArrayException


class TestOptionsArrayCreation(unittest.TestCase):

    def test_create_from_assorted(self):
        """
        I should be able to create an array from assorted objects.
        """
        some_node = UnitOptionsNode('some_dict', {'foo': 'bar'})
        UnitOptionsArray( 'random', ['A', 2, 3.14, some_node])

        
    def test_create_with_unwrapped_dictionary(self):
        """
        I should not be able to create an array when one of the input
        elements is a dictionary.  This is because it is not obvious
        how to name the resulting nodes or what to store under the
        array key ('random').
        """
        create_array = lambda: UnitOptionsArray('random',
                                                ['A', 2, {'pi': 3.14}])
        self.assertRaises(OptionsArrayException, create_array)

        
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
        I create an OptionsArray from a list of differently-typed values,
        one of which is already an OptionsNode.
        """
        node = UnitOptionsNode('some_dict', {'foo': 'bar'})
        self.values = ['A', 2, 3.14, node]
        self.array = UnitOptionsArray('random', self.values)

    def test_element_names(self):
        """
        The name of each element, given by its string representation,
        should be identical to the string representation of the
        corresponding initial value.
        """
        for el, v in zip(self.array, self.values):
            self.assertEqual(str(el), str(v))

    def test_copy(self):
        other = self.array.copy()
        # test for equivalence and non-identity
        self.assertEqual(other, self.array)
        self.assertFalse(other is self.array)


class TestOptionsDictArrayOperations(unittest.TestCase):

    def setUp(self):
        self.letters = UnitOptionsArray('letter', ['A', 'B'])
        self.numbers = UnitOptionsArray('number', range(2))

    # def test_multiplication(self):
    #     tree = self.letters * self.numbers
    #     expected_names = ['A_0', 'A_1', 'B_0', 'B_1']
    #     for el, expected in tree.collapse():
    #         self.assertEqual(str(el), expected)

    
if __name__ == '__main__':
    unittest.main()
        
