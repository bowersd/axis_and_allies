import argparse
import itertools as it
import probability as prb
import evaluate_forces as ef

def pprint_a(*c): 
    """print the joint binomial curve of an army"""
    print("mode: {} ({}%)".format(prb.find_mode(*c), round(prb.mode_value(*c)*100, 1)))
    print("mean: {}".format(round(prb.find_mean(*c), 2)))
    top = int(round(max(*c)*10, 0))
    labels = [str(i*10) for i in range(1, top+1)]
    pipes = ["|" for i in range(top)]
    print((" "*12)+(" "*8).join(labels))
    print((" "*3)+("_"*9)+("_"*9).join(pipes))
    for i in range(len(c)): print("{:3}{}".format(str(i), "*"*int(round(c[i]*100 ,0))))

def pprint_b(*outcomes): 
    """battle summary"""
    mad = sum([x[1]  for x in outcomes if x[0] == (0, 0)]) #its only one now... ridiculous to have a for...
    a1w = sum([x[1]  for x in outcomes if x[0][0] != 0])#excludes mutual destruction 
    a2w = sum([x[1]  for x in outcomes if x[0][1] != 0])
    print("{:>10}{:>10}{:>10}{:>10}{:>10}{:>10}{:>10}{:>10}{:>10}".format("10", "20", "30", "40", "50", "60", "70", "80", "90"))
    print("{:>10}{:>10}{:>10}{:>10}{:>11}{:>9}{:>10}{:>10}{:>10}".format("|", "|", "|", "|", ">|<", "|", "|", "|", "|"))
    print("{}{}{}".format("o"*int(round(a1w*100)), "-"*int(round(mad*100)), "x"*int(round(a2w*100))))
    print("attacker wins {}".format(str(round(a1w*100, 1))))
    print("defender wins {}, survives {} (wins but loses all {})".format(str(round((a2w+mad)*100, 1)), str(round(a2w*100,1)), str(round(mad*100, 1))))

def pprint_c(*outcomes):
    """print casualties of winner"""
    a1w = [x for x in outcomes if x[0][0] != 0] #excludes mutual destruction
    a2w = [x for x in outcomes if x[0][1] != 0] 
    totala1 = sum([x[1] for x in a1w])
    totala2 = sum([x[1] for x in a2w])
    print("attacker casualties when victorious:")
    pprint_a(*[x[1]/totala1 for x in reversed(sorted(a1w))])
    print()
    print("defender casualties when victorious (and survives):")
    pprint_a(*[x[1]/totala2 for x in reversed(sorted(a2w))])

def pprint_d(*deltas):
    """print delta in probability curve"""
    margin = int(round(abs(min(deltas))*100))
    for i in range(len(deltas)):
        if deltas[i] < 0: print(str(i).ljust(3)+("*"*int(round(abs(deltas[i])*100))).rjust(margin))
        else: print("{:3}{}".format(str(i), (" "*margin)+("*"*int(round(abs(deltas[i])*100)))))

def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--defender', nargs=2, action='append', help="pairs of number of units, hit value. as in -d 5 2 -d 3 3 for five twos and three threes")
    parser.add_argument('-a', '--attacker', nargs=2, action='append', help="pairs of number of units, hit value. as in -a 5 2 -a 3 3 for five twos and three threes")
    parser.add_argument('-c', '--casualties', action="store_true", help="whether to show casualties")
    parser.add_argument('-aa', '--anti_aircraft', nargs=2, action='append', help="pairs of number of units, hit value (targets of anti-aircraft). as in -aa 1 3 -aa 2 4 for one fighter and two bombers", default = [])
    parser.add_argument('-b', '--bombardment', nargs=2, action='append', help="pairs of number of units, hit value. as in -b 1 4 for one bombarding battleship", default = [])
    parser.add_argument('-sa', '--submarines_attacker', nargs=2, action='append', help="pairs of number of units, hit value. as in -sa 1 2 for one attacking sub (no opposing destroyer present)", default = [])
    parser.add_argument('-sd', '--submarines_defender', nargs=2, action='append', help="pairs of number of units, hit value. as in -sd 1 2 for one defending sub (no opposing destroyer present)", default = [])
    parser.add_argument('-sap', '--submarines_attacker_planes', nargs=2, action='append', help="pairs of number of units, hit value. as in -sap 1 3 for one attacking fighter", default = [])
    parser.add_argument('-sdp', '--submarines_defender_planes', nargs=2, action='append', help="pairs of number of units, hit value. as in -sdp 1 4 for one defending fighter", default = [])
    return parser


if __name__ == "__main__":
    args = arg_parser().parse_args()
    if (args.defender and not args.attacker) :
        pprint_a(*prb.binomial_joint(*[(int(x[0]), int(x[1])/float(6)) for x in args.defender]))
    elif (args.attacker and not args.defender):
        pprint_a(*prb.binomial_joint(*[(int(x[0]), int(x[1])/float(6)) for x in args.attacker]))
    else:
        #unordered representation for user input
        adict = {int(x[1]):int(x[0]) for x in args.attacker}
        ddict = {int(x[1]):int(x[0]) for x in args.defender}
        #ordered for machine
        a1 = [adict[i] if i in adict else 0 for i in range(6)]
        a2 = [ddict[i] if i in ddict else 0 for i in range(6)]
        n, m = sum(a1), sum(a2)
        if args.bombardment or args.anti_aircraft:
            prior1 = [[[0 for i in range(6)],a2]]
            for x in args.bombardment:
                prior1[0][0][int(x[1])] = int(x[0])
            #prior1 = ([[int(x[0]) if i in [int(x[1]) for x in args.bombardment] else 0 for i in range(6)], a2],)
            prior2 = []
            for x in args.anti_aircraft: 
                prior2.append([[0, int(x[0]), 0, 0, 0, 0], [int(x[0]) if i == int(x[1]) else 0 for i in range(6)]])
            #else: prior2 = ([[0]*6, a1],)
            prior1probs = [prb.binomial_joint(*[(x[0][i], i/float(len(x[0]))) for i in range(len(x[0]))]) for x in prior1]
            prior2probs = [prb.binomial_joint(*[(x[0][i], i/float(len(x[0]))) for i in range(len(x[0]))]) for x in prior2]
            prior1_outcomes = []
            for i in range(len(prior1)): prior1_outcomes.append([(j, prior1[i][1]) for j in range(len(prior1probs[i]))])
            prior2_outcomes = []
            for i in range(len(prior2)): prior2_outcomes.append([(j, prior2[i][1]) for j in range(len(prior2probs[i]))])
            pprint_b(*ef.weight_outcomes(prior1probs, prior2probs, *ef.embedded_battle(prior1_outcomes, prior2_outcomes, a1, a2)))
        elif args.submarines_attacker or args.submarines_defender:
            sa, sd, sap, sdp = ([0 for i in range(6)], [0 for i in range(6)], [0 for i in range(6)], [0 for i in range(6)])
            for x in args.submarines_attacker: sa[int(x[1])] = int(x[0])
            for x in args.submarines_defender: sd[int(x[1])] = int(x[0])
            for x in args.submarines_attacker_planes: sap[int(x[1])] = int(x[0])
            for x in args.submarines_attacker_planes: sdp[int(x[1])] = int(x[0])
            pprint_b(*ef.subs_sneak_strike(sa, sd, sap, sdp, a1, a2))
        else:
            outcomes = ef.sim_or_calc(n, m, a1, a2)
            pprint_b(*outcomes)
            if args.casualties:
                print()
                pprint_c(*outcomes)
