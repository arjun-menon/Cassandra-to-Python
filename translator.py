
from string import Template
import sys

####################
# Utility functions
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

def uniqify(seq): # order preserving uniqifier
    seen = set()
    return [ x for x in seq if x not in seen and not seen.add(x) ]

def identical(seq): # check if all elements in a sequence are identical
    return reduce(lambda a, b: (b, a[0]==b), seq, (seq[0], None))[1]

def hyphens_to_underscores(s):
    if type(s) != str: raise TypeError("argument must be str!")
    return "".join('_' if c == '-' else c for c in s)

def prefix_line(s, prefix):
    return "".join( prefix + line + "\n" for line in s.split('\n') )

def tab(s, indentation_level=1):
    return prefix_line(s, '    '*indentation_level)

####################

class RuleTranslator(object):
    def __init__(self, rule):
        self.rule = rule
    def __repr__(self):
        return repr(self.rule)

class canAc(RuleTranslator):
    def __init__(self, rule):
        super(canAc, self).__init__(rule)
        
    def trans(self):
        return lambda number: Template(
"""\
def canActivate$num(self$params):
$hypotheses"""
        ).substitute\
        (
            num = "" if number==0 else "_" + str(number),
            params = "".join(", " + repr(s) for s in self.rule.concl.args[:-1]) if len(self.rule.concl.args) else "",
            hypotheses = tab("".join("#" + repr(x) + '\n' for x in self.rule.hypos) + 'pass\n')
        )

####################

special_predicates = (None,
'permits',       # 1. permits(e,a) indicates that the entity e is permitted to perform action a.
'canActivate',   # 2. canActivate(e, r) indicates that the entity e can activate role r.
'hasActivated',  # 3. hasActivated(e, r) indicates that the entity e has currently activated role r.
'canDeactivate', # 4. canDeactivate(e1,e2, r) indicates that e1 can deactivate e2's role r (if e2 has really currently activated r).
'isDeactivated', # 5. isDeactivated(e, r) indicates that e's role r shall be deactivated as a consequence of another role deactivation (if e has really currently activated r).
'canReqCred')    # 6. canReqCred(e1,e2.p(~e)) indicates that e1 is allowed to request and receive credentials asserting p(~e) and issued by e2.

class RoleClass(object):
    def __init__(self, name, params):
        self.name = name
        self.params = params
        self.canAcs = []
        self.canDcs = []
        self.isDacs = []
    def __repr__(self):
        return "\ncanActivate rules:\n" + repr(self.canAcs) + "\ncanDeactivate rules:\n" + repr(self.canDcs) + ", \nisDeactivated rules:\n" + repr(self.isDacs) + "\n"
    
    def get_signature(self):
        if not len(self.canAcs):
            raise TypeError("No canActivates associated with this role :(")
        role = self.canAcs[0].rule.concl.args[-1:][0]
        name = role.name
        params = role.args
        return name, params
    
    def trans(self):
        name, params = self.get_signature()
        
        canAc_translation = "".join( rule.trans()(i+1) for (i, rule) in zip(range(len(self.canAcs)), self.canAcs) )
        
        return Template("""\
class $name_u(Role):
    name = "$name"
    
    def __init__(self$params_with_front_comma):
        super($name_u, self).__init__($name_u.name, ($params))
        $self_params_assignment $params
    
$canAc_translation"""
        ).substitute\
        (
            name = name,
            name_u = hyphens_to_underscores(name),
            params = ", ".join(map(repr, params)) if len(params) else "",
            params_with_front_comma = "".join(", " + repr(s) for s in params) if len(params) else "",
            self_params_assignment = ", ".join("self."+repr(s) for s in params) + " = " if len(params) else "",
            canAc_translation = tab(canAc_translation),
        )

def extract_roles(rules):
    """
    Builds a dictionary mapping each unique role to RoleClass objects containing lists 
    of 'canActivate' , 'canDeactivate' , 'isDeactivated' rules associated with that role.
    
    'canActivate' and 'canDeactivate' rules are assigned naively to their associated roles. 
    'isDeactivated' rules are assigned to the predicate that triggers that deactivation.
    """
    
    # Separating the role rules
    three_special_predicates = (special_predicates[2], special_predicates[4], special_predicates[5])
    
    canAc_rules = [rule for rule in rules if rule.concl.name == special_predicates[2]] # canActivate
    canDc_rules = [rule for rule in rules if rule.concl.name == special_predicates[4]] # canDeactivate
    isDac_rules = [rule for rule in rules if rule.concl.name == special_predicates[5]] # isDeactivated
    
    # get role names & params and build dict with it
    role_names = set([rule.concl.args[1].name for rule in canAc_rules])
    role_params = []
    for rn in role_names:
        # search and find rn in rules:
        for r in canAc_rules:
            if r.concl.args[1].name == rn:
                role_params.append(r.concl.args[1].args)
                break
    
    roles = dict((rn, RoleClass(rn, rp)) for (rn, rp) in zip(role_names, role_params))
    
    # grab the rules:
    
    for r in canAc_rules:
        roles[r.concl.args[1].name].canAcs.append( canAc(r) )
    
    for r in canDc_rules:
        roles[r.concl.args[2].name].canDcs.append(r)
    
    for r in isDac_rules:
        for h in r.hypos:
            if type(h) == ehrparse.Atom and h.name == special_predicates[5]: # isDeactivated
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
    
    return outline, roles

####################

def translate_to_file(rules, output_file_name):
    with open(output_file_name, 'w') as f:
        sys.stdout = f
        translate_rules(rules)
        sys.stdout = sys.__stdout__

def translate_rules(rules):
    
    outline, roles = extract_roles(rules)

    
    #print roles['Professional-user'].trans()
    #print roles['Professional-user'].canAcs[0].trans()
    #print roles['PDS-manager'].canAcs[0].trans()(0)
    #print roles['PDS-manager'].trans()

    
    print "from core import *\n\n"
    for i in outline:
        if type(i) == RoleClass:
            #print "<", i.name, i.params, ">"
            print i.trans()
        else:
            print "#\n" + prefix_line(repr(i), "#") + "#\n"



####################

import ehrparse, cPickle as pickle

#rules = ehrparse.parse_one("data/pds.txt")
#pickle.dump(rules, open("data/parse_tree.pickle", "wb"))
rules = pickle.load(open("data/parse_tree.pickle"))

translate_rules(rules)
#translate_to_file(rules, "pds.py")