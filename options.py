from types import FunctionType
from string import Template
from copy import copy


# default settings
name_separator = '_'
template_expansion_max_loops = 5


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
    function accepting a single dictionary argument (i.e. the
    OptionsDict itself).  The dictionary argument is used to look
    things up dynamically.

    (2) An OptionsDict can have a name.  When an OptionsDict is
    updated using another OptionsDict, its name changes to reflect the
    new state.  Updating 'A' with 'B' produces 'A_B'.

    (3) An OptionsDict can expand strings as templates.
    """

    name = ''
    name_separator = name_separator
    template_expansion_max_loops = template_expansion_max_loops
    
    def __init__(self, entries={}, name=None):
        # check argument types
        if not name:
            name = ''
        elif not isinstance(name, str):
                raise OptionsDictException(
                    "name argument must be a string (or None).")
        if not isinstance(entries, dict):
            raise OptionsDictException(
                    "entries argument must be a dictionary.")
        # store name, initialise superclass
        self.name = name
        dict.__init__(self, entries)

    @classmethod
    def named(Self, name, entries={}):
        return Self(entries, name)

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
        eq_names = str(self)==str(other)
        eq_dicts = dict.__eq__(self, other)
        return eq_names and eq_dicts

    def __ne__(self, other):
        return not self==other

    def update(self, other):
        if isinstance(other, OptionsDict):
            # modify name
            names = (str(self), str(other))
            if all(names):
                self.name = name_separator.join(names)
            else:
                self.name = ''.join(names)
        # pass to superclass
        dict.update(self, other)

    def expand_template(self, buffer_string, 
                        max_loops=template_expansion_max_loops):
        """In buffer_string, replaces all substrings prefixed '$' with
        corresponding values from the dictionary."""
        n = 0
        while '$' in buffer_string and n < max_loops:
            buffer_string = Template(buffer_string)
            buffer_string = buffer_string.safe_substitute(self)
            n += 1
        return buffer_string

        
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



def create_node(name, entries={}):
    """
    create_node(name, entries={})
    
    Wraps an OptionsDict to return a one-element list.
    """
    return [OptionsDict.named(name, entries)]

    
def create_sequence(sequence_key, elements, common_entries={}, 
                    name_format='{}'):
    """
    create_sequence(sequence_key, elements, common_entries={},
                    name_format='{}',)

    Creates a list of OptionsDicts, converting the given elements if
    necessary.  That is, if a element is not already an OptionsDict,
    it is converted to a string which becomes the name of a new
    OptionsDict.  All dicts are initialised with common_entries if
    this argument is given.

    The string conversion is governed by name_format, which can either
    be a format string or a callable that takes the element value and
    returns a string.

    An important feature is that for each element, the corresponding
    OptionsDict acquires the entry {sequence_key: element.name} if the
    element is already OptionsDict, and {sequence_key: element}
    otherwise.
    """
    optionsdict_list = []
    for el in elements:
        if isinstance(el, OptionsDict):
            # If the element is already an OptionsDict object, make a
            # copy.  This has the benefit of preventing side effects
            # if the element persists elsewhere.
            od = copy(el)
            # add a special entry using sequence_key
            od.update({sequence_key: str(el)})
        else:
            # instantiate a new OptionsDict with the string
            # represention of the element acting as its name, and the
            # original element stored under sequence_key
            try:
                od = OptionsDict.named(name_format(el),
                                       {sequence_key: el})
            except TypeError:
                try:
                    od = OptionsDict.named(name_format.format(el),
                                           {sequence_key: el})
                except AttributeError:
                    raise OptionsDictException(
                        "name_formatter must be a callable or a format string.")
        # check and add common_entries
        if not isinstance(common_entries, dict):
            raise OptionsDictException(
                    "common_entries argument must be a dictionary.")
        od.update(common_entries)
        # append to the list
        optionsdict_list.append(od)
    return optionsdict_list

