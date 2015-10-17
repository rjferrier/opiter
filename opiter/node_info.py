from base import OptionsBaseException


class Position:
    """
    Records position in a collection.
    """
    def __init__(self, index, collection_size):
        self.index = index
        self.collection_size = collection_size

    def is_at(self, index):
        """
        Checks that the position corresponds to the given index, which if
        negative is relative to the end of the collection.
        """
        return self.index == index or \
            self.index == index + self.collection_size
    
    def is_first(self):
        return self.is_at(0)
        
    def is_last(self):
        return self.is_at(-1)
        
    def __eq__(self, other):
        result = isinstance(other, Position)
        if result:
            result *= self.index == other.index
            result *= self.collection_size == other.collection_size
        return result

    
class NodeInfoException(OptionsBaseException):
    pass

    
class NodeInfo:
    """
    Abstract class for describing contextual information about a node.
    The concrete methods herein are special cases which defer to the
    more general subclass methods.
    """
    def __init__(self, index, collection_size, tags=[]):
        self.position = self.create_position(index, collection_size)
        if isinstance(tags, str):
            raise NodeInfoException(
                "tags must be a list or iterable of strings")
        self.tags = tags
        
    def create_position(self, node_index, array_length):
        """
        Overrideable factory method.
        """
        return Position(node_index, array_length)
        
    def belongs_to_any(self, collection_names_or_tags):
        """
        Returns True if the node in question is associated with any of
        collection_names_or_tags.
        """
        for nm_tg in collection_names_or_tags:
            if self.belongs_to(nm_tg) or nm_tg in self.tags:
                return True
        return False

    def _create_index(self, default, absolute, relative):
        # Helper to subclass get_string() methods
        if absolute is None:
            index = default
        else:
            index = absolute
        if relative is not None:
            index += relative
            if index < 0:
                raise IndexError("list index out of range")
        return index
        
    def __str__(self):
        return self.get_string()
