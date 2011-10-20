import pickle, itertools
from string import Template
from ehrparse import *
from helpers import *

class StopTranslating(Exception):
    def __init__(self, reason):
        self.reason = reason
    def __repr__(self):
        return "todo: " + self.reason

class Wildcard(object):
    def __eq__(self, other):
        return True

class HypothesesTranslator(object):
    def __init__(self, rule):
        self.rule = rule
    def __repr__(self):
        return repr(self.rule)

    @typecheck
    def build_param_bindings(self, params: list_of(Variable)) -> list:
        """Returns a set of constraint code generation functions which binds role parameters to external variables"""
        constraints = []

        for var in params:
            var_name = str(var)

            def param_binding(vn):
                return lambda vd = { vn : vn } : "%s == self.%s" % (vd[vn], vn)

            constraints.append( ({var_name}, param_binding(var_name)) )

        return constraints
    
    
    @typecheck
    def build_constraint_bindings(self, c: Constraint):
        """ returns a special data structure of the form ({ set of bound variable names }, lambda vd: ...)
            The lambda when called returns a string which is translation of the constraint to Python.
            * the first dict is a list of variables names that are bound (or affected) by the constraint 
            * vd is a dictionary where you can substitute these variable names with other variable names 
              of your choice (for example substitute "cli" with "self.cli"). The form of the vd is {"cli":"self.cli"}
        """

        if c.op == 'in':

            if type(c.right) == Range and type(c.right.start) == Variable and type(c.right.end) == Variable:

                # it's of the form "something in [start, end]"
                start, end = h2u(c.right.start.name), h2u(c.right.end.name)

                if type(c.left) == Function:
                    fname = h2u(repr(c.left))

                    if len(c.left.args):
                        raise StopTranslating("can't handle 'in' operator - function with arguments: %r" % c.left)

                    return {start, end}, lambda vd = {start:start, end:end}: \
                        '%s in vrange(%s, %s)' % (fname, vd[start], vd[end])

                if type(c.left) == Variable:
                    vn = h2u(repr(c.left))

                    return {vn, start, end}, lambda vd = {vn:vn, start:start, end:end}: \
                        '%s in vrange(%s, %s)' % (vd[vn], vd[start], vd[end])

        elif c.op == '=' or c.op == '<':

            op = "==" if c.op == '=' else c.op
            
            cl, cr = h2u(repr(c.left)), h2u(repr(c.right))

            if type(c.left) == Variable and type(c.right) == Constant:
                return {cl}, lambda vd = {cl:cl}: "%s %s %s" % (cl, op, cr)

            elif type(c.left) == Variable and type(c.right) == Variable:
                return {cl, cr}, lambda vd = {cl:cl, cr:cr}: "%s %s %s" % (cl, op, cr)

        raise StopTranslating("could not form bindings for constraint: " + repr(c))
    
    
    def build_canAc_bindings(self, canAc):
        subj, role = canAc.args
        
        bound_vars = [var.name for var in [subj] + role.args]
        default_vd = {vn : vn for vn in bound_vars} 
        
        return set(bound_vars), lambda vd = default_vd: \
            "canActivate({subj}, {role_name}({role_args}))".format\
            (role_name = role.name, subj = bound_vars[0], role_args = ", ".join(bound_vars[1:]))
    
    
    def translate_hasActivated(self, hasAc, bindings):
        subj, role = hasAc.args

        def build_if_condition(params, bindings):
            conds = []

            for b in bindings:
                variables, func = b
                
                intersection = params & variables
                if intersection:
                    if intersection != variables:
                        raise StopTranslating(repr(variables) + " variables in constraint: no match in " + repr(params))
                    conds.append( func( {v:'role.'+v for v in variables} ) )

            return " and ".join(conds)


        if_conds = build_if_condition({repr(arg) for arg in role.args}, bindings)

        #print(subj, role, "-->", {repr(arg) for arg in role.args})

        t = Template(
"""{ (subject, role) for subject, role in hasActivated if role.name == "$role_name"$if_conds }"""
        ).substitute\
        (role_name = role.name, if_conds = " and " + if_conds if len(if_conds) else "")

        return t
    
    
    @typecheck
    def translate_hypotheses(self, bindings: list):
        try:
            ctrs, rest = separate( self.rule.hypos, lambda h: type(h) == Constraint )
            
            bindings.extend(map(self.build_constraint_bindings, ctrs))
            
            canAcs, rest = separate( rest, lambda h: h.name == "canActivate" )
            
            bindings.extend(map(self.build_canAc_bindings, canAcs))
            
            
            if any_eq(None, bindings):
                # this means there is a constraint that couldn't be translated.
                # when a constraint is not translated, None is returned by the translating function
                raise StopTranslating("couldn't build bindings")

            nc_hypos = [h for h in self.rule.hypos if type(h) != Constraint]  # non-constraint hypos

            def print_bindings():
                print(self.rule.name)
                for b in bindings:
                    vars, func = b
                    print(vars, " -->", func())
                print("---")
                print()
            print_bindings()

            # Now translate:
            tr = []
            for h in nc_hypos:

#                if(type(h) == RemoteAtom):
#                    # TODO
#                    h = h.atom
#
#                assert type(h) == Atom

                if h.name == "hasActivated":
                    tr.append( self.translate_hasActivated(h, bindings) )
                else:
                    tr.append( h2u(repr(h)) )

            return "return\\\n" + ' and\\\n'.join(tr)

        except StopTranslating as st:
            return "".join("#" + str(x) + '\n' for x in [repr(st)] + self.rule.hypos) + "pass"

class canAc(HypothesesTranslator):
    def __init__(self, rule):
        super().__init__(rule)

    @typecheck
    def translate(self, params: list_of(Variable)):
        return lambda number: Template("""
def canActivate$num(self$params): # $rule_name
$translation"""
        ).substitute\
        (
            rule_name = self.rule.name,
            num = "" if number==0 else "_" + str(number),
            params = "".join(", " + repr(s) for s in self.rule.concl.args[:-1]) if len(self.rule.concl.args) else "",
            translation = tab( self.translate_hypotheses(self.build_param_bindings(params)) )
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

    def canAcs_translator(self):
        assert len(self.canAcs)
        if len(self.canAcs) == 1:
            canAc_translation = self.canAcs[0].translate(self.params)(0)
        else:
            canAc_translation = """
def canActivate(self, *params):
    return %s
""" % " or ".join("self.canActivate_%d(*params)" % i for i in list(range(1, len(self.canAcs) + 1))) +\
        "".join( rule.translate(self.params)(i+1) for (i, rule) in zip(list(range(len(self.canAcs))), self.canAcs) )

        return tab(canAc_translation)

    def translate(self):

        template = """
class $name_u(Role):
    def __init__(self$optional_front_comma$params_comma):
        super().__init__('$name', [$params_quote]) $optional_self_assignment_newline_tab$self_assignment$params_comma
$canAcs_trans$canDcs_trans$isDacs_trans"""

        d = {}

        d['name'  ] =     self.name
        d['name_u'] = h2u(self.name)

        d["optional_front_comma"] = ", " if len(self.params) else ""
        d["params_comma"]= ", ".join(map(repr, self.params))
        d["params_quote"] = ", ".join("'" + repr(p) + "'" for p in self.params) if len(self.params) else ""

        d["optional_self_assignment_newline_tab"] = "\n        " if len(self.params) else ""
        d["self_assignment"] = ", ".join("self."+repr(s) for s in self.params) + " = " if len(self.params) else ""

        d["canAcs_trans"] = self.canAcs_translator()
        d["canDcs_trans"] = tab(''.join(map(trans, self.canDcs)))
        d["isDacs_trans"] = tab(''.join(map(trans, self.isDacs)))
        return Template(template).substitute(d)

def generate_outline(rules):
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
            if type(h) == Atom and h.name == special_predicates[5]: # isDeactivated
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

    return outline


def trans(obj):
    """Translate object by invoking the translate() method."""
    if hasattr(obj, "translate"):
        return obj.translate()
    else: # comment out the repr
        return "\n" + prefix_lines(repr(obj), "#")

def translate_rules(rules):
    outline = generate_outline(rules)

    translation  = ""
    translation += """from cassandra import *
from datetime import datetime
"""
    translation += "".join( map(trans, outline) )

    return translation

####################

rule_set = ('all', 'spine', 'pds', 'hospital', 'ra')[1]

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
    with open("ehr/%s.py" % rule_set, 'w') as f:
        f.write(tr)
    print("Done. Wrote to %s.py" % rule_set)

def get_rules():
    should_parse = False

    def ehr_parse():
        rules = parse_all() if rule_set == 'all' else parse_one("ehr/%s.txt" % rule_set)
        with open("ehr/parse_tree.pickle", "wb") as f:
            pickle.dump(rules, f)
        return rules
    
    if should_parse:
        return ehr_parse()
    else:
        with open("ehr/parse_tree.pickle", "rb") as f:
            return pickle.load(f)

rules = get_rules()

####################

print("Translating %d rules..." % len(rules))

tr = translate_rules(rules)

save(rules)