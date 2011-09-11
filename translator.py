
import ehrparse, pickle, sys
from string import Template

from helpers import hyphens_to_underscores, prefix_lines, tab

# As a general translation policy, translated segments begin with 
# an empty line - this is how individual segments are spaced out.
# There are no blank lines at the end of a segment. 

####################

class RuleTranslator(object):
    def __init__(self, rule):
        self.rule = rule
    def __repr__(self):
        return repr(self.rule)

class canAc(RuleTranslator):
    def __init__(self, rule):
        super().__init__(rule)
        
    def translate(self):
        return lambda number: Template("""
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
    
    def canAcs_translator(self):
        assert len(self.canAcs)
        if len(self.canAcs) == 1:
            canAc_translation = self.canAcs[0].translate()(0)
        else:
            canAc_translation = """
def canActivate(self, *params):
    multi_try(%s)
""" % ", ".join("lambda: self.canActivate_%d(*params)" % i for i in list(range(1, len(self.canAcs) + 1))) +\
        "".join( rule.translate()(i+1) for (i, rule) in zip(list(range(len(self.canAcs))), self.canAcs) )
        
        return tab(canAc_translation)
    
    def translate(self):
        name, params = self.get_signature()
        
        return Template("""
class $name_u(Role):
    name = "$name"
    
    def __init__(self$params_front_comma$params):
        super().__init__($name_u.name, ($params))
        $self_params_assignment $params
$canAcs_trans$canDcs_trans$isDacs_trans"""
        ).substitute\
        (
            name = name,
            name_u = hyphens_to_underscores(name),
            
            params_front_comma = ", " if len(params) else "",
            params = ", ".join(map(repr, params)) if len(params) else "",
            
            self_params_newline = "\n" if len(params) else "",
            self_params_assignment = ( ", ".join("self."+repr(s) for s in params) + " = " if len(params) else "" ) if len(params) else "# no parameters",
            
            canAcs_trans = self.canAcs_translator(),
            canDcs_trans = tab(''.join(map(trans, self.canDcs))),
            isDacs_trans = tab(''.join(map(trans, self.isDacs))),
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


def trans(obj):
    """Translate object by invoking the translate() method."""
    if hasattr(obj, "translate"):
        return obj.translate()
    else: # comment out the repr
        return "\n" + prefix_lines(repr(obj), "#")

def translate_rules(rules):
    outline, roles = extract_roles(rules)

    translation  = ""
    translation += """from core import *
from datetime import datetime
"""
    translation += "".join( map(trans, outline) )
    
    return translation

####################

rule_set = ('spine', 'pds', 'hospital', 'ra')[1]

def repl(): # use python's quit() to break out
    while True:
        #print ">",
        x = input()
        if not len(x):
            continue
        try:
            y = eval(x)
            print(y)
        except Exception as e:
            print((e.message))

def save(rules):
    with open("%s.py" % rule_set, 'w') as f:
        f.write(tr)
    print("Done. Wrote to %s.py" % rule_set)

def get_rules():
    
    def reparse():
        rules = ehrparse.parse_one("data/%s.txt" % rule_set)
        with open("data/parse_tree.pickle", "wb") as f:
            pickle.dump(rules, f)

    reparse()

    with open("data/parse_tree.pickle", "rb") as f:
        return pickle.load(f)

rules = get_rules()

####################

print("Translating %d rules..." % len(rules))

tr = translate_rules(rules)

#save(rules)