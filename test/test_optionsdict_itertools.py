import sys
sys.path.append('..')

import unittest
from optionsdict_itertools import flatten, multizip, \
    combine_elements, create_lookup


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

        
class TestExtendedItertools(unittest.TestCase):
    
    def test_flatten(self):
        tree = [1, ["a string", [{'a': 'dict'}, 4], 5]]
        result = flatten(tree)
        expected = (1, "a string", {'a': 'dict'}, 4, 5)
        self.assertEqual(tuple(result), expected)

    def test_multizip_simple(self):
        parents = ('A', ('B', 'C'))
        children = ((1, 2, 3), (4, 5))
        result = multizip(parents, children)
        expected = (('A', 1), ('A', 2), ('A', 3),
                    ('B', 4), ('B', 5),
                    ('C', 4), ('C', 5))
        for r, e in zip(result, expected):
            self.assertEqual(tuple(r), e)

    # def test_multizip_with_strings_and_dicts(self):
    #     parents = ('A', 'Bee', {'C': 'see'})
    #     children = ((1, 'two'), ({3: 'three'}, 4, 5), 6)
    #     result = multizip(parents, children)
    #     expected = (('A', 1), ('A', 'two'),
    #                 ('Bee', {3: 'three'}), ('Bee', 4), ('Bee', 5),
    #                 ({'C': 'see'}, 6))
    #     for r, e in zip(result, expected):
    #         self.assertEqual(tuple(r), e)

    def test_combine_elements(self):
        src = (1, 2, 3)
        @combine_elements
        def myfunc(x):
            return x**2
        self.assertEqual(myfunc((1, 2, 3)), 36)

    def test_create_lookup(self):
        src = (FakeOptionsDict(1),
               FakeOptionsDict(2),
               FakeOptionsDict(3))
        lookup = create_lookup('n')
        self.assertEqual(lookup(src), 6)
        
