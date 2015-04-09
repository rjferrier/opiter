import sys
sys.path.append('..')

import unittest
from tools import flatten, attach, merge, merges_dicts, Lookup


class TestIterationTools(unittest.TestCase):
    
    def test_flatten(self):
        tree = [1, ["a string", [{'a': 'dict'}, 4], 5]]
        expected = (1, "a string", {'a': 'dict'}, 4, 5)
        result = flatten(tree)
        self.assertEqual(tuple(result), expected)

    def test_attach_simple(self):
        parents = ('A', ('B', 'C'))
        children = ((1, 2, 3), (4, 5))
        expected = (('A', 1), ('A', 2), ('A', 3),
                    ('B', 4), ('B', 5),
                    ('C', 4), ('C', 5))
        result = attach(parents, children)
        for r, e in zip(result, expected):
            self.assertEqual(tuple(r), e)

    def test_attach_with_strings_and_dicts(self):
        parents = ('A', 'bee', {'C': 'see'})
        children = ((1, 'two'), ({3: 'three'}, 4, 5), (6,))
        expected = (('A', 1), ('A', 'two'),
                    ('bee', {3: 'three'}), ('bee', 4), ('bee', 5),
                    ({'C': 'see'}, 6))
        result = attach(parents, children)
        for r, e in zip(result, expected):
            self.assertEqual(tuple(r), e)

            
class TestDictTools(unittest.TestCase):

    def setUp(self):
        self.d1 = {'a': 1, 'b': 1, 'c': 1}
        self.d2 = {'a': 2, 'b': 2}
        self.d3 = {'a': 3}
        self.dicts = [self.d1, self.d2, self.d3]
    
    def test_merge(self):
        d = merge(self.dicts)
        self.assertEqual(d['c'], 1)
        self.assertEqual(d['a'], 3)
    
    def test_merge_single_dict(self):
        d = merge(self.d1)
        self.assertEqual(d['c'], 1)
        self.assertEqual(d['a'], 1)
    
    def test_merges_dicts(self):
        @merges_dicts
        def myfunc(d):
            return d['a'] + d['b'] + d['c']
        self.assertEqual(myfunc(self.dicts), 6)
    
    def test_create_lookup(self):
        lookup = Lookup('c')
        self.assertEqual(lookup(self.dicts), 1)
        lookup = Lookup('a')
        self.assertEqual(lookup(self.dicts), 3)
        
