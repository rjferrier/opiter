from base import IOption, OptionException


class Option(IOption):

    _name = None
    _dict = {}
    # the parent attribute will be set directly by OptionSequence.
    _parent = None

    def __init__(self, name, dictionary={}):
        self._name = name
        self._dict = dictionary
    
    def __str__(self):
        return self._name
    
    def __repr__(self):
        """
        Returns a unique ID based on the object's address in the parent
        structure.  If there is no parent, just return the object's
        name.
        """
        if self._parent:
            return repr(self._parent)+'.'+self._name
        else:
            return self._name
    
    def __getitem__(self, key):
        return self._dict[key]

    def __setitem__(self, key, value):
        self._dict[key] = value


class OptionSequence:
    """
    OptionSequence(name, options)

    Defines an sequence of Options.  The options argument may be
    Options or the names of Options.
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
