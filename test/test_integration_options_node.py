import sys
sys.path.append('..')

import unittest
from tree_elements import OptionsNode
from options_dict import OptionsDict, OptionsDictException
    

class TestOptionsNodeCreationOptions(unittest.TestCase):

    def test_create_with_bad_common_entries(self):
        """
        I create an OptionsNode using something that is not a dictionary
        for the entries argument.  An error should be raised.
        """
        create_array = lambda: OptionsNode('A', 'foo')
        self.assertRaises(OptionsDictException, create_array)


class TestOptionsNodeBasics(unittest.TestCase):

    def setUp(self):
        self.node = OptionsNode('B', {'foo': 'bar'})

    def test_collapse(self):
        self.assertEqual(len(self.node.collapse()), 1)


class TestOrphanNodeAfterCollapse(unittest.TestCase):

    def setUp(self):
        """
        I create a node and collapse it, which should leave an OptionsDict
        with OrphanNodeInfo.
        """
        node = OptionsNode('A', {'foo': 'bar'})
        self.od = node.collapse()[0]

    def test_type(self):
        self.assertIsInstance(self.od, OptionsDict)

    def test_name(self):
        self.assertEqual(str(self.od), 'A')

    def test_contents(self):
        self.assertEqual(self.od['foo'], 'bar')

    def test_node_info_name(self):
        ni = self.od.get_node_info()
        self.assertEqual(ni.str(), 'A')
