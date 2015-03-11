import sys
sys.path.append('../src')

import unittest
from dynamic_dict import *

class TestDynamicDict(unittest.TestCase):
    
    def setUp(self):
        # create DynamicDict with a lambda-based DynamicEntry
        d = DynamicDict({
                'fahrenheit': DynamicEntry(
                    lambda d: d['celsius']*9./5 + 32.),
                })
        # also create a DynamicEntry using a conventional function
        def sensation_function(d):
            "Helper function"
            if d['celsius'] <= 20.:
                return 'cold'
            elif d['celsius'] <= 50.:
                return 'warm'
            else:
                return 'hot'
        # and use it to update the DynamicDict
        d['sensation']: DynamicEntry(sensation_function)
        

    def test_missing_information_raises_error(self):
        pass                    # tk

    def test_lambda_based_entry(self):
        d['celsius'] = 0.
        self.assertAlmostEqual(d['fahrenheit'], 32.)
        d['celsius'] = 100.
        self.assertAlmostEqual(d['fahrenheit'], 212.)

    def test_def_based_entry(self):
        pass                    # tk
        


