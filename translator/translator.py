
from . HypothesesTranslator import *

####################

class canAc(HypothesesTranslator):
    def __init__(self, rule):
        super().__init__(rule)
        self.subject = repr(self.rule.concl.args[0])
    
    @typecheck
    def translate(self, role_params: list_of(Variable)):
        self.role_params = [repr(p) for p in role_params]
        
        # build self.external_vars (for HypothesesTranslator)
        self.external_vars = { p : 'self.'+p for p in self.role_params }
        self.external_vars.update( { self.subject : self.subject } )
        
        return lambda number: """
def canActivate{num}(self, {subject}): # {rule_name}
{hypotheses_translation}""".format(
             rule_name = self.rule.name
            ,num = "" if number==0 else "_" + str(number)
            ,subject = self.subject
            ,hypotheses_translation = tab(self.translate_hypotheses())
        )


class canDc(HypothesesTranslator):
    def __init__(self, rule):
        super().__init__(rule)
        
    @typecheck
    def translate(self, role_params: list_of(Variable)):
        self.role_params = [repr(p) for p in role_params]
        
        # build self.external_vars (for HypothesesTranslator)
        self.external_vars = { p : 'self.'+p for p in self.role_params }
        
        subj1 = str(self.rule.concl.args[0])
        subj2 = str(self.rule.concl.args[1])
        
        if subj1 == subj2:
            self.external_vars.update( { subj1 : subj1 } )
            subj2 = subj2 + "_"
            pre_conditional = "%s == %s" % (subj1, subj2)
        else:
            self.external_vars.update( { subj1 : subj1 , subj2 : subj2  } )
            pre_conditional = ""
        
        return lambda number: """
def canDeactivate{num}(self, {subj1}, {subj2}): # {rule_name}
{hypotheses_translation}""".format(
                     rule_name = self.rule.name
                     ,num = "" if number==0 else "_" + str(number)
                    ,subj1 = subj1
                    ,subj2 = subj2
                    ,hypotheses_translation = tab(self.translate_hypotheses(pre_conditional=pre_conditional))
                    )


class FuncRule(HypothesesTranslator):
    def __init__(self, rule):
        super().__init__(rule)
        
        self.kind = None # unknown kind        
        # Determine what kind of function it is...
        if type(self.rule.concl.args[0]) == Aggregate:
            if self.rule.concl.args[0].name == 'count':
                if self.rule.hypos[0].name == SpecialPredicates.hasAc:
                    # it is of the form: count-role-name(count<x>, ...) <- hasActivated(x, ...), ...
                    self.kind = 'count'
                    CountFunctions.funcs.append(self.rule.concl.name)
            elif self.rule.concl.args[0].name == 'group':
                self.kind = 'group'
                self.group_key = self.rule.concl.args[0].args[0]
        elif self.rule.concl.name == "no-main-role-active":
            self.kind = 'nmra'
    
    def nmra_trans_hypo(self):
        conditionals = []
        ctrs, funcs = separate(self.rule.hypos, lambda h: type(h) == Constraint)
        if len(ctrs) == 1:        
            varn, foo  = self.build_constraint_bindings(ctrs[0])
            if varn == {'n'}:
                for f in funcs:
                    if f.name in CountFunctions.funcs:
                        f_name = h2u(f.name)
                        f_args = [str(a) for a in f.args[1:]]
                        n = f_name + "(" + ", ".join(f_args) + ")"
                        conditionals.append( foo( { 'n' : n } ) )
                return "return  " + " and \\\n        ".join(conditionals)
        
        return untranslated(self.rule)
    
    def translate(self):
        if self.kind == 'count' or self.kind == 'group' or self.kind == 'nmra':
            
            if self.kind == 'nmra':
                args = [h2u(repr(a)) for a in self.rule.concl.args]
            else:
                args = [h2u(repr(a)) for a in self.rule.concl.args[1:]]
            
            self.external_vars = { a:a for a in args }
            
            if self.kind == 'nmra':
                hypotheses_translation = tab(self.nmra_trans_hypo())
            elif self.kind == 'count':
                hypotheses_translation = tab(self.translate_hypotheses( ["len(" , ")"] ))
            elif self.kind == 'group':
                hypotheses_translation = tab(self.translate_hypotheses( group_key = self.group_key ))
            
            return"""
def {func_name}({func_args}): # {rule_name}
{hypotheses_translation}""".format(
                 rule_name = self.rule.name
                ,func_name = h2u(self.rule.concl.name)
                ,func_args = ", ".join(args)
                ,hypotheses_translation = hypotheses_translation
                )
        
        return untranslated(self.rule)


class PermitsRule(HypothesesTranslator):
    def __init__(self, rule):
        super().__init__(rule)
        self.subject = str(self.rule.concl.args[0])
    
    def translate(self, action_params):
        # build self.external_vars (for HypothesesTranslator)
        self.external_vars = { p : 'self.'+p for p in action_params }
        self.external_vars.update( { self.subject : self.subject } )
        
        return lambda number: """
def permits{num}(self, {subject}): # {rule_name}
{hypotheses_translation}""".format(
             rule_name = self.rule.name
            ,num = "" if number==0 else "_" + str(number)
            ,subject = self.subject
            ,hypotheses_translation = tab(self.translate_hypotheses())
        )

####################

class SpecialPredicates:
    prmts = "permits"        # 1. permits(e,a) indicates that the entity e is permitted to perform action a.
    canAc = "canActivate"    # 2. canActivate(e, r) indicates that the entity e can activate role r.
    hasAc = "hasActivated"   # 3. hasActivated(e, r) indicates that the entity e has currently activated role r.
    canDc = "canDeactivate"  # 4. canDeactivate(e1,e2, r) indicates that e1 can deactivate e2's role r (if e2 has really currently activated r).
    isDac = "isDeactivated"  # 5. isDeactivated(e, r) indicates that e's role r shall be deactivated as a consequence of another role deactivation (if e has really currently activated r).
    canRC = "canReqCred"     # 6. canReqCred(e1,e2.p(~e)) indicates that e1 is allowed to request and receive credentials asserting p(~e) and issued by e2.
    
    @staticmethod
    def list_all():
        return [SpecialPredicates.prmts, SpecialPredicates.canAc, SpecialPredicates.hasAc,
                SpecialPredicates.canDc, SpecialPredicates.isDac, SpecialPredicates.canRC]
    
    @staticmethod
    def separate(rules, predicates):
        #e.g. prmts, canAc, hasAc, canDc, isDac, canRC, funcs = SpecialPredicates.separate(rules, ..)
        return separate(rules, *map(lambda pred: lambda rule: rule.concl.name == pred, predicates))

class RoleClass(object):
    def __init__(self, name, params):
        self.name = name
        self.params = params
        self.canAcs = []
        self.canDcs = []
        self.isDacs = []
    def __repr__(self):
        return "\ncanActivate rules:\n" + repr(self.canAcs) + "\ncanDeactivate rules:\n" + repr(self.canDcs) + ", \nisDeactivated rules:\n" + repr(self.isDacs) + "\n"
    
    def canAcs_canDcs_translator(self, category, rules):
        if len(rules) == 0:
            return ""
        if len(rules) == 1:
            translation = rules[0].translate(self.params)(0)
        else:
            translation = """
def {cat}(self, *params):
    return {or_calls}
""".format(cat = category, 
           or_calls = " or ".join("self.%s_%d(*params)" % (category, i) for i in list(range(1, len(rules) + 1)))
           ) + "".join( rule.translate(self.params)(i+1) for (i, rule) in zip(list(range(len(rules))), rules) )
        
        return tab(translation)
    
    def isDac_translator(self):
        if not self.isDacs:
            return ''
        
        tr = ""
        for rule in self.isDacs:
            assert rule.hypos[0].name == SpecialPredicates.isDac
            
            deac_role =     rule.concl.args[1]
            deac_subj = str(rule.concl.args[0])
            
            trigger = rule.hypos[0]
            rule.hypos = rule.hypos[1:] # remove triggering hypo.
            
            subj = repr(trigger.args[0]) # triggering hypo's subject
            t_params = [p for p in trigger.args[1].args]
            
            ht = HypothesesTranslator(rule)
            ht.external_vars = { repr(tp) : 'self.'+repr(sp) for tp, sp in zip(t_params, self.params) }
            ht.external_vars.update( { subj : 'subj' } )
            
            bound_vars = [deac_subj] + [repr(p) for p in deac_role.args]
            code = "deactivate(hasActivated, {}, {}({}))  # {}\n".format(
                        p(deac_subj), h2u(deac_role.name),
                        ', '.join(p(repr(a)) for a in deac_role.args), 
                        rule.name )
            
            unbound_vars, foo = ht.substitution_func_gen(bound_vars, code)
            vd = { v : "Wildcard()" for v in unbound_vars }
            deac = foo(vd)
            
            cond = ""
            if rule.hypos:
                cond = ht.translate_hypotheses(countf_wildcard = True)
                if cond[:8] == 'return (' and cond[-1:] == ')':
                    cond = cond[13:][:-2]
                if cond[0] == '#':
                    tr += cond[:-4]
                    cond = ''
            
            if cond:
                tr += "if " + cond + ":\n    " + deac
            else:
                tr += deac + '\n'
        
        return """
def onDeactivate(self, subj):
"""+tab(tr)
    
    def translate(self):
        name   =     self.name
        name_u = h2u(self.name)
        
        optional_comma = ", " if len(self.params) else ""
        params = ', '.join(map(repr, self.params))
        params_dict = ', '.join(str(p) + ' = ' + repr(p) for p in self.params)

        canAcs_trans = self.canAcs_canDcs_translator(SpecialPredicates.canAc, self.canAcs)
        canDcs_trans = self.canAcs_canDcs_translator(SpecialPredicates.canDc, self.canDcs)
        isDacs_trans = tab(self.isDac_translator())
        
        return """
class {name_u}(Role):
    def __init__(self{optional_comma}{params}):
        super().__init__('{name}'{optional_comma}{params_dict})
{canAcs_trans}{canDcs_trans}{isDacs_trans}""".format( **locals() )


class canReqCreds(object):
    def __init__(self, canAcs, hasAcs):
        # going to ignore "issuer" here, because "issuer" is always same as the module its part of.
        canAcRoleNames = {r.concl.args[1].args[1].name for r in canAcs}
        hasAcRoleNames = {r.concl.args[1].args[1].name for r in hasAcs}
        
        self.canAcs = { name : [r for r in canAcs if name==r.concl.args[1].args[1].name] for name in canAcRoleNames }
        self.hasAcs = { name : [r for r in hasAcs if name==r.concl.args[1].args[1].name] for name in hasAcRoleNames }
    
    def translate(self):
        #tr = "def canReqCred(subject, issuer, "
        tr  = ""
        
        tr += "# Credential Request Restrictions\n"
        tr += "# ===============================\n"
        tr += "# These rules determine if certain predicates can be \n"
        tr += "# invoked, such as canActivate or hasActivated.\n\n"
        tr += "# They restrict who can invoke such predicates.\n"
        tr += "# These rules have not been translated.\n"
        
        # canAcs
        tr += "\n# Restrictions on canActivate\n\n"
        for key, value in self.canAcs.items():
            tr += "# For the Role '" + key + "'\n"
            for rule in value:
                tr += '# \n' + prefix_lines(repr(rule) + "\n", '# ')
        
        # hasAcs
        tr += "\n# Restrictions on hasActivate\n\n"
        for key, value in self.hasAcs.items():
            tr += "# For the Role '" + key + "'\n"
            for rule in value:
                tr += '# \n' + prefix_lines(repr(rule) + "\n", '# ')
        
        return tr

class ActionClass(object):
    def __init__(self, name, params):
        self.name = name
        self.params = params
        self.permits = []
    
    def add_permits(self, r):
        self.permits.append(r)
    
    def __str__(self):
        r = 'Action: ' + self.name + "(" + ", ".join(self.params) + ")"
        return r
    
    def permits_translator(self):
        assert len(self.permits)
        if len(self.permits) == 1:
            translation = self.permits[0].translate(self.params)(0)
        else:
            translation = """
def permits(self, subj):
    return %s
""" % " or ".join("self.permits_%d(subj)" % i for i in list(range(1, len(self.permits) + 1))) +\
        "".join( rule.translate(self.params)(i+1) for (i, rule) in zip(list(range(len(self.permits))), self.permits) )
        
        return tab(translation)
    
    def translate(self):
        return """
class {name_u}(Role): # Action
    def __init__(self, {params}):
        super().__init__('{name}', {params_dict})
{permits}
""".format(
         name   =     self.name,
         name_u = h2u(self.name)
        ,params = ', '.join(self.params)
        ,params_dict = ', '.join(str(p) + ' = ' + repr(p) for p in self.params)
        ,permits = self.permits_translator()
        )

def generate_outline(rules):
    """
    Builds a dictionary mapping each unique role to RoleClass objects containing lists
    of 'canActivate' , 'canDeactivate' , 'isDeactivated' rules associated with that role.

    'canActivate' and 'canDeactivate' rules are assigned naively to their associated roles.
    'isDeactivated' rules are assigned to the predicate that triggers that deactivation.
    """
    
    # Separating the role rules
    
    three_special_predicates = (SpecialPredicates.canAc, SpecialPredicates.canDc, SpecialPredicates.isDac)
    
    canAc_rules, canDc_rules, isDac_rules, others = SpecialPredicates.separate(rules, three_special_predicates)
    
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
    
    # add canAc, canDc, isDac rules to appropriate RoleClasses:
    
    for r in canAc_rules:
        roles[r.concl.args[1].name].canAcs.append( canAc(r) )
    
    for r in canDc_rules:
        roles[r.concl.args[2].name].canDcs.append( canDc(r) )
    
    for r in isDac_rules:
        for h in r.hypos:
            if type(h) == Atom and h.name == SpecialPredicates.isDac:
                role_name = h.args[1].name
        roles[role_name].isDacs.append( r )
    
    permits = [ r for r in rules if r.concl.name == 'permits' ]
    actions = { r.concl.args[1].name : r.concl.args[1] for r in permits }
    actions = { name : ActionClass(name, [str(prm) for prm in atom.args]) for name, atom in actions.items() }
    [actions[ r.concl.args[1].name ].add_permits(PermitsRule(r)) for r in permits]
    
    canRqs = [ r for r in rules if r.concl.name == 'canReqCred' ]
    canRqs_canAcs = [r for r in canRqs if r.concl.args[1].name == SpecialPredicates.canAc]
    canRqs_hasAcs = [r for r in canRqs if r.concl.args[1].name == SpecialPredicates.hasAc]
    
    outline = []
    list_of_roles =[]
    
    for rule in rules:
        rule_type = rule.concl.name

        if rule_type == SpecialPredicates.canAc:
            # On first encounter of a canAc, place 
            # appropriate RoleClass in translated code.
            role_name = rule.concl.args[1].name
            if role_name in role_names:
                outline.append(roles[role_name])
                role_names.remove(role_name)
                list_of_roles.append(role_name)

        elif rule_type == SpecialPredicates.isDac:
            pass # handled by above
        elif rule_type == SpecialPredicates.canDc:
            pass # handled by above
        
        elif rule_type == SpecialPredicates.prmts:
            if rule.concl.args[1].name in actions:
                action = actions[ rule.concl.args[1].name ]
                outline.append(action)
                actions.pop(action.name)
        
        elif rule_type == SpecialPredicates.canRC:
            pass # canRrs added at end
        else: # func rule
            outline.append( FuncRule(rule) )
    
    outline.append( canReqCreds(canRqs_canAcs, canRqs_hasAcs) )
    
    return outline, list_of_roles

def untranslated(obj):
    return "\n" + prefix_lines("untranslated:\n" + repr(obj), "#")

def trans(obj, *args):
    """Translate object by invoking the translate() method."""
    if hasattr(obj, "translate"):
        return obj.translate(*args)
    else: # comment out the repr
        return untranslated(obj)

def translate_rules(rules, rule_sets, rule_set):
    print("Translating %d rules in %s..." % (len(rules), rule_set) )
    outline, list_of_roles = generate_outline(rules)
    
    other_rule_sets = set(rule_sets) - set([rule_set])
    other_imports = "import " + ", ".join('ehr.'+rs for rs in other_rule_sets) + '\n'

    translation  = "from cassandra import *\n"
    translation += other_imports
    translation += "\nhasActivated = list()  # Set of (subject, role) pairs representing currently active roles.\n"
    translation += "\nlist_of_roles = %s\n" % repr(list_of_roles)
    translation += "".join( map(trans, outline) )

    return translation
