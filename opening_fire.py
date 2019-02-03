import evaluate_forces as ef
import itertools as it

    #bombardment: you can just do ef.a_minus(target) for each of the cells; weight the outcomes by probability of attrition
    #sneak attacks: the submarines stay in the fight after one round, but they can only be casualties in the immediate post-opening round
    #aa requires non a_minus() subtractions (bomber may go down even if a fighter is present fighter)

#assumed: pre-processing of units into appropriate targets, signal for opening fire
#   presumably armies could be broken into sub-armies according to what they target/the enemy targets, and casualties could be calculated on those sub-armies before subtracting point-wise from the overall army.
#produce distribution of outcomes for one round
#calculate remainder of battle for each outcome (adjusting original armies accordingly)
#weight each battle outcome by prior distribution
#sum all weighted battle outcomes

def make_prior_vector(n, m):
    return range(n-m)

def casualties_prior(openers):
    p = ef.binomial_joint(*[(shooters[i], i/float(6)) for i in range(len(shooters))]) #potential for dealing damage...odd mixing of hard-coding (6) and calculating (getting number of slots on die)
    return {i:p[i] for i in range(sum(shooters)+1)}

def embedded_battle(prior, base1, base2): #openers1/2, core1/2
    #2 or  more, use a for... 
    h = []
    for i in range(len(prior)): #could just use the len as an arg, but staying flexible in case more complex situations require the distros to be used here
        alt2 = ef.a_minus(i, *base2)
        n, m = sum(base1), sum(alt2) #in current version, n could be calculated outside of the loop, but it will eventually have to be moved in
        h.append(ef.sim_or_calc(n, m, base1, alt2))
    return h


def weight_outcomes(prior, *outcomes):
    h = {} #working around unchecked assumption that all outcomes are in the same order in each list...
    #h = [0]*max([len(x for x in outcomes)])
    for x in outcomes: print x
    for i in range(len(prior)):
        for x in outcomes[i]:
            print x
            if x[0] not in h: h[x[0]]= x[1]*prior[i]
            else: h[x[0]] += x[1]*prior[i]
    return [(x, h[x]) for x in h]

if __name__ == "__main__":
    open1 = [0,0,0,0,1,0]
    opener_prior = ef.binomial_joint(*[(open1[i], i/float(len(open1))) for i in range(len(open1))]) #allows fully general number of die faces. technically, we never have mixed probabilities in opening fire, but since it is not known ahead of time, it is easier to use binomial_joint() degeneratively
    ef.pprint_b(*weight_outcomes(opener_prior, *embedded_battle(opener_prior, [0,2,0,0,0,0], [0,0,2,0,0,0])))

