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

class CassandraException(Exception):
    def __init__(self, description):
        self.description = description
    def __str__(self):
        return repr(self.description)

def test(func, src):
    if not func():
        raise CassandraException("test <" + src + "> failed.")

def multi_try(*funcs):
    """
    Try multiple functions, if any of them do not throw a CassandraException, multi_try returns None.
    If all of them throw CassandraExceptions, then multi_try throws a CassandraException their descriptions.
    """
    
    def try_func(func):
        try:
            func()
        except CassandraException as e:
            return e
        return None
    
    e_list = map(try_func, funcs)
    
    for e in e_list:
        if e == None:
            return None # success
     
    raise CassandraException( "Tried %d rules, and all failed:" % len(funcs) + "\n".join(e.description for e in e_list) )

class vrange(object):
    def __init__(self, start, end):
        self.start, self.end = start, end
    def __contains__(self, val):
        if not (val >= self.start and val <= self.end):
            #raise CassandraException("test failed: %r is not in [%r, %r]" % (val, self.start, self.end))
            return False
        return True

###################

def canActivate(subject, role):
    role.canActivate(subject)

def Current_time():
    return datetime.utcnow()

###################

# This should not be here, it should be in Cassandra external access functions
# all .py rule files import core, external interface imports them and has functions such as these below:
def activate(subject, role):
    try:
        role.canActivate(subject)
    except CassandraException:
        print("Error: ", CassandraException.description)

def repl(): # use python's quit() to break out
    while True:
        #print ">",
        x = input()
        try:
            if not len(x):
                continue
            y = eval(x)
            print(y)
        except Exception as e:
            print(repr(e))
