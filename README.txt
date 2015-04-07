======================================================================
 options_iteration
======================================================================

The classes and functions in this module can be used to assemble
combinations of options dictionaries (OptionsDicts) for iterating
over.  Each OptionsDict can be defined with a set of variable values
that the client can access and use for the purpose of template
expansion, input to a binary, postprocessing, etc.
  
  water = OptionsDict.named('water', {
      'density'           : 1.00e3,
      'dynamic_viscosity' : 0.89e-3})
  
  ethanol = OptionsDict.named('ethanol', {
      'density'           : 0.79e3,
      'dynamic_viscosity' : 1.09e-3})

One application of this is factorial design of experiments.  For
example, given an independent variable 'pipe_diameter', which may take
states [0.10, 0.15], and an independent variable 'velocity', which may
take states [0.01, 0.02, 0.04], we might want to test combinations
(0.10, 0.01), (0.10, 0.02), etc.  We might also want to do these for
each of the 'fluids' specified above.  These combinations are easily
expressed by creating sequences of OptionsDicts and using product()
from the itertools library.
  
  fluids     = OptionsDict.sequence('fluid', [water, ethanol])
  pipe_dias  = OptionsDict.sequence('pipe_diameter', [0.10, 0.15])
  velocities = OptionsDict.sequence('velocity', [0.01, 0.02, 0.04])
  combos = itertools.product(fluids, pipe_dias, velocities)

A combination of OptionsDicts can be merged so that the client only
ever needs to consult one OptionsDict.  The string representation of
the merged OptionsDict gives the client a unique identifier for the
combination.  The client can look up any variable in the dictionary
through the usual syntax.
  
  for combo in combos:
      opt = merge(combo)
      ID = str(opt)
      kinematic_visc = opt['dynamic_viscosity'] / opt['density']
      Re = opt['velocity'] * opt['pipe_diameter'] / kinematic_visc
      print 'Test ID = {}, Reynolds number = {:.2e}'.\
          format(ID, Re)
  
A serial 'for' loop is not the only means of performing a batch of
operations.  The operations can be encoded as a function taking a
single dictionary argument.  This can then be passed to a parallel map
function.  The @merges_dicts decorator takes care of the dictionary
merging.
  
  @merges_dicts
  def calculate_Re(opt):
    kinematic_visc = opt['dynamic_viscosity'] / opt['density']
    return opt['velocity'] * opt['pipe_diameter'] / kinematic_visc
  p = multiprocessing.Pool(4)
  Reynolds_numbers = p.map(calculate_Re, combos)

In practice, the client may have to deal with many dependent variables
that would clutter the function body.  For this reason, OptionsDicts
have some extra functionality compared to conventional dicts.  Entries
can be defined as dynamic, updating automatically according to the
values of others.  Such dynamic entries might be added locally, or in
a separate OptionsDict which is then applied globally.
  
  def calculate_kinematic_visc(opt):
      return opt['dynamic_viscosity'] / opt['density']
  fluids = OptionsDict.sequence('fluid', [water, ethanol], 
      common_entries={
          'kinematic_viscosity': calculate_kinematic_visc})
  
  def calculate_Re(opt):
      return opt['velocity'] * opt['pipe_diameter'] / \
          opt['kinematic_viscosity']
  root = OptionsDict({'Reynolds_number': calculate_Re})
  
  combos = itertools.product(root, fluids, pipe_dias, velocities)
  p = multiprocessing.Pool(4)
  Reynolds_numbers = p.map(Lookup('Reynolds_number'), combos)

