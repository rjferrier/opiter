import sys
sys.path.append('..')

from test_functional_common import *
import unittest


class TestOptionsDictCartesianProductSerialIteration(
        TestOptionsDictCartesianProductIteration):
    """
    The base test fixture is defined in test_functional_common.
    """

    def test_manual_iteration(self):
        """
        I want to iterate over all combinations of speed and time and
        calculate distance for each combination.
        """
        tree = self.speed * self.time
        for opt, expected in zip(tree.collapse(),
                                 self.expected_distances):
            result = opt['speed'] * opt['travel_time']
            self.assertAlmostEqual(result, expected)
            
    def test_manual_iteration_with_extra_dict_and_dynamic_entry(self):
        """
        Instead of calculating the distance myself, I might include
        another OptionsDict which does the work via a dynamic entry.
        """
        common = OptionsNode('common', [distance])
        tree = common * self.speed * self.time
        for opt, expected in zip(tree.collapse(),
                                 self.expected_distances):
            self.assertAlmostEqual(opt['distance'], expected)

    def test_mapping(self):
        """
        I want to create combinations of speed and travel time and
        calculate the correct distances using a map.
        """
        tree = self.speed * self.time
        resulting_distances = map(distance, tree.collapse())
        for resulting, expected in \
                zip(resulting_distances, self.expected_distances):
            self.assertAlmostEqual(resulting, expected)


class TestOptionsDictTreeSerialIteration(TestOptionsDictTreeIteration):
        
    def test_manual_iteration_and_name_check(self):
        resulting_names = []
        for opt in self.tree.collapse():
            resulting_names.append(str(opt))
        self.check_names(resulting_names)

    def test_manual_iteration_and_lookup(self):
        resulting_times = []
        for opt in self.tree.collapse():
            resulting_times.append(opt['cost'])
        self.check_times(resulting_times)

    def test_mapping_and_name_check(self):
        resulting_names = map(label, self.tree.collapse())
        self.check_names(resulting_names)
            
    def test_mapping_and_lookup(self):
        resulting_times = map(Lookup('cost'), self.tree.collapse())
        self.check_times(resulting_times)
            
            
if __name__ == '__main__':
    unittest.main()
        
