
from ehr import *

print( spine.Spine_clinician(1,2,3).canActivate(1) )

# REPL
while True:
    print('>', end = '')
    x = input()
    if not len(x):
        continue
    try:
        y = eval(x)
        print(y)
    except Exception as e:
        print((e.message))
