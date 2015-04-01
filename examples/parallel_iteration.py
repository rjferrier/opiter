import sys
sys.path.append('..')

import numpy as np
from options import create_sequence
from tools import merges_dicts

from multiprocessing import Pool
from time import time, sleep
from copy import deepcopy


## INPUTS

n_proc = 2
n_samples = 4
job_times = [0.1, 0.1, 0.2]


## PREPROCESSING

# create iterable structure and some operation
combos = create_sequence('sleep_time', job_times)
@merges_dicts
def operation(opt):
    sleep(opt['sleep_time'])
    
print "\nIteration over jobs with times {0}:".format(job_times)

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
            map(operation, combos)
        elif j==1:
            p.map(operation, combos)
        else:
            p.map(operation, reversed(combos))
        T[i,j] = time() - t0
    # report
    print "{0:5g} ".format(i+1) + results_fmt.format(*T[i])

p.close()
print 
print "  ave."+results_fmt.format(*T.mean(axis=0))
