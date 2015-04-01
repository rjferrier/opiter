from collections import Iterable
from itertools import imap, izip, chain, product
from functools import wraps
from copy import copy

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

            
def multizip(parents, children):
    """
    multizip(parents, children)

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
    @wraps(client_function)
    def decorator(dict_combination):
        return client_function(
            merge(dict_combination))
    return decorator


def create_lookup(key):
    """
    create_lookup(key)

    Returns a function that simply looks up a key when it is passed a
    combination of dictionaries.
    """
    @merges_dicts
    def lookup(single_dict):
        return single_dict[key]
    return lookup

