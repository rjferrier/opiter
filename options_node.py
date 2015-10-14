from options_tree_elements import OptionsTreeElement, \
    OptionsTreeElementException
from node_info import NodeInfo, Position
from options_dict import OptionsDict
from copy import deepcopy
from warnings import warn


class OptionsNodeException(OptionsTreeElementException):
    pass


class OrphanNodeInfo(NodeInfo):
    """
    Describes a node which is not part of any collection.
    """
    def __init__(self, node_name, tags=[]):
        NodeInfo.__init__(self, 0, 0, tags=tags)
        self.node_name = node_name

    def belongs_to(self, collection_name):
        """
        The node is not part of a collection, so this method will
        always return False.
        """
        return False

    def get_string(self, absolute=None, relative=None,
                   collection_separator=None):
        """
        Returns the name of the node in question.  The optional arguments
        are not applicable for an orphan node.
        """
        args = [absolute, relative]
        for i, a in enumerate(args):
            if isinstance(a, dict):
                args[i] = None
        if self.position.is_at(self._create_index(0, *args)):
            return self.node_name
        else:
            raise IndexError("list index out of range")
        
    def __eq__(self, other):
        result = isinstance(other, OrphanNodeInfo)
        if result:
            result *= self.node_name == other.node_name
        return result


class OptionsNode(OptionsTreeElement):
    """
    Contains an options dictionary and optionally a child
    OptionsTreeElement, hence forming a tree structure.
    """
    def __init__(self, arg1={}, arg2={}, child=None, name_format='{}',
                 array_name=None, tags=[], dict_hooks=[], item_hooks=[]):
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
        
          arg         node name        options dict items
          -----       ---------        --------------------
          name        name             array_name: name
          value       str(value)       array_name: value
          class       class.__name_    array_name: class.__name__,
                                       **class.__dict__
          items                        **items
        """
        OptionsTreeElement.__init__(self, dict_hooks=dict_hooks,
                                    item_hooks=item_hooks)

        # try and infer a name from the first arg; set tags
        self.set_name_general(arg1, name_format)
        self.tags = tags
        
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
    def another(Class, arg1={}, arg2={}, child=None, tags=[],
                dict_hooks=[], item_hooks=[]):
        return Class(arg1, arg2, child, tags=tags,
                     dict_hooks=dict_hooks, item_hooks=item_hooks)

        
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
            raise OptionsNodeException(
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

        
    def create_options_dict(self, items={}):
        """
        Overrideable factory method, used by OptionsNode.set_options_dict.
        """
        od = OptionsDict(items)
        od.set_node_info(self.create_info())
        return od

        
    def create_info(self):
        """
        Overrideable factory method, used by
        OptionsNode.create_options_dict.
        """
        return OrphanNodeInfo(self.name, tags=self.tags)

        
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
            
        except AttributeError:
            # this is a leaf, so just return the current options
            # dictionary as a one-element list
            result = [deepcopy(self.options_dict)]

        self.apply_hooks(result)
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

                
    def update(self, items):
        """
        Updates the leaf dictionaries with items.
        """
        if self.child:
            self.child.update(items)
        else:
            self.options_dict.update(items)

    
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
            raise OptionsNodeException(str(type(self.options_dict)) + ' '+\
                                       repr(self.options_dict))

        
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

    def __delitem__(self, subscript):
        if self.child:
            del self.child[subscript]
        else:
            raise IndexError('no iterable children')

    def __str__(self):
        return str(self.name)

