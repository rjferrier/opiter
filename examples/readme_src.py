import sys
sys.path.append('..')

from options import OptionsDict
from tools import product, merge, merges_dicts, identify, Lookup
import multiprocessing

# setup

water = OptionsDict.named('water', {
    'density'           : 1.00e3,
    'dynamic_viscosity' : 0.89e-3})

ethanol = OptionsDict.named('ethanol', {
    'density'           : 0.79e3,
    'dynamic_viscosity' : 1.09e-3})

fluids     = [water, ethanol]
pipe_dias  = OptionsDict.sequence('pipe_diameter', [0.10, 0.15])
velocities = OptionsDict.sequence('velocity', [0.01, 0.02, 0.04])
combos = product(fluids, pipe_dias, velocities)

print "\nUsing serial loop:\n"

for combo in combos:
    opt = merge(combo)
    ID = str(opt)
    kinematic_visc = opt['dynamic_viscosity'] / opt['density']
    Re = opt['velocity'] * opt['pipe_diameter'] / kinematic_visc
    print 'Test ID = {}, Reynolds number = {:.2e}'.\
        format(ID, Re)


print "\nUsing parallel iterator:\n"

@merges_dicts
def calculate_Re(opt):
  kinematic_visc = opt['dynamic_viscosity'] / opt['density']
  return opt['velocity'] * opt['pipe_diameter'] / kinematic_visc

p = multiprocessing.Pool(4)
Reynolds_numbers = p.map(calculate_Re, combos)

# for completeness...
IDs = map(identify, combos)
for ID, Re in zip(IDs, Reynolds_numbers):
    print 'Test ID = {}, Reynolds number = {:.2e}'.\
        format(ID, Re)
    

print "\nUsing dynamic entries:\n"

def kinematic_viscosity(opt):
    return opt['dynamic_viscosity'] / opt['density']
fluids = OptionsDict.sequence('fluid', [water, ethanol], 
                              common_entries=[kinematic_viscosity])

def Reynolds_number(opt):
    return opt['velocity'] * opt['pipe_diameter'] / \
        opt['kinematic_viscosity']
common = OptionsDict([Reynolds_number])

combos = product(common, fluids, pipe_dias, velocities)
p = multiprocessing.Pool(4)
Reynolds_numbers = p.map(Lookup('Reynolds_number'), combos)

# for completeness...
IDs = map(identify, combos)
for ID, Re in zip(IDs, Reynolds_numbers):
    print 'Test ID = {}, Reynolds number = {:.2e}'.\
        format(ID, Re)
