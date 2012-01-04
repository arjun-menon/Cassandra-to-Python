
from ehr import *
from ehr.spine import Spine_clinician

#print( spine.Spine_clinician(1,2,3).canActivate('Dr. Bob') )
#print( canActivate('Dr. Bob', Spine_clinician(1,2,3)) )

# The following test attempts to satisfy/
# successfully execute the rule S1.1.1
# The rule is shown below for reference:

# canActivate(cli, Spine-clinician(ra, org, spcty)) <-
# ra.hasActivated(x, NHS-clinician-cert(org, cli, spcty, start, end)),
# canActivate(ra, Registration-authority()),
# no-main-role-active(cli),
# Current-time() in [start, end]

# First create a NHS-clinician-cert and add it to hasActivated:
new_role = Role('NHS-clinician-cert', ['org', 'cli', 'spcty', 'start', 'end'])
new_role.org = 'GPs'
new_role.cli = 'Dr.Bob'
new_role.spcty = 'Dermatologist'
new_role.start = MINYEAR
new_role.end = MAXYEAR

spine.hasActivated.add(new_role)

# The second hypothesis depends on rule S1.5.1 shown below:
#
# canActivate(ra, Registration-authority()) <-
# "NHS".hasActivated(x, NHS-registration-authority(ra, start, end)),
# Current-time() in [start, end]

# Let's create a new registration authority and add it as well
new_role = Role('NHS-registration-authority', ['ra', 'start', 'end'])
new_role.ra = 'Bar'
new_role.start = MINYEAR
new_role.end = MAXYEAR

spine.hasActivated.add(new_role)

# no-main-role should work fine, since no other roel has been activated.
print(spine.hasActivated.list_of_objects)

# Testing it:
result = canActivate('Dr. Bob', Spine_clinician('Bar', 'GPs', 'Dermatologist'))
print('Result = ', result)

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

