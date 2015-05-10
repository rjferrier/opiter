"""
This module takes advantage of the Mock class to decouple the
OptionsDict and NodeInfo classes.  If mock.Mock isn't available, we
can still run tests with the classes coupled - but they will be
integration tests rather than unit tests.
"""

from options import OptionsDict, OptionsDictException, \
    OrphanNodeInfo, ArrayNodeInfo

try:
    from unittest.mock import Mock
    HAVE_MOCK = True
except ImportError:
    try:
        from mock import Mock
        HAVE_MOCK = True
    except ImportError:
        HAVE_MOCK = False
        import warnings

        
if HAVE_MOCK:
    class OptionsDictUnderTest(OptionsDict):
        """
        This is OptionsDict decoupled from the NodeInfo implementations
        for unit testing purposes.  The mock OrphanNodeInfo and
        ArrayNodeInfo objects it creates will respond to str() simply
        by returning the OptionsDict's original name.  This way we can
        examine how OptionsDict manages its NodeInfo objects.
        """
        @classmethod
        def node(Self, name, entries={}):
            obj = OptionsDict.node(name, entries)
            obj.original_name = name
            return obj

        def create_orphan_node_info(self, node_name):
            ni = Mock(spec=OrphanNodeInfo)
            ni.str.return_value = self.original_name
            return ni

        def create_array_node_info(self, array_name, node_names, node_index):
            ni = Mock(spec=OrphanNodeInfo)
            ni.str.return_value = self.original_name
            return ni
            
else:
    class OptionsDictUnderTest(OptionsDict):
        """
        This is simply the original OptionsDict that creates full
        OrphanNodeInfo and ArrayNodeInfo objects.
        """
        pass
    
    warnings.warn("""
    mock module not found.  Unit tests with mock objects will be
    replaced by integration tests with full objects.
    """)

