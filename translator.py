
import ehrparse
import cPickle as pickle
import operator

#rules = ehrparse.parse()
#pickle.dump(rules, open("data/parse_tree.pickle", "wb"))
rules = pickle.load(open("data/parse_tree.pickle"))

def repl(): # use python's quit() to break out
    while True:
        #print ">",
        x = raw_input()
        try:
            y = eval(x)
            print y
        except Exception as e:
            print e.message

def uniq(seq): # order preserving uniqifier
    seen = set()
    seen_add = seen.add
    return [ x for x in seq if x not in seen and not seen_add(x) ]

def iden(seq): # check if all elements in a sequence are identical
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

# Separating the role rules
canAc_rules = [rule for rule in rules if rule.concl.name == the_role_predicates[0]]
canDe_rules = [rule for rule in rules if rule.concl.name == the_role_predicates[1]]
isDac_rules = [rule for rule in rules if rule.concl.name == the_role_predicates[2]]

# Get the names of unqiue roles
uniq_role_names = uniq([rule.concl.args[1].name for rule in canAc_rules])

roles = dict([(role_name, Role(role_name)) for role_name in uniq_role_names])

# load canAcs grouping them by name into roles
for canAc_rules_group in ([rule for rule in canAc_rules if rule.concl.args[1].name == role_name] for role_name in uniq_role_names):
    roles[ canAc_rules_group[0].concl.args[1].name ].canAcs = canAc_rules_group


repl()