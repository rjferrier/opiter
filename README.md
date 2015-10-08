# Options Iteration

The classes in this package can be used to assemble and iterate over
combinations of options.  Each set of options is represented by a
dictionary that the client can define with variable values and access
for the purpose of template expansion, input to a binary,
postprocessing, etc.

One application of this is factorial design of experiments.  For
example, given an independent variable `pipe_diameter`, which may take
states [0.10, 0.15], and an independent variable `velocity`, which may
take states [0.01, 0.02, 0.04], we might want to test combinations
(0.10, 0.01), (0.10, 0.02), etc.  These combinations are easily
expressed by creating arrays of options and using the multiplication
operator to produce a tree.
  
```python
pipe_dias  = OptionsArray('pipe_diameter', [0.10, 0.15])
velocities = OptionsArray('velocity', [0.01, 0.02, 0.04])
options_tree = pipe_dias * velocities
```

We might also want to do this for fluids with different properties.
The properties may be represented by a dictionary which is wrapped by
a named `OptionsNode`, or for syntactic convenience they may be
represented by a class.

```python
class water:
    density = 1.00e3
    dynamic_viscosity = 0.89e-3

class ethanol:
    density = 0.79e3
    dynamic_viscosity = 1.09e-3
    
options_tree *= OptionsArray('fluid', [water, ethanol])
```

An options tree may be collapsed to form a single list of options
dictionaries.  Each of these `OptionsDict`s merges a combination of
options which can be accessed either through the usual dictionary
syntax or through the dot operator.  There is also a `get_string`
method which can be used to identify the combination.
  
```python
options_dicts = options_tree.collapse()

for opt in options_dicts:
    kinematic_visc = opt.dynamic_viscosity / opt.density
    Re = opt.velocity * opt.pipe_diameter / kinematic_visc
    print '{:20s}: Reynolds number = {:.2e}'.\
        format(opt.get_string(), Re)
```
  
A serial `for` loop is not the only means of performing a batch of
operations.  The operations can be encoded as a function taking a
single dictionary argument.  This can be passed to a multiprocessing
map function.
  
```python
def calculate_Re(opt):
  kinematic_visc = opt.dynamic_viscosity / opt.density
  return opt.velocity * opt.pipe_diameter / kinematic_visc

p = multiprocessing.Pool(4)
Reynolds_numbers = p.map(calculate_Re, options_dicts)
```

In practice, the client may have to deal with many dependent variables
that would clutter the function body.  For this reason, an
`OptionsDict` has some extra functionality compared to a conventional
dict.  Entries can be defined as dependent, updating automatically
according to the values of others.  Such dependent entries may be
defined by (possibly inherited) methods in the classes used to
construct the options...

```python
class fluid:
    def kinematic_viscosity(self):
        return self.dynamic_viscosity / self.density

class water(fluid):
    density = 1.00e3
    dynamic_viscosity = 0.89e-3

class ethanol(fluid):
    density = 0.79e3
    dynamic_viscosity = 1.09e-3

fluids = OptionsArray('fluid', [water, ethanol])
options_tree = pipe_dias * velocities * fluids
```

...or they may be defined by lambdas or free functions.  The options
tree structure has an update method for broadcasting new entries to
all of its nodes.

```python
options_tree.update({
    'Reynolds_number': lambda opt: opt.velocity * opt.pipe_diameter /
    opt.kinematic_viscosity})

def observation(opt):
    if opt.Reynolds_number < 2100.:
        return 'laminar'
    elif opt.Reynolds_number < 4000.:
        return 'transitional'
    else:
        return 'turbulent'
options_tree.update([observation])
```
 
A caveat is that dependent entries may have to be converted back to
independent values before multiprocessing.  This is because Python's
`pickle` module has trouble serialising anonymous and locally defined
functions.  Template engines such as Jinja2 may also need dependent
entries to be converted back to regular dictionary entries.  A
`transform_entries` function is provided for such a purpose.  It
accepts function objects such as `unlink`, `check` and `remove` to
help the user deal with troublesome entries.

```python
options_dicts = options_tree.collapse()
Reynolds_numbers = p.map(Lookup('Reynolds_number'),
                         transform_entries(options_dicts, unlink))
```
