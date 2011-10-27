import pickle, itertools
from string import Template
from ehrparse import *
from helpers import *

class StopTranslating(Exception):
    def __init__(self, reason):
        self.reason = reason
    def __repr__(self):
        return "todo: " + self.reason

@typecheck
def warn(message : str):
    print(message)

class CountFunctions(object):
    funcs = []

class HypothesesTranslator(object):
    def __init__(self, rule):
        self.rule = rule
        self.external_vars = None # initialized by derived class, will become dict
    
    def __repr__(self):
        return repr(self.rule)
    
    def substitution_func_gen(self, variables, code):
        """ 'variables' is a list of variables that appear in 'code'.
        'code' is a format string on which string.format is invoked. """
        
        ext, rest = separate(variables, lambda v: v in set(self.external_vars))
        
        substitution_dict = dict()
        
        substitution_dict.update( { e : self.external_vars[e] for e in ext } )
        
        substitution_dict.update( { r : p(r) for r in rest } )
        
        new_format_string = code.format(**substitution_dict)
        
        return ( set(rest), lambda vd = { r : r for r in rest }: new_format_string.format(**vd) )
    
    @typecheck
    def build_param_bindings(self, params: list_of(str)) -> list:
        """Returns a set of constraint code generation functions which binds role parameters to external variables"""
        constraints = []

        for var_name in params:

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
                # it's of the form "something in [lower, upper]"
                lower, upper = h2u(c.right.start.name), h2u(c.right.end.name)
                
                # Current-time() in [lower, upper]
                if type(c.left) == Function:
                    func_name = h2u(repr(c.left))

                    if len(c.left.args):
                        raise StopTranslating("can't handle 'in' operator - function with arguments: %r" % c.left)
                    
                    return self.substitution_func_gen([lower, upper],"%s in vrange({%s}, {%s})" % (func_name, lower, upper))
                
                # var in [lower, upper]
                if type(c.left) == Variable:
                    vn = h2u(repr(c.left))
                    
                    return self.substitution_func_gen([vn, lower, upper], "{%s} in vrange({%s}, {%s})" % (vn, lower, upper))
                
            elif type(c.right) == Function:
                func_name = h2u(str(c.right.name))
                func_args = [repr(arg) for arg in c.right.args]
                
                if type(c.left) == Variable:
                    vn = h2u(repr(c.left))
                    return self.substitution_func_gen( [vn] + func_args, 
                        "{%s} in %s" % (vn, func_name) + '(' + ', '.join('{'+a+'}' for a in func_args) + ')')
            
            elif type(c.right) == Variable:
                if type(c.left) == Variable:
                    cl, cr = h2u(repr(c.left)), h2u(repr(c.right))
                    return self.substitution_func_gen([cl, cr], "{%s} in {%s}" % (cl, cr))
        
        elif c.op == '=' or c.op == '<' or c.op == '!=':

            op = "==" if c.op == '=' else c.op
            
            cl, cr = h2u(repr(c.left)), h2u(repr(c.right))

            if type(c.left) == Variable and type(c.right) == Constant:
                return self.substitution_func_gen([cl], p(cl) + ' ' + op + ' ' + cr)

            elif type(c.left) == Variable and type(c.right) == Variable:
                return self.substitution_func_gen([cl, cr], p(cl) + ' ' + op + ' ' + p(cr))
        
        raise StopTranslating("could not translate constraint: " + repr(c))
    
    
    def build_canAc_bindings(self, canAc):
        subj, role = canAc.args
        
        bound_vars = [var.name for var in [subj] + role.args]
        default_vd = {vn : vn for vn in bound_vars}
        
        return self.substitution_func_gen(bound_vars, "canActivate({}, {}({}))".format(
            p(bound_vars[0]), h2u(role.name), ", ".join(p(v) for v in bound_vars[1:])
            ) )
    
    
    @typecheck
    def translate_hypotheses(self, wrapper:[str,str]=['',''], pre_conditional:str=''):
        try:
            ctrs, canAcs, hasAcs, funcs = separate(self.rule.hypos, 
                                                  lambda h: type(h) == Constraint, 
                                                  lambda h: h.name == "canActivate",
                                                  lambda h: h.name == "hasActivated")
            
            conditionals = []
            
            if pre_conditional:
                conditionals.append(pre_conditional)
            
            # translate hasActivated:
            tr = ""
            
            if len(hasAcs) == 1:
                hasAc = hasAcs[0]
                role = hasAc.args[1]
                hasAc_subj = repr(hasAc.args[0])
                role_name = role.name
                role_params = [repr(param) for param in role.args]
                
                # turn role_params into a set
                if len(role_params) != len(set(role_params)):
                    raise StopTranslating("duplicate role params in %s" + repr(role_params))
                else:
                    role_params = set(role_params)
                
                conditionals.append( 'role.name == "%s"' % role_name )
                
                # find which role params already exist in external_vars
                existing_role_params = role_params & set(self.external_vars)
                
                # create conditionals for existing role params
                conditionals.extend([ "role."+param + " == " + self.external_vars[param] for param in existing_role_params ])
                
                role_param_mapping = { rp : "role."+rp for rp in role_params }
                self.external_vars.update( role_param_mapping )
                
                if hasAc_subj in set(self.external_vars):
                    conditionals.append( "subj == " + self.external_vars[hasAc_subj] )
                self.external_vars.update({ hasAc_subj : 'subj' })
                
                tr = "return %s{\n\t1 for subj, role in hasActivated if \n\t" % ('' if not wrapper else wrapper[0])
                ending = "\n}" + wrapper[1]
                
            elif len(hasAcs) == 2:
                h1, h2 = hasAcs
                
                
                raise StopTranslating("a rule with 2 hasActivates - in progress")
            
            elif not hasAcs:
                tr = "return "
                ending = ""
                raise StopTranslating("a rule with no hasActivates")
            
            else:
                raise StopTranslating("Not implemented: %d hasAcs in a rule." % len(hasAcs))
            
            
            # handle canActivated:
            
            for (canAc_vars, canAc_cond_func) in map(self.build_canAc_bindings, canAcs):
                if(len(canAc_vars)):
                    pass#warn("check "+self.rule.name+" whether wildcards in canActivate are okay")
                vd = { canAc_var : "Wildcard()" for canAc_var in canAc_vars }
                conditionals.append( canAc_cond_func(vd) )
            
            # Handle the special case of (only) 1 count function invoked in a rule:
            
            count_funcs =  [f for f in funcs if f.name in CountFunctions.funcs]
            
            if len(count_funcs) == 1:
                f = count_funcs[0]
                f_return = str(f.args[0])
                args = [str(a) for a in f.args[1:]]
                
                unbound_vars, code_gen = self.substitution_func_gen(args, 
                    h2u(f.name) + '(' + ", ".join(p(str(a)) for a in args) + ')' )
                
                if unbound_vars:
                    raise StopTranslating("unbound vars in %s" % repr(f))
                
                # create a mapping from the return value of f to its code
                self.external_vars.update( { f_return : code_gen() } )
                              
                # remove f from funcs:
                funcs = [func for func in funcs if func.name != f.name]
                
            elif len(count_funcs) > 1:
                raise StopTranslating("more than 1 count function invoked in a rule")
            
            # handle constraints:
            
            for (ctr_vars, ctr_cond_func) in map(self.build_constraint_bindings, ctrs):
                if(ctr_vars):
                    raise StopIteration("unable to bind vars %s in constraint %s" % (ctr_vars, ctr_cond_func))
                else:
                    conditionals.append( ctr_cond_func() )
            
            # handle functions:
            
            for f in funcs:
                f_args = [str(a) for a in f.args]
                
                unbound_vars, code_gen = self.substitution_func_gen(f_args, 
                    h2u(f.name) + '(' + ", ".join(p(str(a)) for a in f_args) + ')' )
                
                if unbound_vars:
                    raise StopTranslating("unbound vars in %s" % repr(f))
                
                conditionals.append( code_gen() )
            
            if len(conditionals):
                tr += " and \n\t".join(conditionals)
            
            return tr + ending
        
        except StopTranslating as st:
            #print(self.rule.name + " was not translated.")
            return "".join("#" + str(x) + '\n' for x in [repr(st)] + self.rule.hypos) + "pass"

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
        
        #print(subj1, subj2)
        #print(self.rule)
        
        return"""
def canDeactivae(self, {subj1}, {subj2}): # {rule_name}
{hypotheses_translation}""".format(
                     rule_name = self.rule.name
                    ,subj1 = subj1
                    ,subj2 = subj2
                    ,hypotheses_translation = tab(self.translate_hypotheses(pre_conditional=pre_conditional))
                    )


class isDac(HypothesesTranslator):
    def __init__(self, rule):
        super().__init__(rule)
        
    def translate(self):
        return untranslated(self.rule)


class FuncRule(HypothesesTranslator):
    def __init__(self, rule):
        super().__init__(rule)
        #print(str(type(self.rule.concl.args[0])) + " " + repr(self.rule.concl.args[0]) + "  " + rule.concl.name)
        
        self.kind = None # Determine what kind of function it is:
        
        # is this of the form count-role-name(count<x>, ...) <- hasActivated(x, ...), ... ?
        if type(self.rule.concl.args[0]) == Aggregate:
            if self.rule.concl.args[0].name == 'count':
                if self.rule.hypos[0].name == SpecialPredicates.hasAc:
                    self.kind = 'count'
                    CountFunctions.funcs.append(self.rule.concl.name)
    
    def translate(self):
        if self.kind == 'count':
            args = [repr(a) for a in self.rule.concl.args[1:]]
            
            self.external_vars = { a:a for a in args }
            
            return"""
def {func_name}({func_args}): # {rule_name}
{hypotheses_translation}""".format(
                 rule_name = self.rule.name
                ,func_name = h2u(self.rule.concl.name)
                ,func_args = ", ".join(args)
                ,hypotheses_translation = tab(self.translate_hypotheses( ["len(" , ")"] ))
                )
        
        #print(self.rule)
        return untranslated(self.rule)

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
        return """
class {name_u}(Role):
    def __init__(self{optional_front_comma}{params_comma}):
        super().__init__('{name}', [{params_quote}]) {optional_self_assignment_newline_tab}{self_assignment}{params_comma}
{canAcs_trans}{canDcs_trans}{isDacs_trans}""".format(
        name   =     self.name,
        name_u = h2u(self.name)

        ,optional_front_comma = ", " if len(self.params) else ""
        ,params_comma= ", ".join(map(repr, self.params))
        ,params_quote = ", ".join("'" + repr(p) + "'" for p in self.params) if len(self.params) else ""

        ,optional_self_assignment_newline_tab = "\n        " if len(self.params) else ""
        ,self_assignment = ", ".join("self."+repr(s) for s in self.params) + " = " if len(self.params) else ""

        ,canAcs_trans = self.canAcs_translator()
        ,canDcs_trans = tab(''.join(map(lambda canDc: trans(canDc, self.params), self.canDcs)))
        ,isDacs_trans = tab(''.join(map(lambda isDac: trans(isDac), self.isDacs)))
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
    
    # grab the rules:
    
    for r in canAc_rules:
        roles[r.concl.args[1].name].canAcs.append( canAc(r) )
    
    for r in canDc_rules:
        roles[r.concl.args[2].name].canDcs.append( canDc(r) )
    
    for r in isDac_rules:
        for h in r.hypos:
            if type(h) == Atom and h.name == SpecialPredicates.isDac:
                role_name = h.args[1].name
        roles[role_name].isDacs.append( isDac(r) )
    
    # non-role rules
    outline = []
    
    for rule in rules:
        rule_type = rule.concl.name

        if rule_type == SpecialPredicates.canAc:
            # On first encounter of a canAc, place 
            # appropriate RoleClass in translated code.
            role_name = rule.concl.args[1].name
            if role_name in role_names:
                outline.append(roles[role_name])
                role_names.remove(role_name)

        elif rule_type == SpecialPredicates.isDac:
            pass # handled by above
        elif rule_type == SpecialPredicates.canDc:
            pass # handled by above
        
        elif rule_type == SpecialPredicates.prmts:
            outline.append(rule)
        elif rule_type == SpecialPredicates.canRC:
            outline.append(rule)
        else: # func rule
            outline.append( FuncRule(rule) )
    
    return outline

def untranslated(obj):
    return "\n" + prefix_lines("untranslated:\n" + repr(obj), "#")

def trans(obj, *args):
    """Translate object by invoking the translate() method."""
    if hasattr(obj, "translate"):
        return obj.translate(*args)
    else: # comment out the repr
        return untranslated(obj)

def translate_rules(rules, rule_set):
    print("Translating %d rules in %s..." % (len(rules), rule_set) )
    outline = generate_outline(rules)
    
#    for i in outline:
#        print(type(i))

    translation  = ""
    translation += """from cassandra import *
from datetime import datetime
"""
    translation += "".join( map(trans, outline) )

    return translation

####################

rule_sets = ['spine', 'pds', 'hospital', 'ra']
rules_collections = None

def parse_rules():
    global rules_collections, rule_sets
    rules_collections = [ ( rule_set, parse_one("ehr/%s.txt" % rule_set) ) for rule_set in rule_sets ]
    with open("ehr/parse_tree.pickle", "wb") as f:
        pickle.dump(rules_collections, f)

def unpickle_rules():
    global rules_collections
    with open("ehr/parse_tree.pickle", "rb") as f:
        rules_collections = pickle.load(f)

def translate_all():
    global rules_collections
    
    def write(tr, rule_set):
        with open("ehr/%s.py" % rule_set, 'w') as f:
            f.write(tr)
        print("Done. Wrote to %s.py\n" % rule_set)
        
    for (rule_set, rules) in rules_collections:
        tr = translate_rules(rules, rule_set)
        write(tr, rule_set)

#parse_rules()
unpickle_rules()
translate_all()
