from translator import *

def num_constraints(r):
    return len([h for h in r.hypos if type(h) == Constraint])

#print([num_constraints(r) for r in rules])

s = [r for r in rules if num_constraints(r) > 1]

print(len(s))

def func_hypos():
    """This test shows only 3 special predicates appear in hypos, 
    and all other non-constraint predicates are function calls."""
    
    hs = []
    for r in rules:
        for h in r.hypos:
            if type(h) != Constraint:
                if type(h) == RemoteAtom:
                    h = h.atom
                hs.append(h)
    
    print(len(hs))
    
    hy = [h for h in hs if h.name!="hasActivated" and h.name !="isDeactivated" and h.name!="canActivate"]
    print(len(hy))
    
    for i in hy:
        print(i)

#func_hypos()

def hasActivated_in_hypos():
    
    for r in rules:
        n = 0
        for h in r.hypos:
            
            if type(h) != Constraint:
                if type(h) == RemoteAtom:
                    h = h.atom
                
                if h.name == "hasActivated":
                    n += 1
        
        print(n)

hasActivated_in_hypos()