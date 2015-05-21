from options_dict import OptionsDict


class UnitOptionsDict(OptionsDict):
    """
    This is OptionsDict decoupled from the NodeInfo and NodeFormat
    implementations for unit testing purposes.
    """

    def create_orphan_node_info(self, node_name):
        "Throwaway implementation."
        return node_name

    def create_array_node_info(self, array_name, node_names, node_index):
        "Throwaway implementation."
        return ':'.join((array_name, node_names[node_index]))

    def create_node_info_format(self):
        return lambda node_info, absolute, relative: ''
