
from functools import reduce

##################
# Helper functions
##################

def uniqify(seq): # order preserving uniqifier
    seen = set()
    return [ x for x in seq if x not in seen and not seen.add(x) ]

def identical(seq): # check if all elements in a sequence are identical
    return reduce(lambda a, b: (b, a[0]==b), seq, (seq[0], None))[1]

def str_substitue(s, c_from, c_to):
    if type(s) != str: raise TypeError("s must be of type str")
    return "".join(c_to if c == c_from else c for c in s)

def hyphens_to_underscores(s):
    return str_substitue(s, '-', '_')

def prefix_lines(s, prefix):
    if type(s) != str: raise TypeError("s must be of type str")
    return "".join( prefix + line + "\n" for line in s.splitlines() )

def tab(s, indentation_level=1):
    return prefix_lines(s, '    '*indentation_level)

