import sys
sys.path.append('..')

import unittest
from optionsdict import OptionsDict, OptionsDictException
from re import search

class TestOptionsDictCreation(unittest.TestCase):
    
    def test_create_from_non_name(self):
        """
        When I create an OptionsDict using something other than a
        string or None, an error should be raised.
        """
        create_od = lambda: OptionsDict({'foo': 'bar'})
        self.assertRaises(OptionsDictException, create_od)
    
    def test_create_from_non_dict(self):
        """
        When I create an OptionsDict using a name and something other
        than a dict, an error should be raised.
        """
        create_od = lambda: OptionsDict('foo', 'bar')
        self.assertRaises(OptionsDictException, create_od)

        
class TestOptionsDictBasics(unittest.TestCase):

    def setUp(self):
        """I create a simple OptionsDict."""
        self.od = OptionsDict('foo', {'bar': 1})

    def test_name(self):
        self.assertEqual(str(self.od), 'foo')

    def test_repr(self):
        self.assertEqual(repr(self.od), "foo:{'bar': 1}")

    def test_equal_names_and_dicts(self):
        self.assertEqual(self.od, OptionsDict('foo', {'bar': 1}))

    def test_equal_names_but_unequal_dicts(self):
        self.assertNotEqual(self.od, OptionsDict('foo', {'bar': 2}))

    def test_unequal_names_but_equal_dicts(self):
        self.assertNotEqual(self.od, OptionsDict('baz', {'bar': 1}))


class TestOptionsDictAddition(unittest.TestCase):
        
    def setUp(self):
        """
        I create two OptionsDicts, A and B.  One of the keys appears
        in both dictionaries but with different corresponding values.
        I add the OptionsDicts together and store the result as C.
        """
        self.A = OptionsDict('A', {'foo': 1, 'bar': 2})
        self.B = OptionsDict('B', {'foo': 3, 'baz': 4})
        self.C = self.A + self.B
        
    def test_name(self):
        """
        The string representation of C should be 'A_B'.
        """
        self.assertEqual(str(self.C), 'A_B')
        
    def test_add_nameless(self):
        """
        I add another OptionsDict, but I give it 

        The string representation of C should be 'A_B'.
        """
        self.assertEqual(str(self.C), 'A_B')
        
    def test_repr(self):
        """
        repr(C) should be 'A_B:{<contents>}'.
        """
        dict_pattern = "{['a-z: 0-9,]*}"
        self.assertIsNotNone(search('A_B:'+dict_pattern, repr(self.C)))

    def test_right_overrides_left(self):
        """
        Looking up the shared key in C should return B's value.
        """
        self.assertEqual(self.C['foo'], 3)

    def test_incremental_addition(self):
        """
        Doing an incremental addition should produce the same result
        as C.
        """
        self.A += self.B
        self.assertEqual(self.A, self.C)

    def test_sum(self):
        """
        Summing a list containing A and B should produce the same
        result as C.
        """
        self.assertEqual(sum([self.A, self.B]), self.C)

        
class TestAnonymousOptionsDict(unittest.TestCase):
    
    def setUp(self):
        """I create an anonymous OptionsDict."""
        self.od = OptionsDict(None, {'foo': 'bar'})
        
    def test_name(self):
        self.assertEqual(str(self.od), '')

    def test_repr(self):
        self.assertEqual(repr(self.od), ":{'foo': 'bar'}")

    def test_add_names(self):
        A = OptionsDict('A')
        B = OptionsDict('B')
        C = A + self.od + B
        self.assertEqual(str(self.od + self.od), "")
        self.assertEqual(str(self.od + A), "A")
        self.assertEqual(str(A + self.od + B), "A_B")

    
class TestOptionsDictDynamicEntries(unittest.TestCase):
    
    def setUp(self):
        """
        I create an OptionsDict with two options entries: 'fahrenheit',
        which is lambda-based, and 'water_state', which is def-based
        (i.e. based on a conventionally defined function).  Both rely
        on the 'celsius' entry, but I haven't defined this yet.
        """
        self.od = OptionsDict('temperature', {
            'fahrenheit': lambda d: d['celsius']*9./5 + 32.})
        def water_state(d):
            if d['celsius'] < 0.:
                return 'ice'
            elif d['celsius'] < 100.:
                return 'liquid'
            else:
                return 'steam'
        self.od['water_state'] = water_state

    def test_missing_information_raises_error(self):
        """
        I try and obtain 'fahrenheit' before 'celsius' is defined.  A
        KeyError should be raised.
        """
        self.assertRaises(KeyError, 
                          lambda: self.od['fahrenheit'])
        
    def test_lambda_based_entry(self):
        """
        I define and change 'celsius'. 'fahrenheit' should update
        automatically.
        """
        self.od['celsius'] = 0.
        self.assertAlmostEqual(
            self.od['fahrenheit'], 32.)
        self.od['celsius'] = 100.
        self.assertAlmostEqual(
            self.od['fahrenheit'], 212.)

    def test_def_based_entry(self):
        """
        I define and change 'celsius'.  'water_state' should update
        automatically.
        """
        self.od['celsius'] = -10.
        self.assertEqual(
            self.od['water_state'], 'ice')
        self.od['celsius'] = 50.
        self.assertAlmostEqual(
            self.od['water_state'], 'liquid')

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
        self.od['human_response'] = human_response
        # now test
        self.od['celsius'] = 0.
        self.assertIsNone(self.od['human_response'])
        self.od['celsius'] = 120.
        self.assertEqual(self.od['human_response'], 'ouch!')
        
    def test_nested_object(self):
        """
        Suppose I use self.od to create a new OptionsDict.  The new
        object should be equivalent, but not identical to, the old
        object.  That is, it should be a copy.
        """
        self.od['celsius'] = 0.
        dd = OptionsDict(str(self.od), self.od)
        # test for equivalence and non-identity
        self.assertEqual(dd, self.od)
        self.assertFalse(dd is self.od)
        # try changing the new object.  Its options entries should
        # update accordingly, while the old object should be unaffected
        dd['celsius'] = 100.
        self.assertAlmostEqual(dd['fahrenheit'], 212.)
        self.assertAlmostEqual(self.od['fahrenheit'], 32.)
        
        
if __name__ == '__main__':
    unittest.main()
        
