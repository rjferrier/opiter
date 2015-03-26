import sys
sys.path.append('..')

import unittest
from optionsdict import create_sequence, OptionsDict, \
    OptionsDictException


class TestOptionsDictSequence(unittest.TestCase):

    def setUp(self):
        """
        I create an OptionsDict sequence from a list of
        different-typed values, one of which is already an
        OptionsDict.
        """
        od = OptionsDict('some_dict', {'foo': 'bar'})
        self.values = ['A', od, 2, 3.14]
        self.seq = create_sequence('random_thing', self.values)

    def test_element_types(self):
        """
        Each element in the sequence should be an OptionsDict.
        """
        for el in self.seq:
            self.assertIsInstance(el, OptionsDict)

    def test_element_names(self):
        """
        The name of each element, given by its string representation,
        should be identical to the string representation of the
        corresponding initial value.
        """
        for el, v in zip(self.seq, self.values):
            self.assertEqual(str(el), str(v))

    def test_element_dicts(self):
        """
        While all the elements should be dictionaries, only the
        preexisting OptionsDict should have the {'foo': 'bar'} entry.
        """
        for i, el in enumerate(self.seq):
            lookup = lambda: el['foo']
            if i==1:
                self.assertEqual(lookup(), 'bar')
            else:
                self.assertRaises(KeyError, lookup)

    def test_lookup_sequence_key(self):
        """
        When the sequence key is looked up in each element, the
        element should return the corresponding initial value.  The
        initial value representation of the preexisting OptionsDict is
        simply its name.
        """
        for i, el in enumerate(self.seq):
            result = el['random_thing']
            if i==1:
                self.assertEqual(result, 'some_dict')
            elif i==3:
                # careful with floats
                self.assertAlmostEqual(result, 3.14)
            else:
                self.assertEqual(result, self.values[i])
        
        
if __name__ == '__main__':
    unittest.main()
        
