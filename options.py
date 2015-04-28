from types import FunctionType, LambdaType
from string import Template
from collections import OrderedDict
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
    OptionsDict itself).  The dictionary argument is used to look
    things up dynamically.  These functions may be listed in the
    entries argument if there are no other key-value pairs, in which
    case the functions' names become the keys.

    (2) An OptionsDict can be identified through its string
    representation.  When an OptionsDict is updated using another
    OptionsDict, its string representation changes to reflect the new
    state.  For example, updating 'A' with 'B' produces 'A_B'.

    (3) An OptionsDict can expand strings as templates.

    (4) When the OptionsDict is created as part of an array, or is
    updated with such an OptionsDict, extra information is stored.
    See array, str and get_position methods.
    
    ** If using the multiprocessing module, it is important that
       dynamic entries are created using defs rather than lambdas.  It
       seems that lambdas cause pickling problems, and there is
       currently no way to protect against them.
    """
    
    # settings
    name_separator = NAME_SEPARATOR
    
    def __init__(self, entries={}):
        # with just an entries argument, treat as a simple dict.
        # Default the name substrings and other attributes first.
        # This is necessary to prevent dynamic entries from possibly
        # referencing name before it exists
        self._name_substrings = []
        self._positions = OrderedDict()
        self.update(entries)

    @classmethod
    def named(Self, name, entries={}):
        # check name argument
        if not name:
            name = ''
        elif not isinstance(name, str):
            raise OptionsDictException(
                "name argument must be a string (or None).")
        # instantiate object and set the first name
        obj = Self(entries)
        obj._name_substrings = [name]
        return obj

    @classmethod
    def array(Self, array_name, elements, common_entries={},
              name_format='{}'):
        """
        OptionsDict.array(array_name, elements, 
                          common_entries={}, name_format='{}')

        Returns a list of OptionsDicts, wrapping the given elements as
        necessary.

        If a given element is not already an OptionsDict, it is
        converted to a string which becomes the name of a new
        OptionsDict.  The new OptionsDict acquires the entry
        {array_name: element}.  This feature is useful for setting up
        an independent variable with an associated array of values.
        For example,
           OptionsDict.array('velocity', [0.01, 0.02, 0.04])
        is equivalent to
          [OptionsDict.named('0.01', {'velocity': 0.01}),
           OptionsDict.named('0.02', {'velocity': 0.02}),
           OptionsDict.named('0.04', {'velocity': 0.04})]

        If an element is already an OptionsDict, it simply acquires
        the entry {array_name: element.name}.
        
        All dicts are initialised with common_entries if this argument
        is given.  The element-to-string conversion is governed by
        name_format, which can either be a format string or a callable
        that takes the element value and returns a string.
        
        A position object becomes registered and accessible through the
        get_position(array_name) method.
        """
        optionsdict_list = []
        name_list = []
        
        # first pass: instantiate OptionsDict elements
        for el in elements:
            if isinstance(el, Self):
                # If the element is already an OptionsDict object,
                # make a copy.  This has the benefit of preventing
                # side effects if the element persists elsewhere.
                od = el.copy()
                # add a special entry using array_name
                od.update({array_name: str(el)})
            else:
                # otherwise, instantiate a new OptionsDict with the
                # string represention of the element acting as its
                # name and the original element stored under
                # array_name
                try:
                    name = name_format(el)
                except TypeError:
                    try:
                        name = name_format.format(el)
                    except AttributeError:
                        raise OptionsDictException(
                            "name_format must be a callable "+\
                            "or a format string.")
                od = Self.named(name, {array_name: el})
            # add entries
            od.update(common_entries)
            # append to the lists
            optionsdict_list.append(od)
            name_list.append(str(od))

        # second pass: register positions
        for index, od in enumerate(optionsdict_list):
            od._positions[array_name] = od.create_position(
                name_list, index)

        # print array_name, name_list
        return optionsdict_list


    @staticmethod
    def create_position(name_list, index):
        "Overrideable factory method"
        return Position(name_list, index)

    def __repr__(self):
        ckeys = self._positions.keys()
        if ckeys:
            ckeys = "@"+str(ckeys)
        else:
            ckeys = ""
        return '{}:{}{}'.format(
            str(self), dict.__repr__(self), ckeys)

    def __str__(self):
        return self.str()

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
        eq_tests = []
        eq_tests.append(self._name_substrings == other._name_substrings)
        eq_tests.append(self._positions == other._positions)
        eq_tests.append(dict.__eq__(self, other))
        return all(eq_tests)

    def __ne__(self, other):
        return not self==other

    def copy(self):
        obj = OptionsDict(dict.copy(self))
        obj._name_substrings = copy(self._name_substrings)
        obj._positions = copy(self._positions)
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
            self._name_substrings += other._name_substrings
            self._positions.update(other._positions)
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

    def get_position(self, array_name=None):
        """
        If the OptionsDict was initialised as part of an array, calling
        this method with no arguments will return its associated
        Position object.  If the OptionsDict has since been updated
        with other array-initialised OptionsDicts, it is possible to
        recover any of their Positions by passing in the corresponding
        array_name.
        """
        if array_name is None:
            try:
                array_name = self._positions.keys()[0]
            except IndexError:
                return None
        try:
            return self._positions[array_name]
        except KeyError:
            return None

    def str(self, only=[], exclude=[]):
        """
        str(self, only=[], exclude=[])

        Returns a string identifier, providing more control than the
        __str__ idiom through optional arguments.

        Specifically, if the OptionsDict was array-initialised, and/or
        has been updated from other array-initialised OptionsDicts, it
        is possible to control which substrings appear through the
        'only' and 'exclude' arguments.  These arguments take an array
        name or list of array names.
        """
        # wrap 'only' and 'exclude' strings as lists if necessary
        if isinstance(only, str):
            only = [only]
        if isinstance(exclude, str):
            exclude = [exclude]
        # convert array names to node names
        only_substrings = self._get_node_names(only)
        exclude_substrings = self._get_node_names(exclude)
        # loop over name substrings, appending as appropriate
        result_substrings = []
        for substr in self._name_substrings:
            if only:
                if substr not in only_substrings:
                    continue
            if substr in exclude_substrings:
                continue
            result_substrings.append(substr)
        return self._join_substrings(result_substrings)

    def _get_node_names(self, array_names):
        result = []
        for arr in array_names:
            ct = self._positions[arr]
            result.append(str(ct))
        return result

    def _join_substrings(self, substrings):
        if all(substrings):
            return self.name_separator.join(substrings)
        else:
            return ''.join(substrings)
                
    def expand_template(self, buffer_string, loops=1):
        """
        In buffer_string, replaces substrings prefixed '$' with
        corresponding values from the dictionary.
        """
        for i in range(loops):
            buffer_string = Template(buffer_string)
            buffer_string = buffer_string.safe_substitute(self)
        return buffer_string
        

class Position:
    """
    Position(names, index)
    
    Provides information on where a node is in relation to others in a
    sequence.  It also provides the names of the other elements based
    on their absolute or relative indices.
    """

    def __init__(self, names, index):
        self.names = names
        self.index = index

    def __str__(self):
        return self.str()

    def __repr__(self):
        return 'Position({}, {})'.format(self.names, self.index)

    def str(self, absolute=None, relative=None):
        """
        Returns the name of the node in question or, if arguments are
        given, one of its siblings.  The optional arguments correspond
        to absolute and relative indices, respectively.  In accordance
        with Python indexing rules, a negative absolute index returns
        a node from the end of the array.  To avoid confusion, this
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

