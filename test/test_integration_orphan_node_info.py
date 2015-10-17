import unittest
from opiter.options_node import OrphanNodeInfo
        

class TestOrphanNodeInfoPosition(unittest.TestCase):
    
    def setUp(self):
        """
        I create an OrphanNodeInfo object and get its Position.
        """
        self.position = OrphanNodeInfo('A').position
    
    def test_at(self):
        # For an orphan node, the only true position is 0.  To keep
        # the implementation simple, the orphan node has the unusual
        # property of being first but never last according to Python's
        # negative indexing rules.
        self.assertTrue(self.position.is_at(0))
        self.assertFalse(self.position.is_at(1))
        self.assertFalse(self.position.is_at(-1))
    
    def test_is_first(self):
        self.assertTrue(self.position.is_first())
    
    def test_is_last(self):
        self.assertFalse(self.position.is_last())


        
if __name__ == '__main__':
    unittest.main()
        
