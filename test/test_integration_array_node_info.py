import unittest
from opiter.options_array import ArrayNodeInfo


class TestArrayNodeInfoPosition(unittest.TestCase):
    
    def setUp(self):
        """
        With a sequence of nodes named 'A', 'B' and 'C', I create
        ArrayNodeInfos for all three nodes.  I'll want to know which
        of these represent the start or end of the sequence, so I'll
        get their positions.
        """
        seq = ['A', 'B', 'C']
        self.a = ArrayNodeInfo('seq', seq, 0).position
        self.b = ArrayNodeInfo('seq', seq, 1).position
        self.c = ArrayNodeInfo('seq', seq, 2).position
    
    def test_at(self):
        # check position from start
        self.assertTrue(self.b.is_at(1))
        self.assertFalse(self.b.is_at(2))
        # check position from end
        self.assertTrue(self.b.is_at(-2))
        self.assertFalse(self.b.is_at(-1))
    
    def test_is_first(self):
        self.assertTrue(self.a.is_first())
        self.assertFalse(self.b.is_first())
        self.assertFalse(self.c.is_first())
    
    def test_is_last(self):
        self.assertFalse(self.a.is_last())
        self.assertFalse(self.b.is_last())
        self.assertTrue(self.c.is_last())


if __name__ == '__main__':
    unittest.main()
        
