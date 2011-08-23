
import ehrparse
import cPickle as pickle
import operator

#rules = ehrparse.parse()
#pickle.dump(rules, open("data/parse_tree.pickle", "wb"))
rules = pickle.load(open("data/parse_tree.pickle"))

def repl():
    while True:
        #print ">",
        x = raw_input()
        try:
            y = eval(x)
            print y
        except Exception as e:
            print e.message

def uniq(seq):
    seen = set()
    seen_add = seen.add
    return [ x for x in seq if x not in seen and not seen_add(x) ]

def iden(seq):
    if len(seq):
        x = seq[0]
        for i in seq:
            if i != x:
                return False
    return True

####################

class Role(object):
    def __init__(self, name):
        self.name = name
        # these members represent corresponding rules
        self.canAcs = []
        self.canDcs = []
        self.isDeas = []
    def __repr__(self):
        return "\ncanAcs: " + repr(self.canAcs) + ", \ncanDcs: " + repr(self.canDcs) + ", \nisDeas: " + repr(self.isDeas) + "\n"

# Separating rules into those associated with roles & not
the_role_predicates = ("canActivate", "canDeactivate", "isDeactivated")
role_rules = [rule for rule in rules if rule.concl.name in the_role_predicates]
non_role_rules = [rule for rule in rules if rule.concl.name not in the_role_predicates]

# canActivate rules
canAc_rules = [rule for rule in rules if rule.concl.name == the_role_predicates[0]]
canAc_roles = [rule.concl.args[1] for rule in canAc_rules]
canAc_role_names_uniq = uniq([role.name for role in canAc_roles])
#canAc_roles_grouped = [[role for role in canAc_roles if role.name == i] for i in canAc_role_names_uniq]
#canAc_roles_grouped_multi = filter(lambda g: len(g) > 1, canAc_roles_grouped)

# canDeactivate rules
canDc_rules = [rule for rule in rules if rule.concl.name == the_role_predicates[1]]
canDc_roles = [rule.concl.args[1] for rule in canDc_rules]

# isDeactivated rules
isDea_rules = [rule for rule in rules if rule.concl.name == the_role_predicates[2]]
isDea_roles = [rule.concl.args[1] for rule in isDea_rules]

roles = {}

for i in canAc_role_names_uniq:
    roles[i] = Role(i)
    roles[i].canAcs = [rule for rule in canAc_rules if rule.concl.args[1].name == i]

#[rl for rl in canAc_grouped]

repl()