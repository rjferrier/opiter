import sys
sys.path.append('..')

from test_functional_common import *
from tools import product, Lookup
from multiprocessing import Pool


def pool():
    return Pool(2)

    
class TestOptionsDictCartesianProductParallelIteration(
        TestOptionsDictCartesianProductIteration):

    def test_mapping(self):
        tree = self.speed * self.time
        resulting_distances = pool().map(distance, tree.collapse())
        for resulting, expected in \
                zip(resulting_distances, self.expected_distances):
            self.assertAlmostEqual(resulting, expected)
            
    def test_mapping_with_extra_dict_and_dynamic_entry(self):
        common = OptionsNode('common', [distance])
        tree = common * self.speed * self.time
        resulting_distances = pool().map(distance, tree.collapse())
        for resulting, expected in \
                zip(resulting_distances, self.expected_distances):
            self.assertAlmostEqual(resulting, expected)


class TestOptionsDictTreeParallelIteration(
        TestOptionsDictTreeIteration):
            
    def test_mapping_and_name_check(self):
        resulting_names = pool().map(label, self.tree.collapse())
        self.check_names(resulting_names)
            
    def test_mapping_and_lookup(self):
        resulting_times = pool().map(Lookup('cost'), self.tree.collapse())
        self.check_times(resulting_times)

            
if __name__ == '__main__':
    unittest.main()
