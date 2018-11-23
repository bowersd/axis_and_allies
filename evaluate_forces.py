import math
import random
import itertools as it
from functools import reduce
import operator
import argparse

#todo: opening fire, expected value of strategic bombing raid against risk, sub withdrawal, 
#sub/plane individuation:
#   sub not hit planes, 
#   chance of taking territory (planes can't take territory)
#   planes potential targets for aa
#expected cost of victory, financial damage wrought (requires unit costs, unit individuation)

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

def a_minus(n, *v):
    """deplete v (an army) from left to right (->0) until n is exhausted"""
    #this assumes that the least probable hitters are removed first ... not necessarily valid (bombers may be preserved on defense
    h = []
    pos = 0
    while n and pos < len(v):
        x = v[pos]
        pos += 1
        if x > n: 
            h.append(x-n)
            n = 0
        else:
            h.append(0)
            n -= x
    h += v[pos:]
    return h

def make_grid(n, m):
    """nxm array with labeled coordinates ... pretty superfluous"""
    return [[(i,j) for j in range(m+1)] for i in range(n+1)]
    #h = []
    #for i in range(n+1): h.append([(i, j) for j in range(m+1)])
    #return h
    #return [(i, j) for i in range(n+1) for j in range(m+1)]

def make_transitions(n, m):
    h = {}
    #could just make all transitions and give the non-downwards ones weight zero when weighting
    for x in it.product(range(1, n+1), range(1, m+1)): #start coordinates can't be terminal, so leave 0 out:
        h[x] = []
        for y in it.product(range(n+1), range(m+1)):
            if y[0]<=x[0] and y[1]<=x[1]: h[x].append(y)
    return h

def weight_transitions(a1, a2, trans):
    """calculate weights for each transition in trans"""
    h = {} #trans plus weights 
    for s in trans: #start
        h[s] = {}
        a11, a21 = a_minus(sum(a1)-s[0], *a1), a_minus(sum(a2)-s[1], *a2) #take away losses
        c1, c2 = binomial_joint(*[(a11[i], i/float(6)) for i in range(len(a11))]), binomial_joint(*[(a21[i], i/float(6)) for i in range(len(a21))])#get damage dealing capacity of each army
        overkill1, overkill2 = sum(c1[s[1]:]), sum(c2[s[0]:]) #p(army deals critical hit)
        for e in trans[s]: #end
            i, j = s[0]-e[0], s[1]-e[1] #damage dealt to a1, a2
            if i > s[1] or j > s[0]: continue #tasked damage too great for at least one party, don't include
            #if i > s[1] or j > s[0]: h[s][e] = 0 #tasked damage too great for at least one party, include 0
            if not(e[0] or e[1]): h[s][e] = overkill1*overkill2 #a1 and a2 elimination, overkill options
            elif not e[0]: h[s][e] = c1[j]*overkill2 #a1 elimination, overkill option for a2
            elif not e[1]: h[s][e] = c2[i]*overkill1 #a2 elimination, overkill option for a1
            else: h[s][e] = c1[j]*c2[i]
    #for x in sorted(h): print x, h[x]
    return h

def self_loop_dict(trans):
    """store key values for calculating self-loop probability re-distribution in dict"""
    h = {x:[0, 0] for x in trans}
    d = 0
    for x in trans:
        for y in trans[x]:
            if x == y: h[x][0] = trans[x][y]
            else: h[x][1] += trans[x][y]
    return h


#1972 iterations for 5 2 v 3 3, with zeroes dropped, 1503
def start_pct(grid, trans):
    """probability each end state will be reached"""
    #track forward from start, augmenting finals when they come up!
    #uses nested transitions
    h = {x:0 for x in ([x[0] for x in grid[1:]] + grid[0])} #gotta be a smoother way
    start = grid[-1][-1]
    sld = self_loop_dict(trans)
    #cnt = 0
    #depth = 0
    #paths = 0
    undone = [[(start, 1)]]
    while undone:
        path = undone.pop()
        prevn, prevv = path[-1]
        for n in trans[prevn]:
            #cnt += 1
            if n in h:
                h[n] += prevv*(trans[prevn][n]+(sld[prevn][0]*(trans[prevn][n]/sld[prevn][1])))
                #paths += 1
                #depth += len(path)+1
            elif n != prevn and trans[prevn][n] != 0: undone.append(path+[(n, prevv*(trans[prevn][n]+(sld[prevn][0]*(trans[prevn][n]/sld[prevn][1]))))]) #we don't actually need the whole path, can just store the last node and its probability!
    #print "total length of paths {}".format(depth)
    #print "average length of paths {}".format(round(depth/float(paths), 2))
    #print "total nodes {}".format(cnt)
    #print "total paths {}".format(paths)
    return [(x, h[x]) for x in h]

def simulate(grid, trans, cap):
    h = {x:0 for x in ([x[0] for x in grid[1:]] + grid[0])} #gotta be a smoother way
    start = grid[-1][-1]
    sld = self_loop_dict(trans)
    paths = 0
    while paths < cap:
        prevn = start
        while prevn not in h:
            x =random.random()
            cumsum = 0
            nextn = sorted(trans[prevn])
            while cumsum < x:
                n = nextn.pop(0) #favors smaller jumps by starting at left edge of curve
                if n != prevn:
                    cumsum += trans[prevn][n]+(sld[prevn][0]*(trans[prevn][n]/sld[prevn][1]))
            prevn = n
        h[prevn] += 1
        paths += 1
    return [(x, h[x]/float(paths)) for x in h]

def pprint_a(*c): 
    """print the joint binomial curve of an army"""
    print "mode: {} ({}%)".format(find_mode(*c), round(mode_value(*c)*100, 1))
    print "mean: {}".format(round(find_mean(*c), 2))
    top = int(round(max(*c)*10, 0))
    labels = [str(i*10) for i in range(1, top+1)]
    pipes = ["|" for i in range(top)]
    print (" "*12)+(" "*8).join(labels)
    print (" "*3)+("_"*9)+("_"*9).join(pipes)
    for i in range(len(c)): print "{:3}{}".format(str(i), "*"*int(round(c[i]*100 ,0)))

def pprint_b(*outcomes): 
    """battle summary"""
    mad = sum([x[1]  for x in outcomes if x[0] == (0, 0)]) #its only one now... ridiculous to have a for...
    a1w = sum([x[1]  for x in outcomes if x[0][0] != 0])#excludes mutual destruction 
    a2w = sum([x[1]  for x in outcomes if x[0][1] != 0])
    print "{:>10}{:>10}{:>10}{:>10}{:>10}{:>10}{:>10}{:>10}{:>10}".format("10", "20", "30", "40", "50", "60", "70", "80", "90")
    print "{:>10}{:>10}{:>10}{:>10}{:>10}{:>10}{:>10}{:>10}{:>10}".format("|", "|", "|", "|", "|", "|", "|", "|", "|")
    print "{}{}{}".format("o"*int(round(a1w*100)), "-"*int(round(mad*100)), "x"*int(round(a2w*100)))
    print "attacker wins {}".format(str(round(a1w*100, 1)))
    print "defender wins {}, survives {} (wins but loses all {})".format(str(round((a2w+mad)*100, 1)), str(round(a2w*100,1)), str(round(mad*100, 1)))

def pprint_c(*outcomes):
    """print casualties of winner"""
    a1w = [x for x in outcomes if x[0][0] != 0] #excludes mutual destruction
    a2w = [x for x in outcomes if x[0][1] != 0] 
    totala1 = sum([x[1] for x in a1w])
    totala2 = sum([x[1] for x in a2w])
    print "attacker casualties when victorious:"
    pprint_a(*[x[1]/totala1 for x in reversed(sorted(a1w))])
    print
    print "defender casualties when victorious (and survives):"
    pprint_a(*[x[1]/totala2 for x in reversed(sorted(a2w))])

def pprint_d(*deltas):
    """print delta in probability curve"""
    margin = int(round(abs(min(deltas))*100))
    for i in range(len(deltas)):
        if deltas[i] < 0: print str(i).ljust(3)+("*"*int(round(abs(deltas[i])*100))).rjust(margin)
        else: print "{:3}{}".format(str(i), (" "*margin)+("*"*int(round(abs(deltas[i])*100))))

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--defender', nargs=2, action='append', help="pairs of number of units, hit value. as in -d 5 2 -d 3 3 for five twos and three threes")
parser.add_argument('-a', '--attacker', nargs=2, action='append', help="pairs of number of units, hit value. as in -a 5 2 -a 3 3 for five twos and three threes")
parser.add_argument('-c', '--casualties', action="store_true", help="whether to show casualties")
parser.add_argument('-aa', '--anti_aircraft', nargs=2, action='append', help="pairs of number of units, hit value (targets of anti-aircraft). as in -aa 1 3 -aa 2 4 for one fighter and two bombers")
parser.add_argument('-b', '--bombardment', nargs=2, action='append', help="pairs of number of units, hit value. as in -b 1 4 for one bombarding battleship")
parser.add_argument('-sa', '--submarines_attacker', nargs=2, action='append', help="pairs of number of units, hit value. as in -sa 1 2 for one attacking sub (no opposing destroyer present)")
parser.add_argument('-sd', '--submarines_defender', nargs=2, action='append', help="pairs of number of units, hit value. as in -sd 1 2 for one defending sub (no opposing destroyer present)")

def sim_or_calc(n, m, a1, a2):
    if n > 7 and m > 7:
        outcomes = simulate(make_grid(n, m), weight_transitions(a1, a2, make_transitions(n, m)), 10000)
    else:
        outcomes = start_pct(make_grid(n, m), weight_transitions(a1, a2, make_transitions(n, m)))
    return outcomes

if __name__ == "__main__":
    args = parser.parse_args()
    if (args.defender and not args.attacker) :
        pprint_a(*binomial_joint(*[(int(x[0]), int(x[1])/float(6)) for x in args.defender]))
    elif (args.attacker and not args.defender):
        pprint_a(*binomial_joint(*[(int(x[0]), int(x[1])/float(6)) for x in args.attacker]))
    else:
        #unordered representation for user input
        adict = {int(x[1]):int(x[0]) for x in args.attacker}
        ddict = {int(x[1]):int(x[0]) for x in args.defender}
        #ordered for machine
        a1 = [adict[i] if i in adict else 0 for i in range(6)]
        a2 = [ddict[i] if i in ddict else 0 for i in range(6)]
        n, m = sum(a1), sum(a2)
        outcomes = sim_or_calc(n, m, a1, a2)
        pprint_b(*outcomes)
        if args.casualties:
            print
            pprint_c(*outcomes)
