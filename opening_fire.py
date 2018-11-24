import force_rating as fr

def opening_round(open_p, *target):
    #open_v = fr.binomial_joint(*[(opener[i], i/float(6)) for i in range(len(opener))])
    return [fr.a_minus(i, *target) for i in range(len(open_p))]
    #for bombardment, you can just do fr.a_minus(target) for each of the cells; weight the outcomes by probability of attrition
    #sneak attacks require that the submarines stay in the fight after one round, but they can't be used in the immediately post-opening round
    #aa requires non a_minus() subtractions (bomber may go down even if a fighter is present fighter)
