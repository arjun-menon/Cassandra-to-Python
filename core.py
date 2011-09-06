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

def constraint(constraint_function, constraint_description):
    if not constraint_function():
        raise CassandraException("Constraint [" + constraint_description + "] failed.")

def activate(subject, role):
    try:
        role.canActivate(subject)
    except CassandraException:
        print("Error: ", CassandraException.description)

def multi_try(*funcs):
    def try_and_get_exception(func):
        try:
            func()
        except CassandraException as e:
            return e
        return None
    
    e_list = map(try_and_get_exception, funcs)
    
    for e in e_list:
        if e == None:
            return None # success
     
    raise CassandraException( "Tried %d rules, and all failed:" % len(funcs) + "\n".join(e.description for e in e_list) )

########
# Spine
########

class Spine_clinician(Role):
    name = "Spine-clinician"
    
    def __init__(self, ra, org, spcty):
        super().__init__(self.name, (ra, org, spcty))
        self.ra, self.org, self.spcty = ra, org, spcty
    
    def canActivate(self, cli):
        current_time = datetime.utcnow()
        return no_main_role_active(cli) and \
            Registration_authority.canActivate(self.ra) and \
            len([x for (x, y) in hasActivated if y.name==NHS_clinician_cert.name and y.start < current_time and y.end > current_time]) > 0 #todo issuer ra, check both locations here and ra

class NHS_clinician_cert(Role):
    name = "NHS-clinician-cert"
    
    def __init__(self, org, cli, spcty, start, end):
        super().__init__(NHS_clinician_cert.name, (org, cli, spcty, start, end))
        self.org, self.cli, self.spcty, self.start, self.end = org, cli, spcty, start, end

class Registration_authority(Role):
    def canActivate(self):
        pass

def no_main_role_active(user):
    pass

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
