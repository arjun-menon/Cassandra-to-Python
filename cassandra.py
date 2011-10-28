from helpers import *
from datetime import datetime

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



class vrange(object):
    def __init__(self, start, end):
        self.start, self.end = start, end
    def __contains__(self, val):
        if not (val >= self.start and val <= self.end):
            #raise CassandraException("test failed: %r is not in [%r, %r]" % (val, self.start, self.end))
            return False
        return True

class Wildcard(object):
    def __eq__(self, other):
        return True

###################

def canActivate(subject, role):
    role.canActivate(subject)

def Current_time():
    return datetime.utcnow()

