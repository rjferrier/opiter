"""
This is the client-facing layer of optree.  In the core
implementation layer, modules and classes are uncoupled for unit
testing purposes.  Here they are finally coupled together using
dependency injection.
"""

from dynamic_dict import DynamicDict
from callable_entry import CallableEntry
from factory import Option, OptionSequence, OptionCreationError, \
    OptionSequenceCreationError

