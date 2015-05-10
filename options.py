from types import FunctionType
from string import Template
from copy import copy

# default settings
NAME_SEPARATOR = '_'


class OptionsDictException(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg

class NodeInfoException(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg

        
class OptionsDict(dict):
    """
    An OptionsDict inherits from a conventional dict, but it has a few
    enhancements:

    (1) An OptionsDict can be created as a named node, or as part of
        an array of named nodes.  This node information accumulates
        when OptionsDicts are merged via the update() method, and can
        be used to form a string identifier for the ensemble.  For
        example, updating node 'A' with node 'B' will produce node
        'A_B'.  The identifier can be accessed via the usual str()
        idiom, but a str() method is also provided with optional
        arguments for customising the identifier and inferring the
        identifiers of other combinations.

    (2) Values can be runtime-dependent upon the state of other values
        in the dictionary.  Each of these special values is specified
        by a function accepting a single dictionary argument (i.e. the
        OptionsDict itself).  The dictionary argument is used to look
        things up dynamically.  An OptionsDict can be constructed or
        updated with a list of functions instead of the usual
        key-value pairs, in which case the functions' names become the
        keys.

        N.B.  If using the multiprocessing module, it is important
        that dynamic entries are created using defs rather than
        lambdas.  It seems that lambdas cause pickling problems, and
        there is currently no way to protect against them.

    (3) An OptionsDict can expand strings as templates.
    """
    
    # settings
    name_separator = NAME_SEPARATOR

    
    def __init__(self, entries={}):
        """
        OptionsDict(entries={})

        Returns an OptionsDict with no node information.
        """
        # with just an entries argument, treat as a simple dict.
        # Default the node_info component first.  This is necessary to
        # prevent dynamic entries from possibly referencing the
        # component before it exists
        self.node_info = []
        self.update(entries)

        
    @classmethod
    def node(Self, name, entries={}):
        """
        OptionsDict.node(name, entries={})

        Returns an OptionsDict as an orphan node, i.e. having a name
        for identification purposes but not belonging to a collection.
        """
        # check name argument
        if not name:
            name = ''
        elif not isinstance(name, str):
            raise OptionsDictException(
                "name argument must be a string (or None).")
        # instantiate object and set the first node information
        obj = Self(entries)
        obj.node_info.append(obj.create_orphan_node_info(name))
        return obj

        
    @classmethod
    def array(Self, array_name, elements, common_entries={}, name_format='{}'):
        """
        OptionsDict.array(array_name, elements, common_entries={},
                          name_format='{}')

        Returns a list of OptionsDicts, wrapping the given elements as
        necessary.

        If a given element is not already an OptionsDict node, it is
        converted to a string which becomes the name of a new
        OptionsDict.  The new OptionsDict acquires the entry
        {array_name: element}.  This feature is useful for setting up
        an independent variable with an associated array of values.
        For example,
           OptionsDict.array('velocity', [0.01, 0.02, 0.04])
        would be equivalent to
          [OptionsDict.node('0.01', {'velocity': 0.01}),
           OptionsDict.node('0.02', {'velocity': 0.02}),
           OptionsDict.node('0.04', {'velocity': 0.04})]
        except that the NodeInfo components are different.

        If an element is already an OptionsDict node, it simply
        acquires the entry {array_name: str(element)}.
        
        All dicts are initialised with common_entries if this argument
        is given.  The element-to-string conversion is governed by
        name_format, which can either be a format string or a callable
        that takes the element value and returns a string.
        """
        options_dicts = []
        node_names = []
        
        # First pass: instantiate OptionsDict elements
        for index, el in enumerate(elements):
            if isinstance(el, OptionsDict):
                # If the element is already an OptionsDict object,
                # copy it and add a special entry using array_name.
                # Keep track of the node name.
                od = el.copy()
                node_name = str(el)
                od.update({array_name: node_name})
            else:
                # otherwise, instantiate a new OptionsDict node with
                # the original element stored under array_name.
                # Determine the node name.
                try:
                    node_name = name_format(el)
                except TypeError:
                    try:
                        node_name = name_format.format(el)
                    except AttributeError:
                        raise OptionsDictException(
                            "name_format must be a callable "+\
                            "or a format string.")
                od = Self.node(node_name, {array_name: el})

            # add entries
            od.update(common_entries)
            # append to the lists
            options_dicts.append(od)
            node_names.append(node_name)

        # Second pass: set array node information.  This will replace
        # the preexisting orphan node information.
        for index, od in enumerate(options_dicts):
            od.set_node_info(
                od.create_array_node_info(array_name, node_names, index))
        
        return options_dicts

        
    def create_orphan_node_info(self, node_name):
        """
        self.create_orphan_node_info(node_name)

        Overrideable factory method, used by OptionsDict.node().
        """
        return OrphanNodeInfo(node_name)

        
    def create_array_node_info(self, array_name, node_names, node_index):
        """
        self.create_array_node_info(node_name)

        Overrideable factory method, used by OptionsDict.array().
        """
        return ArrayNodeInfo(array_name, node_names, node_index)

    
    def update(self, entries):
        """
        self.update(entries)
        
        As with conventional dicts, updates entries with the key-value
        pairs given in the entries argument.  Alternatively, a list of
        functions may be supplied which will go on to become dynamic
        entries.
        """
        if isinstance(entries, dict):
            # argument is a dictionary, so updating is straightforward
            self._update_from_dict(entries)
        else:
            # argument is presumably a list of dynamic entries
            self._update_from_dynamic_entries(entries)

            
    def str(self, only=[], exclude=[], absolute={}, relative={}):
        """
        self.str(only=[], exclude=[], absolute={}, relative={})

        Returns a string identifier, providing more control than the
        str() idiom through optional arguments.

        Specifically, if the OptionsDict was initialised from a
        collection and/or has been updated from other
        collection-initialised OptionsDicts, it is possible to control
        which substrings appear through the 'only' and 'exclude'
        arguments.  These arguments take an collection name or list of
        collection names.
        """
        # wrap 'only' and 'exclude' strings as lists if necessary
        if isinstance(only, str):
            only = [only]
        if isinstance(exclude, str):
            exclude = [exclude]
        substrings = []
        for ni in self.node_info:
            # filter nodes according to corresponding collection names
            # given in the optional args
            if only:
                if not ni.belongs_to_any(only):
                    continue
            if ni.belongs_to_any(exclude):
                continue
            # if we are still in the loop at this point, we can include
            # the current node name in the result.
            substrings.append(ni.str(relative=relative, absolute=absolute))
        # finally join up the node names
        return self._join_substrings(substrings)

        
    def get_node_info(self, collection_name=None):
        """
        self.get_node_info(collection_name=None)
        
        Returns the OptionDict's first NodeInfo object.  If the
        OptionsDict has accumulated several NodeInfo objects, the
        client can get a particular one by passing in the
        corresponding collection name.
        """
        if collection_name is None:
            try:
                return self.node_info[0]
            except IndexError:
                raise NodeInfoException(
                    "there aren't any node_info objects")
        else:
            for ni in self.node_info:
                if ni.belongs_to(collection_name):
                    return ni
            raise NodeInfoException(
                "couldn't find any node information corresponding to '{}'".\
                format(collection_name))

        
    def set_node_info(self, new_node_info, collection_name=None):
        """
        self.set_node_info(new_node_info, collection_name=None)
        
        Sets the OptionDict's first NodeInfo object.  If the
        OptionsDict has accumulated several NodeInfo objects, the
        client can set a particular one by passing in the
        corresponding collection name.
        """
        if collection_name is None:
            try:
                self.node_info[0] = new_node_info
            except IndexError:
                raise NodeInfoException(
                    "there aren't any node_info objects")
        else:
            for i, ni in enumerate(self.node_info):
                if ni.belongs_to(collection_name):
                    self.node_info[i] = new_node_info
                    return
            raise NodeInfoException(
                "couldn't find any node information corresponding to '{}'".\
                format(collection_name))

        
    def expand_template(self, buffer_string, loops=1):
        """
        self.expand_template(buffer_string, loops=1)
        
        In buffer_string, replaces substrings prefixed '$' with
        corresponding values in the OptionsDict.  More than one loop
        will be needed if the placeholders are nested.
        """
        for i in range(loops):
            buffer_string = Template(buffer_string)
            buffer_string = buffer_string.safe_substitute(self)
        return buffer_string

    def copy(self):
        obj = OptionsDict(dict.copy(self))
        obj.node_info = [ni.copy() for ni in self.node_info]
        return obj

    def _update_from_dict(self, other):
        # update OptionsDict attributes
        if isinstance(other, OptionsDict):
            self.node_info += other.node_info
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

    def _join_substrings(self, substrings):
        if all(substrings):
            return self.name_separator.join(substrings)
        else:
            return ''.join(substrings)
            
    def __str__(self):
        return self.str()

    def __repr__(self):
        return dict.__repr__(self) + repr(self.node_info)

    def __iter__(self):
        yield self
        
    def __eq__(self, other):
        result = True
        result *= self.node_info == other.node_info
        result *= dict.__eq__(self, other)
        return result

    def __ne__(self, other):
        return not self==other
    
    def __getitem__(self, key):
        value = dict.__getitem__(self, key)
        # recurse until the return value is no longer a function
        if isinstance(value, FunctionType):
            # dynamic entry
            return value(self)
        else:
            # normal entry
            return value


class NodeInfo:
    """
    Abstract class for describing contextual information about a node.
    The concrete methods herein are special cases which defer to the
    more general subclass methods.
    """
    def belongs_to_any(self, collection_names):
        """
        self.belongs_to_any(collection_names)
        
        Returns True if the node in question is associated with any of
        collection_names.
        """
        for cn in collection_names:
            if self.belongs_to(cn):
                return cn
        return False
    
    def is_first(self):
        """
        self.is_first()
        
        Checks that the node in question is at the beginning of its
        container.
        """
        return self.at(0)
        
    def is_last(self):
        """
        self.is_last()
        
        Checks that the node in question is at the end of its container.
        """
        return self.at(-1)

    def _create_index(self, default, absolute, relative):
        # Helper to subclass str() methods
        if absolute is None:
            index = default
        else:
            index = absolute
        if relative is not None:
            index += relative
            if index < 0:
                raise IndexError("list index out of range")
        return index
        
    def __str__(self):
        return self.str()
        

class OrphanNodeInfo(NodeInfo):
    """
    Describes a node which is not part of any collection.
    """
    def __init__(self, node_name):
        self.node_name = node_name

    def belongs_to(self, collection_name):
        """
        self.belongs_to(collection_name)

        The node is not part of a collection, so this method will
        always return False.
        """
        return False
    
    def at(self, index):
        """
        self.at(index)

        Checks that the node is at the given index, which for an orphan
        node is only true for 0 (first) and -1 (last).
        """
        return index in (0, -1)

    def str(self, absolute=None, relative=None):
        """
        self.str(absolute=None, relative=None)
        
        Returns the name of the node in question.  The optional arguments
        are not applicable for an orphan node.
        """
        # for arg in (absolute, relative):
        #     if isinstance(absolute, dict):
        #         arg = None
        args = [absolute, relative]
        for i, a in enumerate(args):
            if isinstance(a, dict):
                args[i] = None
        if self.at(self._create_index(0, *args)):
            return self.node_name
        else:
            raise IndexError("list index out of range")

    def copy(self):
        return OrphanNodeInfo(self.node_name)

    def __eq__(self, other):
        result = isinstance(other, OrphanNodeInfo)
        if result:
            result *= self.node_name == other.node_name
        return result

        
class ArrayNodeInfo(NodeInfo):
    """
    Describes a node which is part of an array (or sequence).
    """
    def __init__(self, array_name, node_names, node_index):
        self.array_name = array_name
        self.node_names = node_names
        self.node_index = node_index

    def belongs_to(self, collection_name):
        """
        self.belongs_to(collection_name)

        Returns True if the node in question is associated with the
        given collection name.
        """
        return collection_name == self.array_name

    def at(self, index):
        """
        self.at(index)
        
        Checks that the node in question is at the given index, which can
        be negative to signify position from the end of the sequence.
        """
        return self.node_index == index or \
            self.node_index == index + len(self.node_names)
        
    def str(self, absolute=None, relative=None):
        """
        self.str(absolute=None, relative=None)
        
        Returns the name of the node in question or, if arguments are
        given, one of its siblings.  The optional arguments correspond
        to absolute and relative indices, respectively.  In accordance
        with Python indexing rules, a negative absolute index returns
        a node from the end of the array.  To prevent confusion,
        however, this shall not apply when a relative index is given.

        The optional arguments may also be supplied as dicts with
        entries of the form {array_name: index}.  In this case, the
        the indices will be dereferenced if possible using the present
        array name.
        """
        args = [absolute, relative]
        for i, a in enumerate(args):
            try:
                # convert the argument from a dict to an index 
                args[i] = a[self.array_name]
            except KeyError:
                # lookup failed, so give up on this argument
                args[i] = None
            except TypeError:
                # if argument is not a dict, it is presumably already
                # an index
                pass
        return self.node_names[
            self._create_index(self.node_index, *args)]

    def copy(self):
        return ArrayNodeInfo(
            self.array_name, copy(self.node_names), self.node_index)
        
    def __eq__(self, other):
        result = isinstance(other, ArrayNodeInfo)
        if result:
            result *= self.array_name == other.array_name
            result *= self.node_names == other.node_names
            result *= self.node_index == other.node_index
        return result

        
class CallableEntry:
    """
    CallableEntry(function)

    Because the OptionsDict works by evaluating all function objects
    recursively, it is not able to return other functions specified by
    the client unless these are wrapped as callable objects.  This class
    provides such a wrapper.
    """
    def __init__(self, function):
        self.function = function
        
    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)
