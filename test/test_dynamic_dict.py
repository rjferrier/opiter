import sys
sys.path.append('../src')

import unittest
from dynamic_dict import *

class TestDynamicDict(unittest.TestCase):
    
    def setUp(self):
        # create DynamicDict with a lambda-based entry
        self.dynamic_dict = DynamicDict({
                'fahrenheit': lambda d: d['celsius']*9./5 + 32.,
                })
        # add a conventionally defined function
        def water_state(d):
            if d['celsius'] < 0.:
                return 'ice'
            elif d['celsius'] < 100.:
                return 'liquid'
            else:
                return 'steam'
        self.dynamic_dict['water_state'] = water_state

    def test_missing_information_raises_error(self):
        self.assertRaises(KeyError, 
                          lambda: self.dynamic_dict['fahrenheit'])

    def test_lambda_based_entry(self):
        self.dynamic_dict['celsius'] = 0.
        self.assertAlmostEqual(
            self.dynamic_dict['fahrenheit'], 32.)
        self.dynamic_dict['celsius'] = 100.
        self.assertAlmostEqual(
            self.dynamic_dict['fahrenheit'], 212.)

    def test_def_based_entry(self):
        self.dynamic_dict['celsius'] = -10.
        self.assertEqual(
            self.dynamic_dict['water_state'], 'ice')
        self.dynamic_dict['celsius'] = 50.
        self.assertAlmostEqual(
            self.dynamic_dict['water_state'], 'liquid')

    def test_nested_entry(self):
        # modify the dict
        def human_response(d):
            if d['water_state']=='steam':
                return 'ouch!'
        self.dynamic_dict['human_response'] = human_response
        # test for different states
        self.dynamic_dict['celsius'] = 0.
        self.assertIsNone(self.dynamic_dict['human_response'])
        self.dynamic_dict['celsius'] = 120.
        self.assertEqual(self.dynamic_dict['human_response'], 'ouch!')

    def test_custom_function_entry(self):
        # need to wrap custom functions in a callable class
        def my_function(a, b, scale_b=1.):
            return a + b*scale_b
        self.dynamic_dict['my_function'] = CallableEntry(my_function)
        # test 
        self.assertAlmostEqual(
            self.dynamic_dict['my_function'](2., 3.), 5.)
        self.assertAlmostEqual(
            self.dynamic_dict['my_function'](2., 3., scale_b=2.), 8.)

if __name__ == '__main__':
    unittest.main()
        
