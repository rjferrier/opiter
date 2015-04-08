# provide the main classes directly so that the client can do "from
# options_iteration import OptionsDict", etc.
from options import OptionsDict, OptionsDictException, CallableEntry

# everything else will be accessible via the subpackage syntax,
# e.g. "from options_iteration.tools import merge".
