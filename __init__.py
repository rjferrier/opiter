# provide the main classes directly so that the client can do "from
# options_iteration import OptionsDict", etc.
from options_dict import OptionsDict
from options_node import OptionsNode
from options_array import OptionsArray

# provide some useful stuff
from options_dict import CallableEntry, Lookup, GetString, \
    transform_entries, unlink, Check, Remove, \
    missing_dependencies, unpicklable
from options_array import OptionsArrayFactory
from options_tree_elements import product
from utilities import pretty_print, smap, pmap, \
    ExpandTemplate, RunProgram, SimpleTemplateEngine, \
    Jinja2TemplateEngine

# everything else will be accessible via the subpackage syntax,
# e.g. "from options_iteration.options_dict import OptionsDictException".
