import sys
sys.path.append('..')

import unittest
from node_info import SimpleFormatter, TreeFormatter
from itertools import product


class FakeNodeInfo:
    """
    For representing a node on this tree:
    0: a
        1: a
            2: a
            2: b
            2: c
        1: b
            2: a
            2: b
            2: c
    """
    def __init__(self, level, node_name):
        self.level = level
        self.node_name = node_name

    @classmethod
    def combo(Self, node_names):
        return [Self(i, node_name) for i, node_name in enumerate(node_names)]

    def str(self, absolute=None, relative=None):
        result = self.node_name
        if absolute:
            result += absolute
        if relative:
            result += relative
        return result

    def get_collection_name(self):
        return str(self.level)

    def is_first(self):
        return self.node_name == 'a'

        
class TestSimpleFormatter(unittest.TestCase):

    def setUp(self):
        self.node_info = FakeNodeInfo.combo('abc')
        self.formatter = SimpleFormatter()

    def test_simple_formatter_with_no_optional_args(self):
        self.assertEqual(self.formatter(self.node_info), 'a_b_c')

    def test_simple_formatter_with_absolute_arg(self):
        self.assertEqual(
            self.formatter(self.node_info, absolute='A'), 'aA_bA_cA')

    def test_simple_formatter_with_relative_arg(self):
        self.assertEqual(
            self.formatter(self.node_info, relative='R'), 'aR_bR_cR')

    def test_simple_formatter_with_custom_separator(self):
        self.formatter = SimpleFormatter(',')
        self.assertEqual(self.formatter(self.node_info), 'a,b,c')

    def test_simple_formatter_with_collection_names(self):
        self.formatter = SimpleFormatter(collection_separator='-')
        self.assertEqual(self.formatter(self.node_info), '0-a_1-b_2-c')

    
class TestTreeFormatter(unittest.TestCase):

    def setUp(self):
        self.formatter = TreeFormatter()


    def test_tree_formatter_first_combo(self):
        """
        I want to print part of the tree associated with the very first
        node combination, [a,a,a].
        """
        node_info = FakeNodeInfo.combo('aaa')
        expected = """
0: a
    1: a
        2: a"""
        self.assertEqual(self.formatter(node_info), expected)


    def test_tree_formatter_intermediate_combo(self):
        """
        I want to print part of the tree associated with an intermediate
        combination, [a,b,a].
        """
        node_info = FakeNodeInfo.combo('aba')
        expected = """
    1: b
        2: a"""
        self.assertEqual(self.formatter(node_info), expected)


    def test_tree_formatter_leaf_combo(self):
        """
        I want to print e.g. [a,a,b] which does not have any preamble when
        it is printed.
        """
        node_info = FakeNodeInfo.combo('aab')
        expected = """
        2: b"""
        self.assertEqual(self.formatter(node_info), expected)


    def test_tree_formatter_all(self):
        """
        I want to print the entire tree.
        """
        expected = """
0: a
    1: a
        2: a
        2: b
        2: c
    1: b
        2: a
        2: b
        2: c"""
        results = [self.formatter(FakeNodeInfo.combo(c)) \
                   for c in product('a', 'ab', 'abc')]
        self.assertEqual(''.join(results), expected)


    def test_tree_formatter_intermediate_combo_with_optional_args(self):
        """
        Should the optional arguments affect which bits of the tree are
        printed in addition to which node is printed?  I don't think
        so.
        """
        node_info = FakeNodeInfo.combo('aba')
        expected = """
    1: bAR
        2: aAR"""
        self.assertEqual(self.formatter(node_info, absolute='A', relative='R'),
                         expected)


    def test_tree_formatter_intermediate_combo_with_custom_separator(self):
        self.formatter = TreeFormatter(collection_separator='-')
        node_info = FakeNodeInfo.combo('aba')
        expected = """
    1-b
        2-a"""
        self.assertEqual(self.formatter(node_info), expected)


    def test_tree_formatter_intermediate_combo_omitting_collection_names(self):
        """
        I want to omit the collection names altogether, so I'll specify
        the collection separator as None.
        """
        self.formatter = TreeFormatter(collection_separator=None)
        node_info = FakeNodeInfo.combo('aba')
        expected = """
    b
        a"""
        self.assertEqual(self.formatter(node_info), expected)


    def test_tree_formatter_intermediate_combo_with_custom_indent(self):
        self.formatter = TreeFormatter(indent_string='...')
        node_info = FakeNodeInfo.combo('aba')
        expected = """
...1: b
......2: a"""
        self.assertEqual(self.formatter(node_info), expected)
