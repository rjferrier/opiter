# Options Iteration

The classes and functions in this module can be used to assemble
combinations of options dictionaries (OptionsDicts) for iterating
over.  Each OptionsDict can be defined with a set of variable values
that the client can access and use for the purpose of template
expansion, input to a binary, postprocessing, etc.

```python
  water = OptionsDict.node('water', {
      'density'           : 1.00e3,
      'dynamic_viscosity' : 0.89e-3})
  
  ethanol = OptionsDict.node('ethanol', {
      'density'           : 0.79e3,
      'dynamic_viscosity' : 1.09e-3})
```

One application of this is factorial design of experiments.  For
example, given an independent variable `pipe_diameter`, which may take
states [0.10, 0.15], and an independent variable `velocity`, which
may take states [0.01, 0.02, 0.04], we might want to test
combinations (0.10, 0.01), (0.10, 0.02), etc.  We might also want
to do this for each of the fluids specified above.  These combinations
are easily expressed by creating arrays of OptionsDicts and using
`product` (adapted from the `itertools` library).
  
```python
  fluids     = OptionsDict.array('fluid', [water, ethanol])
  pipe_dias  = OptionsDict.array('pipe_diameter', [0.10, 0.15])
  velocities = OptionsDict.array('velocity', [0.01, 0.02, 0.04])
  combos = product(fluids, pipe_dias, velocities)
```

A combination of OptionsDicts can be merged so that the client only
ever needs to consult one OptionsDict.  The str() method can be used
to form an ID or print the combination in tree form.  The client can
look up any variable in the dictionary through the usual syntax.
  
```python
  for combo in combos:
      opt = merge(combo)
      descr = opt.str(formatter=TreeFormatter())
      kinematic_visc = opt['dynamic_viscosity'] / opt['density']
      Re = opt['velocity'] * opt['pipe_diameter'] / kinematic_visc
      print descr + '    Reynolds number = {:.2e}'.format(Re)
```
  
A serial `for` loop is not the only means of performing a batch of
operations.  The operations can be encoded as a function taking a
single dictionary argument.  This can then be passed to a parallel map
function.  The `@merges_dicts` decorator takes care of the dictionary
merging.
  
```python
  @merges_dicts
  def calculate_Re(opt):
    kinematic_visc = opt['dynamic_viscosity'] / opt['density']
    return opt['velocity'] * opt['pipe_diameter'] / kinematic_visc

  p = multiprocessing.Pool(4)
  Reynolds_numbers = p.map(calculate_Re, combos)
```

In practice, the client may have to deal with many dependent variables
that would clutter the function body.  For this reason, OptionsDicts
have some extra functionality compared to conventional dicts.  Entries
can be defined as dynamic, updating automatically according to the
values of others.  Such dynamic entries might be added locally, or in
a separate OptionsDict which is then applied globally.
  
```python
  def kinematic_viscosity(opt):
      return opt['dynamic_viscosity'] / opt['density']
  fluids = OptionsDict.array('fluid', [water, ethanol], 
                             common_entries=[kinematic_viscosity])
  
  def Reynolds_number(opt):
      return opt['velocity'] * opt['pipe_diameter'] / \
          opt['kinematic_viscosity']
  common = OptionsDict([Reynolds_number])
  
  combos = product(common, fluids, pipe_dias, velocities)
  p = multiprocessing.Pool(4)
  Reynolds_numbers = p.map(Lookup('Reynolds_number'), combos)
```

