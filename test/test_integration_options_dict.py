import unittest
from options_dict import OptionsDict, CallableEntry, OptionsDictException, \
    transform_entries, unlink, Check, Remove, Sequence, \
    missing_dependencies, unpicklable
from options_node import OptionsNode
from options_array import OptionsArray
from formatters import SimpleFormatter, TreeFormatter
from copy import deepcopy
from math import sqrt


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
        test_unit_options_dict.TestOptionsDictDependentEntries, but
        put in a nested OptionsDict and extend it so we can test
        recursive transformations.  Omit the independent variables
        velocity, fluid density and fluid bulk modulus.
        """
        self.od = OptionsDict({
            'pipe_diameter': 0.1,
            'fluid': OptionsDict({
                'name': 'water',
                'dynamic_viscosity': 1.e-3,
                
                'kinematic_viscosity': lambda self:
                self['dynamic_viscosity'] / self['density'],
                
                'speed_of_sound': lambda self:
                sqrt(self['bulk_modulus'] / self['density'])
            })
        })
        def Reynolds_number(d):
            return d['velocity'] * d['pipe_diameter'] / \
                d['fluid']['kinematic_viscosity']
        self.od.update([Reynolds_number])

        
    def test_nonrecursive_unlink(self):
        """
        I set velocity and fluid density, which in turn should set both
        the kinematic_viscosity and the Reynolds_number.  After I
        unlink the dictionary entries nonrecursively, redefining fluid
        density should redefine the kinematic_viscosity but not
        the Reynolds number.
        """
        self.od['velocity'] = 0.02
        self.od['fluid']['density'] = 1000.
        self.assertAlmostEqual(self.od['Reynolds_number'], 2000.)
        self.assertAlmostEqual(
            self.od['fluid']['kinematic_viscosity'], 1.e-6)
        self.od.transform_entries(unlink)
        
        self.od['fluid']['density'] = 500.
        self.assertAlmostEqual(
            self.od['fluid']['kinematic_viscosity'], 2.e-6)
        self.assertAlmostEqual(self.od['Reynolds_number'], 2000.)

        
    def test_nonrecursive_unlink_with_missing_dependencies(self):
        """
        I should expect an error if I try to unlink the entries
        nonrecursively before defining all the dependencies of
        Reynolds_number, an outer entry.  On the other hand, I won't
        see an error if an inner dependency like bulk_modulus goes
        undefined.
        """
        self.od['velocity'] = 0.02
        self.assertRaises(KeyError,
                          lambda: self.od.transform_entries(unlink))
        self.od['fluid']['density'] = 1000.
        self.od.transform_entries(unlink)

        
    def test_recursive_unlink(self):
        """
        I define all missing variables.  After I unlink recursively, I
        should find that redefining fluid density affects neither the
        kinematic viscosity nor the Reynolds number.
        """
        self.od['velocity'] = 0.02
        self.od['fluid']['density'] = 1000.
        self.od['fluid']['bulk_modulus'] = 2.
        self.od.transform_entries(unlink, recursive=True)
        self.od['fluid']['density'] = 500.
        self.assertAlmostEqual(
            self.od['fluid']['kinematic_viscosity'], 1.e-6)
        self.assertAlmostEqual(self.od['Reynolds_number'], 2000.)

        
    def test_recursive_unlink_with_missing_dependency(self):
        """
        I should expect an error if I recursively unlink and any
        dependency is missing.
        """
        self.od['velocity'] = 0.02
        self.od['fluid']['density'] = 1000.
        self.assertRaises(KeyError,
                          lambda: self.od.transform_entries(
                              unlink, recursive=True))
        

    def test_nonrecursive_check_missing_dependencies(self):
        """
        Similar to test_nonrecursive_unlink_with_missing_dependencies, but
        using Check(missing_dependencies) nonrecursively should raise
        OptionsDictExceptions instead of KeyErrors.
        """
        self.od['velocity'] = 0.02
        self.assertRaises(OptionsDictException,
                          lambda: self.od.transform_entries(
                              Check(missing_dependencies)))
        self.od['fluid']['density'] = 1000.
        self.od.transform_entries(Check(missing_dependencies))
        
        
    def test_recursive_check_missing_dependency(self):
        """
        Similar to test_recursive_unlink_with_missing_dependency, but
        using Check(missing_dependencies) recursively should raise
        OptionsDictExceptions instead of KeyErrors.
        """
        self.od['velocity'] = 0.02
        self.od['fluid']['density'] = 1000.
        self.assertRaises(OptionsDictException,
                          lambda: self.od.transform_entries(
                              Check(missing_dependencies), recursive=True))

        
    def test_nonrecursive_remove_missing_dependencies(self):
        """
        If not all the dependencies of Reynolds_number are defined, using
        Remove(missing_dependencies) nonrecursively should remove the
        whole entry.  speed_of_sound will be unaffected, so trying to
        access that without defining its dependencies will raise a
        KeyError.
        """
        self.od['velocity'] = 0.02
        self.od.transform_entries(Remove(missing_dependencies))
        self.assertRaises(KeyError,
                          lambda: self.od['speed_of_sound'])

        
    def test_recursive_remove_missing_dependencies(self):
        """
        If all the dependencies of Reynolds_number are defined, but a
        dependency of speed_of_sound is missing, using
        Remove(missing_dependencies) recursively should remove
        speed_of_sound but not Reynolds_number.
        """
        self.od['velocity'] = 0.02
        self.od['fluid']['density'] = 1000.
        self.od.transform_entries(Remove(missing_dependencies),
                                  recursive=True)
        self.od['Reynolds_number']
        self.assertRaises(KeyError,
                          lambda: self.od['speed_of_sound'])
        
        
class TestOptionsDictDependentEntriesWithDotSyntax(unittest.TestCase):
    
    def setUp(self):
        """
        As above, but the dot syntax will mean AttributeErrors are raised
        instead of KeyErrors.  This may affect the logic and should
        therefore be tested.
        """
        self.od = OptionsDict({
            'pipe_diameter': 0.1,
            'fluid': OptionsDict({
                'name': 'water',
                'dynamic_viscosity': 1.e-3,
                
                'kinematic_viscosity': lambda self:
                self.dynamic_viscosity / self.density,
                
                'speed_of_sound': lambda self:
                sqrt(self.bulk_modulus / self.density)
            })
        })
        def Reynolds_number(d):
            return d.velocity * d.pipe_diameter / \
                d.fluid.kinematic_viscosity
        self.od.update([Reynolds_number])

        
    def test_nonrecursive_unlink(self):
        self.od.velocity = 0.02
        self.od.fluid.density = 1000.
        self.assertAlmostEqual(self.od.Reynolds_number, 2000.)
        self.assertAlmostEqual(
            self.od.fluid.kinematic_viscosity, 1.e-6)
        self.od.transform_entries(unlink)
        self.od.fluid.density = 500.
        self.assertAlmostEqual(
            self.od.fluid.kinematic_viscosity, 2.e-6)
        self.assertAlmostEqual(self.od.Reynolds_number, 2000.)

        
    def test_nonrecursive_unlink_with_missing_dependencies(self):
        self.od.velocity = 0.02
        self.assertRaises(AttributeError,
                          lambda: self.od.transform_entries(unlink))
        self.od.fluid.density = 1000.
        self.od.transform_entries(unlink)

        
    def test_recursive_unlink(self):
        self.od.velocity = 0.02
        self.od.fluid.density = 1000.
        self.od.fluid.bulk_modulus = 2.
        self.od.transform_entries(unlink, recursive=True)
        self.od.fluid.density = 500.
        self.assertAlmostEqual(
            self.od.fluid.kinematic_viscosity, 1.e-6)
        self.assertAlmostEqual(self.od.Reynolds_number, 2000.)

        
    def test_recursive_unlink_with_missing_dependency(self):
        self.od.velocity = 0.02
        self.od.fluid.density = 1000.
        self.assertRaises(AttributeError,
                          lambda: self.od.transform_entries(
                              unlink, recursive=True))
        

    def test_nonrecursive_check_missing_dependencies(self):
        self.od.velocity = 0.02
        self.assertRaises(OptionsDictException,
                          lambda: self.od.transform_entries(
                              Check(missing_dependencies)))
        self.od.fluid.density = 1000.
        self.od.transform_entries(Check(missing_dependencies))
        
        
    def test_recursive_check_missing_dependency(self):
        self.od.velocity = 0.02
        self.od.fluid.density = 1000.
        self.assertRaises(OptionsDictException,
                          lambda: self.od.transform_entries(
                              Check(missing_dependencies), recursive=True))

        
    def test_nonrecursive_remove_missing_dependencies(self):
        self.od.velocity = 0.02
        self.od.transform_entries(Remove(missing_dependencies))
        self.assertRaises(AttributeError,
                          lambda: self.od.speed_of_sound)

        
    def test_recursive_remove_missing_dependencies(self):
        self.od.velocity = 0.02
        self.od.fluid.density = 1000.
        self.od.transform_entries(Remove(missing_dependencies),
                                  recursive=True)
        self.od.Reynolds_number
        self.assertRaises(AttributeError,
                          lambda: self.od.speed_of_sound)
        
        
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
        'my_func'.  This could be nested in order to test recursive
        entry transformations, but recursion has already been tested
        extensively in TestOptionsDictDependentEntries and
        TestOptionsDictDependentEntriesWithDotSyntax.
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


    def test_check_unpicklable(self):
        """
        I can use Check(unpicklable) and expect an OptionsDictException.
        """
        self.assertRaises(OptionsDictException,
                          lambda: self.od.transform_entries(
                              Check(unpicklable)))

    def test_remove_unpicklable(self):
        """
        When I use Remove(unpicklable), I should end up with an empty
        dict.
        """
        self.od.transform_entries(Remove(unpicklable))
        self.assertEqual(len(self.od), 0)
        

    def test_sequence(self):
        """
        I can use a sequence that goes [Check(unpicklable),
        Remove(unpicklable)] and expect an OptionsDictException,
        indicating that the first function in the sequence has been
        executed.  I can also use a sequence that goes [unlink,
        Check(unpicklable)] and still expect an OptionsDictException,
        indicating that the second function in the sequence has been
        executed.
        """
        self.assertRaises(OptionsDictException,
                          lambda: self.od.transform_entries(
                              Sequence([Check(unpicklable),
                                        Remove(unpicklable)])))
        self.assertRaises(OptionsDictException,
                          lambda: self.od.transform_entries(
                              Sequence([unlink, Check(unpicklable)])))


        
if __name__ == '__main__':
    unittest.main()
