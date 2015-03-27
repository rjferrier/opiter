import sys
sys.path.append('..')

import unittest
from optionsdict import create_sequence, OptionsDict
from optionsdict_itertools import product, chain, flatten, multizip, \
    combine_elements, create_lookup

class TestOptionsDictTwoSequenceIteration(unittest.TestCase):
    
    def setUp(self):
        """
        I create two OptionsDict sequences, one for 'speed' and one
        for 'travel time'.
        """
        self.speed = create_sequence('speed', [30, 40, 60])
        self.time  = create_sequence('travel_time', [0.5, 1])
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
            opt = sum(combo)
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
        calc = (OptionsDict('calculator',
                            {'distance': lambda self: \
                                 self['speed'] * self['travel_time']}),)
        combos = product(calc, self.speed, self.time)
        for combo, expected in zip(combos, self.expected_distances):
            opt = sum(combo)
            self.assertAlmostEqual(opt['distance'], expected)

    def test_combination_mapping(self):
        """
        I should be able create combinations of speed and travel time
        and calculate the correct distances using a map.  I will use
        the combine_elements decorator so that my distance calculator
        only has to deal with one dictionary.
        """
        @combine_elements
        def calc(opt):
            return opt['speed'] * opt['travel_time']
        combos = product(self.speed, self.time)
        resulting_distances = map(calc, combos)
        for resulting, expected in \
                zip(resulting_distances, self.expected_distances):
            self.assertAlmostEqual(resulting, expected)


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
        root = (OptionsDict(None, 
                {'computation_time': \
                     lambda self: self['res']**self['dim']}),)
        dims = create_sequence('dim', [1, 2, 3], name_format='{}d')        
        res1 = create_sequence('res', [10, 20, 40, 80])
        res2 = create_sequence('res', [10, 20, 40])
        res3 = create_sequence('res', [10, 20])
        branches = multizip(dims, (res1, res2, res3))
        self.tree = product(root, chain(branches))
        
    def test_manual_iteration_and_name_check(self):
        """I should be able to iterate over the tree and find that the
        resulting OptionsDicts are named according to expected
        position in the tree."""
        expected_names = ['1d_10', '1d_20', '1d_40', '1d_80', 
                          '2d_10', '2d_20', '2d_40',
                          '3d_10', '3d_20']
        for combo, name in zip(self.tree, expected_names):
            opt = sum(flatten(combo))
            self.assertEqual(str(opt), name)
            
    def test_combination_mapping_and_lookup(self):
        """I should be able to get the computation time using a map
        and a function that looks up the 'computation_time' entry."""
        expected_times = [10., 20., 40., 80.,
                          100., 400., 1600.,
                          1000., 8000.]
        lookup = create_lookup('computation_time')
        resulting_times = map(lookup, self.tree)
        for result, expected in zip(resulting_times, expected_times):
            self.assertAlmostEqual(result, expected)

            
if __name__ == '__main__':
    unittest.main()
        
