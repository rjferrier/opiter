import unittest
from test_functional_common import \
    TestOptionsDictCartesianProductIteration, \
    TestOptionsDictTreeIteration
from opiter import Lookup, GetString, transform_items, unlink
from multiprocessing import Pool


def pool():
    return Pool(2)

def distance_func(opt):
    return opt['speed'] * opt['travel_time']

    
class TestOptionsDictCartesianProductParallelIteration(
        TestOptionsDictCartesianProductIteration):

    def test_mapping(self):
        """
        I pass distance_func to a multiprocessing map.  Note that
        distance_func must be a global, named function to avoid
        pickling errors (which is why it resides outside the present
        test class)
        """
        options_dicts = self.tree.collapse()
        results = pool().map(distance_func,
                             transform_items(options_dicts, unlink))
        self.assertAlmostEqual(results, self.expected_distances)
            
    def test_mapping_with_extra_dict_and_dependent_item(self):
        """
        I define distance as a dependent item and pass a corresponding
        Lookup functor to a multiprocessing map.
        """
        self.tree.update({'distance': lambda opt: \
                          opt['speed'] * opt['travel_time']})
        options_dicts = self.tree.collapse()
        results = pool().map(Lookup('distance'),
                             transform_items(options_dicts, unlink))
        self.assertAlmostEqual(results, self.expected_distances)


class TestOptionsDictTreeParallelIteration(
        TestOptionsDictTreeIteration):
            
    def test_mapping_and_name_check(self):
        resulting_names = pool().map(
            GetString(), transform_items(self.options_dicts, unlink))
        self.check_names(resulting_names)
            
    def test_mapping_and_lookup(self):
        resulting_times = pool().map(
            Lookup('cost'), transform_items(self.options_dicts, unlink))
        self.check_times(resulting_times)

            
if __name__ == '__main__':
    unittest.main()
