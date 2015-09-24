from base import OptionsBaseException
from operator import mul
from copy import deepcopy


def product(iterable):
    """
    Works like the sum function, but is multiplicative instead of
    additive.  Might be useful for factorial design of experiments.
    """
    return reduce(mul, iterable, 1)


def nonmutable(method):
    """
    Decorator that calls method but provides a new object instead of
    modifying the current one.  This means the call can be inlined
    neatly without mutating the operands.
    """
    def decorator(self, other):
        result = deepcopy(self)
        method(result, other)
        return result
    return decorator


class Position:
    """
    Records position in a collection.
    """
    def __init__(self, index, collection_size):
        self.index = index
        self.collection_size = collection_size

    def is_at(self, index):
        """
        Checks that the position corresponds to the given index, which if
        negative is relative to the end of the collection.
        """
        return self.index == index or \
            self.index == index + self.collection_size
    
    def is_first(self):
        return self.is_at(0)
        
    def is_last(self):
        return self.is_at(-1)
        
    def __eq__(self, other):
        result = isinstance(other, Position)
        if result:
            result *= self.index == other.index
            result *= self.collection_size == other.collection_size
        return result

    
class NodeInfo:
    """
    Abstract class for describing contextual information about a node.
    The concrete methods herein are special cases which defer to the
    more general subclass methods.
    """
    def __init__(self, index, collection_size):
        self.position = self.create_position(index, collection_size)
        
    def create_position(self, node_index, array_length):
        """
        Overrideable factory method.
        """
        return Position(node_index, array_length)
        
    def belongs_to_any(self, collection_names):
        """
        Returns True if the node in question is associated with any of
        collection_names.
        """
        for cn in collection_names:
            if self.belongs_to(cn):
                return cn
        return False

    def _create_index(self, default, absolute, relative):
        # Helper to subclass get_string() methods
        if absolute is None:
            index = default
        else:
            index = absolute
        if relative is not None:
            index += relative
            if index < 0:
                raise IndexError("list index out of range")
        return index
        
    def __str__(self):
        return self.get_string()
        

class OptionsTreeElement:
    """
    Abstract class to be inherited by OptionsArray and OptionsNode.
    This inheritance hierarchy is similar to the Composite pattern in
    that it can be used to build an arbitrary tree.  However,
    OptionsNode can act as a branch as well as a leaf, so it shares
    some of the parent-child functionality.
    """

    def __ne__(self, other):
        return not self == other

    @nonmutable
    def __mul__(self, other):
        self.multiply_attach(other)

    @nonmutable
    def __rmul__(self, other):
        # this conditional stops us trying to multiply with 1 during a
        # product() call
        if isinstance(other, OptionsTreeElement):
            self.multiply_attach(other)

    @nonmutable
    def __add__(self, other):
        self.attach(other)

    @nonmutable
    def __radd__(self, other):
        # this conditional stops us trying to add to 0 during a
        # product() call
        if isinstance(other, OptionsTreeElement):
            self.attach(other)

    def __imul__(self, other):
        self.multiply_attach(other)
        return self

    def __iadd__(self, other):
        self.attach(other)
        return self

