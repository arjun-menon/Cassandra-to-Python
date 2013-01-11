# Copyright (C) 2011-2012 Arjun G. Menon
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""Generates Python snippets for Datalog-with-constraints hypotheses.

Hypothese are the latter part of horn clauses (ie. after the ->).
They are the "conditions" that have to be satisfied for a horn clause to be true.

Hypotheses make up bulk of the translation work.
"""

import pickle, itertools
from string import Template

from . ehrparse import *
from . helpers import *

class StopTranslating(Exception):
    count = 0
    
    def __init__(self, rule, reason):
        self.rule, self.reason = rule, reason
        self.msg = self.rule.name + " todo: " + self.reason
        
        StopTranslating.count += 1
        #print(StopTranslating.count, "TODO: ", self.reason, "\n", self.rule, "\n")
    
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
        return StopTranslating(self.rule, reason)
    
    @typecheck
    def build_param_bindings(self, params: list_of(str)) -> list:
        """Returns a set of constraint code generation functions which binds role parameters to external variables"""
        constraints = []
        
        for var_name in params:
            
            def param_binding(vn):
                return lambda vd = { vn : vn } : "%s == self.%s" % (vd[vn], vn)
            
            constraints.append( ({var_name}, param_binding(var_name)) )
        
        return constraints
    
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
    
    
    def translate_hasActivated_hypo(self, hasAcs, wrapper):
        conditionals = []

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
        
        return tr, ending, conditionals
    
    def translate_canAcs(self, canAcs):
        # handle canActivated:
        
        for (canAc_vars, canAc_cond_func) in map(self.build_canAc_bindings, canAcs):
            if(len(canAc_vars)):
                pass#warn("check "+self.rule.name+" whether wildcards in canActivate are okay")
            vd = { canAc_var : "Wildcard()" for canAc_var in canAc_vars }
            return [ canAc_cond_func(vd) ]
        return []        
    
    def translate_countf(self, funcs, countf_wildcard):
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
        
        return funcs
    
    def translate_constraints(self, ctrs):
        # handle constraints:
        
        for (ctr_vars, ctr_cond_func) in map(self.build_constraint_bindings, ctrs):
            if(ctr_vars):
                raise self.stopTranslating("unable to bind vars %s in constraint %s" % (ctr_vars, ctr_cond_func()))
            else:
                return [ ctr_cond_func() ]
        return []
    
    @typecheck
    def translate_funcs(self, funcs) -> list:
        # handle functions:
        
        for f in funcs:
            f_args = [str(a) for a in f.args]
            
            unbound_vars, code_gen = self.substitution_func_gen(f_args, 
                h2u(f.name) + '(' + ", ".join(p(str(a)) for a in f_args) + ')' )
            
            if unbound_vars:
                raise self.stopTranslating("unbound vars in %s" % repr(f))
            
            return [ code_gen() ]
        
        return []
    
    def translate_group_rules(self, group_key, tr) -> str:
        # translate group<x> rules
        
        if group_key:
            group_key = str(group_key)
            if not group_key in set(self.external_vars):
                raise self.stopTranslating("could not find %s in %s" % (group_key, set(self.external_vars)))
            group_key = self.external_vars[group_key]
        else:
            group_key = True
        
        return Template(tr).safe_substitute(group_key = group_key)
    
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
            
            tr, ending,     hasAc_conditionals = self.translate_hasActivated_hypo(hasAcs, wrapper)
            conditionals += hasAc_conditionals
            
            conditionals += self.translate_canAcs(canAcs)
            funcs         = self.translate_countf(funcs, countf_wildcard)
            conditionals += self.translate_constraints(ctrs)
            conditionals += self.translate_funcs(funcs)
            tr            = self.translate_group_rules(group_key, tr)
            
            if len(conditionals):
                tr += " and \n    ".join(conditionals)
            
            if self.rule.name == 'S3.3.5':
                print("-----------------------------------")
            
            return tr + ending
        
        except StopTranslating as st:
            #print(self.rule.name + " was not translated.")
            return "".join("#" + str(x) + '\n' for x in [repr(st)] + self.rule.hypos) + "pass"
