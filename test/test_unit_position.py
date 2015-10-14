import unittest
from node_info import Position


class TestPosition(unittest.TestCase):

    def test_is_first(self):
        self.assertTrue(Position(0, 5).is_first())
        self.assertFalse(Position(2, 5).is_first())

    def test_is_last(self):
        self.assertTrue(Position(4, 5).is_last())
        self.assertFalse(Position(2, 5).is_last())

    def test_is_at(self):
        self.assertTrue(Position(2, 5).is_at(2))
        self.assertTrue(Position(4, 5).is_at(-1))
        self.assertFalse(Position(2, 5).is_at(-2))

    def test_equals(self):
        pos = Position(2, 5)
        self.assertEqual(pos, Position(2, 5))
        self.assertNotEqual(pos, Position(3, 5))
        self.assertNotEqual(pos, Position(2, 4))

