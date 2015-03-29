from collections import Iterable
from itertools import imap, izip, chain, product
from functools import wraps

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
    dictionary elements
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


def combine_args(client_function):
    """
    combine(client_function)

    A decorator that flattens and sums the elements of a collection,
    passing the result to the client function.
    
    This may be useful in situations where one wants to use itertools
    to iterate over trees of OptionDicts.  The handling of (possibly
    nested) combinations of OptionsDicts should not be something that
    the client has to deal with.  This decorator merges those
    OptionsDicts into one convenient dictionary that the client can
    use.
    """
    @wraps(client_function)
    def decorator(args):
        arg = sum(flatten(args))
        return client_function(arg)
    return decorator


def create_lookup(key):
    """
    create_lookup(key)

    Returns a function that simply looks up a key when it is passed a
    combination of OptionsDicts.
    """
    @combine_args
    def lookup(opt):
        return opt[key]
    return lookup

