import sys
sys.path.append('..')

import unittest
from copy import copy

from tree_elements import OptionsArray, OptionsNode
from options_dict import OptionsDict


class NodeAndArrayOperationsTestFixture(unittest.TestCase):
    """Provides common test functions."""

    @staticmethod
    def plus(left_operand, right_operand):
        return left_operand + right_operand

    @staticmethod
    def times(left_operand, right_operand):
        return left_operand * right_operand
    
    def check_array_or_node_operation(
            self, left_operand, right_operand, operator, expected_names):
        # perform operation and flatten the result so we can inspect it
        result = operator(left_operand, right_operand)
        ods = result.collapse()
        # check result
        self.assertEqual(len(ods), len(expected_names))
        self.assertEqual([str(od) for od in ods], expected_names)
    
    def check_array_or_node_operation_does_not_mutate(
            self, left_operand, right_operand, operator):
        left_operand_init = copy(left_operand)
        right_operand_init = copy(right_operand)
        # perform operation 
        result = operator(left_operand, right_operand)
        # check the operands haven't mutated
        self.assertEqual(left_operand_init, left_operand)
        self.assertEqual(right_operand_init, right_operand)


class TestNodeOperationsWithNode(NodeAndArrayOperationsTestFixture):

    def setUp(self):
        self.A = OptionsNode('A')
        self.B = OptionsNode('B')

    def test_addition(self):
        self.check_array_or_node_operation(
            self.A, self.B, self.plus, ['A_B'])

    def test_multiplication(self):
        self.check_array_or_node_operation(
            self.A, self.B, self.times, ['A_B'])

    def test_addition_does_not_mutate(self):
        self.check_array_or_node_operation_does_not_mutate(
            self.A, self.B, self.plus)

    def test_multiplication_does_not_mutate(self):
        self.check_array_or_node_operation_does_not_mutate(
            self.A, self.B, self.times)

        
class TestNodeOperationsWithArray(NodeAndArrayOperationsTestFixture):

    def setUp(self):
        self.A = OptionsNode('A')
        self.numbers = OptionsArray('number', range(3))

    def test_addition(self):
        """
        Adding many nodes on the right (R) to a single node on the left
        (L) should work, but the surplus right hand nodes will get
        discarded (to leave L_R).
        """
        self.check_array_or_node_operation(
            self.A, self.numbers, self.plus, ['A_0'])

    def test_multiplication(self):
        self.check_array_or_node_operation(
            self.A, self.numbers, self.times, ['A_0', 'A_1', 'A_2'])

    def test_addition_does_not_mutate(self):
        self.check_array_or_node_operation_does_not_mutate(
            self.A, self.numbers, self.plus)

    def test_multiplication_does_not_mutate(self):
        self.check_array_or_node_operation_does_not_mutate(
            self.A, self.numbers, self.times)

        
class TestNodeOperationsWithList(NodeAndArrayOperationsTestFixture):
    def setUp(self):
        self.A = OptionsNode('A')
        self.numbers = [OptionsNode(str(i)) for i in range(3)]

    def test_addition(self):
        """
        As with TestNodeOperationsWithArray.test_addition, but here the
        first array in the list gets added to the node on the left
        hand side, and the other arrays get discarded.
        """
        self.check_array_or_node_operation(
            self.A, self.numbers, self.plus, ['A_0'])

    def test_addition_does_not_mutate(self):
        self.check_array_or_node_operation_does_not_mutate(
            self.A, self.numbers, self.plus)
        

        
class TestArrayOperationsWithNode(NodeAndArrayOperationsTestFixture):

    def setUp(self):
        self.numbers = OptionsArray('number', range(3))
        self.A = OptionsNode('A')

    def test_addition(self):
        """
        Adding one node on the right (R) to many on the left (L) should
        work, but the result will be uneven (L_R, L, L).
        """
        self.check_array_or_node_operation(
            self.numbers, self.A, self.plus, ['0_A', '1', '2'])

    def test_multiplication(self):
        self.check_array_or_node_operation(
            self.numbers, self.A, self.times, ['0_A', '1_A', '2_A'])

    def test_addition_does_not_mutate(self):
        self.check_array_or_node_operation_does_not_mutate(
            self.numbers, self.A, self.plus)

    def test_multiplication_does_not_mutate(self):
        self.check_array_or_node_operation_does_not_mutate(
            self.numbers, self.A, self.times)

        
class TestArrayOperationsWithArray(NodeAndArrayOperationsTestFixture):

    def setUp(self):
        self.letters = OptionsArray('letter', ['A', 'B', 'C'])
        self.numbers = OptionsArray('number', range(3))

    def test_addition(self):
        self.check_array_or_node_operation(
            self.letters, self.numbers, self.plus, ['A_0', 'B_1', 'C_2'])

    def test_multiplication(self):
        self.check_array_or_node_operation(
            self.letters, self.numbers, self.times,
                         ['A_0', 'A_1', 'A_2',
                          'B_0', 'B_1', 'B_2',
                          'C_0', 'C_1', 'C_2'])

    def test_addition_does_not_mutate(self):
        self.check_array_or_node_operation_does_not_mutate(
            self.letters, self.numbers, self.plus)

    def test_multiplication_does_not_mutate(self):
        self.check_array_or_node_operation_does_not_mutate(
            self.letters, self.numbers, self.times)

        
class TestArrayOperationsWithList(NodeAndArrayOperationsTestFixture):
    def setUp(self):
        self.letters = OptionsArray('letter', ['A', 'B', 'C'])
        self.numbers = [OptionsNode(str(i)) for i in range(3)]

    def test_addition(self):
        self.check_array_or_node_operation(
            self.letters, self.numbers, self.plus, ['A_0', 'B_1', 'C_2'])

    def test_addition_does_not_mutate(self):
        self.check_array_or_node_operation_does_not_mutate(
            self.letters, self.numbers, self.plus)


class TestTreeOperationsWithNode(NodeAndArrayOperationsTestFixture):

    def setUp(self):
        self.tree = OptionsNode('root') * \
                    OptionsArray('letter', ['A', 'B', 'C'])
        self.node = OptionsNode('0')

    def test_addition(self):
        self.check_array_or_node_operation(
            self.tree, self.node, self.plus, ['root_A_0', 'root_B', 'root_C'])

    def test_multiplication(self):
        self.check_array_or_node_operation(
            self.tree, self.node, self.times,
            ['root_A_0', 'root_B_0', 'root_C_0'])

    def test_addition_does_not_mutate(self):
        self.check_array_or_node_operation_does_not_mutate(
            self.tree, self.node, self.plus)

    def test_multiplication_does_not_mutate(self):
        self.check_array_or_node_operation_does_not_mutate(
            self.tree, self.node, self.times)


class TestTreeOperationsWithArray(NodeAndArrayOperationsTestFixture):

    def setUp(self):
        self.tree = OptionsNode('root') * \
                    OptionsArray('letter', ['A', 'B', 'C'])
        self.array = OptionsArray('number', range(3))

    def test_addition(self):
        self.check_array_or_node_operation(
            self.tree, self.array, self.plus,
            ['root_A_0', 'root_B_1', 'root_C_2'])

    def test_multiplication(self):
        self.check_array_or_node_operation(
            self.tree, self.array, self.times,
            ['root_A_0', 'root_A_1', 'root_A_2',
             'root_B_0', 'root_B_1', 'root_B_2',
             'root_C_0', 'root_C_1', 'root_C_2'])

    def test_addition_does_not_mutate(self):
        self.check_array_or_node_operation_does_not_mutate(
            self.tree, self.array, self.plus)

    def test_multiplication_does_not_mutate(self):
        self.check_array_or_node_operation_does_not_mutate(
            self.tree, self.array, self.times)

        
class TestTreeOperationsWithList(NodeAndArrayOperationsTestFixture):
    def setUp(self):
        self.tree = OptionsNode('root') * \
                    OptionsArray('letter', ['A', 'B', 'C'])
        self.numbers = [OptionsNode(str(i)) for i in range(3)]

    def test_addition(self):
        self.check_array_or_node_operation(
            self.tree, self.numbers, self.plus,
            ['root_A_0', 'root_B_1', 'root_C_2'])

    def test_addition_does_not_mutate(self):
        self.check_array_or_node_operation_does_not_mutate(
            self.tree, self.numbers, self.plus)
