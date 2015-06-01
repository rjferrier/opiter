import sys
sys.path.append('..')

from __init__ import OptionsNode, OptionsArray, OptionsDict, Lookup
import multiprocessing

# setup

water = OptionsNode('water', {
    'density'           : 1.00e3,
    'dynamic_viscosity' : 0.89e-3})

ethanol = OptionsNode('ethanol', {
    'density'           : 0.79e3,
    'dynamic_viscosity' : 1.09e-3})

fluids     = OptionsArray('fluid', [water, ethanol])
pipe_dias  = OptionsArray('pipe_diameter', [0.10, 0.15])
velocities = OptionsArray('velocity', [0.01, 0.02, 0.04])
options_tree = fluids * pipe_dias * velocities

print "\nUsing serial loop:\n"

for opt in options_tree.collapse():
    kinematic_visc = opt['dynamic_viscosity'] / opt['density']
    Re = opt['velocity'] * opt['pipe_diameter'] / kinematic_visc
    print 'ID = {}, Reynolds number = {:.2e}'.format(opt.str(), Re)

print "\nUsing parallel iterator:\n"

def calculate_Re(opt):
  kinematic_visc = opt['dynamic_viscosity'] / opt['density']
  return opt['velocity'] * opt['pipe_diameter'] / kinematic_visc

p = multiprocessing.Pool(4)
Reynolds_numbers = p.map(calculate_Re, options_tree.collapse())

# for completeness...
def label(opt):
  return opt.str()
for descr, Re in zip(map(label, options_tree.collapse()), Reynolds_numbers):
    print 'ID = {}, Reynolds number = {:.2e}'.format(opt.str(), Re)
    

print "\nUsing dynamic entries:\n"

def kinematic_viscosity(opt):
    return opt['dynamic_viscosity'] / opt['density']
fluids = OptionsArray('fluid', [water, ethanol], 
                      common_entries=[kinematic_viscosity])
options_tree = fluids * pipe_dias * velocities

def Reynolds_number(opt):
    return opt['velocity'] * opt['pipe_diameter'] / opt['kinematic_viscosity']
options_tree.update(OptionsDict([Reynolds_number]))

p = multiprocessing.Pool(4)
Reynolds_numbers = p.map(Lookup('Reynolds_number'), options_tree.collapse())

# for completeness...
for descr, Re in zip(map(label, options_tree.collapse()), Reynolds_numbers):
    print 'ID = {}, Reynolds number = {:.2e}'.format(descr, Re)
