=======================================================================
 optionsdict
=======================================================================

The classes in this module can be used to create options dictionaries
(OptionsDicts) and build trees of OptionsDict combinations to iterate
over.  Each OptionsDict can be defined with a set of variable values
that one can access and use for the purpose of template expansion,
input to a binary, postprocessing, etc.

One application of this is factorial design of experiments.  Given an
independent variable 'speed', which may take states 10, 20, ..., and
an independent variable 'travel_time', which may take states 0.5, 1.0,
..., we might want to test combinations (10, 0.5), (10, 1.0), ...,
(20, 0.5), (20, 1.0), ..., etc.  These combinations are easily
expressed by creating two sequences of OptionsDicts and using
product() from the standard itertools library.

  combos = product(create_sequence('speed', [10, 20, ...]), 
                   create_sequence('travel_time', [0.5, 1.0, ...])

A combination of OptionsDicts iterators can be merged so that client
only ever needs to deal with one OptionsDict at a time.  Additionally,
when an OptionsDict is instantiated via create_sequence, it acquires
the special entry {sequence_name: node_value}.  This entry may be read
as the name and value of the independent variable.

  for combo in combos:
     opt = sum(combo)
     print 'distance =', opt['speed'] * opt['travel_time']

Clients need not loop through combinations in serial when performing a
batch of operations.  An operation can be encoded as a function taking
a single dictionary argument and passed to a mapping for parallel
iteration.  A @combine decorator takes care of flattening the
combination of OptionsDicts iterators, if they are nested, and merging
them.

  from IPython import dview
  @combine
  def calc_distance(opt):
     opt['speed'] * opt['travel_time']
  distances = dview.map(calc_distance, combos)

In practice, the client may have to deal with many dependent variables
that would clutter the code.  For this reason, OptionsDicts have some
extra functionality.  Entries can be defined as dynamic, updating
automatically according to the values of others.  We might define such
a dynamic entry at the root of a tree; then all combinations will
acquire this entry.

  main = OptionsDict('main', {
      'distance': lambda self: self['speed'] * self['travel_time']})
  combos = product((main,)
                   create_sequence('speed', [10, 20, ...]), 
                   create_sequence('travel_time', [0.5, 1.0, ...]))
