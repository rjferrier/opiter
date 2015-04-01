======================================================================
 options_iteration
======================================================================

The classes and functions in this module can be used to create and
assemble combinations of options dictionaries (OptionsDicts) for
iterating over.  Each OptionsDict can be defined with a set of
variable values that the client can access and use for the purpose of
template expansion, input to a binary, postprocessing, etc.

One application of this is factorial design of experiments.  For
example, given an independent variable 'speed', which may take states
10, 20, ..., and an independent variable 'travel_time', which may take
states 0.5, 1.0, ..., we might want to test combinations (10, 0.5),
(10, 1.0), ..., (20, 0.5), (20, 1.0), ..., etc.  These combinations
can be expressed by creating two sequences of OptionsDicts and using
product() from the itertools library.

  combos = product(create_sequence('speed', [10, 20, ...]), 
                   create_sequence('travel_time', [0.5, 1.0, ...])

A combination of OptionsDicts can be merged so that the client only
ever needs to consult one OptionsDict.  Additionally, when an
OptionsDict is instantiated via create_sequence, it acquires the
special entry {sequence_name: node_value}.  This entry may be
interpreted as the name and value of an independent variable.  In the
above example, values for the two independent variables may be
accessed like this:

  for combo in combos:
     opt = merge(combo)
     print 'distance =', opt['speed'] * opt['travel_time']

A serial 'for' loop is not the only means performing a batch of
operations.  The operations can be encoded as a function taking a
single dictionary argument and passed to a mapping function for
parallel iteration.  The @merges_dicts decorator takes care of the
OptionsDict merging.

  @merges_dicts
  def calc_distance(opt):
     opt['speed'] * opt['travel_time']
  p = multiprocessing.Pool(4)
  distances = p.map(calc_distance, combos)

In practice, the client may have to deal with many dependent variables
that would clutter the function body.  For this reason, OptionsDicts
have some extra functionality compared to conventional dicts.  Entries
can be defined as dynamic, updating automatically according to the
values of others.  We might define such a dynamic entry at the root of
a tree; then all combinations will acquire this entry.

  root = create_node('main', {
      'distance': lambda self: self['speed'] * self['travel_time']})
  combos = product(root,
                   create_sequence('speed', [10, 20, ...]), 
                   create_sequence('travel_time', [0.5, 1.0, ...]))
