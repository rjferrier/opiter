import sys
sys.path.append('..')

import unittest
from tree_elements import OptionsArray, OptionsNode
from options_dict import OptionsDict, OptionsDictException
    

class TestOptionsArrayCreation(unittest.TestCase):

    def test_create_with_common_entries(self):
        """
        I create an OptionsArray 'A' using three integers and a valid
        common_entries argument.  I should be able to use the latter
        after collapsing the array to get options dictionaries.
        """
        array = OptionsArray('A', range(3), {'foo': 'bar'})
        ods = array.collapse()
        for od in ods:
            self.assertEqual(od['foo'], 'bar') 

    def test_create_with_bad_common_entries(self):
        """
        I create an OptionsArray 'A' using three integers and
        something that is not a dictionary for the common_entries
        argument.  An error should be raised.
        """
        create_array = lambda: OptionsArray('A', range(3), 'foo')
        self.assertRaises(OptionsDictException, create_array)

    # TODO fill more of these out to reflect
    # test_integration_options_dict_array_nodes



class TestOptionsArrayBasics(unittest.TestCase):

    def setUp(self):
        """
        I create an OptionsArray from a list of assorted objects, one of
        which is an OptionsNode.
        """
        node = OptionsNode('some_dict', {'foo': 'bar'})
        self.values = ['A', 2, 3.14, node]
        self.array = OptionsArray('random', self.values)
        self.expected_names = ['A', '2', '3.14', 'some_dict']

    def test_element_types(self):
        for el in self.array:
            self.assertIsInstance(el, OptionsNode)

    def test_element_types_after_collapse(self):
        for el in self.array.collapse():
            self.assertIsInstance(el, OptionsDict)

    def test_element_names_after_collapse(self):
        for el, expected in zip(self.array.collapse(), self.expected_names):
            self.assertEqual(str(el), expected)

    def test_element_contents_after_collapse(self):
        """
        Getting the options dictionaries and querying 'random' should
        return the various values; alternatively, the OptionsNode
        dictionary we started with should now be queryable.  All
        dictionaries should have the common entry.
        """
        for i, el in enumerate(self.array.collapse()):
            if i==3:
                self.assertEqual(el['foo'], 'bar')
            else:
                self.assertEqual(el['random'], self.values[i])

    def test_element_node_name_after_collapse(self):
        """
        Each options dictionary should return a node info object that has
        the correct name, indicating that it is a NodeInfo object.
        """
        for i, el in enumerate(self.array.collapse()):
            ni = el.get_node_info()
            self.assertEqual(ni.str(), self.expected_names[i])

    def test_element_node_position_after_collapse(self):
        """
        Each options dictionary should return a node info object that has
        the correct position, indicating that it is an ArrayNodeInfo
        object.
        """
        for i, el in enumerate(self.array.collapse()):
            ni = el.get_node_info()
            self.assertTrue(ni.at(i))

    def test_getitem(self):
        node = self.array[2]
        self.assertIsInstance(node, OptionsNode)
        self.assertEqual(str(node), '3.14')
        
            

class TestOptionsArraySlice(unittest.TestCase):

    def setUp(self):
        """
        I create an OptionsArray and take a slice which should leave me
        the second, fifth and eighth nodes.  This test fixture is
        important for checking that node information is being injected
        correctly into the options dictionaries.
        """
        node_names = [c for c in 'ABCDEFGHIJKL']
        self.array = OptionsArray('alphabet', node_names)
        self.array = self.array[1:10:3]
        self.expected_names = 'BEH'

    def test_element_names_after_collapse(self):
        for el, expected in zip(self.array.collapse(), self.expected_names):
            self.assertEqual(str(el), expected)

    def test_element_node_position_after_collapse(self):
        for i, el in enumerate(self.array.collapse()):
            ni = el.get_node_info()
            self.assertTrue(ni.at(i))
