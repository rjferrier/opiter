import unittest
from options_array import OptionsArray, OptionsArrayException, ArrayNodeInfo, \
    OptionsArrayFactory
from options_node import OptionsNode, OrphanNodeInfo
from options_dict import OptionsDict
    

def dict_function(d):
    "For testing apply_hooks"
    d.update({'A': -1})

def item_function(d, k):
    "For testing apply_hooks"
    d[k] += 1

    
class TestOptionsArrayCreation(unittest.TestCase):

    def test_create(self):
        """
        I create an OptionsArray 'A' using three integers and update it
        with a dict.  I should be able to use the latter after
        collapsing the array to get options dictionaries.
        """
        array = OptionsArray('A', range(3))
        array.update({'foo': 'bar'})
        ods = array.collapse()
        for od in ods:
            self.assertEqual(od['foo'], 'bar') 

    def test_format_names_with_string(self):
        """
        I create an OptionsDict array 'A' using integers 2, 5, 10.
        Format the element names as A02, A05, A10.
        """
        seq = OptionsArray('A', [2, 5, 10], name_format='A{:02g}')
        expected_names = ['A02', 'A05', 'A10']
        for el, expected in zip(seq, expected_names):
            self.assertEqual(str(el), expected)

    def test_format_names_with_function(self):
        """
        I create an OptionsDict array 'A' using floats 1, 2.5, 6.25.
        Format the element names as 1p00, 2p50, 6p25.
        """
        formatter = lambda x: '{:.2f}'.format(x).replace('.', 'p')
        seq = OptionsArray('A', [1., 2.5, 6.25], name_format=formatter)
        expected_names = ['1p00', '2p50', '6p25']
        for el, expected in zip(seq, expected_names):
            self.assertEqual(str(el), expected)

    def test_format_names_with_bad_formatter(self):
        """
        I create an OptionsDict array with an inappropriate object
        as name_format.  An error should be raised.
        """
        create_seq = lambda: OptionsArray('A', [1., 2.5, 6.25],
                                          name_format=None)
        self.assertRaises(OptionsArrayException, create_seq)


class TestOptionsArrayBasics(unittest.TestCase):

    def setUp(self):
        """
        I create an OptionsArray from a list of assorted objects, two of
        which are OptionsNodes - one created from a string and dict,
        the other from a class.
        """
        node = OptionsNode('some_dict', {'foo': 'bar'})
        class another_dict:
            qux = 2
        another_node = OptionsNode(another_dict)
        self.values = ['A', 3.14, node, another_node]
        self.array = OptionsArray('random', self.values)
        self.expected_names = ['A', '3.14', 'some_dict', 'another_dict']

    def test_create_options_node(self):
        node = self.array.create_options_node('baz')
        self.assertIsInstance(node, OptionsNode)
        self.assertEqual(str(node), 'baz')

    def test_create_options_node_from_node_and_name_format(self):
        src = OptionsNode('baz')
        fmt = lambda x: '<'+x+'>'
        node = self.array.create_options_node(src, name_format=fmt)
        self.assertIsInstance(node, OptionsNode)
        self.assertEqual(str(node), '<baz>')
        self.assertEqual(dict(node.collapse()[0]), {'random': 'baz'})

    def test_create_options_node_from_node_and_items(self):
        src = OptionsNode('baz', {'a': 0})
        node = self.array.create_options_node(src, {'b': 1})
        self.assertIsInstance(node, OptionsNode)
        self.assertEqual(str(node), 'baz')
        self.assertEqual(dict(node.collapse()[0]),
                         {'a': 0, 'b': 1, 'random': 'baz'})

    def test_create_node_info(self):
        ni = self.array.create_node_info(1)
        self.assertIsInstance(ni, ArrayNodeInfo)
        self.assertEqual(ni.get_string(collection_separator=':'),
                         'random:3.14')

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
        dictionaries we started with should now be queryable.
        """
        for i, el in enumerate(self.array.collapse()):
            if i==2:
                self.assertEqual(el['foo'], 'bar')
            elif i==3:
                self.assertEqual(el['qux'], 2)
            else:
                self.assertEqual(el['random'], self.values[i])

    def test_element_node_name_after_collapse(self):
        """
        Each options dictionary should return a node info object that has
        the correct name, indicating that it is a NodeInfo object.
        """
        for i, el in enumerate(self.array.collapse()):
            ni = el.get_node_info()
            self.assertEqual(ni.get_string(), self.expected_names[i])

    def test_element_node_position_after_collapse(self):
        """
        Each options dictionary should return a node info object that has
        the correct position, indicating that it is an ArrayNodeInfo
        object.
        """
        for i, el in enumerate(self.array.collapse()):
            ni = el.get_node_info()
            self.assertTrue(ni.position.is_at(i))

    def test_getitem_from_index_and_check_type_and_node_info(self):
        node = self.array[2]
        self.assertIsInstance(node, OptionsNode)
        # check node info is up to date
        od = node.collapse()[0]
        ni = od.get_node_info()
        self.assertTrue(ni.position.is_at(2))

    def test_getitem_from_slice_and_check_type_and_node_info(self):
        subarray = self.array[1:4:2]
        self.assertIsInstance(subarray, OptionsArray)
        # check that all items are nodes
        for node in self.array:
            self.assertIsInstance(node, OptionsNode)
        # check that node info is up to date in this subarray
        for i, od in enumerate(subarray.collapse()):
            ni = od.get_node_info()
            self.assertTrue(ni.position.is_at(i))

    def test_setitem_from_index_and_check_type_and_node_info(self):
        node = OptionsNode('some_other_dict', {'foo': 'baz'})
        self.array[2] = 3
        # check that the value has been converted into a node
        self.assertIsInstance(self.array[2], OptionsNode)
        # check that node info is up to date
        for i, od in enumerate(self.array.collapse()):
            ni = od.get_node_info()
            self.assertTrue(ni.position.is_at(i))

    def test_setitem_from_slice_and_check_type_and_node_info(self):
        node = OptionsNode('some_other_dict', {'foo': 'baz'})
        self.array[1:4:2] = [3, node]
        self.assertIsInstance(self.array[1:4:2], OptionsArray)
        # check that all set items have been converted to nodes
        for node in self.array:
            self.assertIsInstance(node, OptionsNode)
        # check that node info is up to date
        for i, od in enumerate(self.array.collapse()):
            ni = od.get_node_info()
            self.assertTrue(ni.position.is_at(i))

    def test_delitem_from_index_and_check_type_and_node_info(self):
        del self.array[2]
        # check that node info is up to date
        for i, od in enumerate(self.array.collapse()):
            ni = od.get_node_info()
            self.assertTrue(ni.position.is_at(i))

    def test_delitem_from_slice_and_check_type_and_node_info(self):
        del self.array[1:4:2]
        # check that node info is up to date
        for i, od in enumerate(self.array.collapse()):
            ni = od.get_node_info()
            self.assertTrue(ni.position.is_at(i))

    def check_array_node_info(self, index, expected_node_names):
        """
        Helper function.  Checks that node info is up to date in the
        OptionsArray under test.
        """
        od = self.array.collapse()[index]
        ni = od.get_node_info()
        self.assertIsInstance(ni, ArrayNodeInfo)
        self.assertTrue(ni.position.is_at(index))
        self.assertEqual(ni.node_names, expected_node_names)

    def test_append_and_check_node_info(self):
        # append with primitive
        self.array.append(OptionsNode('5'))
        self.check_array_node_info(-1, self.expected_names + ['5'])
        # append with node
        self.array.append(OptionsNode('another_dict'))
        self.check_array_node_info(
            -1, self.expected_names + ['5', 'another_dict'])

    def test_pop_and_check_node_info(self):
        node = self.array.pop()
        # check that this node is now an orphan node
        od = node.collapse()[0]
        ni = od.get_node_info()
        self.assertIsInstance(ni, OrphanNodeInfo)
        # check remaining array
        self.check_array_node_info(-1, self.expected_names[:-1])
        
            

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
            pos = el.get_position()
            self.assertTrue(pos.is_at(i))

            
class TestOptionsArrayWithHooks(unittest.TestCase):
    
    def test_apply_dict_hooks(self):
        array = OptionsArray('A', range(3), dict_hooks=[dict_function])
        ods = array.collapse()
        for od in ods:
            self.assertEqual(od['A'], -1)

    def test_apply_item_hooks(self):
        array = OptionsArray('A', range(3), item_hooks=[item_function])
        ods = array.collapse()
        for od, i in zip(ods, [1, 2, 3]):
            self.assertEqual(od['A'], i)


class TestOptionsArrayFactory(unittest.TestCase):

    def test_apply_formatting_with_format_string(self):
        self.assertEqual(
            OptionsArrayFactory.apply_formatting('{:.2f}', 1./3), '0.33')

    def test_apply_formatting_with_function(self):
        self.assertEqual(
            OptionsArrayFactory.apply_formatting(lambda i: str(i**2), 2), '4')

    def check_names(self, array, expected_names):
        names = [str(node) for node in array]
        self.assertEqual(names, expected_names)

    def check_items(self, array, key, expected_values):
        values = [od[key] for od in array.collapse()]
        self.assertEqual(values, expected_values)
        
    def test_default_factory_first_array(self):
        factory = OptionsArrayFactory()
        array = factory('colour', ['red', 'yellow', 'blue'])
        self.check_names(array, ['A00', 'A01', 'A02'])
        self.check_items(array, 'colour', ['red', 'yellow', 'blue'])

    def test_default_factory_second_array(self):
        factory = OptionsArrayFactory()
        array1 = factory('colour', ['red', 'yellow', 'blue'])
        array2 = factory('object', ['lolly', 'lorry'])
        self.check_names(array2, ['B00', 'B01'])
        self.check_items(array2, 'object', ['lolly', 'lorry'])

    def test_default_factory_too_many_nodes(self):
        factory = OptionsArrayFactory()
        self.assertRaises(OptionsArrayException,
                          lambda: factory('foo', range(101)))

    def test_default_factory_too_many_arrays(self):
        factory = OptionsArrayFactory()
        for i in range(26):
            array = factory('foo', ['bar'])
        self.assertRaises(OptionsArrayException,
                          lambda: factory('foo', ['bar']))

    def test_other_array_index_format(self):
        factory = OptionsArrayFactory(array_index_format='{:1d}-')
        array = factory('foo', range(3))
        self.check_names(array, ['0-00', '0-01', '0-02'])

    def test_other_node_index_format(self):
        factory = OptionsArrayFactory(node_index_format=lambda i: (i + 1)*'i')
        array = factory('foo', range(3))
        self.check_names(array, ['Ai', 'Aii', 'Aiii'])

        
            
if __name__ == '__main__':
    unittest.main()
