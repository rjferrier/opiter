"""
This is the base layer of optree, containing an exception class
and interface classes.  Although the interfaces are not really needed
by the concrete classes owing to Python's soft typing, they are
useful for creating mocks in unit tests.
"""

class OptionException(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg

class IOption:
    def __str__(self):
        pass
        
    def __repr__(self):
        pass
        
    def __getitem__(self, key):
        pass

    def __setitem__(self, key, value):
        pass

        
