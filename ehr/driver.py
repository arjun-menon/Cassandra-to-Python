
import spine, pds, ra, hospital

from cassandra import Role

a = spine.Spine_clinician(1,2,3)
b = spine.Spine_clinician(1,2,3)

print(a==b)

Role('ee', ['a'])

# repl
while True:
    #print ">",
    x = input()
    if not len(x):
        continue
    try:
        y = eval(x)
        print(y)
    except Exception as e:
        print((e.message))
