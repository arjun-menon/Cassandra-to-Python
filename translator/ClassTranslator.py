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

from . RuleTranslator import *

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
           ) + "".join( rule.translate(self.params)(i+1) for (i, rule) in enumerate(rules) )
        
        return tab(translation)
    
    def isDac_translator(self):
        if not self.isDacs:
            return ''
        
        tr = ""
        for rule in self.isDacs:
            target_role =     rule.concl.args[1]
            target_subj = str(rule.concl.args[0])
            
            trigger = rule.hypos[0]
            rule.hypos = rule.hypos[1:] # remove triggering hypo.
            
            subj = repr(trigger.args[0]) # triggering hypo's subject
            t_params = [p for p in trigger.args[1].args]
            
            ht = HypothesesTranslator(rule)
            ht.external_vars = { repr(tp) : 'self.'+repr(sp) for tp, sp in zip(t_params, self.params) }
            ht.external_vars.update( { subj : 'subj' } )
            
            unbound_vars = [target_subj] + [repr(p) for p in target_role.args]
            # hasActivated -= {(s, r) for (s, r) in hasActivated if s == subj and r == role}
            # deactivate(hasActivated, self.agent, Agent(self.pat))
            deac = "hasActivated -= { "
            deactivation_expression = "(s, r) for (s, r) in hasActivated if s == {subject} and r == {role_name}({role_params})".format( 
                        subject = p(target_subj), 
                        role_name = h2u(target_role.name),
                        role_params = ', '.join(p(repr(a)) for a in target_role.args) )

            # code = "deactivate(hasActivated, {}, {}({}))  # {}\n".format(
            #             p(target_subj), h2u(target_role.name),
            #             ', '.join(p(repr(a)) for a in target_role.args), 
            #             rule.name )
            
            print(unbound_vars, deactivation_expression)
            unbound_vars, foo = ht.substitution_func_gen(unbound_vars, deactivation_expression)
            print(unbound_vars, foo())
            vd = { v : "Wildcard()" for v in unbound_vars }
            print(unbound_vars, foo(vd))
            print()
            deac += foo(vd)

            deac += " } # {%s}\n" % rule.name
            
            cond = ""
            if rule.hypos:
                cond = ht.translate_hypotheses(countf_wildcard = True)
                print('---------------------------------------------')
                print(cond)
                print('---------------------------------------------')
                print()
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
        "".join( rule.translate(self.params)(i+1) for (i, rule) in enumerate(self.permits) )
        
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

