
import pickle, itertools
from ehrparse import *
from helpers import *
from string import Template

class StopTranslating(Exception):
    def __init__(self, rn, reason):
        self.rn, self.reason = rn, reason
        self.msg = "%s todo: " % self.rn + self.reason
        print(self.msg)
        print()
    def __repr__(self):
        return self.msg

@typecheck
def warn(message : str):
    print(message)

class CountFunctions:
    funcs = []

def loc_trans(loc):
    if loc == '"PDS"':
        loc = 'pds'
    elif loc == '"Spine"':
        loc = 'spine'
    elif loc == '"RA-ADB"':
        loc = 'ra'
    
    return 'ehr.'+loc

class HypothesesTranslator(object):
    def __init__(self, rule):
        self.rule = rule
        self.external_vars = None # initialized by derived class, will become dict
    
    def __repr__(self):
        return repr(self.rule)
    
    def stopTranslating(self, reason):
        return StopTranslating(self.rule.name, reason)
    
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
                        raise self.stopTranslating("can't handle 'in' operator - function with arguments: %r" % c.left)
                    
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
            
            elif type(c.left) == Function and type(c.right) == Variable:
                func_name, func_args = h2u(c.left.name), [str(a) for a in c.left.args]
                return self.substitution_func_gen([cr]+func_args, func_name + 
                            '(' + ", ".join(p(a) for a in func_args) + ') ' + op + ' ' + p(cr))
        
        raise self.stopTranslating("could not translate constraint: " + repr(c))
    
    
    def build_canAc_bindings(self, canAc):
        subj, role = canAc.args
        
        bound_vars = [var.name for var in [subj] + role.args]
        
        loc = ''
        if canAc.issuer:
            loc = loc_trans( repr(canAc.issuer) )+'.'
        if canAc.location:
            loc = loc_trans( repr(canAc.location) )+'.'
        
        return self.substitution_func_gen(bound_vars, "canActivate({}, {}{}({}))".format(
            p(bound_vars[0]), loc, h2u(role.name), ", ".join(p(v) for v in bound_vars[1:])
            ) )
    
    
    @typecheck
    def translate_hypotheses(self, wrapper:[str,str]=['',''], pre_conditional:str='', group_key=None, countf_wildcard=False) -> lambda t: t:
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
                    raise self.stopTranslating("duplicate role params in %s" + repr(role_params))
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
                self.external_vars.update( { hasAc_subj : 'subj' } )
                
                loc = loc_trans( repr(hasAc.location) ) +'.' if hasAc.location else ''
                
                tr = "return %s{\n    $group_key for subj, role in %shasActivated if \n    " % (wrapper[0], loc)
                ending = "\n}" + wrapper[1]
                
            elif len(hasAcs) == 2:
                h1, h2 = hasAcs
                subj1, subj2 = str(h1.args[0]), str(h2.args[0])
                role1, role2 = h1.args[1], h2.args[1]
                
                conditionals.append( 'role1.name == "%s"' % role1.name )
                conditionals.append( 'role2.name == "%s"' % role2.name )
                
                if subj1 in set(self.external_vars):
                    conditionals.append( "subj1 == " + self.external_vars[subj1] )
                if subj2 in set(self.external_vars):
                    conditionals.append( "subj2 == " + self.external_vars[subj2] )
                
                role1_args, role2_args = [str(a) for a in role1.args], [str(a) for a in role1.args]
                conditionals.extend([ "role1."+p + " == " + self.external_vars[p] for p in (set(role1_args) & set(self.external_vars)) ])
                conditionals.extend([ "role2."+p + " == " + self.external_vars[p] for p in (set(role2_args) & set(self.external_vars)) ])
                
                self.external_vars.update( { subj1 : 'subj1' } )
                self.external_vars.update( { subj2 : 'subj2' } )
                self.external_vars.update( { rp : "role1."+rp for rp in role1_args } )
                self.external_vars.update( { rp : "role2."+rp for rp in role2_args } )
                
                loc1 = loc_trans( repr(h1.location) )+'.' if h1.location else ''
                loc2 = loc_trans( repr(h2.location) )+'.' if h2.location else ''
                
                tr = "return %s{\n    $group_key for (subj1, role1) in %shasActivated for (subj2, role2) in %shasActivated if \n    " % (wrapper[0], loc1, loc2)
                ending = "\n}" + wrapper[1]
                
                #print("Rule with 2 hasActivates:", self.rule.name)
            
            elif len(hasAcs) == 0:
                tr = "return (\n    "
                ending = "\n)"
                #raise self.stopTranslating("a rule with no hasActivates")
            
            else:
                raise self.stopTranslating("Not implemented: %d hasAcs in a rule." % len(hasAcs))
            
            
            # handle canActivated:
            
            for (canAc_vars, canAc_cond_func) in map(self.build_canAc_bindings, canAcs):
                if(len(canAc_vars)):
                    pass#warn("check "+self.rule.name+" whether wildcards in canActivate are okay")
                vd = { canAc_var : "Wildcard()" for canAc_var in canAc_vars }
                conditionals.append( canAc_cond_func(vd) )
            
            # Handle the special case of (only) 1 count function invoked in a rule:
            
            count_funcs =  [f for f in funcs if f.name in CountFunctions.funcs]
            
            for f in count_funcs:
                f_return = str(f.args[0])
                args = [str(a) for a in f.args[1:]]
                
                unbound_vars, code_gen = self.substitution_func_gen(args, 
                    h2u(f.name) + '(' + ", ".join(p(str(a)) for a in args) + ')' )
                
                if unbound_vars:
                    if countf_wildcard:
                        self.external_vars.update( { v : "Wildcard()" for v in unbound_vars } )
                    else:
                        raise self.stopTranslating("unbound vars %r in %r" % (unbound_vars, f))
                
                # create a mapping from the return value of f to its code
                self.external_vars.update( { f_return : code_gen() } )
                
                if unbound_vars and countf_wildcard:
                    for v in unbound_vars:
                        self.external_vars.pop(v)
                
                # remove f from funcs:
                funcs = [func for func in funcs if func.name != f.name]
            
            # handle constraints:
            
            for (ctr_vars, ctr_cond_func) in map(self.build_constraint_bindings, ctrs):
                if(ctr_vars):
                    raise self.stopTranslating("unable to bind vars %s in constraint %s" % (ctr_vars, ctr_cond_func()))
                else:
                    conditionals.append( ctr_cond_func() )
            
            # handle functions:
            
            for f in funcs:
                f_args = [str(a) for a in f.args]
                
                unbound_vars, code_gen = self.substitution_func_gen(f_args, 
                    h2u(f.name) + '(' + ", ".join(p(str(a)) for a in f_args) + ')' )
                
                if unbound_vars:
                    raise self.stopTranslating("unbound vars in %s" % repr(f))
                
                conditionals.append( code_gen() )
            
            # for group<x> rules
            if group_key:
                group_key = str(group_key)
                if not group_key in set(self.external_vars):
                    raise self.stopTranslating("could not find %s in %s" % (group_key, set(self.external_vars)))
                group_key = self.external_vars[group_key]
            else:
                group_key = True
            
            tr = Template(tr).safe_substitute(group_key = group_key)
            
            if len(conditionals):
                tr += " and \n    ".join(conditionals)
            
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
        return """
class {name_u}(RoleAction):
    def __init__(self, {params}):
        super().__init__('{name}', **{params_dict})
{canAcs_trans}{canDcs_trans}{isDacs_trans}""".format(
         name   =     self.name
        ,name_u = h2u(self.name)
        ,params = ', '.join(map(repr, self.params))
        ,params_dict = '{' + ', '.join("'"+repr(p)+"':"+repr(p) for p in self.params) + '}'

        ,canAcs_trans = self.canAcs_canDcs_translator(SpecialPredicates.canAc, self.canAcs)
        ,canDcs_trans = self.canAcs_canDcs_translator(SpecialPredicates.canDc, self.canDcs)
        ,isDacs_trans = tab(self.isDac_translator()) #tab(''.join(map(lambda isDac: trans(isDac), self.isDacs)))
        )
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

        ,canAcs_trans = self.canAcs_canDcs_translator(SpecialPredicates.canAc, self.canAcs)
        ,canDcs_trans = self.canAcs_canDcs_translator(SpecialPredicates.canDc, self.canDcs)
        ,isDacs_trans = tab(self.isDac_translator()) #tab(''.join(map(lambda isDac: trans(isDac), self.isDacs)))
        )

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
class {name_u}(RoleAction):
    def __init__(self, {params}):
        super().__init__('{name}', **{params_dict})
{permits}
""".format(
         name   =     self.name,
         name_u = h2u(self.name)
        ,params = ', '.join(self.params)
        ,params_dict = '{' + ', '.join("'"+p+"':"+p for p in self.params) + '}'
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

def translate_rules(rules, rule_set):
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

####################

ehr_path = "ehr/"

rule_sets = ['spine', 'pds', 'hospital', 'ra']
rules_collections = None

def parse_rules():
    global rules_collections, rule_sets
    rules_collections = [ ( rule_set, parse_one(ehr_path+"%s.txt" % rule_set) ) for rule_set in rule_sets ]
    with open(ehr_path+"parse_tree.pickle", "wb") as f:
        pickle.dump(rules_collections, f)

def unpickle_rules():
    global rules_collections
    with open(ehr_path+"parse_tree.pickle", "rb") as f:
        rules_collections = pickle.load(f)

def translate_all():
    global rules_collections
    
    def write(tr, rule_set):
        with open(ehr_path+"%s.py" % rule_set, 'w') as f:
            f.write(tr)
        print("Done. Wrote to %s.py\n" % rule_set)
        
    for (rule_set, rules) in rules_collections:
        tr = translate_rules(rules, rule_set)
        write(tr, rule_set)

if __name__ == "__main__":
    #parse_rules()
    unpickle_rules()
    translate_all()
