import sys
sys.path.append('../src')

import unittest
from mock import Mock
from options import _Option, _OptionSequence, OptionError


class TestOptionCreation(unittest.TestCase):
    
    def test_create_from_non_name(self):
        """
        I create an Option using something other than a name, and an
        error is raised.
        """
        self.assertRaises(OptionError, lambda: _Option({'foo': 'bar'}))
    
    def test_create_from_non_dict(self):
        """
        I create an Option using a name and something other than a
        dict, and an error is raised.
        """
        self.assertRaises(OptionError, lambda: _Option('2D', 'bar'))
        
    

class TestOptionWithNameOnly(unittest.TestCase):
    
    def setUp(self):
        """
        I create an Option using just a name.
        """
        self.opt = _Option('2D')

    def test_ID(self):
        """
        repr(opt) should return a unique ID based on the Option's
        address in the parent structure.  Since there is no parent
        structure in this instance, only the Option's name should be
        returned.
        """
        self.assertEqual(repr(self.opt), '2D')

    def test_name(self):
        """
        When the Option is string-formatted, its name should be
        returned.
        """
        self.assertEqual(str(self.opt), '2D')

    def test_as_dict(self):
        """
        I should be able to use the Option as a dictionary, even though
        it has no entries.
        """
        self.assertRaises(KeyError, lambda: self.opt['geometry'])
        self.opt['geometry'] = 'square'
        self.assertEqual(self.opt['geometry'], 'square')

        
class TestOption(unittest.TestCase):

    def setUp(self):
        """
        I create an Option using a name and a dict.
        """
        self.opt = _Option('2D', {'geometry': 'square'})

    def test_as_dict(self):
        """
        I should be able to use the Option as a dictionary.
        """
        self.assertEqual(self.opt['geometry'], 'square')
        self.opt['geometry'] = 'circle'
        self.assertEqual(self.opt['geometry'], 'circle')


class TestOptionSequenceWithOptionNamesOnly(unittest.TestCase):
    
    def setUp(self):
        """
        I create an OptionSequence from a name and a list of Option
        names.
        """
        self.opt_seq = _OptionSequence('space', ('1D', '2D', '3D'))

    def test_ID(self):
        """
        repr(opt_seq) should return a unique ID based on the
        OptionSequence's address in the parent structure.  Since there
        is no parent structure in this instance, only the
        OptionSequence's name should be returned.
        """
        self.assertEqual(repr(self.opt_seq), 'space')

    def test_name(self):
        """
        When the OptionSequence is string-formatted, its name should be
        returned.
        """
        self.assertEqual(str(self.opt_seq), 'space')

    def test_iterate_options_and_check_type(self):
        """
        I should be able to iterate over the options and each one will
        be an Option.
        """
        for opt in self.opt_seq:
            self.assertIsInstance(opt, _Option)

    def test_iterate_options_and_check_ID(self):
        """
        I should be able to iterate over the options and each should
        return an ID in the format 'sequence_name.option_name'.
        """
        opt_names = ('1D', '2D', '3D')
        for opt, nm in zip(self.opt_seq, opt_names):
            ref_ID = 'space.'+nm
            self.assertEqual(repr(opt), ref_ID)


class TestOptionSequence(unittest.TestCase):
            
    def setUp(self):
        """
        I create an OptionSequence from a list of Options.
        """
        opt1 = _Option('1D', {'geometry': 'line'})
        opt2 = _Option('2D', {'geometry': 'square'})
        opt3 = _Option('3D', {'geometry': 'cube'})
        self.opt_seq = _OptionSequence('space', ('1D', '2D', '3D'))

    def test_as_dict(self):
        """
        The OptionSequence has no knowledge of its children's contents,
        so trying to access 'geometry' should raise a KeyError.
        """
        self.assertRaises(KeyError, lambda: self.opt_seq['geometry ']) 
        

class TestSimpleTreeCreation(unittest.TestCase):
    pass
