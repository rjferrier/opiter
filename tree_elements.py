from copy import copy

from base import OptionsBaseException
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
    def __mul__(self, other):
        """
        Delegates to the copy_to_leaves method, but provides a new object
        instead of modifying the current one.  This means the function
        can be inlined neatly.
        """
        result = self.copy()
        result.copy_to_leaves(other)
        return result
    
    
class OptionsNode(OptionsTreeElement):
    """
    Contains an options dictionary and optionally a child
    OptionsTreeElement, hence forming a tree structure.
    """
    def __init__(self, name, entries={}, child=None, info=None):
        # check name argument
        if name is None:
            name = ''
        elif not isinstance(name, str):
            raise OptionsNodeException(
                "name argument must be a string (or None)")
        # check child argument
        if child is not None and not isinstance(child, OptionsTreeElement):
            raise OptionsNodeException(
                "child argument must be an OptionsTreeElement (or None)")
        # set attributes
        self.name = name
        self.options_dict = self.create_options_dict(entries)
        self.child = child
        if info:
            self.info = info
        else:
            self.info = self.create_info()
        
    @classmethod
    def another(Class, name, entries={}, child=None, info=None):
        return Class(name, entries, child, info)

    def create_options_dict(self, entries):
        """
        Overrideable factory method, used by the OptionsNode
        constructor.
        """
        return OptionsDict(entries)
        
    def create_info(self):
        """
        Overrideable factory method, used by the OptionsNode
        constructor.
        """
        return OrphanNodeInfo(self.name)

    def copy(self):
        if self.child:
            child = self.child.copy()
        else:
            child = None
        return self.another(self.name, entries=self.options_dict.copy(), 
                            child=child, info=self.info)
        
    def collapse(self):
        """
        Returns a list of options dictionaries corresponding to the leaves
        in the the present tree structure.  Each dictionary is the
        result of a merge from the root, through the branch nodes, to
        the corresponding leaf.
        """
        # At this point it is appropriate to inject node information.
        # Injecting it earlier on would mess up copy operations, since
        # updating OptionsDicts with one another duplicates node info.
        od = self.options_dict.copy()
        od.set_node_info(self.info)
        
        # might rework this function as a generator in future.
        try:
            # recurse 
            result = []
            for sub_od in self.child.collapse():
                # copy and update the present dictionary with each
                # element in the result of the recursion
                od.update(sub_od)
                result.append(od)
            # return the merged dictionaries
            return result
            
        except AttributeError:
            # this is a leaf, so just return the current options
            # dictionary as a one-element list
            return [od]
            
    def copy_to_leaves(self, tree_element):
        """
        Appends a copy of tree_element to each leaf node in the present
        tree structure.
        """
        try:
            # recurse
            self.child.copy_to_leaves()
        except AttributeError:
            # can no longer recurse, so this is a leaf
            self.child = tree_element.copy()

    def update(self, entries):
        self.options_dict.update(entries)
        
    def set_info(self, node_info):
        self.info = node_info
        
    def __eq__(self, other):
        result = isinstance(other, OptionsNode)
        if result:
            result *= self.name == other.name
            result *= self.options_dict == other.options_dict
        return result
        
    def __str__(self):
        return str(self.name)


class OptionsArray(OptionsTreeElement, list):
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
        self.node_names = []
                
        # First pass: instantiate OptionsNodes and record node names
        for el in elements:
            
            if isinstance(el, dict):
                raise OptionsArrayException(
                    "\nDictionaries as elements are not allowed, because "+\
                    "it is not obvious\nhow to name them or what to enter "+\
                    "under the array key.  Please use\nOptionsNodes instead.")
                
            elif isinstance(el, OptionsNode):
                # If the element is alrady an OptionsNode, simply copy
                # it and keep track of the node name.
                node = el.copy()
                node_name = str(el)
                
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
            
            # append to the lists
            self.append(node)
            self.node_names.append(node_name)

        # Second pass: set array node information.  This will replace
        # any preexisting node information.
        for i, node in enumerate(self):
            node.set_info(self.create_info(i))


    @classmethod
    def another(Class, array_name, elements, common_entries={},
                name_format='{}'):
        return Class(array_name, elements, common_entries, name_format)
        
    def copy(self):
        return self.another(self.name, copy(list(self)))
 
        
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
        return ArrayNodeInfo(self.name, self.node_names, index)


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
            
    def copy_to_leaves(self, tree_element):
        """
        Appends a copy of tree_element to each leaf node in the present
        tree structure.
        """
        for el in self:
            el.copy_to_leaves(tree_element)

    def update(self, entries):
        for el in self:
            el.update(entries)

    def __eq__(self, other):
        result = isinstance(other, OptionsArray)
        if result:
            result *= self.name == other.name
            result *= self.node_names == other.node_names
            result *= list(self) == list(other)
        return result

    def __getitem__(self, index_or_slice):
        elements = list.__getitem__(self, index_or_slice)
        if isinstance(elements, list):
            return self.another(self.name, elements)
        else:
            return elements
        
