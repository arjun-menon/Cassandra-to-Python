
from core import *
from datetime import datetime

########
# Spine
########

class Spine_clinician(Role):
    name = "Spine-clinician"
    
    def __init__(self, ra, org, spcty):
        super(Spine_clinician, self).__init__(self.name, (ra, org, spcty))
        self.ra, self.org, self.spcty = ra, org, spcty
    
    def canActivate(self, cli):
        current_time = datetime.utcnow()
        return no_main_role_active(cli) and \
            Registration_authority.canActivate(self.ra) and \
            len([x for (x, y) in hasActivated if y.name==NHS_clinician_cert.name and y.start < current_time and y.end > current_time]) > 0 #todo issuer ra, check both locations here and ra

class NHS_clinician_cert(Role):
    name = "NHS-clinician-cert"
    
    def __init__(self, org, cli, spcty, start, end):
        super(NHS_clinician_cert, self).__init__(NHS_clinician_cert.name, (org, cli, spcty, start, end))
        self.org, self.cli, self.spcty, self.start, self.end = org, cli, spcty, start, end

class Registration_authority(Role):
    def canActivate(self):
        pass

def no_main_role_active(user):
    pass