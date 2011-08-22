
import cPickle as pickle
import ehrparse
import operator

#rules = ehrparse.parse()
#pickle.dump(rules, open("parse_tree", "wb"))
rules = pickle.load(open("parse_tree"))

def repl():
    while True:
        #print ">",
        x = raw_input()
        try:
            y = eval(x)
        except Exception as e:
            print e.message
        print y

def uniq(seq):
    seen = set()
    seen_add = seen.add
    return [ x for x in seq if x not in seen and not seen_add(x)]

####################

class Role(object):
    pass

the_role_predicates = ("canActivate", "canDeactivate", "isDeactivated")
role_rules = [rule for rule in rules if rule.concl.name in the_role_predicates]
non_role_rules = [rule for rule in rules if rule.concl.name not in the_role_predicates]

canAc_rules = [rule for rule in rules if rule.concl.name == the_role_predicates[0]]
canAc_roles = [rule.concl.args[1] for rule in canAc_rules]

canAc_role_names_uniq = uniq([role.name for role in canAc_roles])

canAc_roles_grouped = [[role for role in canAc_roles if role.name == i] for i in canAc_role_names_uniq]
canAc_roles_grouped_multi = filter(lambda g: len(g) > 1, canAc_roles_grouped)

def check_group_integrity(canAc_role_names_group):
    args_list = [x.args for x in canAc_role_names_group]
    if len(set([len(lst) for lst in args_list])) == 1: # check if they have the same number of arguments
        if len(args_list[0]) == 0:
            return True
        else:
            return True
    else:
        return False
    #return reduce( operator.and_, [ pair[0] == pair[1] for pair in reduce( lambda a,b: zip(a.args, b.args), canAc_role_names_group ) ] )

for g in canAc_roles_grouped_multi:
    print check_group_integrity(g), " ", g

#[rl for rl in canAc_grouped]

repl()