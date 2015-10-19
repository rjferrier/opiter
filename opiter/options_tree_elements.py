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


class OptionsTreeElementException(OptionsBaseException):
    pass


class OptionsTreeElement:
    """
    Abstract class to be inherited by OptionsArray and OptionsNode.
    This inheritance hierarchy is similar to the Composite pattern in
    that it can be used to build an arbitrary tree.  However,
    OptionsNode can act as a branch as well as a leaf, so it shares
    some of the parent-child functionality.
    """
    def __init__(self, list_hooks=[], dict_hooks=[], item_hooks=[]):
        self.list_hooks = list_hooks
        self.dict_hooks = dict_hooks
        self.item_hooks = item_hooks

    @classmethod
    def another(Class, *args, **kwargs):
        return Class(*args, **kwargs)
        
    def apply_hooks(self, options_dicts):
        """
        Loops over options_dicts, applying the functions in
        self.list_hooks, self.dict_hooks and self.item_hooks.  In the
        latter case the dictionary items are looped over and each item
        hook is applied within an inner loop.
        """
        for func in self.list_hooks:
            func(options_dicts)
        for od in options_dicts:
            for func in self.dict_hooks:
                func(od)
            # could import the Sequence functor here, but writing a
            # closure is trivial and incurs no coupling
            def run_item_hooks(target_dict, key):
                for func in self.item_hooks:
                    func(target_dict, key)
            od.transform_items(run_item_hooks, recursive=True)

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

