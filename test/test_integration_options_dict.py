import sys
sys.path.append('..')

import unittest
from options import OptionsDict, CallableEntry


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

    
# class TestGetLocation(unittest.TestCase):

#     def setUp(self):
#         """
#         I create an OptionsDict sequence 'A' using three integers.  I
#         store the second node and its location object.
#         """
#         seq = OptionsDict.sequence('A', ['i', 'ii', 'iii'])
#         self.od = seq[1]
#         self.loc = self.od.get_location()

#     def test_location_type(self):
#         """
#         The stored location should be an instance of Location.
#         """
#         self.assertIsInstance(self.loc, Location)

#     def test_get_location_by_sequence_key(self):
#         """
#         I should get the same location by passing the sequence key to
#         the OptionDict's get_location method.
#         """
#         self.assertEqual(self.loc, self.od.get_location('A'))

#     def test_nonexistent_location(self):
#         """
#         Conversely, passing anything else should raise an error.
#         """
#         self.assertRaises(OptionsDictException,
#                           lambda: self.od.get_location('B'))

        
if __name__ == '__main__':
    unittest.main()
        
