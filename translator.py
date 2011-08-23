
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

def build_roles():   
    class Role(object):
        def __init__(self, name):
            self.name = name
            # these members represent corresponding rules
            self.canAcs = []
            self.canDcs = []
            self.isDacs = []
        def __repr__(self):
            return "\ncanActivate rules:\n" + repr(self.canAcs) + "\ncanDeactivate rules:\n" + repr(self.canDcs) + ", \nisDeactivated rules:\n" + repr(self.isDacs) + "\n"
       
    # Separating the role rules
    the_three_predicates = ("canActivate", "canDeactivate", "isDeactivated")
    canAc_rules = [rule for rule in rules if rule.concl.name == the_three_predicates[0]]
    canDc_rules = [rule for rule in rules if rule.concl.name == the_three_predicates[1]]
    isDac_rules = [rule for rule in rules if rule.concl.name == the_three_predicates[2]]
    
    # Get the names of unqiue roles
    uniq_role_names = uniq([rule.concl.args[1].name for rule in canAc_rules])
    
    roles = dict((role_name, Role(role_name)) for role_name in uniq_role_names)
    
    for r in canAc_rules:
        roles[r.concl.args[1].name].canAcs.append(r)
    
    for r in canDc_rules:
        roles[r.concl.args[2].name].canDcs.append(r)
    
    for r in isDac_rules:
        for h in r.hypos:
            if type(h) == ehrparse.Atom and h.name == the_three_predicates[2]:
                role_name = h.args[1].name
        roles[role_name].isDacs.append(r)
    
    return roles


####################



repl()