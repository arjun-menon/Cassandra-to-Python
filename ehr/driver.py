
import spine, pds, ra, hospital

from cassandra import Role

x = spine.Spine_clinician(1,2,3)
y = spine.Spine_clinician(1,2,3)

print(x==y)

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
