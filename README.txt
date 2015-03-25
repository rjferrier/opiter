=======================================================================
 optionsdict
=======================================================================

The classes in this module can be used to build a tree of options
dictionaries to iterate over.  Each level of the tree is represented
by an OptionSequence containing several Options.  Each Option may have
a child OptionSequence, and so on down to an arbitrary number of
levels.


*** THE FUNCTIONALITY DESCRIBED BELOW HAS NOT BEEN IMPLEMENTED YET ***

One application of option trees is factorial design of experiments.
Given an independent variable A, which may take states 1, 2, ..., and
an independent variable B, which may take states i, ii, ..., we might
want to test combinations 1i, 1ii, ..., 2i, 2ii, ..., etc.  These
combinations are easily expressed by multiplying OptionSequences
together:

  options = OptionSequence('A', ['1', '2', ...]) * \
            OptionSequence('B', ['i', 'ii', ...])

When a client iterates over an options tree, he or she steps through
the Options in turn.  Each Option has an corresponding set of variable
values that the client can access through a dictionary and use for the
purpose of template expansion, input to a binary, postprocessing, etc.
The dictionary encompasses all levels from the current Option up to
the root of the tree, and so the client has access to all variables
associated with a given combination of options.

In practice, some variables depend on Options at multiple levels.  For
this reason, Option dictionaries have been given some extra
functionality.  Entries can be defined as "dynamic", updating
automatically according to the values of others.  For instance, we
might define such a dynamic entry at the root of a tree:

  main = Option('main', {
      'distance': lambda self: self['speed'] * self['travel_time'],
      })

Then we might build and iterate over the rest of the tree as follows:

  options = main * \
            OptionSequence('speed', [30, 40, 60]) * \
            OptionSequence('travel_time', [0.5, 1, 1.5])
  for opt in options:
      print opt[distance]

This prints out the values 15, 30, 45, 20, 40, etc.
