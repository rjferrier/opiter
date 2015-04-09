import sys
sys.path.append('..')

import numpy as np
from options import OptionsDict
from tools import product, merge, merges_dicts

from multiprocessing import Pool
from time import time, sleep
from copy import deepcopy


## INPUTS

n_proc = 2
n_samples = 4
modifiers = [0.5, 1]
job_times = [0.1, 0.3]

## PREPROCESSING

# create iterable structure and some operation
modifier_seq = OptionsDict.sequence('modifier', modifiers)
job_time_seq = OptionsDict.sequence('job_time', job_times)
combos = product(modifier_seq, job_time_seq)

sleep_time = lambda opt: opt['modifier'] * opt['job_time']
@merges_dicts
def dummy_operation_time(opt):
    return sleep_time(opt)
@merges_dicts
def dummy_operation(opt):
    sleep(sleep_time(opt))

print "\nIteration over jobs with total times:"
print map(dummy_operation_time, combos)

p = Pool(n_proc)
n_test = 3
results_fmt = "{0:11.3f}{1:12.3f}{2:12.3f}"
T = np.array(np.zeros((n_samples, n_test)))

print
print " trial#     serial        parallel(n={0})".format(n_proc)
print "           forward     forward     reverse"
    
## PROCESSING
    
for i in range(n_samples):
    for j in range(n_test):
        t0 = time()
        if j==0:
            map(dummy_operation, combos)
        elif j==1:
            p.map(dummy_operation, combos)
        else:
            p.map(dummy_operation, reversed(combos))
        T[i,j] = time() - t0
    # report
    print "{0:5g} ".format(i+1) + results_fmt.format(*T[i])

p.close()
print 
print "  ave."+results_fmt.format(*T.mean(axis=0))
