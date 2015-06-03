import sys
sys.path.append('..')

import unittest
from options_dict import Lookup, Str, freeze


class TestOptionsDictHelpers(unittest.TestCase):
        
    def test_lookup_functor(self):
        objs = [{'foo': 'bar'}] * 3
        results = map(Lookup('foo'), objs)
        self.assertEqual(results, ['bar'] * 3)

    def test_str_functor(self):
        class Stringifiable:
            def str(self, only=[], exclude=[], absolute={}, relative={}, 
                    formatter=None):
                return only + exclude + absolute + relative + formatter
        objs = [Stringifiable()] * 3
        functor = Str(only='a', exclude='b', absolute='c', relative='d',
                          formatter='e')
        results = map(functor, objs)
        self.assertEqual(results, ['abcde'] * 3)

    def test_freeze(self):
        class Freezable:
            def __init__(self):
                self.frozen = False
            def freeze(self):
                self.frozen = True
                
        objs = [Freezable()] * 3
        before = [obj.frozen for obj in objs]
        self.assertEqual(before, [False] * 3)

        objs = freeze(objs)
        after = [obj.frozen for obj in freeze(objs)]
        self.assertEqual(after, [True] * 3)

        
if __name__ == '__main__':
    unittest.main()
