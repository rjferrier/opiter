import sys
sys.path.append('..')

import unittest
from copy import deepcopy

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

    @staticmethod
    def plus_equals(left_operand, right_operand):
        left_operand += right_operand
        return left_operand

    @staticmethod
    def times_equals(left_operand, right_operand):
        left_operand *= right_operand
        return left_operand
    
    def check_array_or_node_operation(
            self, left_operand, right_operand, operator, expected_names, 
            is_incremental=False):
        
        # save the states of the operands so we can check mutation
        left_operand_init = deepcopy(left_operand)
        right_operand_init = deepcopy(right_operand)
        
        # perform operation and flatten the result so we can inspect it
        if is_incremental:
            left_operand = operator(left_operand, right_operand)
            result = left_operand
        else:
            result = operator(left_operand, right_operand)
        ods = result.collapse()
        
        # check result
        self.assertEqual(len(ods), len(expected_names))
        self.assertEqual([str(od) for od in ods], expected_names)
        
        # check the states of the operands
        if is_incremental:
            self.assertNotEqual(left_operand_init, left_operand)
        else:
            self.assertEqual(left_operand_init, left_operand)
        self.assertEqual(right_operand_init, right_operand)


class TestNodeOperations(NodeAndArrayOperationsTestFixture):

    def setUp(self):
        self.node = OptionsNode('A')
        self.other_node = OptionsNode('B')
        self.array = OptionsArray('number', range(3))
        self.node_list = [OptionsNode(str(i)) for i in range(3)]
        self.od = OptionsDict({'foo': 'bar'})

    def test_addition_with_node(self):
        self.check_array_or_node_operation(
            self.node, self.other_node, self.plus, ['A_B'])

    def test_incremental_addition_with_node(self):
        self.check_array_or_node_operation(
            self.node, self.other_node, self.plus_equals, ['A_B'],
            is_incremental=True)

    def test_multiplication_with_node(self):
        self.check_array_or_node_operation(
            self.node, self.other_node, self.times, ['A_B'])

    def test_incremental_multiplication_with_node(self):
        self.check_array_or_node_operation(
            self.node, self.other_node, self.times_equals, ['A_B'],
            is_incremental=True)

    def test_addition_with_array(self):
        """
        Adding many nodes on the right (R) to a single node on the left
        (L) should work, but the surplus right hand nodes will get
        discarded (to leave L_R).
        """
        self.check_array_or_node_operation(
            self.node, self.array, self.plus, ['A_0'])

    def test_incremental_addition_with_array(self):
        self.check_array_or_node_operation(
            self.node, self.array, self.plus_equals, ['A_0'],
            is_incremental=True)

    def test_multiplication_with_array(self):
        self.check_array_or_node_operation(
            self.node, self.array, self.times, ['A_0', 'A_1', 'A_2'])

    def test_incremental_multiplication_with_array(self):
        self.check_array_or_node_operation(
            self.node, self.array, self.times_equals, ['A_0', 'A_1', 'A_2'],
            is_incremental=True)

    def test_addition_with_list(self):
        """
        As with TestNodeOperationsWithArray.test_addition, but here the
        first array in the list gets added to the node on the left
        hand side, and the other arrays get discarded.
        """
        self.check_array_or_node_operation(
            self.node, self.node_list, self.plus, ['A_0'])

    def test_incremental_addition_with_list(self):
        self.check_array_or_node_operation(
            self.node, self.node_list, self.plus_equals, ['A_0'],
            is_incremental=True)

    def test_update_with_options_dict(self):
        self.node.update(self.od)
        node_od = self.node.collapse()[0]
        self.assertEqual(node_od['foo'], 'bar')
        

        
class TestArrayOperations(NodeAndArrayOperationsTestFixture):

    def setUp(self):
        self.array = OptionsArray('letter', ['A', 'B', 'C'])
        self.other_array = OptionsArray('number', range(3))
        self.node = OptionsNode('0')
        self.node_list = [OptionsNode(str(i)) for i in range(3)]
        self.od = OptionsDict({'foo': 'bar'})

    def test_addition_with_node(self):
        self.check_array_or_node_operation(
            self.array, self.node, self.plus, ['A_0', 'B', 'C'])
        
    def test_incremental_addition_with_node(self):
        """
        Adding one node on the right (R) to many on the left (L) should
        work, but the result will be uneven (L_R, L, L).
        """
        self.check_array_or_node_operation(
            self.array, self.node, self.plus, ['A_0', 'B', 'C'],
            is_incremental=True)

    def test_multiplication_with_node(self):
        self.check_array_or_node_operation(
            self.array, self.node, self.times, ['A_0', 'B_0', 'C_0'])
        
    def test_incremental_multiplication_with_node(self):
        self.check_array_or_node_operation(
            self.array, self.node, self.times, ['A_0', 'B_0', 'C_0'],
            is_incremental=True)

    def test_addition_with_array(self):
        self.check_array_or_node_operation(
            self.array, self.other_array, self.plus, 
            ['A_0', 'B_1', 'C_2'])

    def test_incremental_addition_with_array(self):
        self.check_array_or_node_operation(
            self.array, self.other_array, self.plus_equals,
            ['A_0', 'B_1', 'C_2'], is_incremental=True)

    def test_multiplication_with_array(self):
        self.check_array_or_node_operation(
            self.array, self.other_array, self.times,
                         ['A_0', 'A_1', 'A_2',
                          'B_0', 'B_1', 'B_2',
                          'C_0', 'C_1', 'C_2'])

    def test_incremental_multiplication_with_array(self):
        self.check_array_or_node_operation(
            self.array, self.other_array, self.times_equals,
                         ['A_0', 'A_1', 'A_2',
                          'B_0', 'B_1', 'B_2',
                          'C_0', 'C_1', 'C_2'],
            is_incremental=True)

    def test_addition_with_list(self):
        self.check_array_or_node_operation(
            self.array, self.node_list, self.plus,
            ['A_0', 'B_1', 'C_2'])

    def test_incremental_addition_with_list(self):
        self.check_array_or_node_operation(
            self.array, self.node_list, self.plus_equals,
            ['A_0', 'B_1', 'C_2'], is_incremental=True)

    def test_update_with_options_dict(self):
        self.array.update(self.od)
        array_ods = self.array.collapse()[0]
        for od in array_ods:
            self.assertEqual(od['foo'], 'bar')

        
class TestTreeOperations(NodeAndArrayOperationsTestFixture):

    def setUp(self):
        self.tree = OptionsNode('root') * \
                    OptionsArray('letter', ['A', 'B', 'C'])
        self.node = OptionsNode('0')
        self.array = OptionsArray('number', range(3))
        self.node_list = [OptionsNode(str(i)) for i in range(3)]
        self.od = OptionsDict({'foo': 'bar'})

    def test_addition_with_node(self):
        self.check_array_or_node_operation(
            self.tree, self.node, self.plus, 
            ['root_A_0', 'root_B', 'root_C'])

    def test_incremental_addition_with_node(self):
        self.check_array_or_node_operation(
            self.tree, self.node, self.plus_equals, 
            ['root_A_0', 'root_B', 'root_C'], is_incremental=True)

    def test_multiplication_with_node(self):
        self.check_array_or_node_operation(
            self.tree, self.node, self.times,
            ['root_A_0', 'root_B_0', 'root_C_0'])

    def test_incremental_multiplication_with_node(self):
        self.check_array_or_node_operation(
            self.tree, self.node, self.times_equals,
            ['root_A_0', 'root_B_0', 'root_C_0'],
            is_incremental=True)

    def test_addition_with_array(self):
        self.check_array_or_node_operation(
            self.tree, self.array, self.plus,
            ['root_A_0', 'root_B_1', 'root_C_2'])

    def test_incremental_addition_with_array(self):
        self.check_array_or_node_operation(
            self.tree, self.array, self.plus_equals,
            ['root_A_0', 'root_B_1', 'root_C_2'],
            is_incremental=True)

    def test_multiplication_with_array(self):
        self.check_array_or_node_operation(
            self.tree, self.array, self.times,
            ['root_A_0', 'root_A_1', 'root_A_2',
             'root_B_0', 'root_B_1', 'root_B_2',
             'root_C_0', 'root_C_1', 'root_C_2'])

    def test_incremental_multiplication_with_array(self):
        self.check_array_or_node_operation(
            self.tree, self.array, self.times_equals,
            ['root_A_0', 'root_A_1', 'root_A_2',
             'root_B_0', 'root_B_1', 'root_B_2',
             'root_C_0', 'root_C_1', 'root_C_2'],
            is_incremental=True)

    def test_addition_with_list(self):
        self.check_array_or_node_operation(
            self.tree, self.node_list, self.plus,
            ['root_A_0', 'root_B_1', 'root_C_2'])

    def test_incremental_addition_with_list(self):
        self.check_array_or_node_operation(
            self.tree, self.node_list, self.plus_equals,
            ['root_A_0', 'root_B_1', 'root_C_2'],
            is_incremental=True)

    def test_update_with_options_dict(self):
        self.tree.update(self.od)
        tree_ods = self.tree.collapse()[0]
        for od in tree_ods:
            self.assertEqual(od['foo'], 'bar')

            
if __name__ == '__main__':
    unittest.main()
