import sys
sys.path.append('..')

import unittest
from optree import create_option_sequence, OptionCreationError
from optree.options import Option


class TestOptionSequenceCreation(unittest.TestCase):

    def test_create_from_non_name(self):
        """
        When I create an OptionSequence using something other than a
        name (even when I also correctly supply a tuple or list of
        options) an error should be raised.
        """
        self.assertRaises(OptionCreationError,
                          lambda: create_option_sequence(
                              {'foo': 'bar'}, ('1D', '2D', '3D')))

        
class TestOptionSequenceWithOptionNames(unittest.TestCase):

    def setUp(self):
        """
        I create an OptionSequence from a name and a list of Option
        names.
        """
        self.opt_seq = create_option_sequence('space',
                                              ('1D', '2D', '3D'))

    def test_iterate_options_and_check_type(self):
        """
        I should be able to iterate over the options and each one will
        be an Option.
        """
        for opt in self.opt_seq:
            self.assertIsInstance(opt, Option)

    def test_iterate_options_and_check_ID(self):
        """
        I should be able to iterate over the options and each should
        return an ID in the format 'sequence_name.option_name'.
        """
        names = ('1D', '2D', '3D')
        for opt, nm in zip(self.opt_seq, names):
            ref_ID = 'space.'+nm
            self.assertEqual(repr(opt), ref_ID)
