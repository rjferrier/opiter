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
        I create an OptionsDict array 'A' using three integers.  I
        store the second node and its location object.
        """
        seq = OptionsDict.array('A', [1, 2, 3])
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

    def test_get_location_by_array_key(self):
        """
        I should get the same location by passing the array key to
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


class TestOptionsDictWithSeveralLocations(unittest.TestCase):

    def setUp(self):
        """
        I create three OptionsDict arrays, 'A', 'B' and 'C', and
        store an element from each.  I update the OptionsDict
        corresponding to 'B' with the other two OptionsDicts.
        """
        A = OptionsDict.array('A', [1, 2, 3])
        B = OptionsDict.array('B', ['i', 'ii', 'iii'])
        C = OptionsDict.array('C', [0.6, 1.6])
        self.a2 = A[2]
        self.b1 = B[1]
        self.c0 = C[0]
        self.b1.update(c0)
        self.b1.update(a2)

    def test_get_other_location(self):
        """
        get_location('A') should return a Location from which we can
        recover the ID of the third element in A.
        """
        self.assertEqual(self.od.get_location('A').id())

    def test_get_default_location(self):
        """
        When I call get_location with no arguments, the result should
        be the same as that of get_location('B'), i.e. it should not
        have changed since B was updated.
        """
        self.assertEqual(self.od.get_location(),
                         self.od.get_location('B'))

        
class TestOptionsDictWithSeveralLocations(unittest.TestCase):

    def setUp(self):
        """
        I create three OptionsDict arrays, 'A', 'B' and 'C', and
        store the second element of B.  I update this OptionsDict
        with the first and third elements of C and A, respectively.
        """
        A = OptionsDict.array('A', [1, 2, 3])
        B = OptionsDict.array('B', ['i', 'ii', 'iii'])
        C = OptionsDict.array('C', [0.25, 0.5, 1.0])
        self.od = B[1]
        self.od.update(C[0])
        self.od.update(A[2])

    def test_repr(self):
        self.assertEqual(
            repr(self.od),
            "ii_0.25_3:{'A': 3, 'C': 0.25, 'B': 'ii'}@['B', 'C', 'A']")
        
    def test_get_other_location(self):
        """
        get_location('A') should return a Location from which we can
        recover the name of the third element in A.
        """
        self.assertEqual(self.od.get_location('A').str(), '3')

    def test_get_default_location(self):
        """
        When I call get_location with no arguments, the result should
        be the same as that of get_location('B'), i.e. it should not
        have changed since B was updated.
        """
        self.assertEqual(self.od.get_location(),
                         self.od.get_location('B'))

        
if __name__ == '__main__':
    unittest.main()
        
