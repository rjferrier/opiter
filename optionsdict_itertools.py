from collections import Iterable
from itertools import imap, izip, chain, product

def flatten(iterable):
    """
    flatten(iterable)

    Flatten an arbitrary tree of iterators, e.g. (1, (2, 3)) -> (1, 2,
    3).  Taken from the webpage below, with an added condition to stop
    iterating if the iterable is an OptionsDict.
    
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
    performs a product.  The results are chained.
    """
    def protect(el):
        # if (isinstance(el, basestring) and len(el) > 1) or \
        #         isinstance(el, dict):
        #     yield el
        return el
    return chain.from_iterable(
        imap(lambda i: product(*i),
             izip(imap(protect, parents),
                  children)))


def combine(client_function):
    """
    combine(client_function)

    A decorator that flattens and sums the elements of a collection,
    passing the result to the client function.
    
    This may be useful in situations where one wants to use itertools
    to iterate over combinations of OptionDicts.  The handling of
    lists of OptionsDicts should not be something that the client
    function has to deal with.  This decorator merges those
    OptionsDicts into one convenient dictionary that the client can
    use.
    """
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
    @combine
    def lookup(opt):
        return opt[key]
    return lookup

