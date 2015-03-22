"""
In the core modules, classes are uncoupled for unit testing
purposes.  Here they are finally coupled together using dependency
injection.
"""

from dynamic_dict import DynamicDict
from base import OptionException
from optree.options import Option, OptionSequence


class OptionCreationError(OptionException):
    def __init__(self, msg):
        OptionException.__init__(self, msg)

        
def create_option(name, dictionary={}):
    """
    create_option(name, dictionary={})

    Defines one possible state out of several in an OptionSequence.
    Upon instantiation, the Option is given a name.  Additionally
    there may be dependent variables defined in a dict or a
    DynamicDict.

    When an Option is used to instantiate an OptionSequence, it
    acquires a reference to the sequence as its parent.  The parent's
    name can then be looked up in the dictionary to retrieve the name
    of the Option at hand.  Thus the parent-child relationship
    between OptionSequence and Option may also be considered a
    key-value relationship.
    """
    if not isinstance(name, str):
        raise OptionCreationError(
            "name argument must be a string.")
    if not isinstance(dictionary, dict):
        raise OptionCreationError(
            "dictionary argument must be a dict.")
    return Option(name, DynamicDict(dictionary))

        
def create_option_sequence(name, options):
    """
    OptionSequence(name, options)

    Defines an sequence of Options.  The options argument may be
    Options or the names of Options.
    """
    if not isinstance(name, str):
        raise OptionCreationError(
            "name argument must be a string.")
    options = []
    for opt in options:
        # instantiate a new Option.  If opt is a string, this is
        # needed anyway.  If opt is already an Option object, a copy
        # will be made.  This has the benefit of preventing side
        # effects if opt persists elsewhere.
        opt = Option(opt)
        opt._parent = self
        self.options.append(opt)
    return OptionSequence(name, options)
