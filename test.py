import pickle, ehrparse

with open("data/parse_tree.pickle", "rb") as f:
    rules = pickle.load(f)


def num_constraints(r):
    return len([h for h in r.hypos if type(h) == ehrparse.Constraint])

#print([num_constraints(r) for r in rules])

s = [r for r in rules if num_constraints(r) > 1]

print(len(s))
