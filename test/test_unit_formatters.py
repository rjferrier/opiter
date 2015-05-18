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

    def str(self, absolute=None, relative=None, collection_separator=None):
        result = ''
        if collection_separator:
            result += str(self.level) + collection_separator
        return result + self.node_name

    def is_first(self):
        return self.node_name == 'a'

        
class TestSimpleFormatter(unittest.TestCase):

    def setUp(self):
        self.node_info = FakeNodeInfo.combo('abc')
        self.formatter = SimpleFormatter()

    def test_simple_formatter(self):
        self.assertEqual(self.formatter(self.node_info), 'a_b_c')

    def test_simple_formatter_with_custom_separator(self):
        self.formatter = SimpleFormatter(',')
        self.assertEqual(self.formatter(self.node_info), 'a,b,c')

    
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
        self.assertEqual('\n'+self.formatter(node_info), expected)


    def test_tree_formatter_intermediate_combo(self):
        """
        I want to print part of the tree associated with an intermediate
        combination, [a,b,a].
        """
        node_info = FakeNodeInfo.combo('aba')
        expected = """
    1: b
        2: a"""
        self.assertEqual('\n'+self.formatter(node_info), expected)


    def test_tree_formatter_leaf_combo(self):
        """
        I want to print e.g. [a,a,b] which does not have any preamble when
        it is printed.
        """
        node_info = FakeNodeInfo.combo('aab')
        expected = """
        2: b"""
        self.assertEqual('\n'+self.formatter(node_info), expected)


    def test_tree_formatter_all(self):
        """
        I want to print the entire tree.
        """
        expected = """0: a
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
        self.assertEqual('\n'.join(results), expected)


    def test_tree_formatter_intermediate_combo_with_custom_separator(self):
        self.formatter = TreeFormatter(collection_separator='-')
        node_info = FakeNodeInfo.combo('aba')
        expected = """
    1-b
        2-a"""
        self.assertEqual('\n'+self.formatter(node_info), expected)


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
        self.assertEqual('\n'+self.formatter(node_info), expected)


    def test_tree_formatter_intermediate_combo_with_custom_indent(self):
        self.formatter = TreeFormatter(indent_string='...')
        node_info = FakeNodeInfo.combo('aba')
        expected = """
...1: b
......2: a"""
        self.assertEqual('\n'+self.formatter(node_info), expected)
