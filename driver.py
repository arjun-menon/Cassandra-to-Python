
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
new_role = RoleAction('NHS-clinician-cert', 
                    **{'org':'GPs', 
                       'cli':'Dr.Bob', 
                       'spcty':'Dermatologist', 
                       'start':MINYEAR, 
                       'end':MAXYEAR })

spine.hasActivated.append(new_role)

# The second hypothesis depends on rule S1.5.1 shown below:
#
# canActivate(ra, Registration-authority()) <-
# "NHS".hasActivated(x, NHS-registration-authority(ra, start, end)),
# Current-time() in [start, end]

# Let's create a new registration authority and add it as well
new_role = RoleAction('NHS-registration-authority', 
                    **{'ra':'Bar', 
                       'start':MINYEAR, 
                       'end':MAXYEAR })

spine.hasActivated.append(new_role)

# no-main-role should work fine, since no other roel has been activated.

#print(ActionRole('Force-read-spine-record-item', **{'pat':1, 'id':2}))

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

