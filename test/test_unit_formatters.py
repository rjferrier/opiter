import sys
sys.path.append('..')

import unittest
from node_info import SimpleFormatter
from itertools import product


class FakeNodeInfo:
    def __init__(self, level, name):
        self.level = level
        self.name = name

    @classmethod
    def combo(Self, names):
        return [Self(i, name) for i, name in enumerate(names)]

    def str(self, absolute=None, relative=None):
        result = self.name
        if absolute:
            result += absolute
        if relative:
            result += relative
        return result


class TestSimpleFormat(unittest.TestCase):

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

    
