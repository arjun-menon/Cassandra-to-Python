from cassandra import *
from datetime import datetime

class PDS_manager(Role):
    def __init__(self):
        super().__init__('PDS-manager', []) 
    
    def canActivate(self, adm): # P1.1.1
        return {
        	1 for subj, role in hasActivated if 
        	role.name == "Register-PDS-manager" and 
        	role.adm == adm and 
        	no_main_role_active(role.adm)
        }
    
    def canDeactivate(self, adm, adm_): # P1.1.2
        #todo: a rule with no hasActivates
        pass

def count_PDS_manager_activations(user): # P1.1.4
    return len({
    	1 for subj, role in hasActivated if 
    	role.name == "PDS-manager" and 
    	subj == user
    })

class Register_PDS_manager(Role):
    def __init__(self, adm2):
        super().__init__('Register-PDS-manager', ['adm2']) 
        self.adm2 = adm2
    
    def canActivate(self, adm1): # P1.1.5
        return {
        	1 for subj, role in hasActivated if 
        	role.name == "PDS-manager" and 
        	subj == adm1 and 
        	pds_admin_regs(self.adm2) == 0
        }
    
    def canDeactivate(self, adm1, x): # P1.1.6
        return {
        	1 for subj, role in hasActivated if 
        	role.name == "PDS-manager" and 
        	subj == adm1
        }
    
    #untranslated:
    #'P1.1.3'
    #isDeactivated(adm, PDS-manager()) <-
    #	isDeactivated(x, Register-PDS-manager(adm))

def pds_admin_regs(adm): # P1.1.7
    return len({
    	1 for subj, role in hasActivated if 
    	role.name == "Register-PDS-manager" and 
    	role.adm == adm
    })

class Patient(Role):
    def __init__(self):
        super().__init__('Patient', []) 
    
    def canActivate(self, pat): # P1.2.1
        return {
        	1 for subj, role in hasActivated if 
        	role.name == "Register-patient" and 
        	role.pat == pat and 
        	no_main_role_active(role.pat)
        }
    
    def canDeactivate(self, pat, pat_): # P1.2.2
        #todo: a rule with no hasActivates
        pass

def count_patient_activations(user): # P1.2.4
    return len({
    	1 for subj, role in hasActivated if 
    	role.name == "Patient" and 
    	subj == user
    })

class Agent(Role):
    def __init__(self, pat):
        super().__init__('Agent', ['pat']) 
        self.pat = pat
    
    def canActivate(self, ag): # P1.3.1
        return {
        	1 for subj, role in hasActivated if 
        	role.name == "Register-patient" and 
        	role.ag == ag and 
        	canActivate(role.ag, Agent(self.pat)) and 
        	no_main_role_active(role.ag)
        }
    
    def canDeactivate(self, ag, ag_): # P1.3.2
        #todo: a rule with no hasActivates
        pass

def count_agent_activations(user): # P1.3.5
    return len({
    	1 for subj, role in hasActivated if 
    	role.name == "Agent" and 
    	subj == user
    })

class Professional_user(Role):
    def __init__(self, ra, org):
        super().__init__('Professional-user', ['ra', 'org']) 
        self.ra, self.org = ra, org
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params) or self.canActivate_3(*params) or self.canActivate_4(*params)
    
    def canActivate_1(self, x): # P1.4.1
        return {
        	1 for subj, role in hasActivated if 
        	role.name == "NHS-clinician-cert" and 
        	role.org == self.org and 
        	subj == x and 
        	canActivate(self.ra, Registration_authority()) and 
        	Current_time() in vrange(role.start, role.end) and 
        	no_main_role_active(role.cli)
        }
    
    def canActivate_2(self, x): # P1.4.2
        return {
        	1 for subj, role in hasActivated if 
        	role.name == "NHS-clinician-cert" and 
        	role.org == self.org and 
        	subj == x and 
        	canActivate(self.ra, Registration_authority()) and 
        	Current_time() in vrange(role.start, role.end) and 
        	no_main_role_active(role.cli)
        }
    
    def canActivate_3(self, x): # P1.4.3
        return {
        	1 for subj, role in hasActivated if 
        	role.name == "NHS-Caldicott-guardian-cert" and 
        	role.org == self.org and 
        	subj == x and 
        	canActivate(self.ra, Registration_authority()) and 
        	Current_time() in vrange(role.start, role.end) and 
        	no_main_role_active(role.cg)
        }
    
    def canActivate_4(self, x): # P1.4.4
        return {
        	1 for subj, role in hasActivated if 
        	role.name == "NHS-Caldicott-guardian-cert" and 
        	role.org == self.org and 
        	subj == x and 
        	canActivate(self.ra, Registration_authority()) and 
        	Current_time() in vrange(role.start, role.end) and 
        	no_main_role_active(role.cg)
        }
    
    def canDeactivate(self, x, x_): # P1.4.5
        #todo: a rule with no hasActivates
        pass

def count_professional_user_activations(user): # P1.4.6
    return len({
    	1 for subj, role in hasActivated if 
    	role.name == "Professional-user" and 
    	subj == user
    })

#untranslated:
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
        	1 for subj, role in hasActivated if 
        	role.name == "NHS-registration-authority" and 
        	role.ra == ra and 
        	Current_time() in vrange(role.start, role.end)
        }
    
    def canActivate_2(self, ra): # P1.5.3
        return {
        	1 for subj, role in hasActivated if 
        	role.name == "NHS-registration-authority" and 
        	role.ra == ra and 
        	Current_time() in vrange(role.start, role.end)
        }

class Register_patient(Role):
    def __init__(self, pat):
        super().__init__('Register-patient', ['pat']) 
        self.pat = pat
    
    def canActivate(self, adm): # P2.1.1
        return {
        	1 for subj, role in hasActivated if 
        	role.name == "PDS-manager" and 
        	subj == adm and 
        	patient_regs(self.pat) == 0
        }
    
    def canDeactivate(self, adm, x): # P2.1.2
        return {
        	1 for subj, role in hasActivated if 
        	role.name == "PDS-manager" and 
        	subj == adm
        }
    
    #untranslated:
    #'P1.2.3'
    #isDeactivated(pat, Patient()) <-
    #	isDeactivated(x, Register-patient(pat))
    
    #untranslated:
    #'P1.3.3'
    #isDeactivated(ag, Agent(pat)) <-
    #	isDeactivated(x, Register-patient(ag))
    
    #untranslated:
    #'P1.3.4'
    #isDeactivated(ag, Agent(pat)) <-
    #	isDeactivated(x, Register-patient(pat))

def patient_regs(pat): # P2.1.3
    return len({
    	1 for subj, role in hasActivated if 
    	role.name == "Register-patient" and 
    	role.pat == pat
    })

#untranslated:
#'P2.2.1'
#canReqCred(pat, "PDS".hasActivated(x, Register-patient(pat))) <-
#	hasActivated(pat, Patient())

#untranslated:
#'P2.2.2'
#canReqCred(ag, "PDS".hasActivated(x, Register-patient(pat))) <-
#	hasActivated(ag, Agent(pat))

#untranslated:
#'P2.2.3'
#canReqCred(usr, "PDS".hasActivated(x, Register-patient(pat))) <-
#	hasActivated(usr, Professional-user(ra, org))

#untranslated:
#'P2.2.4'
#canReqCred(org, "PDS".hasActivated(x, Register-patient(pat))) <-
#	ra.hasActivated(x, NHS-health-org-cert(org, start, end)), canActivate(ra, Registration-authority())

#untranslated:
#'P2.2.5'
#canReqCred(org, "PDS".hasActivated(x, Register-patient(pat))) <-
#	org@ra.hasActivated(x, NHS-health-org-cert(org, start, end)), canActivate(ra, Registration-authority())

#untranslated:
#'P2.2.5'
#canReqCred(ra, "PDS".hasActivated(x, Register-patient(pat))) <-
#	canActivate(ra, Registration-authority())

#untranslated:
#'P2.2.5'
#canReqCred(spine, "PDS".hasActivated(x, Register-patient(pat))) <-
#	spine = "Spine"
