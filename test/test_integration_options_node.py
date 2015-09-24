import unittest
from options_node import OptionsNode, OrphanNodeInfo
from options_dict import OptionsDict
    

class TestOptionsNodeCreation(unittest.TestCase):
    
    def check_name_and_entries(self, node, expected_name, expected_entries={}):
        self.assertEqual(str(node), expected_name)
        self.assertEqual(dict(node.collapse()[0]), expected_entries)
    
    def test_create_node_from_class(self):
        class a_node:
            foo = 'bar'
        node = OptionsNode(a_node)
        self.check_name_and_entries(node, 'a_node', {'foo': 'bar'})
        
    def test_create_node_from_class_and_array(self):
        class a_node:
            foo = 'bar'
        node = OptionsNode(a_node, array_name='an_array')
        self.check_name_and_entries(node, 'a_node',
                                    {'an_array': 'a_node',
                                     'foo': 'bar'})
        
    def test_create_node_from_name_and_format_function_and_array(self):
        name_format = lambda s: '<'+s+'>'
        node = OptionsNode('a_node', array_name='an_array',
                           name_format=name_format)
        self.check_name_and_entries(node, '<a_node>', {'an_array': 'a_node'})
        
    
        
class TestOptionsNodeBasics(unittest.TestCase):

    def setUp(self):
        self.node = OptionsNode('B', {'foo': 1})

    def test_create_options_dict(self):
        od = self.node.create_options_dict({'bar': 2})
        self.assertIsInstance(od, OptionsDict)
        self.assertEqual(od['bar'], 2)

    def test_create_info(self):
        ni = self.node.create_info()
        self.assertIsInstance(ni, OrphanNodeInfo)
        self.assertEqual(str(ni), 'B')

    def test_collapse(self):
        ods = self.node.collapse()
        self.assertEqual(len(ods), 1)
        od = ods[0]
        self.assertIsInstance(od, OptionsDict)
        self.assertEqual(od['foo'], 1)

        
class TestOrphanNodeAfterCollapse(unittest.TestCase):

    def check_type(self):
        self.assertIsInstance(self.od, OptionsDict)

    def check_name(self):
        self.assertEqual(str(self.od), 'A')

    def check_contents(self):
        self.assertEqual(self.od['foo'], 'bar')

    def check_node_info_name(self):
        ni = self.od.get_node_info()
        self.assertEqual(ni.get_string(), 'A')

        
class TestOrphanNodeFromUsualArgsAfterCollapse(TestOrphanNodeAfterCollapse):

    def setUp(self):
        """
        I create a node and collapse it, which should leave an OptionsDict
        with OrphanNodeInfo.
        """
        node = OptionsNode('A', {'foo': 'bar'})
        self.od = node.collapse()[0]

    def test_type(self):
        self.check_type()

    def test_name(self):
        self.check_name()

    def test_contents(self):
        self.check_contents()

    def test_node_info_name(self):
        self.check_node_info_name()

        
class TestOrphanNodeFromClassAfterCollapse(TestOrphanNodeAfterCollapse):

    def setUp(self):
        """
        I create a node from a class and collapse it, which should leave
        an OptionsDict with OrphanNodeInfo.
        """
        class A:
            foo = 'bar'
        node = OptionsNode(A)
        self.od = node.collapse()[0]

    def test_type(self):
        self.check_type()

    def test_name(self):
        self.check_name()

    def test_contents(self):
        self.check_contents()

    def test_node_info_name(self):
        self.check_node_info_name()


class TestOptionsNodeWithChild(unittest.TestCase):
    
    def setUp(self):
        child = OptionsNode('qux')
        self.node = OptionsNode('foo', {'bar': 1}, child=child)

    def test_compare_with_node_from_class(self):
        class foo:
            bar = 1
        class qux: 
            pass
        node_from_class = OptionsNode(foo, child=OptionsNode(qux))
        self.assertEqual(node_from_class, self.node)


if __name__ == '__main__':
    unittest.main()
