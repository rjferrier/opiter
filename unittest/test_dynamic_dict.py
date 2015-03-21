import sys
sys.path.append('../src')

import unittest
from dynamic_dict import DynamicDict, CallableEntry


class TestDynamicDict(unittest.TestCase):
    
    def setUp(self):
        """
        I create a DynamicDict with two dynamic entries: 'fahrenheit',
        which is lambda-based, and 'water_state', which is def-based
        (i.e. based on a conventionally defined function).  Both rely
        on the 'celsius' entry, but I haven't defined this yet.
        """
        self.dynamic_dict = DynamicDict({
            'fahrenheit': lambda d: d['celsius']*9./5 + 32.})
        def water_state(d):
            if d['celsius'] < 0.:
                return 'ice'
            elif d['celsius'] < 100.:
                return 'liquid'
            else:
                return 'steam'
        self.dynamic_dict['water_state'] = water_state

    def test_missing_information_raises_error(self):
        """
        I try and obtain 'fahrenheit' before 'celsius' is defined.  A
        KeyError should be raised.
        """
        self.assertRaises(KeyError, 
                          lambda: self.dynamic_dict['fahrenheit'])
        
    def test_lambda_based_entry(self):
        """
        I define and change 'celsius'. 'fahrenheit' should update
        automatically.
        """
        self.dynamic_dict['celsius'] = 0.
        self.assertAlmostEqual(
            self.dynamic_dict['fahrenheit'], 32.)
        self.dynamic_dict['celsius'] = 100.
        self.assertAlmostEqual(
            self.dynamic_dict['fahrenheit'], 212.)

    def test_def_based_entry(self):
        """
        I define and change 'celsius'.  'water_state' should update
        automatically.
        """
        self.dynamic_dict['celsius'] = -10.
        self.assertEqual(
            self.dynamic_dict['water_state'], 'ice')
        self.dynamic_dict['celsius'] = 50.
        self.assertAlmostEqual(
            self.dynamic_dict['water_state'], 'liquid')

    def test_nested_entry(self):
        """
        I add a 'human_response' entry which depends on 'water_state'.
        When 'celsius' is changed, 'human_response' should update
        automatically.
        """
        def human_response(d):
            if d['water_state']=='steam':
                return 'ouch!'
        # modify the dict
        self.dynamic_dict['human_response'] = human_response
        # now test
        self.dynamic_dict['celsius'] = 0.
        self.assertIsNone(self.dynamic_dict['human_response'])
        self.dynamic_dict['celsius'] = 120.
        self.assertEqual(self.dynamic_dict['human_response'], 'ouch!')

    def test_custom_function_entry(self):
        """
        I add a function.  As discussed in the dynamic_dict module, I
        need to protect this function using a wrapper class such as
        CallableEntry.  I should be able to retrieve the function as I
        would any other entry, and it should behave as expected.
        """
        def my_function(a, b, scale_b=1.):
            return a + b*scale_b
        # modify the dict
        self.dynamic_dict['my_function'] = CallableEntry(my_function)
        # now test 
        fun = self.dynamic_dict['my_function']
        self.assertAlmostEqual(fun(2., 3.), 5.)
        self.assertAlmostEqual(fun(2., 3., scale_b=2.), 8.)
        
    def test_nested_object(self):
        """
        Suppose I mistake dynamic_dict for a conventional dict, and I
        try using it to create a new DynamicDict.  The new object
        should be equivalent, but not identical to, the old object.
        That is, it should be a copy.
        """
        self.dynamic_dict['celsius'] = 0.
        dd = DynamicDict(self.dynamic_dict)
        # test for equivalence and non-identity
        self.assertEqual(dd, self.dynamic_dict)
        self.assertFalse(dd is self.dynamic_dict)
        # try changing the new object.  Its dynamic entries should
        # update accordingly, while the old object should be unaffected
        dd['celsius'] = 100.
        self.assertAlmostEqual(dd['fahrenheit'], 212.)
        self.assertAlmostEqual(self.dynamic_dict['fahrenheit'], 32.)

if __name__ == '__main__':
    unittest.main()
        
