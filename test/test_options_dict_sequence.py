import sys
sys.path.append('..')

import unittest
from optionsdict import create_sequence, OptionsDict, \
    OptionsDictException


class TestOptionsDictSequence(unittest.TestCase):

    def setUp(self):
        """
        I create a list of names for constructing OptionsDicts.
        """
        self.names = ['A', 'B', 'C']
        
    def test_create_with_incompatible_element(self):
        """
        When I pass create_sequence a list and one of the elements is
        something other than an OptionsDict or a string, an error
        should be raised.
        """
        src = [self.names[0], OptionsDict(self.names[1]), {'foo': 'bar'}]
        self.assertRaises(OptionsDictException, lambda: create_sequence(src))

    def test_create_with_incompatible_common_dict(self):
        """
        When pass create_sequence an acceptable list but the second
        argument is something other than a dict, an error should be
        raised.
        """
        lambda: self.create_and_check_sequence(self.names)
        self.assertRaises(ValueError,
                          lambda: create_sequence(self.names, 'foo'))

    def create_and_check_sequence(self, src):
        """
        This is a helper function that feeds a list into
        create_sequence and checks the resulting elements.
        """
        ods = create_sequence(src)
        for od, nm in zip(ods, self.names):
            self.assertIsInstance(od, OptionsDict)
            self.assertEqual(str(od), nm)

    def test_create_from_names(self):
        """
        I pass create_sequence a list of names.  The elements should
        have the correct type and name.
        """
        self.create_and_check_sequence(self.names)

    def test_create_from_options_dicts(self):
        """
        I pass create_sequence a list of names.  The elements should
        have the correct type and name.
        """
        src = []
        for nm in self.names:
            src.append(OptionsDict(nm))
        self.create_and_check_sequence(src)

    def create_mixed_list(self):
        """
        Helper function that creates a mixed list of things for
        constructing OptionsDicts.
        """
        src = []
        for nm in self.names:
            if nm=='B':
                src.append(OptionsDict(nm, {'special_key':
                                            'special_value'}))
            else:
                src.append(nm)
        return src
        
    def test_create_from_mixed(self):
        """
        I pass create_sequence a list of mixed types.  The elements
        should have the correct type and name.
        """
        self.create_and_check_sequence(self.create_mixed_list())

    def test_dicts(self):
        """
        I pass create_sequence a list of mixed types and a common
        dictionary.  All the elements should return the entry in the
        common dict in addition to any preexisting entries.
        """
        ods = create_sequence(self.create_mixed_list(),
                              {'global_key': 'global_value'})
        for od in ods:
            self.assertEqual(od['global_key'], 'global_value')
            if str(od)=='B':
                self.assertEqual(od['special_key'], 'special_value')


    

        
if __name__ == '__main__':
    unittest.main()
        
