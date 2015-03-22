import sys
sys.path.append('..')

import unittest
from optree import create_option


class TestOption(unittest.TestCase):

    def setUp(self):
        """
        I create an Option using a name and a dict.
        """
        self.opt = create_option('temperature', {
                'fahrenheit': lambda d: d['celsius']*9./5 + 32.})
    
    def test_use_option_as_dynamic_dict(self):
        """
        I should be able to use the Option as a DynamicDict.
        """
        self.opt['celsius'] = 100.
        self.assertAlmostEqual(self.opt['fahrenheit'], 212.)
        
