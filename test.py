
import ehrparse

r = ehrparse.parse_one("data/spine.txt")

r0 = r[0]
print(r0)

x = r0.hypos[0].atom

print(x)
print(type(x))