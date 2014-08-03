# Copyright (C) 2011-2013 Arjun G. Menon
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

from . L2_ClassTranslator import *

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

def trans(obj, *args):
    """Translate object by invoking the translate() method."""
    if hasattr(obj, "translate"):
        return obj.translate(*args)
    else: # comment out the repr
        return untranslated(obj)

def translate_module(rules, rule_sets, rule_set):
    print("Translating %d rules in %s...\n" % (len(rules), rule_set) )
    outline, list_of_roles = generate_outline(rules)
    
    other_rule_sets = set(rule_sets) - set([rule_set])
    other_imports = "import " + ", ".join('ehr.'+rs for rs in other_rule_sets) + '\n'

    translation  = "from auxiliary import *\n"
    translation += other_imports
    translation += "\nhasActivated = list()  # Set of (subject, role) pairs representing currently active roles.\n"
    translation += "\nlist_of_roles = %s\n" % repr(list_of_roles)
    translation += "".join( map(trans, outline) )

    return translation
