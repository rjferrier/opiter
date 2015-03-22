import sys
sys.path.append('..')

import unittest
from optree.dynamic_dict import DynamicDict


class TestDynamicDictUnit(unittest.TestCase):
    
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
        
