from helpers import *
from datetime import *

class Role(object):
    def __init__(self, name, args):
        self.name = name
        self.args = args
    
    def __eq__(self, other):
        if self.name == other.name and self.args == other.args:
            self_params = [self.__dict__[p] for p in self.args]
            other_params = [other.__dict__[p] for p in other.args]
            
            matching_params = [a for (a, b) in zip(self_params, other_params)]
            if len(matching_params) == len(other_params):
                return True
        return False
    
    def __repr__(self):
        return self.name + '(' + ', '.join(map(repr, self.args)) + ')'

class  Action(object):
    def __init__(self, name, **params):
        self.name = name
        self.__dict__.update(params)
        self.prms = list(params)
    
    def __repr__(self):
        r = 'Action(' + repr(self.name)
        a = ', '.join( prm + ' = ' + repr(self.__dict__[prm]) for prm in self.prms )
        return ( (r + ', ' + a) if a else r ) + ')'

class Wildcard(object):
    def __eq__(self, other):
        return True

def canActivate(subject, role):
    role.canActivate(subject)

def deactivate(hasActivated, subj, role):
    hasActivated -= {(s, r) for (s, r) in hasActivated if s == subj and r == role}

def pi7_1(obj):
    pass

def Current_time():
    return datetime.utcnow()

