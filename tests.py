from translator import *

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

func_hypos()

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