import sys
sys.path.append('../optree')

import unittest
from option import _Option

    

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

        
class TestOptionWithNameAndDict(unittest.TestCase):

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

