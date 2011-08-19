
# Current activations are stored in a dictionary which maps strings to Role objects,
#  where the strings are the entity names and the Role objects are activated roles.
current_activations = {}

class Role(object):
    def __init__(self, name, args):
        assert type(args) == tuple
        self.name = name
        self.args = args
    def __eq__(self, other):
        return self.name == other.args and self.args == other.args
    def __repr__(self):
        return self.name + '(' + ', '.join(map(repr, self.args)) + ')'

class CassandraException(Exception):
    def __init__(self, explanation):
        self.explanation = explanation
    def __str__(self):
        return repr(self.explanation)

def constraint(constraint_function, constraint_description):
    if not constraint_function():
        raise CassandraException("Constraint [" + constraint_description + "] failed.")

def hasActivated(entity, role):
    if entity in current_activations:
        assert(type(current_activations[entity]) == set)
        if role in current_activations[entity]:
            return # successful
    raise CassandraException("hasActivated("+entity+","+role+") failed.")

def activate(entity, role):
    try:
        pass
    except CassandraException:
        print "Error: ", CassandraException.explanation


#######
## RA
#######
#
#class Register_RA_Manager(Role):
#    name = "Register-RA-Manger"
#    
#    def __init__(self, mgr):
#        super(Register_RA_Manager, self).__init__(Register_RA_Manager.name, (mgr))
#    
#    def canActivate(self, mgr): # (R1.1.1)
#        hasActivated(mgr, Role("RA-manager",()))
#        constraint(lambda: RA_manager_regs(self) == 0, "RA-manager-regs(n, mgr2), n=0")
#    
#    def canDeactivate(self, mgr, x): # (R1.1.2)
#        #hasActivated(, role)
#        pass
#
#def RA_manager_regs(mgr): # (R1.1.3)
#    return sum([ len([r for r in entity if r==Register_RA_Manager(mgr)]) for entity in current_activations ])


########
# Spine
########

class Spine_clinician(Role):
    def __init__(self, ra, org, spcty):
        super(Spine_clinician, self).__init__("Spine-clinician", (ra, org, spcty))
    
    def canActivate(self, entity):
        pass

#####################
# External Interface
#####################

def repl():
    # use python's quit() to exit
    while True:
        print ">",
        x = raw_input()
        print eval(x)

# test code:
