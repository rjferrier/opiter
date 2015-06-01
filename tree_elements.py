from itertools import islice
from copy import deepcopy

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

    def __ne__(self, other):
        return not self == other

    @nonmutable
    def __mul__(self, other):
        self.multiply_attach(other)

    @nonmutable
    def __add__(self, other):
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
            self.child.multiply_attach(tree)
        except AttributeError:
            # can no longer recurse, so this is a leaf
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
        node_copy = self.copy()
        if acceptor:
            acceptor.attach(node_copy)
        else:
            acceptor = node_copy
        return acceptor, []

                
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
        self.options_dict.set_node_info(node_info)

        
    def __eq__(self, other):
        result = isinstance(other, OptionsNode)
        if result:
            result *= self.name == other.name
            result *= self.options_dict == other.options_dict
            result *= self.child == other.child
        return result

    def __str__(self):
        if self.child:
            child_str = ':' + str(self.child)
        else:
            child_str = ''
        return str(self.name) + child_str



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
                
        # instantiate and record OptionsNodes
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

        # set array node information in each node.  This will replace
        # any preexisting node information.
        self.update_node_info()


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

        
    def copy(self):
        # TODO: find out why 
        #   return self.another(self.name, [el.copy() for el in self])
        # causes problems for non-shallow trees.  Probably has
        # something to do with the accumulated node info objects.
        return deepcopy(self)

        
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
        # emulate a popleft()
        node_copy = self[0].copy()
        node_copy.update_info()
        if acceptor:
            acceptor.attach(node_copy)
        else:
            acceptor = node_copy
        return acceptor, self[1:]

        
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
            node.update_info(self.create_node_info(i))

        
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

    def __getitem__(self, index_or_slice):
        if isinstance(index_or_slice, slice):
            # multiple OptionsNodes; return a new OptionsArray
            return self.another(
                self.name, islice(
                    self.nodes, *index_or_slice.indices(len(self.nodes))))
        else:
            # return single OptionsNode.  Note that, unlike a slice,
            # this neither returns a copy nor modifies the node info.
            return self.nodes[index_or_slice]
            
    def __str__(self):
        return str(self.name)
