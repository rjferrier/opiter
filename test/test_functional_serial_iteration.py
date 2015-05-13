import sys
sys.path.append('..')

from test_functional_common import *
import unittest
from tools import product, attach, merge, identify, Lookup


class TestOptionsDictCartesianProductSerialIteration(
        TestOptionsDictCartesianProductIteration):

    def test_manual_iteration(self):
        """
        I should be able to iterate over all combinations of speed and
        travel time and calculate the correct distance for each
        combination.
        """
        combos = product(self.speed, self.time)
        for combo, expected in zip(combos, self.expected_distances):
            # I can combine the two dictionaries for convenience
            opt = merge(combo)
            resulting_distance = opt['speed'] * opt['travel_time']
            self.assertAlmostEqual(resulting_distance, expected)
            
    def test_manual_iteration_with_extra_dict_and_dynamic_entry(self):
        """
        Instead of calculating the distance myself, I might include
        another OptionsDict which does the work via a dynamic entry.
        """
        common = OptionsDict([distance])
        combos = product(common, self.speed, self.time)
        for combo, expected in zip(combos, self.expected_distances):
            opt = merge(combo)
            self.assertAlmostEqual(opt['distance'], expected)

    def test_mapping(self):
        """
        I should be able create combinations of speed and travel time
        and calculate the correct distances using a map.  I will use
        the merges_dicts decorator so that my distance calculator
        only has to deal with one dictionary.
        """
        combos = product(self.speed, self.time)
        resulting_distances = map(distance, combos)
        for resulting, expected in \
                zip(resulting_distances, self.expected_distances):
            self.assertAlmostEqual(resulting, expected)


class TestOptionsDictTreeSerialIteration(
        TestOptionsDictTreeIteration):
        
    def test_manual_iteration_and_name_check(self):
        resulting_names = []
        for combo in self.tree:
            opt = merge(combo)
            resulting_names.append(str(opt))
        self.check_names(resulting_names)

    def test_manual_iteration_and_lookup(self):
        resulting_times = []
        for combo in self.tree:
            opt = merge(combo)
            resulting_times.append(opt['cost'])
        self.check_times(resulting_times)

    def test_mapping_and_name_check(self):
        resulting_names = map(identify, self.tree)
        self.check_names(resulting_names)
            
    def test_mapping_and_lookup(self):
        resulting_times = map(Lookup('cost'), self.tree)
        self.check_times(resulting_times)
            
            
if __name__ == '__main__':
    unittest.main()
        
