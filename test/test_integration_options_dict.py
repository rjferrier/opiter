import sys
sys.path.append('..')

import unittest
from options import OptionsDict, CallableEntry, ArrayNodeInfo, \
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

        
    
class TestOptionsDictWithArrayNodeInfo(unittest.TestCase):

    def setUp(self):
        """
        I create an OptionsDict array 'A' using three integers.  I
        store the second node and its node_info object.
        """
        seq = OptionsDict.array('A', [1, 2, 3])
        self.od = seq[1]
        self.node_info = self.od.get_node_info()

    def test_node_info_type(self):
        """
        The stored node info should be an instance of ArrayNodeInfo.
        """
        self.assertIsInstance(self.node_info, ArrayNodeInfo)

    def test_str(self):
        """
        The string representation of the node info should be the same as
        that of the OptionsDict.
        """
        self.assertEqual(str(self.node_info), str(self.od))


        
if __name__ == '__main__':
    unittest.main()
        
