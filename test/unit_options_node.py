from options_node import OptionsNode, OptionsNodeException


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
