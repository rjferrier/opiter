import unittest
from options_dict import Lookup, GetString, dict_key_pairs, \
    transform_entries, unlink

    
    
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


class TestTransformEntryFunctors(unittest.TestCase):

    def test_unlink(self):
        class Foo:
            """
            Class synthesising dependent entries.
            """
            def __init__(self):
                self.items = [0, lambda self: self[0] + 1]
            def __getitem__(self, i):
                val = self.items[i]
                try:
                    return val(self)
                except TypeError:
                    return val
            def __setitem__(self, i, val):
                self.items[i] = val
        foo = Foo()
        # is Foo working?
        self.assertEqual(foo[1], 1)
        foo[0] = 1
        self.assertEqual(foo[1], 2)
        # now try unlinking.
        unlink(foo, 1)
        foo[0] = 2
        self.assertEqual(foo[1], 2)
            

class TestDictKeyPairsGenerator(unittest.TestCase):
    
    def setUp(self):
        self.dict = {
            'A': 1,
            'B': {
                'C': 2,
                'D': {
                    'E': 3}}}

    def test_nonrecursive_dict_key_pairs(self):
        self.assertEqual([d[k] for d, k in dict_key_pairs(self.dict)],
                         [1, {'C': 2, 'D': {'E': 3}}])

    def test_nonrecursive_dict_key_pairs_given_key(self):
        self.assertEqual([d[k] for d, k in dict_key_pairs(self.dict, 'A')],
                         [1])
        self.assertEqual([d[k] for d, k in dict_key_pairs(self.dict, 'B')],
                         [2, {'E': 3}])

    def test_recursive_dict_key_pairs(self):
        self.assertEqual(
            [d[k] for d, k in dict_key_pairs(self.dict, recursive=True)],
            [1, 2, 3])

    def test_recursive_dict_key_pairs_given_key(self):
        self.assertEqual(
            [d[k] for d, k in dict_key_pairs(self.dict, 'A', recursive=True)],
            [1])
        self.assertEqual(
            [d[k] for d, k in dict_key_pairs(self.dict, 'B', recursive=True)],
            [2, 3])
        
    
if __name__ == '__main__':
    unittest.main()
