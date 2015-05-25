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
        ods = product.collapse()
        self.assertEqual(len(ods), 1)
        self.assertEqual([str(od) for od in ods], ['A_B'])

    def test_addition(self):
        summation = self.A + self.B
        ods = summation.collapse()
        self.assertEqual(len(ods), 1)
        self.assertEqual([str(od) for od in ods], ['A_B'])

        
class TestNodeOperationsWithArray(unittest.TestCase):

    def setUp(self):
        self.A = OptionsNode('A')
        self.numbers = OptionsArray('number', range(3))

    def test_multiplication(self):
        product = self.A * self.numbers
        ods = product.collapse()
        self.assertEqual(len(ods), 3)
        self.assertEqual([str(od) for od in ods], ['A_0', 'A_1', 'A_2'])

    def test_addition(self):
        """
        Adding many nodes on the right (R) to a single node on the left
        (L) should work, but the surplus right hand nodes will get
        discarded (to leave L_R).
        """
        summation = self.A + self.numbers
        ods = summation.collapse()
        self.assertEqual(len(ods), 1)
        self.assertEqual([str(od) for od in ods], ['A_0'])
        

        
class TestArrayOperationsWithNode(unittest.TestCase):

    def setUp(self):
        self.numbers = OptionsArray('number', range(3))
        self.A = OptionsNode('A')

    def test_multiplication(self):
        product = self.numbers * self.A
        ods = product.collapse()
        self.assertEqual(len(ods), 3)
        self.assertEqual([str(od) for od in ods], ['0_A', '1_A', '2_A'])

    def test_addition(self):
        """
        Adding one node on the right (R) to many on the left (L) should
        work, but the result will be uneven (L_R, L, L).
        """
        summation = self.numbers + self.A
        ods = summation.collapse()
        self.assertEqual(len(ods), 3)
        self.assertEqual([str(od) for od in ods], ['0_A', '1', '2'])

        
class TestArrayOperationsWithArray(unittest.TestCase):

    def setUp(self):
        self.letters = OptionsArray('letter', ['A', 'B', 'C'])
        self.numbers = OptionsArray('number', range(3))

    def test_multiplication(self):
        product = self.letters * self.numbers
        ods = product.collapse()
        self.assertEqual(len(ods), 9)
        self.assertEqual([str(od) for od in ods],
                         ['A_0', 'A_1', 'A_2',
                          'B_0', 'B_1', 'B_2',
                          'C_0', 'C_1', 'C_2'])

    def test_addition(self):
        summation = self.letters + self.numbers
        ods = summation.collapse()
        self.assertEqual(len(ods), 3)
        self.assertEqual([str(od) for od in ods], ['A_0', 'B_1', 'C_2'])

            
