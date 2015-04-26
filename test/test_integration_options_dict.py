import sys
sys.path.append('..')

import unittest
from options import OptionsDict, CallableEntry, Context, \
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

        
class TestOptionsDictWithContext(unittest.TestCase):

    def setUp(self):
        """
        I create an OptionsDict array 'A' using three integers.  I
        store the second node and its context object.
        """
        seq = OptionsDict.array('A', [1, 2, 3])
        self.od = seq[1]
        self.ct = self.od.get_context()

    def test_context_type(self):
        """
        The stored context should be an instance of Context.
        """
        self.assertIsInstance(self.ct, Context)

    def test_str(self):
        """
        The string representation of the context should be the same as
        that of the OptionsDict.
        """
        self.assertEqual(str(self.ct), str(self.od))


        
if __name__ == '__main__':
    unittest.main()
        
