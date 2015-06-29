import sys
sys.path.append('..')

import unittest
from copy import deepcopy

from tree_elements import OptionsArray, OptionsNode
from options_dict import OptionsDict, Lookup, freeze
from multiprocessing import Pool


def pool():
    return Pool(2)


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


    @staticmethod
    def add_dynamic_entry(tree_element):
        """
        Implements a dynamic entry which returns the product of 'letter'
        and 'number' entries, treating A, B, C as 1, 2, 3.
        """
        tree_element.update({'product': lambda opt: \
                             (1 + 'ABC'.index(opt['letter'])) * opt['number']})


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

    def test_update_with_options_dict_from_other_node(self):
        other_od = self.other_node.collapse()[0]
        self.node.update(other_od)
        node_od = self.node.collapse()[0]
        self.assertEqual(node_od.str(), 'A_B')

    def test_update_with_options_dict_from_array(self):
        other_od = self.array.collapse()[0]
        self.node.update(other_od)
        node_od = self.node.collapse()[0]
        self.assertEqual(node_od.str(), 'A_0')

    def test_collapse_mp_safe(self):
        self.node.update({'letter': 'A', 'number': 2})
        self.add_dynamic_entry(self.node)
        ods = freeze(self.node.collapse())
        results = pool().map(Lookup('product'), ods)
        self.assertEqual(results, [2])

        
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
        array_ods = self.array.collapse()
        for od in array_ods:
            self.assertEqual(od['foo'], 'bar')

    def test_update_with_options_dict_from_node(self):
        node_od = self.node.collapse()[0]
        self.array.update(node_od)
        array_ods = self.array.collapse()
        self.assertEqual([od.str() for od in array_ods],
                         ['A_0', 'B_0', 'C_0'])

    def test_update_with_options_dict_from_other_array(self):
        other_od = self.other_array.collapse()[1]
        self.array.update(other_od)
        array_ods = self.array.collapse()
        self.assertEqual([od.str() for od in array_ods],
                         ['A_1', 'B_1', 'C_1'])

    def test_collapse_and_freeze(self):
        self.array.update({'number': 2})
        self.add_dynamic_entry(self.array)
        ods = freeze(self.array.collapse())
        results = pool().map(Lookup('product'), ods)
        expected = [2, 4, 6]
        self.assertEqual(results, expected)


class TestArraySetItemOperations(TestArrayOperations):
    """
    Let's not linger on these.  If we get what we expect for one or
    two operators, for both single item and slice accessors, then
    OptionsArray.__setitem__ is doing its job.
    """
    def test_item_incremental_addition_with_node(self):
        self.check_array_or_node_operation(
            self.array[1], self.node, self.plus, ['B_0'],
            is_incremental=True)
        
    def test_slice_incremental_addition_with_node(self):
        self.check_array_or_node_operation(
            self.array[1:], self.node, self.plus, ['B_0', 'C'],
            is_incremental=True)

    def test_item_incremental_multiplication_with_node(self):
        self.check_array_or_node_operation(
            self.array[1], self.node, self.times, ['B_0'],
            is_incremental=True)
        
    def test_slice_incremental_multiplication_with_node(self):
        self.check_array_or_node_operation(
            self.array[1:], self.node, self.times, ['B_0', 'C_0'],
            is_incremental=True)

        
class TestTreeOperations(NodeAndArrayOperationsTestFixture):

    def setUp(self):
        letters = OptionsArray('letter', ['A', 'B'])
        numbers = OptionsArray('number', range(2))
        # putting dynamic entries on the leaves is the most rigorous
        # way of testing them after a tree collapse
        self.add_dynamic_entry(numbers)
        self.tree = letters * numbers
        self.node = OptionsNode('i')
        self.array = OptionsArray('subnumber', ['i', 'ii', 'iii'])
        self.node_list = [OptionsNode(name) for name in ['i', 'ii', 'iii']]
        self.od = OptionsDict({'foo': 'bar'})

    def test_copy(self):
        other = self.tree.copy()
        # test for equivalence and non-identity
        self.assertEqual(other, self.tree)
        self.assertFalse(other is self.tree)

    def test_addition_with_node(self):
        self.check_array_or_node_operation(
            self.tree, self.node, self.plus,
            ['A_0_i', 'A_1', 'B_0', 'B_1'])

    def test_incremental_addition_with_node(self):
        self.check_array_or_node_operation(
            self.tree, self.node, self.plus_equals,
            ['A_0_i', 'A_1', 'B_0', 'B_1'], is_incremental=True)

    def test_multiplication_with_node(self):
        self.check_array_or_node_operation(
            self.tree, self.node, self.times,
            ['A_0_i', 'A_1_i', 'B_0_i', 'B_1_i'])

    def test_incremental_multiplication_with_node(self):
        self.check_array_or_node_operation(
            self.tree, self.node, self.times_equals,
            ['A_0_i', 'A_1_i', 'B_0_i', 'B_1_i'],
            is_incremental=True)

    def test_addition_with_array(self):
        self.check_array_or_node_operation(
            self.tree, self.array, self.plus,
            ['A_0_i', 'A_1_ii', 'B_0_iii', 'B_1'])

    def test_incremental_addition_with_array(self):
        self.check_array_or_node_operation(
            self.tree, self.array, self.plus_equals,
            ['A_0_i', 'A_1_ii', 'B_0_iii', 'B_1'],
            is_incremental=True)

    def test_multiplication_with_array(self):
        self.check_array_or_node_operation(
            self.tree, self.array, self.times,
            ['A_0_i', 'A_0_ii', 'A_0_iii',
             'A_1_i', 'A_1_ii', 'A_1_iii',
             'B_0_i', 'B_0_ii', 'B_0_iii',
             'B_1_i', 'B_1_ii', 'B_1_iii'])

    def test_incremental_multiplication_with_array(self):
        self.check_array_or_node_operation(
            self.tree, self.array, self.times_equals,
            ['A_0_i', 'A_0_ii', 'A_0_iii',
             'A_1_i', 'A_1_ii', 'A_1_iii',
             'B_0_i', 'B_0_ii', 'B_0_iii',
             'B_1_i', 'B_1_ii', 'B_1_iii'],
            is_incremental=True)

    def test_addition_with_list(self):
        self.check_array_or_node_operation(
            self.tree, self.node_list, self.plus,
            ['A_0_i', 'A_1_ii', 'B_0_iii', 'B_1'])

    def test_incremental_addition_with_list(self):
        self.check_array_or_node_operation(
            self.tree, self.node_list, self.plus_equals,
            ['A_0_i', 'A_1_ii', 'B_0_iii', 'B_1'],
            is_incremental=True)

    def test_update_with_options_dict(self):
        self.tree.update(self.od)
        tree_ods = self.tree.collapse()
        for od in tree_ods:
            self.assertEqual(od['foo'], 'bar')

    def test_update_with_options_dict_from_node(self):
        node_od = self.node.collapse()[0]
        self.tree.update(node_od)
        tree_ods = self.tree.collapse()
        self.assertEqual([od.str() for od in tree_ods],
                         ['A_0_i', 'A_1_i', 'B_0_i', 'B_1_i'])

    def test_update_with_options_dict_from_array(self):
        array_od = self.array.collapse()[1]
        self.tree.update(array_od)
        tree_ods = self.tree.collapse()
        self.assertEqual([od.str() for od in tree_ods],
                         ['A_0_ii', 'A_1_ii', 'B_0_ii', 'B_1_ii'])

    def test_collapse_and_freeze(self):
        ods = freeze(self.tree.collapse())
        results = pool().map(Lookup('product'), ods)
        expected = [0, 1, 0, 2]
        self.assertEqual(results, expected)


class TestTreeSetItemOperations(TestTreeOperations):
    def test_item_incremental_addition_with_node(self):
        self.check_array_or_node_operation(
            self.tree[1], self.node, self.plus, ['B_0_i', 'B_1'],
            is_incremental=True)
        
    def test_slice_incremental_addition_with_node(self):
        self.check_array_or_node_operation(
            self.tree[1:], self.node, self.plus, ['B_0_i', 'B_1'],
            is_incremental=True)

    def test_item_incremental_multiplication_with_node(self):
        self.check_array_or_node_operation(
            self.tree[1], self.node, self.times, ['B_0_i', 'B_1_i'],
            is_incremental=True)
        
    def test_slice_incremental_multiplication_with_node(self):
        self.check_array_or_node_operation(
            self.tree[1:], self.node, self.times, ['B_0_i', 'B_1_i'],
            is_incremental=True)


            
if __name__ == '__main__':
    unittest.main()
