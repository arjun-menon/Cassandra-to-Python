from cassandra import *
from datetime import datetime

class Register_RA_manager(Role):
    def __init__(self, mgr2):
        super().__init__('Register-RA-manager', ['mgr2']) 
        self.mgr2 = mgr2
    
    def canActivate(self, mgr): # R1.1.1
        return {
        	1 for subj, role in hasActivated if 
        	role.name == "RA-manager" and 
        	subj == mgr and 
        	RA_manager_regs(self.mgr2) == 0
        }
    
    def canDeactivae(self, mgr, x): # R1.1.2
        return {
        	1 for subj, role in hasActivated if 
        	role.name == "RA-manager" and 
        	subj == mgr
        }
    
    #untranslated:
    #'R1.1.6'
    #isDeactivated(mgr, RA-manager()) <-
    #	isDeactivated(x, Register-RA-manager(mgr))

def RA_manager_regs(mgr): # R1.1.3
    return len({
    	1 for subj, role in hasActivated if 
    	role.name == "Register-RA-manager" and 
    	role.mgr == mgr
    })

class RA_manager(Role):
    def __init__(self):
        super().__init__('RA-manager', []) 
    
    def canActivate(self, mgr): # R1.1.4
        return {
        	1 for subj, role in hasActivated if 
        	role.name == "Register-RA-manager" and 
        	role.mgr == mgr
        }
    
    def canDeactivae(self, mgr, mgr_): # R1.1.5
        #todo: a rule with no hasActivates
        pass

#untranslated:
#'R1.2.1'
#canReqCred(x, "NHS".hasActivated(x, NHS-registration-authority(ra, start, end))) <-
#	ra = "RA-ADB"

class NHS_service(Role):
    def __init__(self):
        super().__init__('NHS-service', []) 
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params)
    
    def canActivate_1(self, srv): # R1.2.2
        #todo: a rule with no hasActivates
        #canActivate(srv, Registration-authority())
        pass
    
    def canActivate_2(self, srv): # R1.2.3
        #todo: a rule with no hasActivates
        #srv = "Spine"
        pass

class Registration_authority(Role):
    def __init__(self):
        super().__init__('Registration-authority', []) 
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params)
    
    def canActivate_1(self, ra): # R1.2.4
        return {
        	1 for subj, role in hasActivated if 
        	role.name == "NHS-registration-authority" and 
        	role.ra == ra and 
        	Current_time() in vrange(role.start, role.end)
        }
    
    def canActivate_2(self, ra): # R1.2.5
        return {
        	1 for subj, role in hasActivated if 
        	role.name == "NHS-registration-authority" and 
        	role.ra == ra and 
        	Current_time() in vrange(role.start, role.end)
        }
