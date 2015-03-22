import sys
sys.path.append('..')

import unittest
from mock import Mock
from optree.base import IOption
from optree.options import OptionSequence


class TestOptionSequenceUnit(unittest.TestCase):
            
    def setUp(self):
        """
        I create an OptionSequence from a list of Options.
        """
        options = []
        for name in ('1D', '2D', '3D'):
            opt = Mock(spec=IOption)
            options.append(opt)
        # opt2 = Option('2D', {'geometry': 'square'})
        # opt3 = Option('3D', {'geometry': 'cube'})
        self.opt_seq = OptionSequence('space', options)

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
        
