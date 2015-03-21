"""
In the core modules, classes are uncoupled for unit testing
purposes.  Here they are finally coupled together using dependency
injection.
"""

from dynamic_dict import DynamicDict
from base import OptionException
from option import _Option
from option_sequence import _OptionSequence

class OptionCreationError(OptionException):
    def __init__(self, msg):
        OptionException.__init__(self, msg)
        
class Option(_Option):
    """
    Option(name, dictionary={})

    Defines one possible state out of several in an OptionSequence.
    Upon instantiation, the Option is given a name.  Additionally
    there may be dependent variables defined in a dict or a
    DynamicDict.

    When an _Option is used to instantiate an _OptionSequence, it
    acquires a reference to the sequence as its parent.  The parent's
    name can then be looked up in the dictionary to retrieve the name
    of the _Option at hand.  Thus the parent-child relationship
    between _OptionSequence and _Option may also be considered a
    key-value relationship.
    """

    def __init__(self, name, dictionary={}):
        if not isinstance(name, str):
            raise OptionCreationError(
                "name argument must be a string.")
        if not isinstance(dictionary, dict):
            raise OptionCreationError(
                "dictionary argument must be a dict.")
        _Option.__init__(self, name, DynamicDict(dictionary))


class OptionSequenceCreationError(OptionException):
    def __init__(self, msg):
        OptionException.__init__(self, msg)
        
class OptionSequence(_OptionSequence):
    """
    OptionSequence(name, options)

    Defines an sequence of _Options.  The options argument may be
    Options or the names of Options.
    """

    def __init__(self, name, options):
        self._name = name
        self._options = []
        for opt in options:
            # instantiate a new _Option.  If opt is a string, this is
            # needed anyway.  If opt is already an _Option object, a
            # copy will be made.  This has the benefit of preventing
            # side effects if opt persists elsewhere.
            opt = _Option(opt)
            opt._parent = self
            self._options.append(opt)
