from copy import deepcopy

class NodeHandler:
    def __init__(self, node_name, sublevel=None):
        """"NodeHandler(node_name, sublevel=None) Initialises a node which will
        become part of a handler tree.  To allow trees to be built
        easily, the parent level is not specified at this stage.
        """
        self._level_name = None
        self._node_name = node_name

    def set_level_name(self, level_name):
        self._level_name = level_name

        
class LevelHandler:
    def __init__(self, level_name, node_list):
        # copy node_list to prevent side effects
        self._node_list = deepcopy(node_list)
        # the supplied nodes may be strings, in which case they must be
        # converted into NodeHandlers first.
        for i, node in enumerate(self._node_list):
            if not isinstance(node, NodeHandler):
                self._node_list[i] = NodeHandler(node)

    
def new_handler(arg1, arg2=None, arg3=None):
    """Creates a Handler based on a flexible set of arguments.  Either a
    LevelHandler or NodeHandler will be returned.  The possibilities
    are:
       Create a node:
          new_handler(node_name)
          new_handler(node_name, sublevel)
          new_handler(level_name, node_name)
          new_handler(level_name, node_name, sublevel)
       Create a level:
          new_handler(level_name, node_list)
          new_handler(level_name, node_name_list)
    """

    # are we creating a level or a node?
    is_level = False
    if arg2 is not None:
        if isinstance(arg2, list):
            # we are creating a level and arg2 is the list of nodes
            is_level = True
        elif isinstance(arg2, tuple):
            arg2 = list(arg2)
            is_level = True

    if is_level:
        # the supplied nodes may be represented as strings, in which
        # case they must be converted into NodeHandlers first.  Copy
        # arg2 to prevent side effects.
        arg2 = deepcopy(arg2)
        for i, node in enumerate(arg2):
            if not isinstance(node, NodeHandler):
                arg2[i] = NodeHandler(node)
        new_handler = LevelHandler(arg1, arg2)
    else:
        # we are creating a node
        if isinstance(arg2, str):
            # arg1 is the level name, arg2 is the node name and there
            # may be a sublevel in arg3
            new_handler = NodeHandler(arg2, arg3)
            new_handler.set_level_name(arg1)
        else:
            # arg1 is the node name and there may be a sublevel in arg2
            new_handler = NodeHandler(arg1, arg2)
            
    return new_handler
