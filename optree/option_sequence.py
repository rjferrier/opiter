from base import IOption, OptionException


class _OptionSequence:
    """
    _OptionSequence(name, options)

    Defines an sequence of _Options.  The options argument may be
    _Options or the names of _Options.
    """
    _name = None
    _options = None
    
    def __init__(self, name, options):
        self._name = name
        self._options = options
    
    def __repr__(self):
        return self._name

    def __iter__(self):
        for opt in self._options:
            yield opt

    def __getitem__(self, key):
        return {}[key]

    def __setitem__(self, key, value):
        pass
