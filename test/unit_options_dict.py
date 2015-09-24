from options_dict import OptionsDict, OptionsDictException, \
    NodeInfoException


class UnitOptionsDict(OptionsDict):
    """
    This is OptionsDict decoupled from the NodeInfo and NodeFormat
    implementations for unit testing purposes.
    """
    def create_node_info_formatter(self, which=None):
        return lambda node_info, absolute, relative: ''


class UnitNodeInfo:
    """
    Throwaway NodeInfo implementation for unit testing purposes.
    """
    def __init__(self, name):
        self.name = name
    
    def belongs_to_any(self, collection_names):
        return False
        
    def get_string(self, absolute=None, relative=None,
                   collection_separator=None, only_indent=False):
        return self.name
    
    def copy(self):
        raise NotImplementedError
        
    def belongs_to(self, collection_name):
        raise NotImplementedError
        
    def at(self, index):
        raise NotImplementedError
        
    def is_first(self):
        raise NotImplementedError
        
    def is_last(self):
        raise NotImplementedError
