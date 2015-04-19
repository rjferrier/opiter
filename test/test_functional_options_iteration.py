import sys
sys.path.append('..')

import unittest
from options import OptionsDict
from tools import flatten, attach, merge, merges_dicts, \
    identify, Lookup
from itertools import product, chain
from multiprocessing import Pool

# NOTE: The multiprocessing tests currently cause pickling errors.
# These do not appear in the examples scripts, so there might be an
# incompatibility with the unit testing framework.  The offending
# tests have been commented out.


class TestOptionsDictCartesianProductIteration(unittest.TestCase):
    
    def setUp(self):
        """
        I create two OptionsDict sequences, one for 'speed' and one
        for 'travel time'.
        """
        self.speed = OptionsDict.sequence('speed', [30, 40, 60])
        self.time  = OptionsDict.sequence('travel_time', [0.5, 1])
        self.expected_distances = [15, 30, 20, 40, 30, 60]

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
        I will need to wrap this object as an extra sequence before
        passing to itertools.product, otherwise the object will return
        an iterator to its dictionary entries and mess things up.
        """
        calc = [OptionsDict({'distance': lambda self: \
                            self['speed'] * self['travel_time']})]
        combos = product(calc, self.speed, self.time)
        for combo, expected in zip(combos, self.expected_distances):
            opt = merge(combo)
            self.assertAlmostEqual(opt['distance'], expected)

    def test_serial_mapping(self):
        """
        I should be able create combinations of speed and travel time
        and calculate the correct distances using a map.  I will use
        the merges_dicts decorator so that my distance calculator
        only has to deal with one dictionary.
        """
        @merges_dicts
        def calc(opt):
            return opt['speed'] * opt['travel_time']
        combos = product(self.speed, self.time)
        resulting_distances = map(calc, combos)
        for resulting, expected in \
                zip(resulting_distances, self.expected_distances):
            self.assertAlmostEqual(resulting, expected)

    # def test_parallel_mapping(self):
    #     @merges_dicts
    #     def calc(opt):
    #         return opt['speed'] * opt['travel_time']
    #     pool = Pool(2)
    #     combos = product(self.speed, self.time)
    #     resulting_distances = pool.map(calc, combos)
    #     for resulting, expected in \
    #             zip(resulting_distances, self.expected_distances):
    #         self.assertAlmostEqual(resulting, expected)
    #     pool.close()


class TestOptionsDictTreeIteration(unittest.TestCase):

    def setUp(self):
        """
        Suppose I want to run a simulator on a set of 1D, 2D and 3D
        grids at different resolutions, but it is expensive to do this
        on multi-dimensional grids at higher resolutions.  I decide to
        iterate over the following combinations:

            dim.   res.
             1     10, 20, 40, 80
             2     10, 20, 40
             3     10, 20

        This should be possible using itertools' chain and product.  I
        will implement a dynamic entry at the root of the tree to
        calculate computation time.
        """
        def calc_cost(opt):
            return opt['res']**opt['dim']
        root = [OptionsDict.named(
            'sim', {'cost': calc_cost})]
        dims = OptionsDict.sequence('dim', [1, 2, 3],
                                    name_format='{}d')    
        res1d = OptionsDict.sequence('res', [10, 20, 40, 80])
        res2d = OptionsDict.sequence('res', [10, 20, 40])
        res3d = OptionsDict.sequence('res', [10, 20])
        branches = attach(dims, (res1d, res2d, res3d))
        self.tree = product(root, chain(branches))
        # self.pool = Pool(2)

    def check_names(self, resulting_names):
        "Helper for name_check tests."
        expected_names = [
            'sim_1d_10', 'sim_1d_20', 'sim_1d_40', 'sim_1d_80', 
            'sim_2d_10', 'sim_2d_20', 'sim_2d_40',
            'sim_3d_10', 'sim_3d_20']
        for result, expected in zip(resulting_names, expected_names):
            self.assertEqual(result, expected)

    def check_times(self, resulting_times):
        "Helper for lookup tests."
        expected_times = [
            10., 20., 40., 80.,
            100., 400., 1600.,
            1000., 8000.]
        for result, expected in zip(resulting_times, expected_times):
            self.assertAlmostEqual(result, expected)
        
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

    def test_serial_mapping_and_name_check(self):
        resulting_names = map(identify, self.tree)
        self.check_names(resulting_names)
            
    def test_serial_mapping_and_lookup(self):
        lookup = Lookup('cost')
        resulting_times = map(lookup, self.tree)
        self.check_times(resulting_times)
            
    # def test_parallel_mapping_and_name_check(self):
    #     resulting_names = self.pool.map(identify, self.tree)
    #     self.check_names(resulting_names)
            
    # def test_parallel_mapping_and_lookup(self):
    #     lookup = Lookup('cost')
    #     resulting_times = self.pool.map(lookup, self.tree)
    #     self.check_times(resulting_times)

            
if __name__ == '__main__':
    unittest.main()
        
