from tree_elements import OptionsNode, OptionsArray, OptionsNodeException


class UnitOptionsNode(OptionsNode):
    """
    This is OptionsNode decoupled from the OptionsDict and
    OrphanNodeInfo implementations for unit testing purposes.
    """
    def create_options_dict(self, entries={}):
        """
        Throwaway implementation.  Don't expect it to do anything with
        the passed in entries.
        """
        class FakeOptionsDict(dict):
            def set_node_info(self, node_info):
                pass
        return FakeOptionsDict()
        
    def create_info(self):
        "Throwaway implementation."
        return self.name


    
class UnitOptionsArray(OptionsArray):
    """
    This is OptionsArray decoupled from the OptionsNode and
    ArrayNodeInfo implementations for unit testing purposes.
    """
    def create_options_node(self, arg1={}, arg2={}, name_format='{}'):
        return UnitOptionsNode(arg1, arg2, name_format=name_format,
                               array_name=self.name)

    def create_node_info(self, index):
        "Throwaway implementation."
        return ':'.join((self.name, str(self.nodes[index])))
