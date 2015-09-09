from itertools import islice
from operator import mul

from base import nonmutable, OptionsBaseException
from options_dict import OptionsDict
from node_info import OrphanNodeInfo, ArrayNodeInfo
from copy import deepcopy
from warnings import warn

class OptionsNodeException(OptionsBaseException):
    pass

class OptionsArrayException(OptionsBaseException):
    pass

    
class OptionsTreeElement:
    """
    Abstract class to be inherited by OptionsArray and OptionsNode.
    This inheritance hierarchy is similar to the Composite pattern in
    that it can be used to build an arbitrary tree.  However,
    OptionsNode can act as a branch as well as a leaf, so it shares
    some of the parent-child functionality.
    """

    def __ne__(self, other):
        return not self == other

    @nonmutable
    def __mul__(self, other):
        self.multiply_attach(other)

    @nonmutable
    def __rmul__(self, other):
        # this conditional stops us trying to multiply with 1 during a
        # product() call
        if isinstance(other, OptionsTreeElement):
            self.multiply_attach(other)

    @nonmutable
    def __add__(self, other):
        self.attach(other)

    @nonmutable
    def __radd__(self, other):
        # this conditional stops us trying to add to 0 during a
        # product() call
        if isinstance(other, OptionsTreeElement):
            self.attach(other)

    def __imul__(self, other):
        self.multiply_attach(other)
        return self

    def __iadd__(self, other):
        self.attach(other)
        return self

    
class OptionsNode(OptionsTreeElement):
    """
    Contains an options dictionary and optionally a child
    OptionsTreeElement, hence forming a tree structure.
    """
    def __init__(self, arg1={}, arg2={}, child=None,
                 name_format='{}', array_name=None):
        """
        Constructs an OptionsNode, inferring a name from arg1 and an
        options dictionary from arg1 and arg2, if present.

        name_format controls the string representation of arg1.  It
        may take the form of a one-argument function or a format
        string.

        If array_name is given, a representative value taken from
        either of the arguments will be stored in the dictionary under
        array_name - i.e. {array_name: representative_value}.  arg2
        takes precedence over arg1; this allows initialisations such
        as OptionsNode(node_name, representative_value,
        array_name=array_name).
        
        Possible candidates for the arguments, and consequent node
        attributes, are:
        
          arg         node name        options dict entries
          -----       ---------        --------------------
          name        name             array_name: name
          value       str(value)       array_name: value
          class       class.__name_    array_name: class.__name__,
                                       **class.__dict__
          entries                      **entries
        """

        # try and infer a name from the first arg 
        self.set_name_general(arg1, name_format)
        
        # instantiate the options dict and update from both args (with
        # arg2 taking precedence over arg1)
        self.options_dict = self.create_options_dict()
        self.update_options_dict_general(arg2, array_name)
        self.update_options_dict_general(arg1, array_name)
        
        # Set the child.  The type check is not ideal but it prevents
        # bad things happening later.
        if child is not None and not isinstance(child, OptionsTreeElement):
            raise OptionsNodeException(
                "child argument must be an OptionsTreeElement (or None)")
        self.child = child

        
    @classmethod
    def another(Class, arg1={}, arg2={}, child=None):
        return Class(arg1, arg2, child)

        
    def set_name_general(self, arg, name_format):
        if hasattr(arg, 'name'):
            # if we have another OptionsNode or something with a
            # 'name' attribute, use that name
            name_src = arg.name
        
        elif hasattr(arg, '__name__'):
            # if we have a class, use the class name
            name_src = arg.__name__

        elif arg is None or hasattr(arg, '__iter__'):
            # containers and None are inappropriate for forming names
            name_src = ''
            
        else:
            # everything else can be used directly
            name_src = arg
            
        # convert to a string with the help of name_format
        try:
            self.name = name_format(name_src)
            return
        except TypeError:
            pass

        # if name_format fails as a function, try treating it as a
        # format string
        try:
            self.name = name_format.format(name_src)
        except AttributeError:
            raise OptionsArrayException(
                "name_format must be a callable or a format string; is {}".\
                format(name_format))
            

    def update_options_dict_general(self, arg, array_name):
        # Try and update the options dictionary directly from the
        # arg.  Tolerate failures silently since the arg may not
        # be intended for this purpose.
        try:
            self.options_dict.update(arg)
        except:
            pass
        
        # Try and infer a representative value to be stored under
        # array_name, if one doesn't already exist
        if array_name and array_name not in self.options_dict:
            if hasattr(arg, 'name'):
                # if the arg is another OptionsNode or something with
                # a 'name' attribute, make that name the
                # representative value
                self.options_dict.update({array_name: arg.name})
                
            elif hasattr(arg, '__name__'):
                # if the arg is a class, make its name the
                # representative value
                self.options_dict.update({array_name: arg.__name__})
            
            elif not hasattr(arg, '__iter__'):
                # for all other non-iterable types, store the value
                # directly
                self.options_dict.update({array_name: arg})

        
    def create_options_dict(self, entries={}):
        """
        Overrideable factory method, used by OptionsNode.set_options_dict.
        """
        od = OptionsDict(entries)
        od.set_node_info(self.create_info())
        return od

        
    def create_info(self):
        """
        Overrideable factory method, used by
        OptionsNode.create_options_dict.
        """
        return OrphanNodeInfo(self.name)

        
    def copy(self):
        warn("\nThis is a deprecated method.  Consider using "+\
             "copy.deepcopy \ninstead.")
        return self.another(
            self.name, entries=self.options_dict.copy(),
            child=self.child.copy() if self.child else None)

        
    def collapse(self):
        """
        Returns a list of options dictionaries corresponding to the leaves
        in the the present tree structure.  Each dictionary is the
        result of a merge from the root, through the branch nodes, to
        the corresponding leaf.
        """
        try:
            # recurse 
            result = []
            for sub_od in self.child.collapse():
                # copy, inform and update the present dictionary with
                # each element in the result of the recursion
                od = deepcopy(self.options_dict)
                od.update(sub_od)
                result.append(od)
            # return the merged dictionaries
            return result
            
        except AttributeError:
            # this is a leaf, so just return the current options
            # dictionary as a one-element list
            result = [deepcopy(self.options_dict)]

        return result

            
    def multiply_attach(self, tree):
        """
        Appends a copy of tree to each leaf node in the present
        tree structure.
        """
        try:
            # recurse
            self.child.multiply_attach(tree)
        except AttributeError:
            self.child = deepcopy(tree)

            
    def attach(self, tree):
        """
        Appends a copy of each root node in the tree argument (or
        whichever elements get traversed during iteration) to a
        corresponding leaf node in the present tree.  Returns the
        depleted source tree.
        """
        if not tree:
            # no more elements to attach, so exit early
            return None
        elif not self.child:
            # This is a leaf.  Copy and split the tree, making the
            # first element the child of this node and returning the
            # rest to the client.
            try:
                # polymorphic implementation, needed for handling
                # embedded node info correctly
                self.child, remainder = tree.donate_copy(self.child)
                return remainder
            except AttributeError:
                # manual implementation, for native iterables
                self.child = deepcopy(tree[0])
                return tree[1:]
        else:
            # keep going
            return self.child.attach(tree)


    def donate_copy(self, acceptor):
        node_copy = deepcopy(self)
        if acceptor:
            acceptor.attach(node_copy)
        else:
            acceptor = node_copy
        return acceptor, []

        
    def count_leaves(self):
        if self.child:
            return self.child.count_leaves()
        else:
            return 1

                
    def update(self, entries):
        """
        Updates the leaf dictionaries with entries.
        """
        if self.child:
            self.child.update(entries)
        else:
            self.options_dict.update(entries)

    
    def update_info(self, node_info=None):
        """
        Updates the nodes with node information.  If the argument is
        omitted, node info appropriate to an OptionsNode is
        constructed.
        """
        # default node info
        if not node_info:
            node_info = self.create_info()
        # delegate
        try:
            self.options_dict.set_node_info(node_info)
        except AttributeError:
            raise OptionsNodeException( str(type(self.options_dict)) + ' '+\
                                        repr(self.options_dict) )

        
    def __eq__(self, other):
        result = isinstance(other, OptionsNode)
        if result:
            result *= self.name == other.name
            result *= self.options_dict == other.options_dict
            result *= self.child == other.child
        return result

    def __getitem__(self, subscript):
        if self.child:
            return self.child[subscript]
        else:
            raise IndexError('no iterable children')

    def __setitem__(self, subscript, value_or_values):
        if self.child:
            self.child[subscript] = value_or_values

    def __str__(self):
        return str(self.name)



class OptionsArray(OptionsTreeElement):
    """
    A sequence of OptionsNodes.
    """

    def __init__(self, array_name, elements, common_entries={},
                 name_format='{}'):
        """
        Returns an OptionsArray, wrapping the given elements as
        OptionsNodes where necessary.

        If a given element is not already an OptionsNode, it is
        converted to a string which becomes the name of a new
        OptionsNode.  The embedded dictionary acquires the entry
        {array_name: element}.  This feature is useful for setting up
        an independent variable with an associated array of values.

        For example,
           OptionsArray('velocity', [0.01, 0.02, 0.04])
        will contain
          [OptionsNode('0.01', {'velocity': 0.01}),
           OptionsNode('0.02', {'velocity': 0.02}),
           OptionsNode('0.04', {'velocity': 0.04})]
        but the nodes will contain different node info.
        
        All embedded dictionaries are initialised with common_entries
        if this argument is given.  The element-to-string conversion
        is governed by name_format, which can either be a format
        string or a callable that takes the element value and returns
        a string.
        """
        self.name = array_name
        self.nodes = []
        self.name_format = name_format
                
        # instantiate and record OptionsNodes
        for el in elements:
            node = self.create_options_node(el, common_entries,
                                            name_format=name_format)
            # append to the list
            self.nodes.append(node)

        # set array node information in each node.  This will replace
        # any preexisting node information.
        self.update_node_info()


    @classmethod
    def another(Class, array_name, elements, common_entries={},
                name_format='{}'):
        return Class(array_name, elements, common_entries, name_format)

    
    def create_options_node(self, arg1={}, arg2={}, name_format='{}'):
        """
        Overrideable factory method, used by the OptionsArray constructor.
        """
        if isinstance(arg1, OptionsNode):
            # if the first arg is an existing OptionsNode, catch and
            # copy it
            node = deepcopy(arg1)
            node.set_name_general(arg1, name_format) 
            node.update_options_dict_general(arg2, self.name) 
            node.update_options_dict_general(arg1, self.name) 
            return node
        else:
            return OptionsNode(arg1, arg2, name_format=name_format,
                               array_name=self.name)

    
    def copy(self):
        warn("\nThis is a deprecated method.  Consider using "+\
             "copy.deepcopy \ninstead.")
        return self.another(self.name, [el.copy() for el in self])

        
    def collapse(self):
        """
        Returns a list of options dictionaries corresponding to the leaves
        in the the present tree structure.  Each dictionary is the
        result of a merge from the root, through the branch nodes, to
        the corresponding leaf.
        """
        result = []
        for el in self:
            result += el.collapse()
        return result

        
    def multiply_attach(self, tree):
        """
        Appends a copy of the given tree to each leaf node in the
        present tree.
        """
        # delegate to each node
        for el in self:
            el.multiply_attach(tree)


    def attach(self, tree):
        """
        Appends a copy of each root node in the tree argument (or
        whichever elements get traversed during iteration) to a
        corresponding leaf node in the present tree.  Returns the
        depleted source tree.
        """
        # delegate to each node
        for el in self:
            tree = el.attach(tree)
        return tree


    def donate_copy(self, acceptor):
        # It is nice to preserve array information, so grab a
        # one-element slice rather than a node.  The slice preserves
        # the OptionsArray type.
        one_node_array = self[0:1]
        one_node_array.update_node_info()
        if acceptor:
            acceptor.attach(one_node_array)
        else:
            acceptor = one_node_array
        # also return (a copy of) the depleted array
        return acceptor, self[1:]


    def count_leaves(self):
        return sum([el.count_leaves() for el in self.nodes])

        
    def update(self, entries):
        """
        Updates the leaf dictionaries with entries.
        """
        for el in self:
            el.update(entries)


    def update_node_info(self):
        """
        Updates the nodes with node information appropriate to an
        OptionsArray.
        """
        for i, node in enumerate(self.nodes):
            try:
                node.update_info(self.create_node_info(i))
            except:
                print node
                raise

        
    def create_node_info(self, index):
        """
        Overrideable factory method, used by
        OptionsArray.update_node_info.
        """
        node_names = [str(node) for node in self.nodes]
        return ArrayNodeInfo(self.name, node_names, index)


    def append(self, item):
        if not isinstance(item, OptionsNode):
            raise OptionsArrayException("item needs to be an OptionsNode")
        self.nodes.append(item)
        self.update_node_info()
            
    def pop(self):
        node = self.nodes.pop()
        # update node info on both sides
        node.update_info()
        self.update_node_info()
        return node
        
    def __len__(self):
        return len(self.nodes)
            
    def __eq__(self, other):
        result = isinstance(other, OptionsArray)
        if result:
            result *= self.name == other.name
            result *= len(self.nodes) == len(other.nodes)
            for node, other in zip(self.nodes, other.nodes):
                result *= node == other
        return result


    def __getitem__(self, subscript):
        try:
            # treat argument as a slice
            indices = subscript.indices(len(self.nodes))

            # return an array
            return self.another(self.name, self.nodes[subscript])

        except AttributeError:
            try:
                # treat argument as a name
                index = [str(n) for n in self.nodes].index(subscript)
            except ValueError:
                # default to an index
                index = subscript

            # return a node
            return self.nodes[index]


    def __setitem__(self, subscript, value_or_values):
        try:
            # treat subscript as a slice
            indices = subscript.indices(len(self.nodes))
            # convert values to nodes 
            self.nodes[subscript] = [self.create_options_node(v) \
                                         for v in value_or_values]

        except AttributeError:
            try:
                # treat subscript as a name
                index = [str(n) for n in self.nodes].index(subscript)
            except ValueError:
                # default to an index
                index = subscript
                
            # convert value to a node
            self.nodes[index] = self.create_options_node(value_or_values)

        self.update_node_info()

        
    def __str__(self):
        return str(self.name)

    
def product(iterable):
    return reduce(mul, iterable, 1)
