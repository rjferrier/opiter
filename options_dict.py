from copy import deepcopy
from types import FunctionType
from string import Template
from warnings import warn

from base import OptionsBaseException
from node_info import OrphanNodeInfo, ArrayNodeInfo, SimpleFormatter, \
    TreeFormatter, NodeInfoException


class OptionsDictException(OptionsBaseException):
    pass

        
class OptionsDict(dict):
    """
    An OptionsDict inherits from a conventional dict, but it has a few
    enhancements:

    (1) An OptionsDict can be given 'node information' which lends the
        OptionsDict a name and describes its position in a tree.  This
        node information accumulates when OptionsDicts are merged via
        the update() method, and can be used to form a string
        identifier for the ensemble.  For example, updating node 'A'
        with node 'B' will produce node 'A_B'.  The identifier can be
        accessed via the usual str() idiom, but a str() method is also
        provided with optional arguments for customising the
        identifier and inferring the identifiers of other
        combinations.

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
    
    def __init__(self, entries={}):
        """
        Returns an OptionsDict with no node information.
        """
        # With just an entries argument, treat as a simple dict.  Set
        # the node_info list first.  This is necessary to prevent
        # dynamic entries from possibly referencing the component
        # before it exists.
        self.node_info = []
        self.update(entries)

    @classmethod
    def another(Class, entries={}):
        return Class(entries)

    @classmethod
    def node(Class, name, entries={}):
        """
        Returns an OptionsDict as an orphan node, i.e. having a name
        for identification purposes but not belonging to a collection.
        """

        warn("\nThis is a deprecated method.  Consider using "+\
             "tree_elements.OptionsNode \ninstead.")
        
        # check name argument
        if not name:
            name = ''
        elif not isinstance(name, str):
            raise OptionsDictException(
                "name argument must be a string (or None).")
        # instantiate object and set the first node information
        obj = Class(entries)
        obj.node_info.append(obj.create_orphan_node_info(name))
        return obj

        
    @classmethod
    def array(Class, array_name, elements, common_entries={},
              name_format='{}'):
        """
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

        warn("\nThis is a deprecated method.  Consider using "+\
             "tree_elements.OptionsArray\n instead.")

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
                od = Class.node(node_name, {array_name: el})

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


    def copy(self):
        obj = self.another(dict.copy(self))
        obj.node_info = [ni.copy() for ni in self.node_info]
        return obj

        
    def create_orphan_node_info(self, node_name):
        """
        Overrideable factory method, used by OptionsDict.node().
        """
        return OrphanNodeInfo(node_name)

        
    def create_array_node_info(self, array_name, node_names, node_index):
        """
        Overrideable factory method, used by OptionsDict.array().
        """
        return ArrayNodeInfo(array_name, node_names, node_index)

    
    def update(self, entries):
        """
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

            
    def str(self, only=[], exclude=[], absolute={}, relative={}, 
            formatter=None):
        """
        Returns a string identifier, providing more control than the
        str() idiom through optional arguments.

        Specifically, if the OptionsDict was part of a collection
        and/or has been updated from other such OptionsDicts, it is
        possible to control which substrings appear through the 'only'
        and 'exclude' arguments.  These arguments take a collection
        name or list of collection names.

        If the OptionsDict was part of a tree, the 'absolute' and
        'relative' arguments can be used to infer the name of an
        OptionsDict corresponding to a different node in the tree.
        These arguments take the form of key-value pairs with
        collection names as the keys and indices as the values.  In
        accordance with Python indexing rules, a negative absolute
        index returns a node from the end of the array.  To prevent
        confusion, however, this shall not apply when a relative index
        is given.
        
        If the formatter argument is a string or omitted, the
        OptionsDict constructs and applies a formatter object (see
        OptionsDict.create_node_info_formatter).  Alternatively, the
        client may construct and pass a formatter object directly.
        """
        # wrap 'only' and 'exclude' strings as lists if necessary
        if isinstance(only, str):
            only = [only]
        if isinstance(exclude, str):
            exclude = [exclude]

        # filter the nodes to represent
        filtered_node_info = []
        for ni in self.node_info:
            # filter nodes according to corresponding collection names
            # given in the optional args
            if only:
                if not ni.belongs_to_any(only):
                    continue
            if ni.belongs_to_any(exclude):
                continue
            # if we are still in the loop at this point, we can include
            # the current node info in the result.
            filtered_node_info.append(ni)

        # create a formatter object if necessary
        if isinstance(formatter, str) or not formatter:
            formatter = self.create_node_info_formatter(formatter)
        # pass the filtered list to the formatter object
        return formatter(filtered_node_info, 
                         absolute=absolute, relative=relative)

        
    def create_node_info_formatter(self, which=None):
        """
        Overrideable factory method, used by OptionsDict.str().  The
        argument may be 'simple', 'tree', or omitted (defaulting to
        'simple').
        """
        if not which:
            which = 'simple'
        if which == 'simple':
            return SimpleFormatter()
        elif which == 'tree':
            return TreeFormatter()
        else:
            raise OptionsDictException("'{}' not recognised.".format(which))
            
        
    def get_node_info(self, collection_name=None):
        """
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
        Sets the OptionDict's first NodeInfo object.  If the
        OptionsDict has accumulated several NodeInfo objects, the
        client can set a particular one by passing in the
        corresponding collection name.
        """
        if collection_name is None:
            try:
                self.node_info[0] = new_node_info
            except IndexError:
                self.node_info.append(new_node_info)
        else:
            for i, ni in enumerate(self.node_info):
                if ni.belongs_to(collection_name):
                    self.node_info[i] = new_node_info
                    return
            raise NodeInfoException(
                "couldn't find any node information corresponding to '{}'".\
                format(collection_name))
        
        
    def expand_template_string(self, buffer_string, loops=1):
        """
        In buffer_string, replaces substrings prefixed '$' with
        corresponding values in the OptionsDict.  More than one loop
        will be needed if the placeholders are nested.
        """
        for i in range(loops):
            buffer_string = Template(buffer_string)
            buffer_string = buffer_string.safe_substitute(self)
        return buffer_string
        
        
    def expand_template_file(self, source_filename, target_filename, 
                             loops=1):
        """
        As expand_template_string, but does the reading and writing of
        files for you.
        """
        with open(source_filename, 'r') as src:
            buf = src.read()
            buf = self.expand_template_string(buf, loops)
        with open(target_filename, 'w') as tgt:
            tgt.write(buf)


    def donate_copy(self, acceptor):
        # polymorphic; used by tree_elements
        acceptor.update(self)
        return acceptor, []


    def _update_from_dict(self, other):
        # update OptionsDict attributes
        if isinstance(other, OptionsDict):
            self.node_info += other.node_info
            # if len(self.node_info) > 1: raise Exception
        # now pass to superclass
        dict.update(self, other)

    def _update_from_dynamic_entries(self, functions):
        err = OptionsDictException("entries must be a dict or a sequence "+\
                                   "of dynamic entries (i.e.functions).")
        try:
            for func in functions:
                if not isinstance(func, FunctionType):
                    raise err
                varnames = func.func_code.co_varnames
                self[func.__name__] = func
        except TypeError:
            raise err
            
    def __str__(self):
        return self.str()

    def __repr__(self):
        return dict.__repr__(self) + repr(self.node_info)

    def __iter__(self):
        yield self
        
    def __eq__(self, other):
        result = isinstance(other, OptionsDict)
        if result:
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

        
class CallableEntry:
    """
    Because the OptionsDict works by evaluating all function objects
    recursively, it is not able to return other functions specified by
    the client unless these are wrapped as callable objects.  This class
    provides such a wrapper.
    """
    def __init__(self, function):
        self.function = function
        
    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)


class Lookup:
    """
    Provides a function object that simply looks up a key in a
    dictionary.  This functionality was originally implemented as a
    closure, but the multiprocessing module couldn't pickle it.
    """
    def __init__(self, key):
        self.key = key

    def __call__(self, dictionary):
        return dictionary[self.key]
