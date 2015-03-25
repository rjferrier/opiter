import sys
sys.path.append('..')

import unittest
from optionsdict import OptionsDictSequence, OptionsDict, \
    OptionsDictException


class TestOptionsDictSequenceBasics(unittest.TestCase):

    def setUp(self):
        """
        I create a list of names which will be constructors to
        OptionsDicts.
        """
        self.names = ['A', 'B', 'C']
    
    def test_create_with_incompatible_element(self):
        """
        When I create an OptionsDictSequence and one of the elements is
        something other than an OptionsDict or a string, an error
        should be raised.
        """
        src = [self.names[0], OptionsDict(self.names[1]),
               {'foo', 'bar'}]
        create_ods = lambda: OptionsDictSequence(src)
        self.assertRaises(OptionsDictException, create_ods)

    def create_and_check_elements(self, src):
        """
        This is a helper function that feeds a list into
        OptionsDictSequence and checks the resulting elements.
        """
        ods = OptionsDictSequence(src)
        for od, nm in zip(ods, self.names):
            self.assertIsInstance(od, OptionsDict)
            self.assertEqual(str(od), nm)

    def test_create_from_names(self):
        """
        I create an OptionsDictSequence from a list of names.  The
        elements should have the correct type and name.
        """
        self.create_and_check_elements(self.names)

    def test_create_from_options_dicts(self):
        """
        I create an OptionsDictSequence from a list of OptionsDicts.
        The elements should have the correct type and name.
        """
        src = []
        for nm in self.names:
            src.append(OptionsDict(nm))
        self.create_and_check_elements(src)

    def test_create_from_mixed(self):
        """
        I create an OptionsDictSequence from a list of mixed types.
        The elements should have the correct type and name.
        """
        src = []
        for nm in self.names:
            if nm=='B':
                src.append(nm)
            else:
                src.append(OptionsDict(nm))
        self.create_and_check_elements(src)


class TestOptionsDictSequenceFromNames(unittest.TestCase):
    
    def setUp(self):
        """
        I create an OptionsDictSequence from a list of names.
        """
        self.names = ['A', 'B', 'C']
        self.ods = OptionsDictSequence(self.names)

    def test_iterate_and_check_type(self):
        """
        I should be able to iterate over the elements and each one will
        be an OptionsDict.
        """
        for od in self.ods:
            self.assertIsInstance(od, OptionsDict)

    def test_iterate_options_and_check_name(self):
        """
        I should be able to iterate over the options and each should
        have the correct name.
        """
        for od, nm in zip(self.ods, self.names):
            self.assertEqual(str(od), nm)


class TestOptionsDictSequenceFromOptionsDicts(unittest.TestCase):
    
    def setUp(self):
        """
        I create an OptionsDictSequence from a list of OptionsDicts.
        """
        self.names = ['A', 'B', 'C']
        ods = []
        for nm in self.names:
            ods.append(OptionsDict(nm))
        self.ods = OptionsDictSequence(ods)

    def test_iterate_and_check_type(self):
        """
        I should be able to iterate over the elements and each one will
        be an OptionsDict.
        """
        for od in self.ods:
            self.assertIsInstance(od, OptionsDict)

    def test_iterate_options_and_check_name(self):
        """
        I should be able to iterate over the options and each should
        have the correct name.
        """
        for od, nm in zip(self.ods, self.names):
            self.assertEqual(str(od), nm)

    

        
if __name__ == '__main__':
    unittest.main()
        
