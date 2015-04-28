import sys
sys.path.append('..')

import unittest
from options import OptionsDict, CallableEntry, Position, \
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

        
    
class TestOptionsDictWithPosition(unittest.TestCase):

    def setUp(self):
        """
        I create an OptionsDict array 'A' using three integers.  I
        store the second node and its position object.
        """
        seq = OptionsDict.array('A', [1, 2, 3])
        self.od = seq[1]
        self.pos = self.od.get_position()

    def test_position_type(self):
        """
        The stored position should be an instance of Position.
        """
        self.assertIsInstance(self.pos, Position)

    def test_str(self):
        """
        The string representation of the position should be the same as
        that of the OptionsDict.
        """
        self.assertEqual(str(self.pos), str(self.od))


        
if __name__ == '__main__':
    unittest.main()
        
