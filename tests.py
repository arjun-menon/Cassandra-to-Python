from translator import *

rules = rules_collections[0][1] + rules_collections[1][1] + rules_collections[2][1] + rules_collections[3][1]

def func_hypos():
    """This test shows only 3 special predicates appear in hypos, 
    and all other non-constraint predicates are function calls."""
    
    hs = []
    for r in rules:
        for h in r.hypos:
            if type(h) != Constraint:
                hs.append(h)
    
    print(len(hs))
    
    hy = [h for h in hs if h.name!="hasActivated" and h.name !="isDeactivated" and h.name!="canActivate"]
    print(len(hy))
    
    for i in hy:
        print(i)

#func_hypos()

def hasActivated_in_hypos():
    "Count and print number of hasActivated hypotheses in each rule."
    for r in rules:
        n = 0
        for h in r.hypos:
            if type(h) != Constraint:
                if h.name == "hasActivated":
                    n += 1
        print(n)

#hasActivated_in_hypos()

def which_have_canAc_hypos():
    "Print rules that have a canActivate hypo"
    for r in rules:
        for h in r.hypos:
            if type(h) != Constraint:
                    if h.name == "canActivate":
                        print(r)
                        break

#which_have_canAc_hypos()

def count_rule_kinds():
    c = lambda name: print(str(name) + ": " + str(len([r for r in rules if r.concl.name == name])))
    list(map(c, SpecialPredicates.list_all()))
    print("funcs: " + str(len([r for r in rules if r.concl.name not in SpecialPredicates.list_all()])) + '\n')
    
#count_rule_kinds()

def print_func_rules():
    for i in (r for r in rules if r.concl.name not in SpecialPredicates.list_all()):
        print(i)
        
#print_func_rules()

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

#repl()

def remote_hypos():
    for r in rules:
        for h in r.hypos:
            if type(h) != Constraint:
                if h.issuer or h.location:
                    print(r.name, h)
#remote_hypos()