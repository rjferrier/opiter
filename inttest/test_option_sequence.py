import sys
sys.path.append('..')

import unittest
from optree import OptionSequence, OptionSequenceCreationError
from optree import Option


class TestOptionSequenceCreation(unittest.TestCase):

    def test_create_from_non_name(self):
        """
        When I create an OptionSequence using something other than a
        name (even when I also correctly supply a tuple or list of
        options) an error should be raised.
        """
        create_opt_seq = lambda: OptionSequence(
            {'foo': 'bar'}, ('1D', '2D', '3D'))
        self.assertRaises(OptionSequenceCreationError, create_opt_seq)

        
class TestOptionSequenceWithOptionNames(unittest.TestCase):

    def setUp(self):
        """
        I create an OptionSequence from a name and a list of Option
        names.
        """
        self.opt_seq = OptionSequence('space', ('1D', '2D', '3D'))

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
        opt_names = ('1D', '2D', '3D')
        for opt, nm in zip(self.opt_seq, opt_names):
            ref_ID = 'space.'+nm
            self.assertEqual(repr(opt), ref_ID)
