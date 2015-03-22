from types import FunctionType 

class DynamicDict(dict):
    """
    A DynamicDict works the same way as a conventional dict, but it
    allows values to be runtime-dependent upon the state of other
    values in the dict.  Each of these special values is specified as
    a function accepting a single dictionary argument.  The dictionary
    is used within the function body to look things up dynamically.

    Because the DynamicDict works by converting all function objects
    recursively, it is not able to return other functions specified by
    the client unless these are wrapped as callable objects.
    """
    def __getitem__(self, key):
        value = dict.__getitem__(self, key)
        # recurse until the return value is no longer a function
        if isinstance(value, FunctionType):
            return value(self)
        else:
            return value
            
class CallableEntry:
    """Can be used in a DynamicDict to wrap a function."""
    def __init__(self, function):
        self.function = function
    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)
