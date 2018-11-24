
def read_in(filename):
    h = {}
    with open(filename) as f_in:
        for x in f_in:
            div = x.split(":")
            h[div[0]] = int(div[1])
    return h

tdict = {
        "infantry":(1,2),
        "artillery":(2,2),
        "armor":(3,3),
        "fighter":(3,4),
        "bomber":(4,1),
        "transport":(0,1),
        "submarine":(2,2),
        "destroyer":(3,3),
        "aircraft carrier":(1,3),
        "battleship":(4,4),
        }

def human_2_force_vector(machine, human, *args):
    #machine = {}, human = {}
    v = [0 for i in range(6)]
    r = 0
    if "role" in human and human["role"] == "defender": r = 1
    for a in args:
        if a in machine:
            if a == "infantry" and r == 0:
                if human[a] >= human["artillery"]:
                    v[2] += human["artillery"]
                    v[1] += human[a]-human["artillery"]
                else: v[2] += human[a]
            else: v[machine[a][r]] += human[a]
    return v

def battleship(v, human):
    v[0] += human["battleship"]
    return v

def opening_fire_vector(t, **human):
    if t == "anti-aircraft":
        return [0, sum([human["fighter"], human["bomber"]]), 0, 0, 0, 0]
    if t == "bombard":
        return [0, 0, 0, 0, human["battleship"], 0]
    if t == "sneak-attack":
        return [0, 0, human["submarine"], 0, 0, 0]
    return [0 for i in range(6)]
