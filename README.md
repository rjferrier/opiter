# Options Iteration

The classes in this module can be used to assemble combinations of
options dictionaries for iterating over.  Each dictionary can be
defined with a set of variable values that the client can access and
use for the purpose of template expansion, input to a binary,
postprocessing, etc.

```python
water = OptionsNode('water', {
    'density'           : 1.00e3,
    'dynamic_viscosity' : 0.89e-3})

ethanol = OptionsNode('ethanol', {
    'density'           : 0.79e3,
    'dynamic_viscosity' : 1.09e-3})
```

One application of this is factorial design of experiments.  For
example, given an independent variable `pipe_diameter`, which may take
states [0.10, 0.15], and an independent variable `velocity`, which
may take states [0.01, 0.02, 0.04], we might want to test
combinations (0.10, 0.01), (0.10, 0.02), etc.  We might also want
to do this for each of the fluids specified above.

These combinations are easily expressed by creating arrays of
dictionaries and 'multiplying' them.  The result is a tree of options.
  
```python
fluids     = OptionsArray('fluid', [water, ethanol])
pipe_dias  = OptionsArray('pipe_diameter', [0.10, 0.15])
velocities = OptionsArray('velocity', [0.01, 0.02, 0.04])
options_tree = fluids * pipe_dias * velocities
```

An options tree may be collapsed to form a single list of
`OptionsDict`s.  Each of these dictionaries contains a different
combination of variable values that can be accessed through the usual
syntax.  There is also a `str()` method which can be used to form an
ID.
  
```python
for opt in options_tree.collapse():
    kinematic_visc = opt['dynamic_viscosity'] / opt['density']
    Re = opt['velocity'] * opt['pipe_diameter'] / kinematic_visc
    print 'ID = {}, Reynolds number = {:.2e}'.format(opt.str(), Re)
```
  
A serial `for` loop is not the only means of performing a batch of
operations.  The operations can be encoded as a function taking a
single dictionary argument.  This can then be passed to a parallel map
function.
  
```python
def calculate_Re(opt):
  kinematic_visc = opt['dynamic_viscosity'] / opt['density']
  return opt['velocity'] * opt['pipe_diameter'] / kinematic_visc

p = multiprocessing.Pool(4)
Reynolds_numbers = p.map(calculate_Re, options_tree.collapse())
```

In practice, the client may have to deal with many dependent variables
that would clutter the function body.  For this reason, `OptionsDict`s
have some extra functionality compared to conventional dicts.  Entries
can be defined as dynamic, updating automatically according to the
values of others.  Such dynamic entries might be added locally, or in
a separate `OptionsDict` which is then applied globally.
  
```python
def kinematic_viscosity(opt):
    return opt['dynamic_viscosity'] / opt['density']
fluids = OptionsArray('fluid', [water, ethanol], 
                      common_entries=[kinematic_viscosity])

def Reynolds_number(opt):
    return opt['velocity'] * opt['pipe_diameter'] / opt['kinematic_viscosity']
common = OptionsNode(None, [Reynolds_number])

options_tree = common * fluids * pipe_dias * velocities
p = multiprocessing.Pool(4)
Reynolds_numbers = p.map(Lookup('Reynolds_number'), options_tree.collapse())
```

