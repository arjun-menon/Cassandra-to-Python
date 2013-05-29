#
# Cassandra EHR Abstract Syntax Tree (AST) Nodes
#

class Rule(object):
    def __init__(self,name,concl):
        self.name = name
        self.concl = concl
        self.hypos = []
    def addHypothesis(self,hypothesis):
        self.hypos.append(hypothesis)
    def __repr__(self):
        x = [repr(i) for i in self.hypos]
        return repr(self.name)+ '\n' +repr(self.concl)+ ' <-\n\t' + ', '.join(x)

class Atom(object):
    def __init__(self,name,args):
        self.name = name
        self.args = [args]
        self.location = None
        self.issuer = None
    def addArgument(self,arg):
        self.args.append(arg)
    def __repr__(self):
        x = [repr(i) for i in self.args]
        atom_repr = self.name + '(' + ', '.join(x) + ')'
        ret = ""
        if self.location: ret += repr(self.location) + "@"
        if self.issuer: return ret + repr(self.issuer) + '.' + atom_repr
        else: return atom_repr

class Constant(object):
    def __init__(self,value,number=False):
        self.value = value
        self.number = number
    def __repr__(self):
        if self.number: return self.value
        return '\"' + self.value + '\"'

class Variable(object):
    def __init__(self,name):
        self.name = name
    def __repr__(self):
        return self.name
    def __eq__(self, other):
        return other.name == self.name

class Function(object):
    def __init__(self,name):
        self.name = name
        self.args = []
    def addArgument(self,arg):
        self.args.append(arg)
    def __repr__(self):
        x = [repr(i) for i in self.args]
        return (self.name) + '(' + ', '.join(x) + ')'    
    def __eq__(self, other):
        return self.args == other.args

class Aggregate(object):
    def __init__(self,name,arg):
        self.name = name
        self.args = [arg]
    def addArgument(self,arg):
        self.args.append(arg)
    def __repr__(self):
        x = [repr(i) for i in self.args]
        return self.name + '<' + ', '.join(x) + '>'
        
class Constraint(object):
    def __init__(self,left,op,right):
        self.left = left
        self.right = right
        self.op = op
    def __repr__(self):
        return repr(self.left) + ' ' + self.op + ' ' + repr(self.right)

def makeRemoteAtom(location, issuer, atom):
    atom.location = location
    atom.issuer = issuer
    return atom

class Range(object):
    def __init__(self,start,end):
        self.start = start
        self.end = end
    def __repr__(self):
        return '[' + repr(self.start) + ', ' + repr(self.end) + ']'

class Tuple(object):
    def __init__(self,first):
        self.elems = [first]
    def addElement(self,elem):
        self.elems.append(elem)
    def __repr__(self):
        x = [repr(i) for i in self.elems]
        return '(' + ','.join(x) + ')'
