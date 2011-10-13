from cassandra import *
from datetime import datetime

class PDS_manager(Role):
    def __init__(self):
        super().__init__('PDS-manager', []) 
    
    def canActivate(self, adm): # P1.1.1
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Register-PDS-manager" } and\
        no_main_role_active(adm)
    
    #'P1.1.2'
    #canDeactivate(adm, adm, PDS-manager()) <-
    #	

#'P1.1.4'
#count-PDS-manager-activations(count<u>, user) <-
#	hasActivated(u, PDS-manager()), u = user

class Register_PDS_manager(Role):
    def __init__(self, adm2):
        super().__init__('Register-PDS-manager', ['adm2']) 
        self.adm2 = adm2
    
    def canActivate(self, adm1): # P1.1.5
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "PDS-manager" } and\
        pds_admin_regs(n, adm2)
    
    #'P1.1.6'
    #canDeactivate(adm1, x, Register-PDS-manager(adm2)) <-
    #	hasActivated(adm1, PDS-manager())
    
    #'P1.1.3'
    #isDeactivated(adm, PDS-manager()) <-
    #	isDeactivated(x, Register-PDS-manager(adm))

#'P1.1.7'
#pds-admin-regs(count<x>, adm) <-
#	hasActivated(x, Register-PDS-manager(adm))

class Patient(Role):
    def __init__(self):
        super().__init__('Patient', []) 
    
    def canActivate(self, pat): # P1.2.1
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Register-patient" } and\
        no_main_role_active(pat)
    
    #'P1.2.2'
    #canDeactivate(pat, pat, Patient()) <-
    #	

#'P1.2.4'
#count-patient-activations(count<u>, user) <-
#	hasActivated(u, Patient()), u = user

class Agent(Role):
    def __init__(self, pat):
        super().__init__('Agent', ['pat']) 
        self.pat = pat
    
    def canActivate(self, ag): # P1.3.1
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Register-patient" } and\
        no_main_role_active(ag) and\
        canActivate(ag, Agent(pat))
    
    #'P1.3.2'
    #canDeactivate(ag, ag, Agent(pat)) <-
    #	

#'P1.3.5'
#count-agent-activations(count<u>, user) <-
#	hasActivated(u, Agent(pat)), u = user

class Professional_user(Role):
    def __init__(self, ra, org):
        super().__init__('Professional-user', ['ra', 'org']) 
        self.ra, self.org = ra, org
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params) or self.canActivate_3(*params) or self.canActivate_4(*params)
    
    def canActivate_1(self, x): # P1.4.1
        return\
        no_main_role_active(cli) and\
        { (subject, role) for subject, role in hasActivated if role.name == "NHS-clinician-cert" and role.org == self.org and Current_time() in vrange(role.start, role.end) } and\
        canActivate(ra, Registration_authority())
    
    def canActivate_2(self, x): # P1.4.2
        return\
        no_main_role_active(cli) and\
        { (subject, role) for subject, role in hasActivated if role.name == "NHS-clinician-cert" and role.org == self.org and Current_time() in vrange(role.start, role.end) } and\
        canActivate(ra, Registration_authority())
    
    def canActivate_3(self, x): # P1.4.3
        return\
        no_main_role_active(cg) and\
        { (subject, role) for subject, role in hasActivated if role.name == "NHS-Caldicott-guardian-cert" and role.org == self.org and Current_time() in vrange(role.start, role.end) } and\
        canActivate(ra, Registration_authority())
    
    def canActivate_4(self, x): # P1.4.4
        return\
        no_main_role_active(cg) and\
        { (subject, role) for subject, role in hasActivated if role.name == "NHS-Caldicott-guardian-cert" and role.org == self.org and Current_time() in vrange(role.start, role.end) } and\
        canActivate(ra, Registration_authority())
    
    #'P1.4.5'
    #canDeactivate(x, x, Professional-user(ra, org)) <-
    #	

#'P1.4.6'
#count-professional-user-activations(count<u>, user) <-
#	hasActivated(u, Professional-user(ra, org)), u = user

#'P1.5.1'
#no-main-role-active(user) <-
#	count-agent-activations(n, user), count-patient-activations(n, user), count-PDS-manager-activations(n, user), count-professional-user-activations(n, user), n = 0

class Registration_authority(Role):
    def __init__(self):
        super().__init__('Registration-authority', []) 
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params)
    
    def canActivate_1(self, ra): # P1.5.2
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "NHS-registration-authority" and Current_time() in vrange(role.start, role.end) }
    
    def canActivate_2(self, ra): # P1.5.3
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "NHS-registration-authority" and Current_time() in vrange(role.start, role.end) }

class Register_patient(Role):
    def __init__(self, pat):
        super().__init__('Register-patient', ['pat']) 
        self.pat = pat
    
    def canActivate(self, adm): # P2.1.1
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "PDS-manager" } and\
        patient_regs(n, pat)
    
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

#'P2.1.3'
#patient-regs(count<x>, pat) <-
#	hasActivated(x, Register-patient(pat))

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
