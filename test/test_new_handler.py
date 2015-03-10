import sys
sys.path.append('../src')

import unittest
from mock import Mock
from handlers import new_handler, NodeHandler, LevelHandler


class TestNewHandler(unittest.TestCase):

    def test_new_node_from_node_name(self):
        self.assertIsInstance(
            new_handler('1'), NodeHandler)

    def test_new_node_from_level_name_and_node_name(self):
        self.assertIsInstance(
            new_handler('A', '1'), NodeHandler)

    def test_new_level_from_node_name_list(self):
        self.assertIsInstance(
            new_handler('A', ['1', '2', '3']), LevelHandler)

    def test_new_level_from_node_name_tuple(self):
        self.assertIsInstance(
            new_handler('A', ('1', '2', '3')), LevelHandler)

    def test_new_node_from_node_name_and_sublevel(self):
        sub = new_handler('B', ('1', '2'))
        self.assertIsInstance(
            new_handler('1', sub), NodeHandler)

    def test_new_node_from_three_args(self):
        sub = new_handler('B', ('1', '2'))
        self.assertIsInstance(
            new_handler('A', '1', sub), NodeHandler)


if __name__ == '__main__':
    unittest.main()
        
