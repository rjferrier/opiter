import sys
sys.path.append('..')

import numpy as np
import scipy as sp
from options import create_sequence
from tools import merges_dicts

from multiprocessing import Pool
from time import time


## INPUTS

n_proc = 4
n_samples = 10
matrix_size = 200

## SETUP

# define matrices
def create_random_matrix(matrix_size):
    A = np.zeros((matrix_size, matrix_size))
    for i in range(matrix_size):
        A[i] = np.random.rand(matrix_size)
    return sp.matrix(A)
A = create_random_matrix(matrix_size)
B = create_random_matrix(matrix_size)    

# create iterable structure and some operation 
combos = create_sequence('batch', range(2), {'A': A, 'B': B})
@merges_dicts
def operation(opt):
    opt['A'] * opt['B']


## PROCESSING

print " trial#     serial      parallel(n={0})".format(n_proc)
p = Pool(n_proc)

T = np.array(np.zeros((n_samples, 2)))
for i in range(n_samples):
    # serial
    t0 = time()
    map(operation, combos)
    T[i,0] = time() - t0
    # parallel
    t0 = time()
    p.map(operation, combos)
    T[i,1] = time() - t0
    # report
    print "{0:5g} {1:14.3e}{2:15.3e}".format(i+1, *T[i])

p.close()
print 
print "  ave.{1:14.3e}{2:15.3e}".\
    format(i+1, *T.mean(axis=0))
