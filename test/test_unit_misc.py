import unittest
from options_dict import Lookup, GetString, dict_key_pairs, \
    transform_items, unlink, OptionsDictException, Check, Remove, \
    Sequence, missing_dependencies, unpicklable


class MixedItems:
    """
    Class synthesising a dictionary with dependent items.
    """
    def __init__(self, items):
        self.items = items
    def __getitem__(self, i):
        val = self.items[i]
        try:
            return val(self)
        except TypeError:
            return val
    def __setitem__(self, i, val):
        self.items[i] = val

                
def not_bumpable(dictionary, key):
    "For testing Check and Remove functors."
    val = dictionary[key]
    try: 
        val += 1
        return None
    except TypeError:
        return "this item cannot be bumped by 1."

    
def picklable_function(self):
    "For testing unpicklable test function"
    return "This function was declared in the module space."


def bump(dictionary, key):
    "For testing Sequence functor"
    dictionary[key] += 1

def double(dictionary, key):
    "For testing Sequence functor"
    dictionary[key] *= 2
    

    
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



class TestTransformItemFunctors(unittest.TestCase):

    def test_unlink(self):
        mixed_items = MixedItems([0, lambda self: self[0] + 1])
        # is MixedItems working?
        self.assertEqual(mixed_items[1], 1)
        mixed_items[0] = 1
        self.assertEqual(mixed_items[1], 2)
        # now try unlinking.
        unlink(mixed_items, 1)
        mixed_items[0] = 2
        self.assertEqual(mixed_items[1], 2)
        
    def test_check(self):
        tgt = {'a': 1,
               'b': 'some_str',
               'c': 3.14}
        check = Check(not_bumpable)
        for i in 'abc':
            if i == 'b':
                # this item should raise an error
                self.assertRaises(OptionsDictException,
                                  lambda: check(tgt, i))
            else:
                # this one should not
                check(tgt, i)
        
    def test_remove(self):
        tgt = {'a': 1,
               'b': 'some_str',
               'c': 3.14}
        rm = Remove(not_bumpable)
        for i in 'abc':
            rm(tgt, i)
        self.assertEqual(tgt, {'a': 1, 'c': 3.14})
        
    def test_sequence(self):
        tgt = [1, 2, 3]
        seq = Sequence([double, bump])
        for i in range(3):
            seq(tgt, i)
        self.assertEqual(tgt, [3, 5, 7])
        

        
class TestTestFunctors(unittest.TestCase):

    def test_missing_dependencies(self):
        mixed_items = MixedItems({'a': 1,
                                  'b': lambda self: self['c'] + 1})
        self.assertFalse(
            missing_dependencies(mixed_items, 'a'))
        self.assertTrue(
            missing_dependencies(mixed_items, 'b'))

    def test_unpicklable(self):
        def unpicklable_function(self):
            return "This function was declared in a method."
        items = {'f1': picklable_function,
                   'f2': unpicklable_function}
        self.assertFalse(
            unpicklable(items, 'f1'))
        self.assertTrue(
            unpicklable(items, 'f2'))
    

    
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
