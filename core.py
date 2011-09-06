
hasActivated = set()  # Set of (entity, role) pairs representing current activations.

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

def activate(subject, role):
    try:
        role.canActivate(subject)
    except CassandraException:
        print("Error: ", CassandraException.explanation)

def hyphens_to_underscores(s):
    return "".join('_' if c == '-' else c for c in s)

