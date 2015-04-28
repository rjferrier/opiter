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

    def test_get_position_by_array_name(self):
        """
        I should get the same position by passing the array key to
        the OptionDict's get_position method.
        """
        self.assertEqual(self.pos, self.od.get_position('A'))

    def test_copy(self):
        other = self.od.copy()
        # test for equivalence and non-identity
        self.assertEqual(other, self.od)
        self.assertFalse(other is self.od)

    def test_nonexistent_position(self):
        """
        Conversely, passing anything else should return None.
        """
        self.assertIsNone(self.od.get_position('B'))


class TestOptionsDictWithSeveralPositions(unittest.TestCase):

    def setUp(self):
        """
        I create three OptionsDict arrays, 'A', 'B' and 'C', and store
        the second element of B.  I update this OptionsDict with the
        first and third elements of C and A, respectively.  To
        complicate its name, I'll also update it with an OptionsDict
        that is not part of an array.
        """
        A = OptionsDict.array('A', [1, 2, 3])
        B = OptionsDict.array('B', ['i', 'ii', 'iii'])
        C = OptionsDict.array('C', [0.25, 0.5, 1.0])
        d = OptionsDict.named('orphan', {})
        self.od = B[1]
        self.od.update(C[0])
        self.od.update(d)
        self.od.update(A[2])

    def test_repr(self):
        """
        repr() should return all details about the OptionsDict and its
        position components.
        """
        self.assertEqual(
            repr(self.od),
            "ii_0.25_orphan_3:{'A': 3, 'C': 0.25, 'B': 'ii'}"+\
            "@['B', 'C', 'A']")

    def test_get_default_position(self):
        """
        When I call get_position with no arguments, the result should
        be the same as that of get_position('B'), i.e. it should not
        have changed since B was updated.
        """
        self.assertEqual(self.od.get_position(),
                         self.od.get_position('B'))

    def test_get_other_position(self):
        """
        get_position('A') should return a Position from which we can
        recover the name of the third element in A.
        """
        self.assertEqual(self.od.get_position('A').str(), '3')

    def test_copy(self):
        other = self.od.copy()
        # test for equivalence and non-identity
        self.assertEqual(other, self.od)
        self.assertFalse(other is self.od)
        # test that positions have been copied and not simply linked
        E = OptionsDict.array('E', ['foo', 'bar'])
        other.update(E[0])
        self.assertIsNone(self.od.get_position('E'))

    def test_str_from_array_names(self):
        """
        I should be able to get a subset of the name of the merged
        OptionsDict by passing array names to its str() method.  The
        ordering of the resulting substrings should be insensitive to
        the order in which I give the array names.
        """
        self.assertEqual(self.od.str('A'), '3')
        self.assertEqual(self.od.str(['C', 'A']), '0.25_3')
        self.assertEqual(self.od.str(['A', 'C']), '0.25_3')

    def test_str_with_exclusions(self):
        """
        I should be able to exclude substrings from the name of the
        merged OptionsDict by passing array names via the 'exclude'
        argument of its str() method.  The ordering of the resulting
        substrings should be insensitive to the order in which I give
        the array names.
        """
        self.assertEqual(self.od.str(exclude='C'), 'ii_orphan_3')
        self.assertEqual(self.od.str(exclude=['C', 'B']), 'orphan_3')

    def test_str_from_array_names_with_exclusions(self):
        """
        I should be able to use the 'only' and 'exclude' arguments
        together, although the latter will override the former.
        Having an array name that features in the latter but not the
        former should do nothing.
        """
        self.assertEqual(self.od.str(['A', 'C'], exclude='A'), '0.25')
        self.assertEqual(self.od.str('C', exclude='A'), '0.25')
        self.assertEqual(self.od.str('A', exclude=['A', 'C']), '')

    def test_str_key_error(self):
        """
        I expect a KeyError will result when passing str() array names
        that haven't been registered yet.
        """
        self.assertRaises(KeyError, lambda: self.od.str(['D']))
        self.assertRaises(KeyError, lambda: self.od.str(exclude='E'))

        
if __name__ == '__main__':
    unittest.main()
        
