
import ehrparse
import cPickle as pickle
import operator

#rules = ehrparse.parse_one("data/pds.txt")
#pickle.dump(rules, open("data/parse_tree.pickle", "wb"))
rules = pickle.load(open("data/parse_tree.pickle"))

####################

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

def extract_roles():
    """
    Builds a dictionary mapping each unique role to a RoleIR objects containing a lists 
    of 'canActivate' , 'canDeactivate' , 'isDeactivated' rules associated with that role.
    
    'canActivate' and 'canDeactivate' rules are assigned naively to their associated roles. 
    'isDeactivated' rules are assigned to the predicate that triggers that deactivation.
    """
    
    class RoleIR(object):
        def __init__(self, name, params):
            self.name = name
            self.params = params
            self.canAcs = []
            self.canDcs = []
            self.isDacs = []
        def __repr__(self):
            return "\ncanActivate rules:\n" + repr(self.canAcs) + "\ncanDeactivate rules:\n" + repr(self.canDcs) + ", \nisDeactivated rules:\n" + repr(self.isDacs) + "\n"
    
    # Separating the role rules
    three_special_predicates = (special_predicates[2], special_predicates[4], special_predicates[5])
    
    canAc_rules = [rule for rule in rules if rule.concl.name == special_predicates[2]]
    canDc_rules = [rule for rule in rules if rule.concl.name == special_predicates[4]]
    isDac_rules = [rule for rule in rules if rule.concl.name == special_predicates[5]]
       
    # get role names & params and build dict with it
    role_names = set([rule.concl.args[1].name for rule in canAc_rules])
    role_params = []
    for rn in role_names:
        # search and find rn in rules:
        for r in canAc_rules:
            if r.concl.args[1].name == rn:
                role_params.append(r.concl.args[1].args)
                break
    
    roles = dict((rn, RoleIR(rn, rp)) for (rn, rp) in zip(role_names, role_params))
    
    # grab the rules:
    
    for r in canAc_rules:
        roles[r.concl.args[1].name].canAcs.append(r)
    
    for r in canDc_rules:
        roles[r.concl.args[2].name].canDcs.append(r)
    
    for r in isDac_rules:
        for h in r.hypos:
            if type(h) == ehrparse.Atom and h.name == special_predicates[5]:
                role_name = h.args[1].name
        roles[role_name].isDacs.append(r)
    
    # non-role rules
    outline = []
    
    for rule in rules:
        rule_name = rule.concl.name
        
        if rule.concl.name == special_predicates[2]: # canActivate 
            role_name = rule.concl.args[1].name
            
            if role_name in role_names:
                outline.append(roles[role_name])
                
                role_names.remove(role_name)
        
        if rule_name not in three_special_predicates:
            outline.append(rule)
    
    for i in outline:
        if type(i) != RoleIR:
            print i
        else:
            print "<", i.name, ">"
    
    return outline, roles

####################

outline, roles = extract_roles()

print "\n\n\n"
print roles

with open('pds.py', 'w') as f:
    pass
