# Component functions and algorithms.

import logging
import random

log = logging.getLogger("utilities")

def gcd(a, b):
    if b == 0:
        return a
    else:
        return gcd(b, a % b)

def mod_expon(a, m, n): # Calculate a^m (mod n) using repeated squaring.
    bits = list(bin(m)[2:][::-1])
    tot = 1
    for i in range(len(bits)):
        if bits[i] == '1':
            sub = a
            for j in range(i):
                sub = (sub ** 2) % n
            tot = (tot * sub) % n
    return tot

def quick_sort(l):
    if len(set(l)) <= 1:
        return l
    mid = l[(len(l) - 1)//2]
    lower = [x for x in l if x < mid]
    middle = [x for x in l if (x == mid)]
    higher = [x for x in l if x > mid]
    return quick_sort(lower) + middle + quick_sort(higher)

def tuple_quick_sort(l, i=0): # Quick sort by the i-th element of each tuple, default 0.
    if len(set([x[0] for x in l])) <= 1:
        return l
    mid = l[(len(l) - 1)//2][i]
    lower = [x for x in l if x[i] < mid]
    middle = [x for x in l if (x[i] == mid)]
    higher = [x for x in l if x[i] > mid]
    return tuple_quick_sort(lower) + middle + tuple_quick_sort(higher)


''' Potentially convert to explicitly use row operations so this can be used to produce inverses of square matrices'''
def rref(M): # Apply Gaussian elimination to convert a matrix M to reduced row echelon form (RREF).
    m = len(M)
    n = len(M[0])
    M = [x[1] for x in tuple_quick_sort([(min([i for i in range(n) if row[i] != 0]), row) for row in M])] # Sort rows by number of leading 0s.
    
    assert all(len(r) == n for r in M[1:]), "Utilities:RREF:Invalid matrix - inconsistent row length."
    
    for i in range(min(m, n)): # Clearing with respect to pivot in i-th row.
        pivots = [min([i for i in range(n) if row[i] != 0]) for row in M]

        c = M[i][pivots[i]]
        for k in range(pivots[i], n): # Normalise the row to the pivot.
            M[i][k] /= c

        for j in [x for x in range(m) if x != i]: # Add a multiple of the current row to all other rows.
            mult = M[j][pivots[i]]
            for k in range(pivots[i], n):
                M[j][k] -= mult * M[i][k]        
        
    return M

def rand_mat(m, n):
    return [[random.randint(-5, 5) for x in range(n)] for y in range(m)]


