import sys
sys.path.append('..')

import unittest
from optionsdict_itertools import flatten, multizip, \
    combine, create_lookup


class TestOptionsDictIterationTools(unittest.TestCase):
    
    def test_flatten(self):
        tree = [1, ["a string", [{'a': 'dict'}, 4], 5]]
        expected = (1, "a string", {'a': 'dict'}, 4, 5)
        result = flatten(tree)
        self.assertEqual(tuple(result), expected)

    def test_multizip_simple(self):
        parents = ('A', ('B', 'C'))
        children = ((1, 2, 3), (4, 5))
        expected = (('A', 1), ('A', 2), ('A', 3),
                    ('B', 4), ('B', 5),
                    ('C', 4), ('C', 5))
        result = multizip(parents, children)
        for r, e in zip(result, expected):
            self.assertEqual(tuple(r), e)

    def test_multizip_with_strings_and_dicts(self):
        parents = ('A', 'bee', {'C': 'see'})
        children = ((1, 'two'), ({3: 'three'}, 4, 5), (6,))
        expected = (('A', 1), ('A', 'two'),
                    ('bee', {3: 'three'}), ('bee', 4), ('bee', 5),
                    ({'C': 'see'}, 6))
        result = multizip(parents, children)
        for r, e in zip(result, expected):
            self.assertEqual(tuple(r), e)

    def test_combine(self):
        src = (1, 2, 3)
        @combine
        def myfunc(x):
            return x
        self.assertEqual(myfunc((1, 2, 3)), 6)
    
    class FakeOptionsDict:
        def __init__(self, n):
            self.n = n
        def __add__(self, other):
            self.n += other.n
            return self
        def __radd__(self, other):
            if not other:
                return self
            else:
                return self + other
        def __getitem__(self, key):
            if key=='n':
                return self.n
    
    def test_create_lookup(self):
        src = []
        for x in (1, 2, 3):
            src.append(self.FakeOptionsDict(x))
        lookup = create_lookup('n')
        self.assertEqual(lookup(src), 6)
        
