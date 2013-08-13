import tpg
from ast_nodes import *

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
        VarConst/iss dot Atom     $ a = makeRemoteAtom(None, iss, Atom)
      | VarConst/loc at VarConst/iss dot Atom
                                  $ a = makeRemoteAtom(loc, iss, Atom)
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

def parse_ehr(code):
  return EhrParser()(code)

def parse_ehr_file(file_name):
    with open(file_name) as f:
        return parse_ehr( f.read() )
