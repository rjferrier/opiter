


class SimpleFormatter:
    """
    Function object that represents a combination of nodes as
    c0:n0_c1:n1_c2:n2, where ci and ni are the collection and node
    names associated with the i'th node.  The ':' and '_' separators
    can be defined upon initialisation.
    """
    def __init__(self, node_separator='_', collection_separator=None):
        self.node_separator = node_separator
        self.collection_separator = collection_separator

    def __call__(self, node_info_list, absolute={}, relative={}, 
                 only_indent=False):
        if only_indent:
            return ''
        substrings = []
        for ni in node_info_list:
            substr = ''
            substr += ni.str(absolute=absolute, relative=relative, 
                             collection_separator=self.collection_separator)
            if substr:
                substrings.append(substr)
        if node_info_list:
            result = self.node_separator.join(substrings)
        else:
            result = ''.join(substrings)
        return result

        
class TreeFormatter:
    """
    Function object that represents a combination of nodes as a tree
    fragment, e.g.
    c0:n0
        c1:n1
            c2:n2
    where ci and ni are the collection and node names associated with
    the i'th node.  The indent and the ':' separator can be defined
    upon initialisation.

    When the object is made to operate on a complete list of node
    combinations in serial, the complete tree emerges.
    """
    def __init__(self, indent_string=' '*4, collection_separator=': '):
        self.indent_string = indent_string
        self.collection_separator = collection_separator
 
    def __call__(self, node_info_list, absolute={}, relative={}, 
                 only_indent=False):
        branch = ''
        indent = ''
        for level, ni in enumerate(node_info_list):
            # get a descriptor for the current node
            substr = ni.str(absolute=absolute, relative=relative, 
                            collection_separator=self.collection_separator)

            # if not the first node, the branch up to this point will
            # have already been printed, so reset the branch
            if not ni.is_first():
                branch = ''

            # cycle if blank
            if not substr:
                continue

            # if we are not at the root, do a newline in preparation
            # for the new node
            if branch:
                branch += '\n'

            # add the node to the branch and increase the indent for
            # next time
            branch += indent + substr
            indent += self.indent_string

        if only_indent:
            return indent
        else:
            return branch
