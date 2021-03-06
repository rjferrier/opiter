import unittest
from unit_options_dict import UnitOptionsDict, UnitNodeInfo, \
    OptionsDictException, NodeInfoException
from types import MethodType


def bump(target_dict, key):
    "For testing transform_items"
    try:
        target_dict[key] += 1
    except TypeError:
        pass

    
class TestOptionsDictCreation(unittest.TestCase):

    def test_create_from_dict(self):
        """
        When I create an OptionsDict from a dict, there is no error.
        """
        UnitOptionsDict({'foo': 'bar'})

    def test_create_from_dependent_items(self):
        """
        When I create an OptionsDict from an iterable of functions, there
        is no error.
        """
        def foo(opt):
            return 'bar'
        UnitOptionsDict([foo])
        UnitOptionsDict((foo,))
        UnitOptionsDict({foo})

    def test_create_from_class(self):
        """
        When I create an OptionsDict from a class, there is no error.
        """
        class basis:
            foo = 'bar'
            def baz(self): return 0
        UnitOptionsDict(basis)

    def test_create_from_other(self):
        """
        When I create an OptionsDict using something other than a dict,
        a list of functions or a class, an error should be raised.
        """
        for thing in ['foo', 3, 3.14]:
            create_od = lambda: UnitOptionsDict(thing)
            self.assertRaises(OptionsDictException, create_od)

    def test_create_with_attribute_name_clash(self):
        """
        When I create an OptionsDict and one of my items has the same
        name as a preexisting attribute, an error should be raised.
        """
        create_od = lambda: UnitOptionsDict({'get_string': 'hello'})
        self.assertRaises(OptionsDictException, create_od)

    def test_create_with_underscore_prefixed_item_name(self):
        """
        When I create an OptionsDict and one of my items has the same
        name as a preexisting attribute, an error should be raised.
        """
        create_od = lambda: UnitOptionsDict({'_foo': 'bar'})
        self.assertRaises(OptionsDictException, create_od)


class TestOptionsDictBasics(unittest.TestCase):
    
    def setUp(self):
        "I create an anonymous OptionsDict."
        self.od = UnitOptionsDict(items={'foo': 'bar'})
        
    def test_equal(self):
        self.assertEqual(self.od, UnitOptionsDict({'foo': 'bar'}))
                
    def test_unequal(self):
        self.assertNotEqual(self.od, UnitOptionsDict({'baz': 'bar'}))

    def test_node_info_empty(self):
        self.assertRaises(NodeInfoException, lambda: self.od.get_node_info())

    def test_setitem_dot_syntax(self):
        self.od.baz = 'qux'
        self.assertEqual(self.od['baz'], 'qux')
        
    def test_getitem_dot_syntax(self):
        self.assertEqual(self.od.foo, 'bar')

    def test_setitem_dot_syntax_clashes_with_attribute(self):
        def setter():
            self.od.get_string = 'qux'
        self.assertRaises(OptionsDictException, setter)
        
    def test_getitem_dot_syntax_clashes_with_attribute(self):
        self.od['get_string'] = 'baz'
        self.assertIsInstance(self.od.get_string, MethodType)
    
    def test_set_and_get_node_info(self):
        od = UnitOptionsDict({'foo': 'bar'})
        ni = UnitNodeInfo('foo')
        # ni should be some throwaway value
        self.assertIsNotNone(ni)
        od.set_node_info(ni)
        self.assertEqual(ni, od.get_node_info())

    def test_compare_with_options_dict_from_class(self):
        """
        This can be done as long as there aren't any dependent items.
        Dependent items are created from functions, and functions
        created in different contexts aren't equal.
        """
        class basis:
            foo = 'bar'
        od_from_class = UnitOptionsDict(basis)
        self.assertEqual(self.od, od_from_class)
        
        
class TestOptionsDictDependentItems(unittest.TestCase):
    
    def setUp(self):
        """
        I create an OptionsDict with two variables: kinematic_viscosity
        and pipe_diameter.  I define Reynolds_number, which is a dependent
        item dependent on velocity, pipe_diameter and
        kinematic_viscosity.  I haven't defined velocity yet.
        """
        self.od = UnitOptionsDict({
            'kinematic_viscosity': 1.e-6,
            'pipe_diameter'      : 0.1 })
        def Reynolds_number(d):
            return d['velocity'] * d['pipe_diameter'] / \
                d['kinematic_viscosity']
        self.od.update([Reynolds_number])
        
    def test_missing_information_raises_error(self):
        """
        I try and obtain Reynolds_number before velocity is defined.  A
        KeyError should be raised.
        """
        self.assertRaises(KeyError, 
                          lambda: self.od['Reynolds_number'])

    def test_dependent_item(self):
        """
        I define velocity and change one the variables.
        Reynolds_number should update automatically.
        """
        self.od['velocity'] = 0.02
        self.assertAlmostEqual(self.od['Reynolds_number'], 2000.)
        self.od['pipe_diameter'] = 0.15
        self.assertAlmostEqual(self.od['Reynolds_number'], 3000.)

    def test_twice_removed_dependent_item(self):
        """
        I add an 'observation' item which depends on Reynolds_number.
        When velocity is changed, observation should update
        automatically.
        """
        def observation(d):
            if d['Reynolds_number'] < 2100.:
                return 'laminar'
            elif d['Reynolds_number'] > 4000.:
                return 'turbulent'
            else:
                return 'transitional'
        # modify the dict
        self.od.update([observation])
        # now test
        self.od['velocity'] = 0.02
        self.assertEqual(self.od['observation'], 'laminar')
        self.od['velocity'] = 0.05
        self.assertEqual(self.od['observation'], 'turbulent')
        
    def test_independence_after_duplication(self):
        """
        Suppose I use self.od to create a new OptionsDict.  The new
        object should be equivalent, but not identical to, the old
        object.  That is, it should be a copy.
        """
        self.od['velocity'] = 0.
        dd = UnitOptionsDict(self.od)
        # test for equivalence and non-identity
        self.assertEqual(dd, self.od)
        self.assertFalse(dd is self.od)
        # try changing the new object.  Its options items should
        # update accordingly, while the old object should be unaffected
        dd['velocity'] = 0.02
        self.assertAlmostEqual(dd['Reynolds_number'], 2000.)
        self.assertAlmostEqual(self.od['Reynolds_number'], 0.)


class TestNestedOptionsDictBasics(unittest.TestCase):

    def setUp(self):
        self.od = UnitOptionsDict({
            'foo': 1,
            'bar': UnitOptionsDict({
                'baz': 2})})
        
    def test_equal(self):
        other = UnitOptionsDict({
            'foo': 1,
            'bar': UnitOptionsDict({
                'baz': 2})})
        self.assertEqual(self.od, other)
        
    def test_unequal(self):
        other = UnitOptionsDict({
            'foo': 1,
            'bar': UnitOptionsDict({})})
        self.assertNotEqual(self.od, other)
    
    def test_setitem_dot_syntax(self):
        self.od.bar.baz = 3
        self.assertEqual(self.od['bar']['baz'], 3)
        
    def test_getitem_dot_syntax(self):
        self.assertEqual(self.od.bar.baz, 2)

    def test_nonrecursive_transform_items(self):
        self.od.transform_items(bump, recursive=False)
        expected = UnitOptionsDict({
            'foo': 2,
            'bar': UnitOptionsDict({
                'baz': 2})})
        self.assertEqual(self.od, expected)

    def test_recursive_transform_items(self):
        self.od.transform_items(bump)
        expected = UnitOptionsDict({
            'foo': 2,
            'bar': UnitOptionsDict({
                'baz': 3})})
        self.assertEqual(self.od, expected)

        
class TestNestedOptionsDictDependentItems(unittest.TestCase):
    
    def setUp(self):
        inner_od = UnitOptionsDict({
            'foo': 1,
            'bar': lambda self: self['foo'] + 1})
        self.od = UnitOptionsDict({
            'inner': inner_od,
            'baz': lambda self: self['inner']['bar'] + 1})

    def test_nested_dependent_item(self):
        self.od['inner']['foo'] = 2
        self.assertEqual(self.od['inner']['bar'], 3)
        self.assertEqual(self.od['baz'], 4)

        
        
class TestOptionsDictFromClassDependentItems(unittest.TestCase):

    def check_dependent_items(self):
        self.od['velocity'] = 0.02
        self.assertAlmostEqual(self.od['Reynolds_number'], 2000.)
        self.od['pipe_diameter'] = 0.15
        self.assertAlmostEqual(self.od['Reynolds_number'], 3000.)
        
    def test_dependent_item_from_simple_class(self):
        """
        I repeat the setup and a key test in TestOptionsDictDependentItems,
        but I use a class with attributes and methods to construct the
        OptionsDict.  Ideally an equality check would be used to check the
        state of this OptionsDict, but functions and hence dependent items
        created in different contexts are never equal.
        """
        class basis:
            kinematic_viscosity = 1.e-6
            pipe_diameter = 0.1
            def Reynolds_number(self):
                return self['velocity'] * self['pipe_diameter'] / \
                    self['kinematic_viscosity']
        self.od = UnitOptionsDict(basis)
        self.check_dependent_items()

    def test_dependent_item_from_inheritance(self):
        """
        This time the dependent item is inherited from a base class.
        """
        class parent_basis:
            def Reynolds_number(self):
                return self['velocity'] * self['pipe_diameter'] / \
                    self['kinematic_viscosity']
        class child_basis(parent_basis):
            kinematic_viscosity = 1.e-6
            pipe_diameter = 0.1
        self.od = UnitOptionsDict(child_basis)
        self.check_dependent_items()

    def test_dependent_item_from_multiple_inheritance(self):
        """
        This time the dependent item is inherited from one of two parallel
        base classes.
        """
        class parent_basis_1:
            def Reynolds_number(self):
                raise AssertionError(
                    "class parent_basis_1 should be overridden by "+\
                    "parent_basis_2")
        class parent_basis_2:
            def Reynolds_number(self):
                return self['velocity'] * self['pipe_diameter'] / \
                    self['kinematic_viscosity']
        class child_basis(parent_basis_1, parent_basis_2):
            kinematic_viscosity = 1.e-6
            pipe_diameter = 0.1
        self.od = UnitOptionsDict(child_basis)
        self.check_dependent_items()

    def test_dependent_item_from_extended_inheritance(self):
        """
        This time the items are spread over an extended inheritance
        hierarchy.
        """
        class grandparent_basis:
            kinematic_viscosity = 1.e-6
        class parent_basis(grandparent_basis):
            def Reynolds_number(self):
                return self['velocity'] * self['pipe_diameter'] / \
                    self['kinematic_viscosity']
        class child_basis(parent_basis):
            pipe_diameter = 0.1
        self.od = UnitOptionsDict(child_basis)
        self.check_dependent_items()
            

class TestOptionsDictTemplateExpansion(unittest.TestCase):

    def setUp(self):
        self.od = UnitOptionsDict({'fluid'         : 'water',
                                   'melting_point' :       0,
                                   'boiling_point' :     100})

    def test_expand_string(self):
        template = "$fluid has a melting point of $melting_point"+\
                   " degrees C."
        expected = "water has a melting point of 0 degrees C."
        self.assertEqual(self.od.expand_template_string(template), expected)

    def test_expand_string_missing_item(self):
        template = "$fluid has a density of $density kg/m^3."
        self.assertRaises(KeyError,
                          lambda: self.od.expand_template_string(template))

        
    def test_expand_nested(self):
        template = "$fluid has a $change point of ${${change}_point}"+\
                   " degrees C."
        
        self.od['change'] = 'melting'
        expected = "water has a melting point of 0 degrees C."
        self.assertEqual(self.od.expand_template_string(template, loops=2),
                         expected)
        
        self.od['change'] = 'boiling'
        expected = "water has a boiling point of 100 degrees C."
        self.assertEqual(self.od.expand_template_string(template, loops=2),
                         expected)

        
    def test_expand_not_enough_loops(self):
        template = "$fluid has a $change point of ${${change}_point}"+\
                   " degrees C."
        
        self.od['change'] = 'melting'
        expected = "water has a melting point of ${melting_point}"+\
                   " degrees C."
        self.assertRaises(KeyError,
                          lambda: self.od.expand_template_string(template, 1))

        
    
if __name__ == '__main__':
    unittest.main()
        
