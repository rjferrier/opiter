import unittest
from options_dict import OptionsDict, CallableEntry, OptionsDictException, \
    transform_entries, unlink
from options_node import OptionsNode
from options_array import OptionsArray
from formatters import SimpleFormatter, TreeFormatter
from copy import deepcopy


def bump(target_dict, key):
    "For testing transform_entries"
    try:
        target_dict[key] += 1
    except TypeError:
        pass

def create_nested(v1, v2, v3):
    "For testing recursive functions"
    return OptionsDict({
        'A': v1,
        'B': {
            'C': v2,
            'D': {
                'E': v3}}})


class TestOptionsDictBasics(unittest.TestCase):

    def setUp(self):
        self.od = OptionsDict({})
        
    def test_str(self):
        """
        Because there is no node information, str() should return an empty
        string.
        """
        self.assertEqual(str(self.od), '')
    
    def test_create_node_info_formatter_default(self):
        self.assertIsInstance(
            self.od.create_node_info_formatter(), SimpleFormatter)
    
    def test_create_node_info_formatter_simple(self):
        self.assertIsInstance(
            self.od.create_node_info_formatter('simple'), SimpleFormatter)

    def test_create_node_info_formatter_tree(self):
        self.assertIsInstance(
            self.od.create_node_info_formatter('tree'), TreeFormatter)

    def test_create_node_info_formatter_error(self):
        self.assertRaises(
            OptionsDictException, 
            lambda: self.od.create_node_info_formatter('madethisup'))
        

class TestOptionsDictDependentEntries(unittest.TestCase):
    
    def setUp(self):
        """
        Reprise the setup of
        test_unit_options_dict.TestOptionsDictDependentEntries.
        """
        self.od = OptionsDict({
            'kinematic_viscosity': 1.e-6,
            'pipe_diameter'      : 0.1 })
        def Reynolds_number(d):
            return d['velocity'] * d['pipe_diameter'] / \
                d['kinematic_viscosity']
        self.od.update([Reynolds_number])

    def test_remove_links(self):
        """
        I set velocity, which should in turn set the Reynolds_number.
        However, after I unlink the dictionary entries, redefining
        velocity should not redefine the Reynolds number.
        """
        self.od['velocity'] = 0.02
        self.assertAlmostEqual(self.od['Reynolds_number'], 2000.)
        self.od.transform_entries(unlink)
        self.od['velocity'] = 0.04
        self.assertAlmostEqual(self.od['Reynolds_number'], 2000.)

    def test_remove_links_with_missing_dependency(self):
        self.assertRaises(KeyError,
                          lambda: self.od.transform_entries(unlink))

    # def test_remove_links_and_clean_missing_dependency(self):
    #     """
    #     Freezing can also remove entries with missing dependencies, so I
    #     won't get a KeyError right away.
    #     """
    #     self.od.remove_links(clean=True)
    #     self.assertRaises(KeyError, lambda: self.od['velocity'])

    # def test_remove_links_and_clean_missing_dependency_via_dot_syntax(self):
    #     """
    #     As above, but the dependency involves attribute-getting syntax.
    #     """
    #     def Reynolds_number(d):
    #         return d.velocity * d.pipe_diameter / d.kinematic_viscosity
    #     self.od.update([Reynolds_number])
    #     self.od.remove_links(clean=True)
    #     self.assertRaises(KeyError, lambda: self.od['velocity'])

    
class TestOptionsDictInteractionsWithNode(unittest.TestCase):

    def setUp(self):
        self.node = OptionsNode('foo')
        self.od = OptionsDict(entries={'bar': 1})

    def test_donate_copy(self):
        """
        Passing a node to OptionsDict's donate_copy method should furnish
        the node with dictionary information.
        """
        od_init = deepcopy(self)
        self.node, remainder = self.od.donate_copy(self.node)
        node_od = self.node.collapse()[0]
        self.assertEqual(node_od['bar'], 1)
        self.assertEqual(len(remainder), 0)


class TestOptionsDictAfterTreeCollapse(unittest.TestCase):

    def setUp(self):
        """
        Run tests on this tree:
        0: a
            1: a
                2: a
                2: b
                2: c
            1: b
                2: a
                2: b
                2: c
        """
        self.tree = OptionsArray('0', ['a']) * \
                    OptionsArray('1', ['a', 'b']) * \
                    OptionsArray('2', ['a', 'b', 'c'])
        
    def test_str_tree(self):
        ods = self.tree.collapse()
        expected = """
0: a
    1: a
        2: a
        2: b
        2: c
    1: b
        2: a
        2: b
        2: c"""
        result = ''.join(['\n' + od.get_string(formatter='tree') \
                          for od in ods])
        self.assertEqual(result, expected)

        
    def test_indent(self):
        ods = self.tree.collapse()
        expected = ('\n' + ' '*12)*6
        result = ''.join(['\n' + od.indent() for od in ods])
        self.assertEqual(result, expected)
        

class TestTransformElementsFreeFunction(unittest.TestCase):

    def setUp(self):
        self.dicts = [create_nested(1, 2, 3),
                      create_nested(4, 5, 6)]

    def test_nonrecursive_transform_entries(self):
        result = transform_entries(self.dicts, bump)
        self.assertEqual(result, [create_nested(2, 2, 3),
                                  create_nested(5, 5, 6)])
        # make sure we haven't mutated the original
        self.assertEqual(self.dicts, [create_nested(1, 2, 3),
                                      create_nested(4, 5, 6)])

    def test_recursive_transform_entries(self):
        result = transform_entries(self.dicts, bump, recursive=True)
        self.assertEqual(result, [create_nested(2, 3, 4),
                                  create_nested(5, 6, 7)])
        # make sure we haven't mutated the original
        self.assertEqual(self.dicts, [create_nested(1, 2, 3),
                                      create_nested(4, 5, 6)])
        

        
class TestCallableEntry(unittest.TestCase):

    def setUp(self):
        """
        I create an OptionsDict with a callable entry stored under
        'my_func'.  
        """
        self.od = OptionsDict({
            'my_func': CallableEntry(lambda a, b=1: a + b)})

    def test_as_function(self):
        """
        The callable should not evaluate like a dependent entry but instead
        remain intact and work as intended.
        """
        self.assertIsInstance(self.od['my_func'], CallableEntry)
        self.assertEqual(self.od['my_func'](1), 2)
        self.assertEqual(self.od['my_func'](1, 2), 3)

        
if __name__ == '__main__':
    unittest.main()
