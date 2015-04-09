from collections import Iterable
from itertools import imap, izip, chain, product
from functools import wraps
from copy import copy
from inspect import getargspec, getargvalues

def flatten(iterable):
    """
    flatten(iterable)

    Flatten an arbitrary tree of iterators, e.g. (1, (2, 3)) -> (1, 2,
    3).  Taken from the webpage below, with an added condition to stop
    iterating if the iterable is a dictionary.
    
    http://stackoverflow.com/questions/2158395/
    flatten-an-irregular-list-of-lists-in-python
    """
    for el in iterable:
        if isinstance(el, Iterable) and \
                not isinstance(el, basestring) and \
                not isinstance(el, dict):
            for sub in flatten(el):
                yield sub
        else:
            yield el

            
def attach(parents, children):
    """
    attach(parents, children)

    Zips parents with children, and for each of these pairings
    performs a product.  The results are chained.  Strings and
    dictionary elements are protected so that their elements don't
    explode.
    """
    def protect(el):
        if (isinstance(el, basestring) and len(el) > 1) or \
                isinstance(el, dict):
            return (el,)
        else:
            return el
    return chain.from_iterable(
        imap(lambda i: product(*i),
             izip(imap(protect, parents),
                  children)))


def merge(dict_combination):
    """
    merge(dict_combination)

    Flattens and merges a combination of dictionaries.  This may be
    useful when one wants to iterate over a collection of combinations
    produced by itertools.
    """
    single_dict = None
    if isinstance(dict_combination, dict):
        dict_combination = (dict_combination,)
    for el in flatten(dict_combination):
        if single_dict is None:
            single_dict = copy(el)
        else:
            single_dict.update(el)
    return single_dict

    
def merges_dicts(client_function):
    """
    merges_dicts(client_function)

    A decorator that flattens and merges a combination of
    dictionaries, passing the result to the client function.  This may
    be useful when one wants to map the function to a collection of
    combinations produced by itertools.
    """
    if len(getargspec(client_function)[0])==2:
        # client_function has two args so is presumably bound to
        # something
        @wraps(client_function)
        def decorator(self, dict_combination):
            return client_function(self, merge(dict_combination))
    else:
        @wraps(client_function)
        def decorator(dict_combination):
            return client_function(merge(dict_combination))
    return decorator


@merges_dicts
def identify(dictionary):
    """
    identify(dict_combination)

    Simply gets the string representation of a dictionary or combination
    of dictionaries.
    """
    return str(dictionary)
    

class Lookup:
    """
    Lookup(key)
    
    Provides a functor that simply looks up a key in a dictionary or
    combination of dictionaries.  This functionality was originally
    implemented as a closure, but the multiprocessing module couldn't
    pickle it.
    """
    def __init__(self, key):
        self.key = key

    @merges_dicts
    def __call__(self, dictionary):
        return dictionary[self.key]
