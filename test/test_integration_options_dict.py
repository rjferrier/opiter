import sys
sys.path.append('..')

import unittest
from options import OptionsDict, CallableEntry, Location, \
    OptionsDictException


class TestCallableEntry(unittest.TestCase):
    
    def test_callable_entry(self):
        """
        I create an OptionsDict with a callable entry stored under
        'my_func'.  This should not evaluate like a dynamic entry but
        instead remain intact and work as intended.
        """
        od = OptionsDict({
            'my_func': CallableEntry(lambda a, b=1: a + b)})
        self.assertIsInstance(od['my_func'], CallableEntry)
        self.assertEqual(od['my_func'](1), 2)
        self.assertEqual(od['my_func'](1, 2), 3)

        
    
class TestOptionsDictWithLocation(unittest.TestCase):

    def setUp(self):
        """
        I create an OptionsDict sequence 'A' using three integers.  I
        store the second node and its location object.
        """
        seq = OptionsDict.sequence('A', ['i', 'ii', 'iii'])
        self.od = seq[1]
        self.loc = self.od.get_location()

    def test_location_type(self):
        """
        The stored location should be an instance of Location.
        """
        self.assertIsInstance(self.loc, Location)

    def test_str(self):
        """
        The string representation of the location should be the same as
        that of the OptionsDict.
        """
        self.assertEqual(str(self.loc), str(self.od))

    def test_get_location_by_sequence_key(self):
        """
        I should get the same location by passing the sequence key to
        the OptionDict's get_location method.
        """
        self.assertEqual(self.loc, self.od.get_location('A'))

    def test_copy(self):
        other = self.od.copy()
        # test for equivalence and non-identity
        self.assertEqual(other, self.od)
        self.assertFalse(other is self.od)

    def test_nonexistent_location(self):
        """
        Conversely, passing anything else should return None.
        """
        self.assertIsNone(self.od.get_location('B'))

        
if __name__ == '__main__':
    unittest.main()
        
