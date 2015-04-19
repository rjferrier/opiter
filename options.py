from types import FunctionType, LambdaType
from string import Template
from copy import copy


# default settings
NAME_SEPARATOR = '_'


class OptionsDictException(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg

        
class OptionsDict(dict):
    """
    OptionsDict(entries={})
    OptionsDict.named(name, entries={})
    
    An OptionsDict inherits from a conventional dict, but it has a few
    enhancements:

    (1) Values can be runtime-dependent upon the state of other values
    in the dict.  Each of these special values is specified by a
    function** accepting a single dictionary argument (i.e. the
    OptionsDict itself).  The dictionary argument is used to look things
    up dynamically.  These functions may be listed in the entries
    argument if there are no other key-value pairs, in which case the
    functions' names become the keys.

    (2) An OptionsDict can have a name.  When an OptionsDict is
    updated using another OptionsDict, its name changes to reflect the
    new state.  Updating 'A' with 'B' produces 'A_B'.

    (3) An OptionsDict can expand strings as templates.

    (4) When the OptionsDict is created as part of a sequence, or is
    updated with such an OptionsDict, extra information is stored.
    See OptionsDict.sequence and the Location class.
    
    ** If using the multiprocessing module, it is important that
       dynamic entries are created using defs rather than lambdas.  It
       seems that lambdas cause pickling problems, and there is
       currently no way to protect against them.
    """

    # variable attributes
    name = ''
    locations = {}
    
    # settings
    name_separator = NAME_SEPARATOR
    
    def __init__(self, entries={}):
        # with just an entries argument, treat as a simple dict
        self.update(entries)

    @classmethod
    def named(Self, name, entries={}):
        # check name argument
        if not name:
            name = ''
        elif not isinstance(name, str):
            raise OptionsDictException(
                "name argument must be a string (or None).")
        # instantiate object and set the name
        obj = Self(entries)
        obj.name = name
        return obj

    @classmethod
    def sequence(Self, sequence_key, elements, common_entries={},
                 name_format='{}'):
        """
        OptionsDict.sequence(sequence_key, elements, 
                             common_entries={}, name_format='{}')

        Creates a list of OptionsDicts, converting the given elements
        if necessary.  That is, if a element is not already an
        OptionsDict, it is converted to a string which becomes the
        name of a new OptionsDict.  All dicts are initialised with
        common_entries if this argument is given.

        The string conversion is governed by name_format, which can
        either be a format string or a callable that takes the element
        value and returns a string.

        The sequence_key argument has two notable effects (assuming it
        is a non-empty string).  Firstly, for each element, the
        corresponding OptionsDict acquires the entry {sequence_key:
        element.name} if the element is already an OptionsDict, and
        {sequence_key: element} otherwise.  This is useful for
        associating a simple independent variable with a selection of
        values.

        Secondly, a Location object becomes registered and accessible
        through the get_location(sequence_key) method.  A Location
        provides information on where an OptionsDict is in relation to
        others in the sequence.  Conversely, it provides the names of
        other OptionsDicts based on their location.
        """

        optionsdict_list = []
        for el in elements:
            if isinstance(el, Self):
                # If the element is already an OptionsDict object,
                # make a copy.  This has the benefit of preventing
                # side effects if the element persists elsewhere.
                od = el.copy()
                # add a special entry using sequence_key
                od.update({sequence_key: str(el)})
            else:
                # instantiate a new OptionsDict with the string
                # represention of the element acting as its name, and
                # the original element stored under sequence_key
                try:
                    od = Self.named(name_format(el),
                                    {sequence_key: el})
                except TypeError:
                    try:
                        od = Self.named(name_format.format(el),
                                        {sequence_key: el})
                    except AttributeError:
                        raise OptionsDictException(
                            "name_formatter must be a callable "+\
                            "or a format string.")
            # add entries
            od.update(common_entries)
            # append to the list
            optionsdict_list.append(od)
        return optionsdict_list

    
    def __repr__(self):
        return self.name + ':' + dict.__repr__(self)

    def __str__(self):
        return self.name

    def __iter__(self):
        yield self
    
    def __getitem__(self, key):
        value = dict.__getitem__(self, key)
        # recurse until the return value is no longer a function
        if isinstance(value, FunctionType):
            # dynamic entry
            return value(self)
        else:
            # normal entry
            return value
        
    def __eq__(self, other):
        eq_names = str(self) == str(other)
        eq_locations = self.locations == other.locations
        eq_dicts = dict.__eq__(self, other)
        return eq_names and eq_dicts

    def __ne__(self, other):
        return not self==other

    def copy(self):
        obj = OptionsDict(dict.copy(self))
        obj.name = self.name
        obj.locations = self.locations
        return obj
        
    def update(self, entries):
        if isinstance(entries, dict):
            # argument is a dictionary, so updating is straightforward
            self._update_from_dict(entries)
        else:
            # argument is presumably a list of dynamic entries
            self._update_from_dynamic_entries(entries)

    def _update_from_dict(self, other):
        # update OptionsDict attributes
        if isinstance(other, OptionsDict):
            names = (str(self), str(other))
            if all(names):
                self.name = self.name_separator.join(names)
            else:
                self.name = ''.join(names)
            # # tk
            # self.locations.update(other.locations)
        # now pass to superclass
        dict.update(self, other)

    def _update_from_dynamic_entries(self, functions):
        err = OptionsDictException("""
entries must be a dict or a sequence of dynamic entries (i.e.
functions).""")
        try:
            for func in functions:
                if not isinstance(func, FunctionType):
                    raise err
                varnames = func.func_code.co_varnames
                self[func.__name__] = func
        except TypeError:
            raise err
                
    def expand_template(self, buffer_string, loops=1):
        """In buffer_string, replaces all substrings prefixed '$' with
        corresponding values from the dictionary."""
        for i in range(loops):
            buffer_string = Template(buffer_string)
            buffer_string = buffer_string.safe_substitute(self)
        return buffer_string


class Location:

    def __init__(self, names, index):
        self.names = names
        self.index = index

    def __str__(self):
        return self.str()

    def str(self, absolute=None, relative=None):
        """
        Returns the name of the node in question or, if arguments are
        given, one of its siblings.  The optional arguments correspond
        to absolute and relative indices, respectively.  In accordance
        with Python indexing rules, a negative absolute index returns
        a node from the end of the sequence.  To avoid confusion, this
        does not apply when a relative index is given.
        """
        if absolute is None:
            index = self.index
        else:
            index = absolute
        if relative is not None:
            index += relative
            if index < 0:
                raise IndexError("list index out of range")
        return self.names[index]
    
        
class CallableEntry:
    """
    CallableEntry(function)

    Because the OptionsDict works by evaluating all function objects
    recursively, it is not able to return other functions specified by
    the client unless these are wrapped as callable objects.  This
    class provides such a wrapper.
    """
    def __init__(self, function):
        self.function = function
        
    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)

