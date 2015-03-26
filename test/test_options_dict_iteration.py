import sys
sys.path.append('..')

import unittest
from optionsdict import create_sequence, combine_elements, OptionsDict

from itertools import imap, product


class TestOptionsDictIteration(unittest.TestCase):
    
    def setUp(self):
        """
        I create two OptionsDict sequences, one for 'speed' and one
        for 'travel time'.
        """
        self.speed = create_sequence('speed', [30, 40, 60])
        self.time  = create_sequence('travel_time', [0.5, 1])
        self.expected_distances = [15, 30, 20, 40, 30, 60]

    def test_two_sequence_iteration(self):
        """
        I should be able to iterate over all combinations of speed and
        travel time and calculate the correct distance for each
        combination.
        """
        combos = product(self.speed, self.time)
        for c, expected in zip(combos, self.expected_distances):
            # I can combine the two dictionaries for convenience
            opt = sum(c)
            resulting_distance = opt['speed'] * opt['travel_time']
            self.assertAlmostEqual(resulting_distance, expected)

    def test_two_sequence_combination_mapping(self):
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
            
    def test_three_sequence_iteration_with_dynamic_entry(self):
        """
        Instead of calculating the distance myself, I might include
        another OptionsDict which does the work via a dynamic entry.
        I will need to wrap this object in a sequence before passing
        to itertools.product, otherwise the object will return an
        iterator to its dictionary entries.
        """
        calc = (OptionsDict('calculator',
                            {'distance': lambda self: \
                                 self['speed'] * self['travel_time']}),)
        combos = product(calc, self.speed, self.time)
        for c, expected in zip(combos, self.expected_distances):
            opt = sum(c)
            self.assertAlmostEqual(opt['distance'], expected)
    

if __name__ == '__main__':
    unittest.main()
        
