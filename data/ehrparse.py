import tpg;

class EhrParser(tpg.Parser):
    r"""
    separator spaces: '\s+';
    token num: '\d+';
    token in: 'in\b';
    token notin: 'notin\b';
    token subseteq: 'subseteq\b';
    token nameident: '[A-Z][0-9]\.(\w|-|\.)+';
    token ident: '(\w|-)+';
    token lpar: '\(';
    token rpar: '\)';
    token comma: ',';
    token myif : '<-';
    token eq: '=';
    token neq: '!=';
    token langle: '<';
    token rangle: '>';
    token quote: '\"';
    token dot: '\.';
    token at: '@';
    token lbra: '\[';
    token rbra: '\]';

    START/f ->
        Rule                      $ f=[Rule]
        ( Rule                    $ f.append(Rule)
          )*;
    Rule/r ->
        Name Conclusion myif      $ r = Rule(Name,Conclusion)
        Hypothesis                $ r.addHypothesis(Hypothesis)
        ( comma Hypothesis        $ r.addHypothesis(Hypothesis)
          )*
      | Name Conclusion myif      $ r = Rule(Name,Conclusion)
      ;
    Name/n -> lpar nameident/n rpar;
    Conclusion/a -> Atom/a;
    Hypothesis/a -> Constraint/a | Atom/a | RemoteAtom/a;
        
    Atom/a ->
        ident lpar Arg            $ a = Atom(ident,Arg)
        ( comma Arg               $ a.addArgument(Arg)
          )* rpar;
    Arg/a ->
        FuncArg/a
      | AggArg/a
      | RemoteAtom/a 
      | ident                             $ a = Variable(ident)
      | quote ident quote                 $ a = Constant(ident)
      | num                               $ a = Constant(num,True)
      | lbra Arg/start comma Arg/end rbra $ a = Range(start,end)
      | lpar Arg                          $ a = Tuple(Arg)
        ( comma Arg                       $ a.addElement(Arg)
          )* rpar;
    FuncArg/a ->
        ident                     $ a = Function(ident)
        lpar Arg                  $ a.addArgument(Arg)
        ( comma Arg               $ a.addArgument(Arg)
          )* rpar
      | ident lpar rpar           $ a = Function(ident)
      ;
    AggArg/a ->
        ident langle Arg          $ a = Aggregate(ident,Arg)
        ( comma Arg               $ a.addArgument(Arg)
          )* rangle;

    RemoteAtom/a ->
        VarConst/iss dot Atom     $ a = RemoteAtom(None, iss, Atom)
      | VarConst/loc at VarConst/iss dot Atom
                                  $ a = RemoteAtom(loc, iss, Atom)
      ;
    VarConst/a ->
        ident                     $ a = Variable(ident)
      | quote ident quote         $ a = Constant(ident)
      | num                       $ a = Constant(num,True) 
      ;

    Constraint/c ->
        Arg/l Operator/o Arg/r    $ c = Constraint(l,o,r)
      ;
    Operator/o -> in/o | notin/o | subseteq/o | eq/o | neq/o | langle/o;
    """

class Rule:
    def __init__(self,name,concl):
        self.name = name
        self.concl = concl
        self.hypos = []
    def addHypothesis(self,hypothesis):
        self.hypos.append(hypothesis)
    def __repr__(self):
        x = [repr(i) for i in self.hypos]
        return repr(self.name)+ '\n' +repr(self.concl)+ ' <-\n\t' + ','.join(x)

class Atom:
    def __init__(self,name,arg):
        self.name = name
        self.args = [arg]
    def addArgument(self,arg):
        self.args.append(arg)
    def __repr__(self):
        x = [repr(i) for i in self.args]
        return self.name + '(' + ','.join(x) + ')'

class Constant:
    def __init__(self,value,number=False):
        self.value = value
        self.number = number
    def __repr__(self):
        if self.number: return self.value
        return '\"' + self.value + '\"'

class Variable:
    def __init__(self,name):
        self.name = name
    def __repr__(self):
        return self.name

class Function:
    def __init__(self,name):
        self.name = name
        self.args = []
    def addArgument(self,arg):
        self.args.append(arg)
    def __repr__(self):
        x = [repr(i) for i in self.args]
        return (self.name) + '(' + ','.join(x) + ')'

class Aggregate:
    def __init__(self,name,arg):
        self.name = name
        self.args = [arg]
    def addArgument(self,arg):
        self.args.append(arg)
    def __repr__(self):
        x = [repr(i) for i in self.args]
        return self.name + '<' + ','.join(x) + '>'
        
class Constraint:
    def __init__(self,left,op,right):
        self.left = left
        self.right = right
        self.op = op
    def __repr__(self):
        return repr(self.left) + ' ' + self.op + ' ' + repr(self.right)

class RemoteAtom:
    def __init__(self,location,issuer,atom):
        self.location = location
        self.issuer = issuer
        self.atom = atom
    def __repr__(self):
        ret = ""
        if self.location: ret += repr(self.location) + "@"
        return ret + repr(self.issuer) + '.' + repr(self.atom)

class Range:
    def __init__(self,start,end):
        self.start = start
        self.end = end
    def __repr__(self):
        return '[' + repr(self.start) + ',' + repr(self.end) + ']'

class Tuple:
    def __init__(self,first):
        self.elems = [first]
    def addElement(self,elem):
        self.elems.append(elem)
    def __repr__(self):
        x = [repr(i) for i in self.elems]
        return '(' + ','.join(x) + ')'

def parse():
    parser = EhrParser()
    ehr = file("spine").read() +\
      file("pds").read() +\
      file("hospital").read() +\
      file("ra").read()
    parse = parser(ehr)
    return parse
