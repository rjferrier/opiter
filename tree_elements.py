from copy import copy

from base import nonmutable, OptionsBaseException
from options_dict import OptionsDict
from node_info import OrphanNodeInfo, ArrayNodeInfo


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

    @nonmutable
    def __mul__(self, other):
        self.multiply_attach(other)

    @nonmutable
    def __add__(self, other):
        self.attach(other)
        
    
class OptionsNode(OptionsTreeElement):
    """
    Contains an options dictionary and optionally a child
    OptionsTreeElement, hence forming a tree structure.
    """
    def __init__(self, name, entries={}, child=None):

        # check and set name argument
        if name is None:
            name = ''
        elif not isinstance(name, str):
            raise OptionsNodeException(
                "name argument must be a string (or None)")
        self.name = name

        # set attributes
        self.options_dict = self.create_options_dict(entries)

        # check child argument
        if child is not None and not isinstance(child, OptionsTreeElement):
            raise OptionsNodeException(
                "child argument must be an OptionsTreeElement (or None)")
        self.child = child

        
    @classmethod
    def another(Class, name, entries={}, child=None):
        return Class(name, entries, child)

        
    def create_options_dict(self, entries):
        """
        Overrideable factory method, used by the OptionsNode
        constructor.
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
        # TODO: consider reworking this function as a generator.
        try:
            # recurse 
            result = []
            for sub_od in self.child.collapse():
                # copy, inform and update the present dictionary with
                # each element in the result of the recursion
                od = self.options_dict.copy()
                od.update(sub_od)
                result.append(od)
            # return the merged dictionaries
            return result
            
        except AttributeError:
            # this is a leaf, so just return the current options
            # dictionary as a one-element list
            return [self.options_dict.copy()]

            
    def multiply_attach(self, tree):
        """
        Appends a copy of tree to each leaf node in the present
        tree structure.
        """
        try:
            # recurse
            self.child.multiply_attach()
        except AttributeError:
            # can no longer recurse, so this is a leaf
            self.child = tree.copy()

            
    def attach(self, tree):
        """
        Appends a copy of each root node in the given tree (or
        whichever elements get traversed during iteration) to a
        corresponding leaf node in the present tree.
        """
        try:
            # recurse
            return self.child.attach(tree)
        except AttributeError:
            # This is a leaf.  Copy and split the tree, making the
            # first element the child of this node and returning the
            # rest to the client.
            try:
                new_child = tree[0].copy()
                remainder = tree[1:]
            except AttributeError:
                # wrap non-iterables as a one-element list
                new_child = tree.copy()
                remainder = []
            except IndexError:
                # no more elements in tree
                new_child = None
                remainder = []
            self.child = new_child
            return remainder

            
    def update(self, entries):
        # delegate
        self.options_dict.update(entries)
        
    def set_info(self, node_info):
        # delegate
        self.options_dict.set_node_info(node_info)
        
    def __eq__(self, other):
        result = isinstance(other, OptionsNode)
        if result:
            result *= self.name == other.name
            result *= self.options_dict == other.options_dict
        return result
        
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
        would contain
          [OptionsNode('0.01', {'velocity': 0.01}),
           OptionsNode('0.02', {'velocity': 0.02}),
           OptionsNode('0.04', {'velocity': 0.04})]
        but with different NodeInfo components.

        If an element is already an OptionsNode, the embedded
        dictionary simply acquires the entry {array_name:
        str(element)}.
        
        All embedded dictionaries are initialised with common_entries
        if this argument is given.  The element-to-string conversion
        is governed by name_format, which can either be a format
        string or a callable that takes the element value and returns
        a string.
        """
        self.name = array_name
        self.nodes = []
                
        # First pass: instantiate and record OptionsNodes
        for el in elements:
            
            if isinstance(el, dict):
                raise OptionsArrayException(
                    "\nDictionaries as elements are not allowed, because "+\
                    "it is not obvious\nhow to name them or what to enter "+\
                    "under the array key.  Please use\nOptionsNodes instead.")
                
            elif isinstance(el, OptionsNode):
                # If the element is already an OptionsNode, simply
                # copy it
                node = el.copy()
                
            else:
                # otherwise, instantiate a new OptionsNode with the
                # original element stored under array_name.  Determine
                # the node name.
                try:
                    node_name = name_format(el)
                except TypeError:
                    try:
                        node_name = name_format.format(el)
                    except AttributeError:
                        raise OptionsArrayException(
                            "name_format must be a callable "+\
                            "or a format string.")
                node = self.create_options_node(node_name, {array_name: el})

            # add entries
            node.update(common_entries)
            
            # append to the list
            self.nodes.append(node)

        # Second pass: set array node information.  This will replace
        # any preexisting node information.
        for i, node in enumerate(self.nodes):
            node.set_info(self.create_info(i))


    @classmethod
    def another(Class, array_name, elements, common_entries={},
                name_format='{}'):
        return Class(array_name, elements, common_entries, name_format)

        
    def create_options_node(self, node_name, entries):
        """
        Overrideable factory method, used by the OptionsArray
        constructor.
        """
        return OptionsNode(node_name, entries)

        
    def create_info(self, index):
        """
        Overrideable factory method, used by the OptionsArray
        constructor.
        """
        node_names = [str(node) for node in self.nodes]
        return ArrayNodeInfo(self.name, node_names, index)

        
    def copy(self):
        return self.another(self.name, copy(list(self)))

        
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
        for el in self:
            el.multiply_attach(tree)


    def attach(self, tree):
        """
        Appends a copy of each root node in the given tree (or
        whichever elements get traversed during iteration) to a
        corresponding leaf node in the present tree.
        """
        for el in self:
            tree = el.attach(tree)
        return tree

        
    def update(self, entries):
        for el in self:
            el.update(entries)

    def __eq__(self, other):
        result = isinstance(other, OptionsArray)
        if result:
            result *= self.name == other.name
            result *= self.nodes == other.nodes
            result *= list(self) == list(other)
        return result

    def __getitem__(self, index_or_slice):
        node_or_nodes = self.nodes[index_or_slice]
        if isinstance(node_or_nodes, list):
            # multiple nodes - wrap in a new OptionsArray
            return self.another(self.name, node_or_nodes)
        else:
            # single OptionsNode
            return node_or_nodes
            
