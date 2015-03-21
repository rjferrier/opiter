import sys
sys.path.append('..')

import unittest
from optree import Option, OptionCreationError


class TestOptionCreation(unittest.TestCase):
    
    def test_create_from_non_name(self):
        """
        When I create an Option using something other than a name, an
        error should be raised.
        """
        self.assertRaises(OptionCreationError, 
                          lambda: Option({'foo': 'bar'}))
    
    def test_create_from_non_dict(self):
        """
        When I create an Option using a name and something other than a
        dict, an error should be raised.
        """
        self.assertRaises(OptionCreationError,
                          lambda: Option('2D', 'bar'))
        
