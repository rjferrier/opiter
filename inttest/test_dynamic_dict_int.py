import sys
sys.path.append('..')

import unittest
from optree.dynamic_dict import DynamicDict, CallableEntry


class TestDynamicDictIntegration(unittest.TestCase):

    def test_custom_function_entry(self):
        """
        I create a DynamicDict with an entry returning a function.  As
        discussed in the dynamic_dict module, I need to protect this
        function using a wrapper class such as CallableEntry.  I
        should be able to retrieve the function as I would any other
        entry, and it should behave as expected.
        """
        def my_function(a, b, scale_b=1.):
            return a + b*scale_b
        dynamic_dict = DynamicDict({
            'my_function': CallableEntry(my_function)})
        # now test 
        fun = dynamic_dict['my_function']
        self.assertAlmostEqual(fun(2., 3.), 5.)
        self.assertAlmostEqual(fun(2., 3., scale_b=2.), 8.)

        
if __name__ == '__main__':
    unittest.main()
        
