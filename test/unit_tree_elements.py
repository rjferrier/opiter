from tree_elements import OptionsNode, OptionsArray


class UnitOptionsNode(OptionsNode):
    """
    This is OptionsNode decoupled from the OptionsDict and
    OrphanNodeInfo implementations for unit testing purposes.
    """
    def create_options_dict(self, entries):
        class FakeOptionsDict(dict):
            def set_node_info(self, node_info):
                pass
        return FakeOptionsDict()

    def create_node_info(self):
        return None


class UnitOptionsArray(OptionsArray):
    """
    This is OptionsArray decoupled from the OptionsNode and
    ArrayNodeInfo implementations for unit testing purposes.
    """
    def create_options_node(self, node_name, entries):
        return UnitOptionsNode(node_name, entries)

    def create_node_info(self, index):
        return None
