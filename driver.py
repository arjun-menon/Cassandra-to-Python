
from ehr import *



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
