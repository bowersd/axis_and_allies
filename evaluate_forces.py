import probability as prb
import pprint
import random
import itertools as it

#todo: opening fire, expected value of strategic bombing raid against risk, sub withdrawal, 
#sub/plane individuation:
#   sub not hit planes, 
#   chance of taking territory (planes can't take territory)
#   planes potential targets for aa
#expected cost of victory, financial damage wrought (requires unit costs, unit individuation)

def a_minus(n, *v):
    """deplete v (an army) from left to right (->0) until n is exhausted"""
    #this assumes that the least probable hitters are removed first ... not necessarily valid (bombers may be preserved on defense)
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

def losses(depleted, full):
    return [full[i]-depleted[i] for i in range(len(full))]

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
        c1, c2 = prb.binomial_joint(*[(a11[i], i/float(6)) for i in range(len(a11))]), prb.binomial_joint(*[(a21[i], i/float(6)) for i in range(len(a21))])#get damage dealing capacity of each army
        overkill1, overkill2 = sum(c1[s[1]:]), sum(c2[s[0]:]) #p(army deals critical hit)
        for e in trans[s]: #end
            i, j = s[0]-e[0], s[1]-e[1] #damage dealt to a1, a2
            if i > s[1] or j > s[0]: continue #tasked damage too great for at least one party, don't include
            #if i > s[1] or j > s[0]: h[s][e] = 0 #tasked damage too great for at least one party, include 0
            if not(e[0] or e[1]): h[s][e] = overkill1*overkill2 #a1 and a2 elimination, overkill options
            elif not e[0]: h[s][e] = c1[j]*overkill2 #a1 elimination, overkill option for a2
            elif not e[1]: h[s][e] = c2[i]*overkill1 #a2 elimination, overkill option for a1
            else: h[s][e] = c1[j]*c2[i]
    #for x in sorted(h): print(x, h[x])
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
    #print("total length of paths {}".format(depth))
    #print("average length of paths {}".format(round(depth/float(paths), 2)))
    #print("total nodes {}".format(cnt))
    #print("total paths {}".format(paths))
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

def sim_or_calc(n, m, a1, a2):
    if n + m > 14:
        outcomes = simulate(make_grid(n, m), weight_transitions(a1, a2, make_transitions(n, m)), 10000)
    else:
        outcomes = start_pct(make_grid(n, m), weight_transitions(a1, a2, make_transitions(n, m)))
    return outcomes

####
#opening fire - under construction
####

    #bombardment: you can just do prb.a_minus(target) for each of the cells; weight the outcomes by probability of attrition
    #sneak attacks: the submarines stay in the fight after one round, but they can only be casualties in the immediate post-opening round
    #aa: non a_minus() subtractions (bomber may go down even if a fighter is present) -> this can be handled by setting up 2 opening fire rounds, one for fighters, one for bombers

#armies could actually be represented as lists containing two lists, one for opening fire, one for later.

#assumed: pre-processing of units into appropriate targets, signal for opening fire
#   presumably armies could be broken into sub-armies according to what they target/the enemy targets, and casualties could be calculated on those sub-armies before subtracting point-wise from the overall army.
#produce distribution of outcomes for one round
#calculate remainder of battle for each outcome (adjusting original armies accordingly)
#weight each battle outcome by prior distribution
#sum all weighted battle outcomes

def embedded_battle(prior_outcomes1, prior_outcomes2, a1, a2): #openers1/2, core1/2
    #2 or  more, use a for... no reason to just have a prior stage of battle, could have entire sequences of prior battles
    h = []
    for p in it.product(*prior_outcomes1): #tuples of (prior casualties inflicted, [vector of targets]) for a1
        alt2 = [x for x in a2]
        #print p
        for x in p: 
            alt2 = losses(losses(a_minus(x[0], *x[1]), x[1]), alt2) #figure out how the targets have been depleted, then remove that much from the overall targeted army
        for q in it.product(*prior_outcomes2): #these could come precompiled as arguments...
            alt1 = [z for z in a1]
            for y in q: alt1 = losses(losses(a_minus(y[0], *y[1]), y[1]), alt1)
            #print alt1
            #print alt2
            #print "---"
            h.append(sim_or_calc(sum(alt1), sum(alt2), alt1, alt2))
    return h

def weight_outcomes(prior_probs1, prior_probs2, *outcomes):
    h = {} #working around unchecked assumption that all outcomes are in the same order in each list...
    #h = [0]*max([len(x for x in outcomes)])
    #d = it.product(range(len(prior_probs1)), range(len(prior_probs2))) #full distribution
    i = 0
    for p in it.product(*prior_probs1):
        for q in it.product(*prior_probs2):
            for x in outcomes[i]:
                if x[0] not in h: h[x[0]]= prb.product(*((x[1],)+q+p))
                else: h[x[0]] += prb.product(*((x[1],)+q+p))
            i += 1
    return [(x, h[x]) for x in h]

if __name__ == "__main__":
    a1 = [0,1,0,2,1,0]
    a2 = [0,0,2,0,0,0]
    a1fig = [0,0,0,2,0,0]
    a1bom = [0,0,0,0,1,0]
    open1 = ([0,0,0,0,1,0], a2)
    open2 = ([0,sum(a1fig),0,0,0,0], a1fig)
    open2b = ([0,sum(a1bom),0,0,0,0], a1bom)
    open1probs = [
            prb.binomial_joint(*[(open1[0][i], i/float(len(open1[0]))) \
                for i in range(len(open1[0]))])
            ] #allows fully general number of die faces. technically, we never have mixed probabilities in opening fire, but since it is not known ahead of time, it is easier to use binomial_joint() degeneratively
    open2probs = [
            prb.binomial_joint(*[(open2[0][i], i/float(len(open2[0]))) \
                    for i in range(len(open2[0]))]), 
            prb.binomial_joint(*[(open2b[0][i], i/float(len(open2b[0]))) \
                for i in range(len(open2b[0]))])
            ]
    pprint.pprint_b(*weight_outcomes(open1probs, open2probs, *embedded_battle([[(i, open1[1]) for i in range(len(open1probs[0]))]], [[(i, open2[1]) for i in range(len(open2probs[0]))], [(i, open2b[1]) for i in range(len(open2probs[1]))]], a1, a2)))

