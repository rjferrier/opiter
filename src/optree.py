"""
This is the client-facing layer of parajob.  In the core
implementation layer, modules and classes are uncoupled for unit
testing purposes.  Here they are finally coupled together using
dependency injection.
"""

from dynamic_dict import DynamicDict
from options import _Option

class Option(_Option):
    def __init__(self, name, dictionary={}):
        _Option.__init__(self, name, DynamicDict(dictionary))

        
