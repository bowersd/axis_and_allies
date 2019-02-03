import math
import itertools as it
from functools import reduce
import operator
import argparse

def binomial(n, N, p):
    """calculate the binomial value of n successes out of N trials with p chance of success"""
    #successes, trials, probability of success
    return (math.factorial(N)/float(math.factorial(n)*math.factorial(N-n)))*(p**n)*((1-p)**(N-n))

def binomial_curve(N, p):
    """calculate the binomial value for all outcomes in N"""
    return [binomial(i, N, p) for i in range(N+1)]

def index_comb(*v):
    """cartesian product of vector indices"""
    return it.product(*[range(len(y)) for y in v])

def product(*args):
    return reduce(operator.mul, [a for a in args], 1)

def binomial_joint(*np):
    """
    combine binomial curves with varying N and p
    np = (N, p)
    """
    #np format different from what is used for grids (where indices provide p)
    d = [0 for i in range(sum([x[0] for x in np])+1)] #domain
    c = [binomial_curve(x[0], x[1]) for x in np] #curves
    i = index_comb(*c) 
    for j in i:
        d[sum(j)] += product(*[c[k][x] for k, x in enumerate(j)])
    return d

#def curve_delta(c1, c2):
#    """difference between c1, c2 in P(outcome) for each outcome"""
#    return [c1[i]-c2[i] if i < len(c2) else c1[i] for i in range(len(c1))]

def find_mode(*c):
    """mode of a curve"""
    i = 0
    best = 0
    for j in range(len(c)):
        if c[j] > best:
            i = j
            best = c[j]
    return i

def mode_value(*c):
    i = 0
    best = 0
    for j in range(len(c)):
        if c[j] > best:
            i = j
            best = c[j]
    return c[i]

def find_mean(*c):
    """mean of a curve"""
    return sum([i*c[i] for i in range(len(c))])

#def rout(n, *c):
#    """what percent of the time does a curve exceed a threshold (winning on first roll)"""
#    p = 0
#    for i in range(len(c)):
#        if i >= n: p+=c[i]
#    return p
