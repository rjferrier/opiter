from base import OptionsBaseException
from options_dict import OptionsDict
from node_info import OrphanNodeInfo, ArrayNodeInfo


class OptionsNodeException(OptionsBaseException):
    pass

class OptionsArrayException(OptionsBaseException):
    pass

    
class OptionsNode:
    """
    Contains an OptionsDict and optionally a child OptionsNode or
    OptionsArray, thus forming a tree.
    """

    def __init__(self, name, entries={}):
        """
        Creates a named OptionsNode and embeds an options dictionary based
        on entries.
        """
        # check name argument
        if name is None:
            name = ''
        elif not isinstance(name, str):
            raise OptionsNodeException(
                "name argument must be a string (or None).")
        # instantiate options dictionary and inject default node info
        self.name = name
        self.options_dict = self.create_options_dict(entries)
        self.options_dict.set_node_info(self.create_node_info())
        
    @classmethod
    def another(Class, name, entries={}):
        return Class(name, entries)

    def copy(self):
        return self.another(self.name, self.options_dict)

    def create_options_dict(self, entries):
        """
        Overrideable factory method, used by the OptionsNode
        constructor.
        """
        return OptionsDict(entries)
        
    def create_node_info(self):
        """
        Overrideable factory method, used by the OptionsNode
        constructor.
        """
        return OrphanNodeInfo(self.name)

    def set_node_info(self, node_info):
        self.node_info = node_info

    def update(self, entries):
        # delegation
        self.options_dict.update(entries)
        
    def __eq__(self, other):
        result = isinstance(other, OptionsNode)
        if result:
            result *= self.name == other.name
            result *= self.options_dict == other.options_dict
        return result
        
    def __str__(self):
        return str(self.name)


        
        
class OptionsArray(list):
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
                
        # First pass: instantiate OptionsNodes
        for el in elements:
            if isinstance(el, OptionsNode):
                # If the element is already an OptionsNode, copy it
                # and add a special entry to its embedded dictionary
                # using array_name.  Keep track of the node name.
                node = el.copy()
                node_name = str(el)
                node.update({array_name: node_name})
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
        # any preexisting orphan node information.
        for i, node in enumerate(self):
            node.set_node_info(self.create_node_info(i))
        
        
    def create_options_node(self, node_name, entries):
        """
        Overrideable factory method, used by the OptionsArray
        constructor.
        """
        return OptionsNode(node_name, entries)

        
    def create_node_info(self, index):
        """
        Overrideable factory method, used by the OptionsArray
        constructor.
        """
        return ArrayNodeInfo(self.name, self.node_names, index)

    
