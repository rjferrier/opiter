import unittest
from options_dict import Lookup, GetString, dict_key_pairs, remove_links

        
class TestOptionsDictHelpers(unittest.TestCase):
    
    def test_lookup_functor(self):
        objs = [{'foo': 'bar'}] * 3
        results = map(Lookup('foo'), objs)
        self.assertEqual(results, ['bar'] * 3)

    def test_get_string_functor(self):
        class Stringifiable:
            def get_string(self, only=[], exclude=[], absolute={},
                           relative={}, formatter=None):
                return only + exclude + absolute + relative + formatter
        objs = [Stringifiable()] * 3
        functor = GetString(only='a', exclude='b', absolute='c',
                             relative='d', formatter='e')
        results = map(functor, objs)
        self.assertEqual(results, ['abcde'] * 3)

    def setUp_remove_links_test(self):
        class Delinkable:
            def __init__(self):
                self.frozen = False
            def remove_links(self, clean=False, recursive=False):
                self.frozen = True
        self.objs = [Delinkable()] * 3
        before = [obj.frozen for obj in self.objs]
        self.assertEqual(before, [False] * 3)
        
    def test_remove_links(self):
        self.setUp_remove_links_test()
        frozen_objs = remove_links(self.objs)
        after = [obj.frozen for obj in frozen_objs]
        self.assertEqual(after, [True] * 3)

    def test_remove_links_does_not_mutate_argument(self):
        self.setUp_remove_links_test()
        remove_links(self.objs)
        after = [obj.frozen for obj in self.objs]
        self.assertEqual(after, [False] * 3)


class TestOptionsDictRecursiveHelpers(unittest.TestCase):

    def setUp(self):
        self.obj = {
            'A': 1,
            'B': {
                'C': 2,
                'D': {
                    'E': 3}}}

    def test_nonrecursive_dict_key_pairs(self):
        self.assertEqual([d[k] for d, k in dict_key_pairs(self.obj)],
                         [1, {'C': 2, 'D': {'E': 3}}])

    def test_nonrecursive_dict_key_pairs_given_key(self):
        self.assertEqual([d[k] for d, k in dict_key_pairs(self.obj, 'A')],
                         [1])
        self.assertEqual([d[k] for d, k in dict_key_pairs(self.obj, 'B')],
                         [2, {'E': 3}])

    def test_recursive_dict_key_pairs(self):
        self.assertEqual(
            [d[k] for d, k in dict_key_pairs(self.obj, recursive=True)],
            [1, 2, 3])

    def test_recursive_dict_key_pairs_given_key(self):
        self.assertEqual(
            [d[k] for d, k in dict_key_pairs(self.obj, 'A', recursive=True)],
            [1])
        self.assertEqual(
            [d[k] for d, k in dict_key_pairs(self.obj, 'B', recursive=True)],
            [2, 3])

        
if __name__ == '__main__':
    unittest.main()
