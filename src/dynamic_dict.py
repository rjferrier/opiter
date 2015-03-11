
class DynamicDict(dict):
    """This works the same way as a conventional dict, but it allows
    values to be runtime-dependent upon the state of others.  Each of
    these values is a DynamicEntry."""
    def __getitem__(self, key):
        value = dict.__getitem__(self, key)
        # recurse until the return value is no longer a lambda function
        if isinstance(value, DynamicEntry):
            return value(self)
        else:
            return value

class DynamicEntry:
    def __init__(self, function):
        """Returns a value which is runtime-dependendent on other values
        in a dictionary.  The object is initialised with a lambda
        function accepting a single dictionary argument.  The dictionary
        may be used within the function body to look up stuff."""
        self.function = function
    def __call__(self, dictionary):
        return self.function(dictionary)

        
