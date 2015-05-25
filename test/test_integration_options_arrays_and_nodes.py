import sys
sys.path.append('..')

import unittest
from tree_elements import OptionsArray, OptionsNode
from options_dict import OptionsDict


class TestNodeOperationsWithNode(unittest.TestCase):

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

    # def test_addition(self):
    #     summation = self.A + self.B
    #     self.assertIsInstance(summation, OptionsNode)
    #     # the collapsed product should be a one-element list
    #     ods = summation.collapse()
    #     self.assertEqual(len(ods), 1)
    #     # inspect this element 
    #     self.assertIsInstance(ods[0], OptionsDict)
    #     self.assertEqual(str(ods[0]), 'A_B')

        
class TestNodeOperationsWithArray(unittest.TestCase):

    def setUp(self):
        self.A = OptionsNode('A')
        self.numbers = OptionsArray('number', range(3))

    def test_multiplication(self):
        product = self.A * self.numbers
        self.assertIsInstance(product, OptionsNode)
        # the collapsed product should be a three-element list
        ods = product.collapse()
        self.assertEqual(len(ods), 3)
        # inspect the elements
        expected_names = ['A_0', 'A_1', 'A_2']
        for od, expected in zip(ods, expected_names):
            self.assertIsInstance(od, OptionsDict)
            self.assertEqual(str(od), expected)

        
class TestArrayOperationsWithNode(unittest.TestCase):

    def setUp(self):
        self.numbers = OptionsArray('number', range(3))
        self.A = OptionsNode('A')

    def test_multiplication(self):
        product = self.numbers * self.A
        self.assertIsInstance(product, OptionsArray)
        # the collapsed product should be a three-element list
        ods = product.collapse()
        self.assertEqual(len(ods), 3)
        # inspect the elements
        expected_names = ['0_A', '1_A', '2_A']
        for od, expected in zip(ods, expected_names):
            self.assertIsInstance(od, OptionsDict)
            self.assertEqual(str(od), expected)
            

class TestArrayOperationsWithArray(unittest.TestCase):

    def setUp(self):
        self.letters = OptionsArray('letter', ['A', 'B'])
        self.numbers = OptionsArray('number', range(2))

    def test_multiplication(self):
        product = self.letters * self.numbers
        self.assertIsInstance(product, OptionsArray)
        # the collapsed product should be a four-element list
        ods = product.collapse()
        self.assertEqual(len(ods), 4)
        # inspect the elements
        expected_names = ['A_0', 'A_1', 'B_0', 'B_1']
        for el, expected in zip(ods, expected_names):
            self.assertEqual(str(el), expected)

            
