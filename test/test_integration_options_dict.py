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

    def test_get_context_by_array_name(self):
        """
        I should get the same context by passing the array key to
        the OptionDict's get_context method.
        """
        self.assertEqual(self.ct, self.od.get_context('A'))

    def test_copy(self):
        other = self.od.copy()
        # test for equivalence and non-identity
        self.assertEqual(other, self.od)
        self.assertFalse(other is self.od)

    def test_nonexistent_context(self):
        """
        Conversely, passing anything else should return None.
        """
        self.assertIsNone(self.od.get_context('B'))


class TestOptionsDictWithSeveralContexts(unittest.TestCase):

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

    def test_get_other_context(self):
        """
        get_context('A') should return a Context from which we can
        recover the ID of the third element in A.
        """
        self.assertEqual(self.od.get_context('A').id())

    def test_get_default_context(self):
        """
        When I call get_context with no arguments, the result should
        be the same as that of get_context('B'), i.e. it should not
        have changed since B was updated.
        """
        self.assertEqual(self.od.get_context(),
                         self.od.get_context('B'))

        
class TestOptionsDictWithSeveralContexts(unittest.TestCase):

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
        
    def test_get_other_context(self):
        """
        get_context('A') should return a Context from which we can
        recover the name of the third element in A.
        """
        self.assertEqual(self.od.get_context('A').str(), '3')

    def test_get_default_context(self):
        """
        When I call get_context with no arguments, the result should
        be the same as that of get_context('B'), i.e. it should not
        have changed since B was updated.
        """
        self.assertEqual(self.od.get_context(),
                         self.od.get_context('B'))

        
if __name__ == '__main__':
    unittest.main()
        
