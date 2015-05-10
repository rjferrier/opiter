import sys
sys.path.append('..')

import unittest
from options import OptionsDictException
from unit_options_dict import OptionsDictUnderTest
        

class TestOptionsDictOrphanNodeCreation(unittest.TestCase):

    def test_create_node_from_non_string(self):
        """
        When I create a node using something other than a string, an error
        should be raised.
        """
        create_od = lambda: OptionsDictUnderTest.node({'foo': 'bar'})
        self.assertRaises(OptionsDictException, create_od)

        
class TestOptionsDictOrphanNode(unittest.TestCase):

    def setUp(self):
        """I create an OptionsDict node."""
        self.od = OptionsDictUnderTest.node('foo', {'bar': 1})

    def test_equal_names_and_dicts(self):
        self.assertEqual(self.od,
                         OptionsDictUnderTest.node('foo', {'bar': 1}))

    def test_equal_names_but_unequal_dicts(self):
        self.assertNotEqual(self.od,
                            OptionsDictUnderTest.node('foo', {'bar': 2}))

    def test_unequal_names_but_equal_dicts(self):
        self.assertNotEqual(self.od,
                            OptionsDictUnderTest.node('baz', {'bar': 1}))

    def test_copy(self):
        other = self.od.copy()
        # test for equivalence and non-identity
        self.assertEqual(other, self.od)
        self.assertFalse(other is self.od)
        # test that name components have been copied and not simply
        # linked
        other.update(OptionsDictUnderTest.node('baz'))
        self.assertNotEqual(other, self.od)

    def test_default_str(self):
        """
        Calling the __str__ idiom and the str() method with no arguments
        should just return the name.
        """
        self.assertEqual(str(self.od), 'foo')
        self.assertEqual(self.od.str(), 'foo')

        
class TestOptionsDictUpdateFromOptionsDict(unittest.TestCase):
        
    def setUp(self):
        """
        I create and store an OptionsDict.  I create another
        OptionsDict, with one entry duplicating a key from the stored
        dict but having a different corresponding value.  I update the
        stored dict with the other dict.
        """
        self.od = OptionsDictUnderTest.node('A', {'foo': 1, 'bar': 2})
        other = OptionsDictUnderTest.node('B', {'foo': 3, 'baz': 4})
        self.od.update(other)
        
    def test_name(self):
        self.assertEqual(str(self.od), 'A_B')

    def test_right_overrides_left(self):
        """
        Looking up the shared key should return the other dict's value.
        """
        self.assertEqual(self.od['foo'], 3)

        
class TestOptionsDictUpdateFromDict(unittest.TestCase):
    
    def setUp(self):
        """
        I create and store an OptionsDict node.  I create a standard dict,
        with one entry duplicating a key from the stored dict but
        having a different corresponding value.  I update the stored
        dict with the other dict.
        """
        self.od = OptionsDictUnderTest.node('A', {'foo': 1, 'bar': 2})
        other = {'foo': 3, 'baz': 4}
        self.od.update(other)
        
    def test_name(self):
        self.assertEqual(str(self.od), 'A')

        
    
if __name__ == '__main__':
    unittest.main()
        
