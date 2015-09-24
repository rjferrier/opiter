from base import OptionsBaseException
from options_tree_elements import OptionsTreeElement, NodeInfo, Position
from options_node import OptionsNode, OptionsNodeException
from copy import deepcopy
from warnings import warn


class OptionsArrayException(OptionsBaseException):
    pass

    
class ArrayNodeInfo(NodeInfo):
    """
    Describes a node which is part of an array (or sequence).
    """
    def __init__(self, array_name, node_names, node_index):
        NodeInfo.__init__(self, node_index, len(node_names))
        self.array_name = array_name
        self.node_names = node_names
        self.node_index = node_index

    def belongs_to(self, collection_name):
        """
        Returns True if the node in question is associated with the
        given collection name.
        """
        return collection_name == self.array_name
       
    def get_string(self, absolute=None, relative=None,
                   collection_separator=None):
        """
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

        If collection_separator is given, the array name will be
        prepended to the string followed by collection_separator.
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
        result = ''
        if collection_separator is not None:
            result += self.array_name + collection_separator
        result += self.node_names[self._create_index(self.node_index, *args)]
        return result
        
    def __eq__(self, other):
        result = isinstance(other, ArrayNodeInfo)
        if result:
            result *= self.array_name == other.array_name
            result *= self.node_names == other.node_names
            result *= self.node_index == other.node_index
        return result


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
            try:
                node = self.create_options_node(el, common_entries,
                                                name_format=name_format)
            except OptionsNodeException as e:
                raise OptionsArrayException(str(e))
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


    def __delitem__(self, subscript):
        try:
            # treat argument as a slice
            indices = subscript.indices(len(self.nodes))
            del self.nodes[subscript]

        except AttributeError:
            try:
                # treat argument as a name
                index = [str(n) for n in self.nodes].index(subscript)
            except ValueError:
                # default to an index
                index = subscript

            del self.nodes[index]

        
    def __str__(self):
        return str(self.name)
