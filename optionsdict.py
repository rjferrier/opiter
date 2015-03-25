from types import FunctionType 
from copy import copy 


class OptionsDictException(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg

        
class OptionsDict(dict):
    """
    OptionsDict(name, entries={})
    
    An OptionsDict inherits from a conventional dict, but it has a few
    enhancements:

    (1) Values can be runtime-dependent upon the state of other values
    in the dict.  Each of these special values is specified by a
    function accepting a single dictionary argument (i.e. the
    OptionsDict itself).  The dictionary argument is used to look
    things up dynamically.  

    (2) OptionsDicts can be added together, in which case their names
    will be concatenated and their entries merged.
    
    """
    def __init__(self, name, entries={}):
        if isinstance(name, str):
            self.name = name
        else:
            raise OptionsDictException(
                "name argument must be a string.")
        # the dict superclass will check that the entries argument is
        # acceptable
        dict.__init__(self, entries)

    def __repr__(self):
        return self.name
            
    def __getitem__(self, key):
        value = dict.__getitem__(self, key)
        # recurse until the return value is no longer a function
        if isinstance(value, FunctionType):
            return value(self)
        else:
            return value
            
            
class CallableEntry:
    """
    CallableEntry(function)

    Because the OptionsDict works by evaluating all function objects
    recursively, it is not able to return other functions specified by
    the client unless these are wrapped as callable objects.  This
    class provides such a wrapper.
    """
    def __init__(self, function):
        self.function = function
        
    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)

    
        
def create_sequence(optionsdicts_or_names, common_entries={}):
    """
    create_sequence(optionsdicts_or_names, common_entries={})

    Creates a list of OptionsDicts after type-checking the arguments
    and converting to OptionsDicts if necessary.  The optional
    common_entries argument is passed to all the OptionsDicts.
    """
    options_dict_list = []
    for od_or_nm in optionsdicts_or_names:
        # create an OptionsDict from od_or_nm
        if isinstance(od_or_nm, OptionsDict):
            # If od_or_nm is already an OptionsDict object, make a
            # copy.  This has the benefit of preventing side
            # effects if od_or_nm persists elsewhere.
            od = copy(od_or_nm)
            od.update(common_entries)
        else:
            # instantiate a new OptionsDict
            od = OptionsDict(od_or_nm, common_entries)
        options_dict_list.append(od)
    return options_dict_list

