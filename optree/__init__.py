"""
This is the client-facing layer of optree.  In the core
implementation layer, modules and classes are uncoupled for unit
testing purposes.  Here they are finally coupled together using
dependency injection.
"""

from dynamic_dict import DynamicDict, CallableEntry
from factory import create_option, create_option_sequence, \
    OptionCreationError
