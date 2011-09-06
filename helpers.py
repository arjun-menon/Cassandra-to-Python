
from functools import reduce

##################
# Helper functions
##################

def uniqify(seq): # order preserving uniqifier
    seen = set()
    return [ x for x in seq if x not in seen and not seen.add(x) ]

def identical(seq): # check if all elements in a sequence are identical
    return reduce(lambda a, b: (b, a[0]==b), seq, (seq[0], None))[1]

def hyphens_to_underscores(s):
    if type(s) != str: raise TypeError("argument must be str!")
    return "".join('_' if c == '-' else c for c in s)

def prefix_line(s, prefix):
    return "".join( prefix + line + "\n" for line in s.split('\n') )

def tab(s, indentation_level=1):
    return prefix_line(s, '    '*indentation_level)

