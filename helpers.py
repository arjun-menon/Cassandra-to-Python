from typecheck import *
from functools import reduce

##################
# Helper functions
##################

def uniq(seq): # returns unique elements (like set) with order preserved
    seen = set()
    return [ x for x in seq if x not in seen and not seen.add(x) ]

def identical(seq): # check if all elements in a sequence are identical
    if len(seq) > 1:
        return reduce(lambda a, b: (b, a[0]==b), seq, (seq[0], None))[1]
    return True

def any_eq(val, seq):
    for k in seq:
        if k == val:
            return True
    return False

@typecheck
def str_substitute(s: str, char_to_sub: lambda s: len(s)==1, sub_with: str):
    if type(s) != str: raise TypeError("s must be of type str")
    return "".join(sub_with if c == char_to_sub else c for c in s)

def h2u(s): # convert hyphens to underscores
    return str_substitute(s, '-', '_')

@typecheck
def prefix_lines(s: str, prefix: str):
    return "".join( prefix + line + "\n" for line in s.splitlines() )

def tab(s, indentation_level=1):
    return prefix_lines(s, '    '*indentation_level)

def separate(alist, *conds):
    """ Examples:
     >  print(separate([1,2,3,4], lambda x: x % 2 ==0))
     >  ([2, 4], [1, 3])
     >  print( separate(range(1,16), lambda x: x % 2 ==0, lambda x: x % 3 ==0) )
     >  ([2, 4, 6, 8, 10, 12, 14], [3, 9, 15], [1, 5, 7, 11, 13]) """
    
    cats = []
    rest = alist
    for cond in conds:
        this, rest = [x for x in rest if cond(x) == True], [x for x in rest if cond(x) == False]
        cats.append(this)
    return tuple(cats+[rest])

def p(s):
    return '{' + s + '}'

##################
# Helper Classes
##################

class anyset(object): # because python sets don't allow dicts/objs
    def __init__(self):
        self.list_of_objects = []
    def add(self, obj):
        if not any_eq(obj, self.list_of_objects):
            self.list_of_objects.append(obj)
#    def __iter__(self):
#        return self
#    def __next__(self):
#        for i in self.list_of_objects:
#            yield i
    def __iter__(self):
        class ListIterator:
            def __init__(self, me):
                self.me = me
                self.pos = 0
            def __iter__(self):
                return self
            def __next__(self):
                if self.pos == len(self.me):
                    raise StopIteration
                else:
                    item = self.me[self.pos]
                    self.pos += 1
                    return item
        return ListIterator(self.list_of_objects)

class bla(object):
    pass

d = set()
d.add(bla())

#x = anyset()
#x.add({'a':'b'})
#x.add('foo')
#for i in x:
#    print(i)

class vrange(object):
    def __init__(self, start, end):
        self.start, self.end = start, end
    def __contains__(self, val):
        if not (val >= self.start and val <= self.end):
            #raise CassandraException("test failed: %r is not in [%r, %r]" % (val, self.start, self.end))
            return False
        return True
