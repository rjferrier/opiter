import sys
sys.path.append('..')

import unittest
from mock import Mock
from base import IOption
from optree.option_sequence import _OptionSequence

            
class TestOptionSequence(unittest.TestCase):
            
    def setUp(self):
        """
        I create an OptionSequence from a list of Options.
        """
        opt1 = Mock(spec=IOption)
        opt2 = Mock(spec=IOption)
        opt3 = Mock(spec=IOption)
        # opt2 = _Option('2D', {'geometry': 'square'})
        # opt3 = _Option('3D', {'geometry': 'cube'})
        self.opt_seq = _OptionSequence('space', ('1D', '2D', '3D'))

    def test_name(self):
        """
        When the OptionSequence is string-formatted, its name should be
        returned.
        """
        self.assertEqual(str(self.opt_seq), 'space')
    
    def test_ID(self):
        """
        repr(opt_seq) should return a unique ID based on the
        OptionSequence's address in the parent structure.  Since there
        is no parent structure in this instance, only the
        OptionSequence's name should be returned.
        """
        self.assertEqual(repr(self.opt_seq), 'space')

    def test_as_dict(self):
        """
        The OptionSequence has no knowledge of its children's contents,
        so trying to access 'geometry' should raise a KeyError.
        """
        self.assertRaises(KeyError, lambda: self.opt_seq['geometry']) 

    def test_iterate_options_and_check_ID(self):
        """
        I should be able to iterate over the options and each should
        return an ID in the format 'sequence_name.option_name'.
        """
        opt_names = ('1D', '2D', '3D')
        # for opt, nm in zip(self.opt_seq, opt_names):
        #     ref_ID = 'space.'+nm
        #     self.assertEqual(repr(opt), ref_ID)
        

class TestSimpleTreeCreation(unittest.TestCase):
    pass
