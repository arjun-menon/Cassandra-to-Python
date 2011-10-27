from cassandra import *
from datetime import datetime

class PDS_manager(Role):
    def __init__(self):
        super().__init__('PDS-manager', []) 
    
    def canActivate(self, adm): # P1.1.1
        return {
        	x for x, role in hasActivated if 
        	role.name == "Register-PDS-manager" and 
        	role.adm == adm
        }
    
    #'P1.1.2'
    #canDeactivate(adm, adm, PDS-manager()) <-
    #	

def count_PDS_manager_activations(user):
    return {
    	u for u, role in hasActivated if 
    	role.name == "PDS-manager"
    }

class Register_PDS_manager(Role):
    def __init__(self, adm2):
        super().__init__('Register-PDS-manager', ['adm2']) 
        self.adm2 = adm2
    
    def canActivate(self, adm1): # P1.1.5
        return {
        	adm1 for adm1, role in hasActivated if 
        	role.name == "PDS-manager"
        }
    
    #'P1.1.6'
    #canDeactivate(adm1, x, Register-PDS-manager(adm2)) <-
    #	hasActivated(adm1, PDS-manager())
    
    #'P1.1.3'
    #isDeactivated(adm, PDS-manager()) <-
    #	isDeactivated(x, Register-PDS-manager(adm))

def pds_admin_regs(adm):
    return {
    	x for x, role in hasActivated if 
    	role.name == "Register-PDS-manager" and 
    	role.adm == adm
    }

class Patient(Role):
    def __init__(self):
        super().__init__('Patient', []) 
    
    def canActivate(self, pat): # P1.2.1
        return {
        	x for x, role in hasActivated if 
        	role.name == "Register-patient" and 
        	role.pat == pat
        }
    
    #'P1.2.2'
    #canDeactivate(pat, pat, Patient()) <-
    #	

def count_patient_activations(user):
    return {
    	u for u, role in hasActivated if 
    	role.name == "Patient"
    }

class Agent(Role):
    def __init__(self, pat):
        super().__init__('Agent', ['pat']) 
        self.pat = pat
    
    def canActivate(self, ag): # P1.3.1
        return {
        	x for x, role in hasActivated if 
        	role.name == "Register-patient" and 
        	role.ag == ag and 
        	canActivate(role.ag, Agent(self.pat))
        }
    
    #'P1.3.2'
    #canDeactivate(ag, ag, Agent(pat)) <-
    #	

def count_agent_activations(user):
    return {
    	u for u, role in hasActivated if 
    	role.name == "Agent"
    }

class Professional_user(Role):
    def __init__(self, ra, org):
        super().__init__('Professional-user', ['ra', 'org']) 
        self.ra, self.org = ra, org
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params) or self.canActivate_3(*params) or self.canActivate_4(*params)
    
    def canActivate_1(self, x): # P1.4.1
        return {
        	x for x, role in hasActivated if 
        	role.name == "NHS-clinician-cert" and 
        	role.org == self.org and 
        	canActivate(self.ra, Registration_authority())
        }
    
    def canActivate_2(self, x): # P1.4.2
        return {
        	x for x, role in hasActivated if 
        	role.name == "NHS-clinician-cert" and 
        	role.org == self.org and 
        	canActivate(self.ra, Registration_authority())
        }
    
    def canActivate_3(self, x): # P1.4.3
        return {
        	x for x, role in hasActivated if 
        	role.name == "NHS-Caldicott-guardian-cert" and 
        	role.org == self.org and 
        	canActivate(self.ra, Registration_authority())
        }
    
    def canActivate_4(self, x): # P1.4.4
        return {
        	x for x, role in hasActivated if 
        	role.name == "NHS-Caldicott-guardian-cert" and 
        	role.org == self.org and 
        	canActivate(self.ra, Registration_authority())
        }
    
    #'P1.4.5'
    #canDeactivate(x, x, Professional-user(ra, org)) <-
    #	

def count_professional_user_activations(user):
    return {
    	u for u, role in hasActivated if 
    	role.name == "Professional-user"
    }

#'P1.5.1'
#no-main-role-active(user) <-
#	count-agent-activations(n, user), count-patient-activations(n, user), count-PDS-manager-activations(n, user), count-professional-user-activations(n, user), n = 0

class Registration_authority(Role):
    def __init__(self):
        super().__init__('Registration-authority', []) 
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params)
    
    def canActivate_1(self, ra): # P1.5.2
        return {
        	x for x, role in hasActivated if 
        	role.name == "NHS-registration-authority" and 
        	role.ra == ra
        }
    
    def canActivate_2(self, ra): # P1.5.3
        return {
        	x for x, role in hasActivated if 
        	role.name == "NHS-registration-authority" and 
        	role.ra == ra
        }

class Register_patient(Role):
    def __init__(self, pat):
        super().__init__('Register-patient', ['pat']) 
        self.pat = pat
    
    def canActivate(self, adm): # P2.1.1
        return {
        	adm for adm, role in hasActivated if 
        	role.name == "PDS-manager"
        }
    
    #'P2.1.2'
    #canDeactivate(adm, x, Register-patient(pat)) <-
    #	hasActivated(adm, PDS-manager())
    
    #'P1.2.3'
    #isDeactivated(pat, Patient()) <-
    #	isDeactivated(x, Register-patient(pat))
    
    #'P1.3.3'
    #isDeactivated(ag, Agent(pat)) <-
    #	isDeactivated(x, Register-patient(ag))
    
    #'P1.3.4'
    #isDeactivated(ag, Agent(pat)) <-
    #	isDeactivated(x, Register-patient(pat))

def patient_regs(pat):
    return {
    	x for x, role in hasActivated if 
    	role.name == "Register-patient" and 
    	role.pat == pat
    }

#'P2.2.1'
#canReqCred(pat, "PDS".hasActivated(x, Register-patient(pat))) <-
#	hasActivated(pat, Patient())

#'P2.2.2'
#canReqCred(ag, "PDS".hasActivated(x, Register-patient(pat))) <-
#	hasActivated(ag, Agent(pat))

#'P2.2.3'
#canReqCred(usr, "PDS".hasActivated(x, Register-patient(pat))) <-
#	hasActivated(usr, Professional-user(ra, org))

#'P2.2.4'
#canReqCred(org, "PDS".hasActivated(x, Register-patient(pat))) <-
#	ra.hasActivated(x, NHS-health-org-cert(org, start, end)), canActivate(ra, Registration-authority())

#'P2.2.5'
#canReqCred(org, "PDS".hasActivated(x, Register-patient(pat))) <-
#	org@ra.hasActivated(x, NHS-health-org-cert(org, start, end)), canActivate(ra, Registration-authority())

#'P2.2.5'
#canReqCred(ra, "PDS".hasActivated(x, Register-patient(pat))) <-
#	canActivate(ra, Registration-authority())

#'P2.2.5'
#canReqCred(spine, "PDS".hasActivated(x, Register-patient(pat))) <-
#	spine = "Spine"
