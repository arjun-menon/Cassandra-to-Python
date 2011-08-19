
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
        if type(current_activations[entity]) != set:
            raise CassandraException("[fatal] Corrupted data state - current_activations member nor set")
        if role in current_activations[entity]:
            return # successful
    raise CassandraException(entity + " has not activated " + role)

def activate(subject, role):
    try:
        role.canActivate(subject)
    except CassandraException:
        print "Error: ", CassandraException.explanation

def hyphens_to_underscores(s):
    return "".join('_' if c == '-' else c for c in s)

########
# Spine
########

class Spine_clinician(Role):
    def __init__(self, ra, org, spcty):
        super(Spine_clinician, self).__init__("Spine-clinician", (ra, org, spcty))
    
    def canActivate(self, subject):
        pass

print hyphens_to_underscores("asdfasd-ads")