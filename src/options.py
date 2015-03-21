
class OptionError(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg

class _Option:
    """
    _Option(name, dictionary={})

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

    # this attribute will be set directly by _OptionSequence.
    _parent = None

    def __init__(self, name, dictionary={}):
        if not isinstance(name, str):
            raise OptionError("name argument must be a string.")
        if not isinstance(dictionary, dict):
            raise OptionError("dictionary argument must be a dict.")
        self._name = name
        self._dict = dictionary
    
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

        
class _OptionSequence:
    """
    _OptionSequence(name, options)

    Defines an sequence of _Options.  The options argument may be
    _Options or the names of _Options.
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
    
    def __repr__(self):
        return self._name

    def __iter__(self):
        for opt in self._options:
            yield opt

    def __getitem__(self, key):
        return {}[key]

    def __setitem__(self, key, value):
        pass
