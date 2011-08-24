
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

special_predicates = (None,
'permits',       # 1. permits(e,a) indicates that the entity e is permitted to perform action a.
'canActivate',   # 2. canActivate(e, r) indicates that the entity e can activate role r.
'hasActivated',  # 3. hasActivated(e, r) indicates that the entity e has currently activated role r.
'canDeactivate', # 4. canDeactivate(e1,e2, r) indicates that e1 can deactivate e2's role r (if e2 has really currently activated r).
'isDeactivated', # 5. isDeactivated(e, r) indicates that e's role r shall be deactivated as a consequence of another role deactivation (if e has really currently activated r).
'canReqCred',)   # 6. canReqCred(e1,e2.p(~e)) indicates that e1 is allowed to request and receive credentials asserting p(~e) and issued by e2.

def build_roles():
    """
    Builds a dictionary mapping each unique role to a Role objects containing a lists 
    of 'canActivate' , 'canDeactivate' , 'isDeactivated' rules associated with that role.
    
    'canActivate' and 'canDeactivate' rules are assigned naively to their associated roles. 
    'isDeactivated' rules are assigned to the predicate that triggers that deactivation.
    """
    
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
    canAc_rules = [rule for rule in rules if rule.concl.name == special_predicates[2]]
    canDc_rules = [rule for rule in rules if rule.concl.name == special_predicates[4]]
    isDac_rules = [rule for rule in rules if rule.concl.name == special_predicates[5]]
    
    # Get the names of unqiue roles
    uniq_role_names = uniq([rule.concl.args[1].name for rule in canAc_rules])
    
    roles = dict((role_name, Role(role_name)) for role_name in uniq_role_names)
    
    for r in canAc_rules:
        roles[r.concl.args[1].name].canAcs.append(r)
    
    for r in canDc_rules:
        roles[r.concl.args[2].name].canDcs.append(r)
    
    for r in isDac_rules:
        for h in r.hypos:
            if type(h) == ehrparse.Atom and h.name == special_predicates[5]:
                role_name = h.args[1].name
        roles[role_name].isDacs.append(r)
    
    return roles

####################

#roles = build_roles()

nrr = [r for r in rules if r.concl.name not in special_predicates]

repl()