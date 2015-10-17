import unittest
from opiter.options_tree_elements import OptionsTreeElement


class FakeOptionsDict(dict):
    def transform_items(self, func, recursive):
        for k in self.keys():
            func(self, k)

def dict_function_1(d):
    d.update({'a': 'new1'})

def dict_function_2(d):
    d.update({'b': 'new2'})

def item_function_1(d, k):
    d[k] += 1

def item_function_2(d, k):
    d[k] *= 2

def list_function_1(l):
    l.reverse()

def list_function_2(l):
    del l[0]

    
class TestOptionsTreeElementWithSingleDict(unittest.TestCase):

    def setUp(self):
        self.options_dict = FakeOptionsDict({'a': 1, 'b': 2})

    def test_apply_single_dict_hook(self):
        tree_el = OptionsTreeElement(
            dict_hooks=[dict_function_1])
        tree_el.apply_hooks([self.options_dict])
        self.assertEqual(self.options_dict, {'a': 'new1', 'b': 2})

    def test_apply_multiple_dict_hooks(self):
        tree_el = OptionsTreeElement(
            dict_hooks=[dict_function_1, dict_function_2])
        tree_el.apply_hooks([self.options_dict])
        self.assertEqual(self.options_dict, {'a': 'new1', 'b': 'new2'})

    def test_apply_single_item_hook(self):
        tree_el = OptionsTreeElement(
            item_hooks=[item_function_1])
        tree_el.apply_hooks([self.options_dict])
        self.assertEqual(self.options_dict, {'a': 2, 'b': 3})

    def test_apply_multiple_item_hooks(self):
        tree_el = OptionsTreeElement(
            item_hooks=[item_function_1, item_function_2])
        tree_el.apply_hooks([self.options_dict])
        self.assertEqual(self.options_dict, {'a': 4, 'b': 6})

        
class TestOptionsTreeElementWithMultipleDicts(unittest.TestCase):

    def setUp(self):
        self.options_dicts = [
            FakeOptionsDict({'a': 1}),
            FakeOptionsDict({'b': 2}),
            FakeOptionsDict({'c': 3})]

    def test_apply_single_list_hook(self):
        tree_el = OptionsTreeElement(
            list_hooks=[list_function_1])
        tree_el.apply_hooks(self.options_dicts)
        self.assertEqual(self.options_dicts, [
            {'c': 3}, {'b': 2}, {'a': 1}])

    def test_apply_multiple_list_hooks(self):
        tree_el = OptionsTreeElement(
            list_hooks=[list_function_1, list_function_2])
        tree_el.apply_hooks(self.options_dicts)
        self.assertEqual(self.options_dicts, [{'b': 2}, {'a': 1}])

        

        
if __name__ == '__main__':
    unittest.main()
        
