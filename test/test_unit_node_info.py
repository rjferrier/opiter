import unittest
from opiter.node_info import NodeInfo, NodeInfoException


class UnitNodeInfo(NodeInfo):
    """
    A throwaway implementation of NodeInfo which is also decoupled
    from the Position implementation for unit testing purposes.
    """
    def __init__(self, collection_name, tags=[]):
        NodeInfo.__init__(self, 0, 0, tags=tags)
        self.collection_name = collection_name
    
    def create_position(self, node_index, array_length):
        return None

    def belongs_to(self, collection_name):
        return self.collection_name == collection_name

        
class TestNodeInfo(unittest.TestCase):
    
    def test_belongs_to_any_with_collection_names(self):
        ni = UnitNodeInfo('A')
        self.assertTrue(ni.belongs_to_any(['A', 'B']))
        self.assertFalse(ni.belongs_to_any(['B', 'C']))

    def test_create_node_info_with_unwrapped_tag(self):
        """
        Passing the tags argument a string should raise an error.
        """
        self.assertRaises(NodeInfoException,
                          lambda: UnitNodeInfo('A', tags='foo'))
        
    def test_belongs_to_any_with_tag_name(self):
        ni = UnitNodeInfo('A', tags=['tag1'])
        self.assertTrue(ni.belongs_to_any(['A']))
        self.assertTrue(ni.belongs_to_any(['tag1']))
        self.assertFalse(ni.belongs_to_any(['tag2']))
        
    def test_belongs_to_any_with_two_tag_names(self):
        ni = UnitNodeInfo('A', tags=['tag1', 'tag2'])
        self.assertTrue(ni.belongs_to_any(['tag2']))
        
