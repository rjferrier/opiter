import sys
sys.path.append('..')

import unittest
from options import OptionsDict, OptionsDictException
from re import search

class TestOptionsDictCreation(unittest.TestCase):

    def test_create_from_dict(self):
        """
        When I create an OptionsDict from a dict, there is no error.
        """
        OptionsDict({'foo': 'bar'})

    def test_create_from_dynamic_entries(self):
        """
        When I create an OptionsDict from a list of functions, there
        is no error.
        """
        def foo(opt):
            return 'bar'
        OptionsDict([foo])

    def test_create_from_non_dict(self):
        """
        When I create an OptionsDict using something other than a dict
        or a list of functions, an error should be raised.
        """
        create_od = lambda: OptionsDict('foo')
        self.assertRaises(OptionsDictException, create_od)

    def test_create_named_from_non_string(self):
        """
        When I create a named OptionsDict using something other than a
        string, an error should be raised.
        """
        create_od = lambda: OptionsDict.named({'foo': 'bar'})
        self.assertRaises(OptionsDictException, create_od)


class TestAnonymousOptionsDict(unittest.TestCase):
    
    def setUp(self):
        """I create an anonymous OptionsDict."""
        self.od = OptionsDict({'foo': 'bar'})
        
    def test_str(self):
        self.assertEqual(str(self.od), '')

    def test_repr(self):
        self.assertEqual(repr(self.od), ":{'foo': 'bar'}")

    def test_equal(self):
        self.assertEqual(self.od, OptionsDict({'foo': 'bar'}))

    def test_unequal(self):
        self.assertNotEqual(self.od, OptionsDict({'baz': 'bar'}))

    def test_positions_empty(self):
        self.assertIsNone(self.od.get_position())

    def test_copy(self):
        other = self.od.copy()
        # test for equivalence and non-identity
        self.assertEqual(other, self.od)
        self.assertFalse(other is self.od)
        # test that entries have been copied and not simply linked (we
        # do not guarantee that their components have been
        # deep-copied, however)
        other.update(OptionsDict({'foo': 'baz'}))
        self.assertNotEqual(other, self.od)
        
        
class TestNamedOptionsDict(unittest.TestCase):

    def setUp(self):
        """I create a named OptionsDict."""
        self.od = OptionsDict.named('foo', {'bar': 1})

    def test_equal_names_and_dicts(self):
        self.assertEqual(self.od,
                         OptionsDict.named('foo', {'bar': 1}))

    def test_equal_names_but_unequal_dicts(self):
        self.assertNotEqual(self.od,
                            OptionsDict.named('foo', {'bar': 2}))

    def test_unequal_names_but_equal_dicts(self):
        self.assertNotEqual(self.od,
                            OptionsDict.named('baz', {'bar': 1}))

    def test_copy(self):
        other = self.od.copy()
        # test for equivalence and non-identity
        self.assertEqual(other, self.od)
        self.assertFalse(other is self.od)
        # test that name components have been copied and not simply
        # linked
        other.update(OptionsDict.named('baz'))
        self.assertNotEqual(other, self.od)
        

    def test_default_str(self):
        """
        Calling the __str__ idiom and the str() method with no arguments
        should just return the name.
        """
        self.assertEqual(str(self.od), 'foo')
        self.assertEqual(self.od.str(), 'foo')

    # def test_str_from_missing_array_name(self):
    #     """
    #     Calling the str() method with the name of an array that hasn't
    #     been registered yet should trigger a KeyError.
    #     """
    #     self.assertRaises(KeyError, lambda: self.od.str(['foo']))

    # def test_str_exclude_missing_array_name(self):
    #     """
    #     Conversely, calling the str() method to exclude the substring
    #     corresponding to the name of an array that hasn't been
    #     registered yet should be fine.
    #     """
    #     self.assertEqual(self.od.str(exclude=['some_array']), 'foo')

        
class TestOptionsDictUpdateFromOptionsDict(unittest.TestCase):
        
    def setUp(self):
        """
        I create and store an OptionsDict.  I create another
        OptionsDict, with one entry duplicating a key from the stored
        dict but having a different corresponding value.  I update the
        stored dict with the other dict.
        """
        self.od = OptionsDict.named('A', {'foo': 1, 'bar': 2})
        other = OptionsDict.named('B', {'foo': 3, 'baz': 4})
        self.od.update(other)
        
    def test_name(self):
        self.assertEqual(str(self.od), 'A_B')
        
    def test_repr(self):
        """
        repr(C) should be 'A_B:{<contents>}'.
        """
        dict_pattern = "{['a-z: 0-9,]*}"
        self.assertIsNotNone(search('A_B:'+dict_pattern,
                                    repr(self.od)))

    def test_right_overrides_left(self):
        """
        Looking up the shared key should return the other dict's value.
        """
        self.assertEqual(self.od['foo'], 3)

        
class TestOptionsDictUpdateFromDict(unittest.TestCase):
    
    def setUp(self):
        """
        I create and store an OptionsDict.  I create a standard dict,
        with one entry duplicating a key from the stored dict but
        having a different corresponding value.  I update the stored
        dict with the other dict.
        """
        self.od = OptionsDict.named('A', {'foo': 1, 'bar': 2})
        other = {'foo': 3, 'baz': 4}
        self.od.update(other)
        
    def test_name(self):
        self.assertEqual(str(self.od), 'A')
        
    def test_repr(self):
        """
        repr(C) should be 'A:{<contents>}'.
        """
        dict_pattern = "{['a-z: 0-9,]*}"
        self.assertIsNotNone(search('A:'+dict_pattern, repr(self.od)))

        
class TestOptionsDictDynamicEntries(unittest.TestCase):
    
    def setUp(self):
        """
        I create an OptionsDict with two variables: kinematic_viscosity
        and pipe_diameter.  I define Reynolds_number, which is a dynamic
        entry dependent on velocity, pipe_diameter and
        kinematic_viscosity.  I haven't defined velocity yet.
        """
        self.od = OptionsDict({
            'kinematic_viscosity': 1.e-6,
            'pipe_diameter'      : 0.1 })
        def Reynolds_number(d):
            return d['velocity'] * d['pipe_diameter'] / \
                d['kinematic_viscosity']
        self.od.update([Reynolds_number])

    def test_missing_information_raises_error(self):
        """
        I try and obtain Reynolds_number before velocity is defined.  A
        KeyError should be raised.
        """
        self.assertRaises(KeyError, 
                          lambda: self.od['Reynolds_number'])

    def test_dynamic_entry(self):
        """
        I define velocity and change one the variables.
        Reynolds_number should update automatically.
        """
        self.od['velocity'] = 0.02
        self.assertAlmostEqual(self.od['Reynolds_number'], 2000.)
        self.od['pipe_diameter'] = 0.15
        self.assertAlmostEqual(self.od['Reynolds_number'], 3000.)

    def test_nested_entry(self):
        """
        I add an 'observation' entry which depends on Reynolds_number.
        When velocity is changed, observation should update
        automatically.
        """
        def observation(d):
            if d['Reynolds_number'] < 2100.:
                return 'laminar'
            elif d['Reynolds_number'] > 4000.:
                return 'turbulent'
            else:
                return 'transitional'
        # modify the dict
        self.od.update([observation])
        # now test
        self.od['velocity'] = 0.02
        self.assertEqual(self.od['observation'], 'laminar')
        self.od['velocity'] = 0.05
        self.assertEqual(self.od['observation'], 'turbulent')
        
    def test_nested_object(self):
        """
        Suppose I use self.od to create a new OptionsDict.  The new
        object should be equivalent, but not identical to, the old
        object.  That is, it should be a copy.
        """
        self.od['velocity'] = 0.
        dd = OptionsDict(self.od)
        # test for equivalence and non-identity
        self.assertEqual(dd, self.od)
        self.assertFalse(dd is self.od)
        # try changing the new object.  Its options entries should
        # update accordingly, while the old object should be unaffected
        dd['velocity'] = 0.02
        self.assertAlmostEqual(dd['Reynolds_number'], 2000.)
        self.assertAlmostEqual(self.od['Reynolds_number'], 0.)
        

class TestOptionsDictTemplateExpansion(unittest.TestCase):

    def setUp(self):
        self.od = OptionsDict({'fluid'         : 'water',
                               'melting_point' :       0,
                               'boiling_point' :     100})

    def test_expand_string(self):
        template = "$fluid has a melting point of $melting_point"+\
                   " degrees C."
        expected = "water has a melting point of 0 degrees C."
        self.assertEqual(self.od.expand_template(template), expected)

    def test_expand_string_missing_entry(self):
        template = "$fluid has a density of $density kg/m^3."
        expected = "water has a density of $density kg/m^3."
        self.assertEqual(self.od.expand_template(template), expected)


    def test_expand_nested(self):
        template = "$fluid has a $change point of ${${change}_point}"+\
                   " degrees C."
        
        self.od['change'] = 'melting'
        expected = "water has a melting point of 0 degrees C."
        self.assertEqual(self.od.expand_template(template, loops=2),
                         expected)
        
        self.od['change'] = 'boiling'
        expected = "water has a boiling point of 100 degrees C."
        self.assertEqual(self.od.expand_template(template, loops=2),
                         expected)

        
    def test_expand_not_enough_loops(self):
        template = "$fluid has a $change point of ${${change}_point}"+\
                   " degrees C."
        
        self.od['change'] = 'melting'
        expected = "water has a melting point of ${melting_point}"+\
                   " degrees C."
        self.assertEqual(self.od.expand_template(template),
                         expected)
        
    
if __name__ == '__main__':
    unittest.main()
        
