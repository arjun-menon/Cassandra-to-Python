from auxiliary import *
import ehr.hospital, ehr.ra, ehr.spine

hasActivated = list()  # Set of (subject, role) pairs representing currently active roles.

list_of_roles = ['PDS-manager', 'Register-PDS-manager', 'Patient', 'Agent', 'Professional-user', 'Registration-authority', 'Register-patient']

class PDS_manager(Role):
    def __init__(self):
        super().__init__('PDS-manager')
    
    def canActivate(self, adm): # P1.1.1
        #
        # canActivate(adm, PDS-manager()) <-
        # hasActivated(x, Register-PDS-manager(adm)), 
        # no-main-role-active(adm)
        #
        return {
            True for subj, role in hasActivated if 
            no_main_role_active(role.adm) and 
            role.adm == adm and 
            role.name == "Register-PDS-manager"
        }
    
    def canDeactivate(self, adm, adm_): # P1.1.2
        #
        # canDeactivate(adm, adm, PDS-manager()) <-
        # 
        #
        return (
            adm == adm_
        )

def count_PDS_manager_activations(user): # P1.1.4
    #
    # count-PDS-manager-activations(count<u>, user) <-
    # hasActivated(u, PDS-manager()), 
    # u = user
    #
    return len([
        True for subj, role in hasActivated if 
        role.name == "PDS-manager" and 
        subj == user
    ])

class Register_PDS_manager(Role):
    def __init__(self, adm2):
        super().__init__('Register-PDS-manager', adm2 = adm2)
    
    def canActivate(self, adm1): # P1.1.5
        #
        # canActivate(adm1, Register-PDS-manager(adm2)) <-
        # hasActivated(adm1, PDS-manager()), 
        # pds-admin-regs(n, adm2), 
        # n = 0
        #
        return {
            True for subj, role in hasActivated if 
            pds_admin_regs(self.adm2) == 0 and 
            role.name == "PDS-manager" and 
            subj == adm1
        }
    
    def canDeactivate(self, adm1, x): # P1.1.6
        #
        # canDeactivate(adm1, x, Register-PDS-manager(adm2)) <-
        # hasActivated(adm1, PDS-manager())
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "PDS-manager" and 
            subj == adm1
        }
    
    def onDeactivate(self, subject):
        # P1.1.3 -- deactive PDS-manager():
        hasActivated -= { (subj, role) for (subj, role) in hasActivated if subj == self.adm2 and role.name == 'PDS_manager' }

def pds_admin_regs(adm): # P1.1.7
    #
    # pds-admin-regs(count<x>, adm) <-
    # hasActivated(x, Register-PDS-manager(adm))
    #
    return len([
        True for subj, role in hasActivated if 
        role.adm == adm and 
        role.name == "Register-PDS-manager"
    ])

class Patient(Role):
    def __init__(self):
        super().__init__('Patient')
    
    def canActivate(self, pat): # P1.2.1
        #
        # canActivate(pat, Patient()) <-
        # hasActivated(x, Register-patient(pat)), 
        # no-main-role-active(pat)
        #
        return {
            True for subj, role in hasActivated if 
            no_main_role_active(role.pat) and 
            role.name == "Register-patient" and 
            role.pat == pat
        }
    
    def canDeactivate(self, pat, pat_): # P1.2.2
        #
        # canDeactivate(pat, pat, Patient()) <-
        # 
        #
        return (
            pat == pat_
        )

def count_patient_activations(user): # P1.2.4
    #
    # count-patient-activations(count<u>, user) <-
    # hasActivated(u, Patient()), 
    # u = user
    #
    return len([
        True for subj, role in hasActivated if 
        role.name == "Patient" and 
        subj == user
    ])

class Agent(Role):
    def __init__(self, pat):
        super().__init__('Agent', pat = pat)
    
    def canActivate(self, ag): # P1.3.1
        #
        # canActivate(ag, Agent(pat)) <-
        # hasActivated(x, Register-patient(ag)), 
        # no-main-role-active(ag), 
        # "Spine"@"Spine".canActivate(ag, Agent(pat))
        #
        return {
            True for subj, role in hasActivated if 
            canActivate(role.ag, ehr.spine.Agent(self.pat)) and 
            no_main_role_active(role.ag) and 
            role.ag == ag and 
            role.name == "Register-patient"
        }
    
    def canDeactivate(self, ag, ag_): # P1.3.2
        #
        # canDeactivate(ag, ag, Agent(pat)) <-
        # 
        #
        return (
            ag == ag_
        )

def count_agent_activations(user): # P1.3.5
    #
    # count-agent-activations(count<u>, user) <-
    # hasActivated(u, Agent(pat)), 
    # u = user
    #
    return len([
        True for subj, role in hasActivated if 
        role.name == "Agent" and 
        subj == user
    ])

class Professional_user(Role):
    def __init__(self, ra, org):
        super().__init__('Professional-user', ra = ra, org = org)
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params) or self.canActivate_3(*params) or self.canActivate_4(*params)
    
    def canActivate_1(self, x): # P1.4.1
        #
        # canActivate(x, Professional-user(ra, org)) <-
        # no-main-role-active(cli), 
        # ra.hasActivated(x, NHS-clinician-cert(org, cli, spcty, start, end)), 
        # canActivate(ra, Registration-authority()), 
        # Current-time() in [start, end]
        #
        return {
            True for subj, role in hasActivated if 
            Current_time() in vrange(role.start, role.end) and 
            canActivate(self.ra, Registration_authority()) and 
            no_main_role_active(role.cli) and 
            role.name == "NHS-clinician-cert" and 
            role.org == self.org and 
            subj == x
        }
    
    def canActivate_2(self, x): # P1.4.2
        #
        # canActivate(x, Professional-user(ra, org)) <-
        # no-main-role-active(cli), 
        # ra@ra.hasActivated(x, NHS-clinician-cert(org, cli, spcty, start, end)), 
        # canActivate(ra, Registration-authority()), 
        # Current-time() in [start, end]
        #
        return {
            True for subj, role in ehr.ra.hasActivated if 
            Current_time() in vrange(role.start, role.end) and 
            canActivate(self.ra, Registration_authority()) and 
            no_main_role_active(role.cli) and 
            role.name == "NHS-clinician-cert" and 
            role.org == self.org and 
            subj == x
        }
    
    def canActivate_3(self, x): # P1.4.3
        #
        # canActivate(x, Professional-user(ra, org)) <-
        # no-main-role-active(cg), 
        # ra.hasActivated(x, NHS-Caldicott-guardian-cert(org, cg, start, end)), 
        # canActivate(ra, Registration-authority()), 
        # Current-time() in [start, end]
        #
        return {
            True for subj, role in hasActivated if 
            Current_time() in vrange(role.start, role.end) and 
            canActivate(self.ra, Registration_authority()) and 
            no_main_role_active(role.cg) and 
            role.name == "NHS-Caldicott-guardian-cert" and 
            role.org == self.org and 
            subj == x
        }
    
    def canActivate_4(self, x): # P1.4.4
        #
        # canActivate(x, Professional-user(ra, org)) <-
        # no-main-role-active(cg), 
        # ra@ra.hasActivated(x, NHS-Caldicott-guardian-cert(org, cg, start, end)), 
        # canActivate(ra, Registration-authority()), 
        # Current-time() in [start, end]
        #
        return {
            True for subj, role in ehr.ra.hasActivated if 
            Current_time() in vrange(role.start, role.end) and 
            canActivate(self.ra, Registration_authority()) and 
            no_main_role_active(role.cg) and 
            role.name == "NHS-Caldicott-guardian-cert" and 
            role.org == self.org and 
            subj == x
        }
    
    def canDeactivate(self, x, x_): # P1.4.5
        #
        # canDeactivate(x, x, Professional-user(ra, org)) <-
        # 
        #
        return (
            x == x_
        )

def count_professional_user_activations(user): # P1.4.6
    #
    # count-professional-user-activations(count<u>, user) <-
    # hasActivated(u, Professional-user(ra, org)), 
    # u = user
    #
    return len([
        True for subj, role in hasActivated if 
        role.name == "Professional-user" and 
        subj == user
    ])

def no_main_role_active(user): # P1.5.1
    return  count_agent_activations(user) == 0 and \
            count_patient_activations(user) == 0 and \
            count_PDS_manager_activations(user) == 0 and \
            count_professional_user_activations(user) == 0

class Registration_authority(Role):
    def __init__(self):
        super().__init__('Registration-authority')
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params)
    
    def canActivate_1(self, ra): # P1.5.2
        #
        # canActivate(ra, Registration-authority()) <-
        # "NHS".hasActivated(x, NHS-registration-authority(ra, start, end)), 
        # Current-time() in [start, end]
        #
        return {
            True for subj, role in hasActivated if 
            Current_time() in vrange(role.start, role.end) and 
            role.name == "NHS-registration-authority" and 
            role.ra == ra
        }
    
    def canActivate_2(self, ra): # P1.5.3
        #
        # canActivate(ra, Registration-authority()) <-
        # ra@"NHS".hasActivated(x, NHS-registration-authority(ra, start, end)), 
        # Current-time() in [start, end]
        #
        return {
            True for subj, role in ehr.ra.hasActivated if 
            Current_time() in vrange(role.start, role.end) and 
            role.name == "NHS-registration-authority" and 
            role.ra == ra
        }

class Register_patient(Role):
    def __init__(self, pat):
        super().__init__('Register-patient', pat = pat)
    
    def canActivate(self, adm): # P2.1.1
        #
        # canActivate(adm, Register-patient(pat)) <-
        # hasActivated(adm, PDS-manager()), 
        # patient-regs(n, pat), 
        # n = 0
        #
        return {
            True for subj, role in hasActivated if 
            patient_regs(self.pat) == 0 and 
            role.name == "PDS-manager" and 
            subj == adm
        }
    
    def canDeactivate(self, adm, x): # P2.1.2
        #
        # canDeactivate(adm, x, Register-patient(pat)) <-
        # hasActivated(adm, PDS-manager())
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "PDS-manager" and 
            subj == adm
        }
    
    def onDeactivate(self, subject):
        # P1.2.3 -- deactive Patient():
        hasActivated -= { (subj, role) for (subj, role) in hasActivated if subj == self.pat and role.name == 'Patient' }
        
        # P1.3.3 -- deactive Agent(pat):
        hasActivated -= { (subj, role) for (subj, role) in hasActivated if subj == self.pat and role.name == 'Agent' }
        
        # P1.3.4 -- deactive Agent(pat):
        hasActivated -= { (subj, role) for (subj, role) in hasActivated if role.name == 'Agent' and role.pat == self.pat }

def patient_regs(pat): # P2.1.3
    #
    # patient-regs(count<x>, pat) <-
    # hasActivated(x, Register-patient(pat))
    #
    return len([
        True for subj, role in hasActivated if 
        role.name == "Register-patient" and 
        role.pat == pat
    ])

# Credential Request Restrictions
# ===============================
# These rules place restrictions on access to certain canActivate and hasActivated predicates.

# <<< No restrictions on canActivate rules in this module. >>>

# Restrictions on hasActivated
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# <<< For the Role 'Register-patient' >>>

def canReqCred_canActivate_Register_patient_1(pat, pat): # P2.2.1
    #
    # canReqCred(pat, "PDS".hasActivated(x, Register-patient(pat))) <-
    # hasActivated(pat, Patient())
    #
    return {
        True for subj, role in hasActivated if 
        role.name == "Patient" and 
        subj == pat
    }

def canReqCred_canActivate_Register_patient_2(ag, pat): # P2.2.2
    #
    # canReqCred(ag, "PDS".hasActivated(x, Register-patient(pat))) <-
    # hasActivated(ag, Agent(pat))
    #
    return {
        True for subj, role in hasActivated if 
        role.name == "Agent" and 
        role.pat == pat and 
        subj == ag
    }

def canReqCred_canActivate_Register_patient_3(usr, pat): # P2.2.3
    #
    # canReqCred(usr, "PDS".hasActivated(x, Register-patient(pat))) <-
    # hasActivated(usr, Professional-user(ra, org))
    #
    return {
        True for subj, role in hasActivated if 
        role.name == "Professional-user" and 
        subj == usr
    }

def canReqCred_canActivate_Register_patient_4(org, pat): # P2.2.4
    #
    # canReqCred(org, "PDS".hasActivated(x, Register-patient(pat))) <-
    # ra.hasActivated(x, NHS-health-org-cert(org, start, end)), 
    # canActivate(ra, Registration-authority())
    #
    return {
        True for subj, role in hasActivated if 
        canActivate(Wildcard(), Registration_authority()) and 
        role.name == "NHS-health-org-cert" and 
        role.org == org
    }

def canReqCred_canActivate_Register_patient_5(org, pat): # P2.2.5
    #
    # canReqCred(org, "PDS".hasActivated(x, Register-patient(pat))) <-
    # org@ra.hasActivated(x, NHS-health-org-cert(org, start, end)), 
    # canActivate(ra, Registration-authority())
    #
    return {
        True for subj, role in ehr.org.hasActivated if 
        canActivate(Wildcard(), Registration_authority()) and 
        role.name == "NHS-health-org-cert" and 
        role.org == org
    }

def canReqCred_canActivate_Register_patient_6(ra, pat): # P2.2.5
    #
    # canReqCred(ra, "PDS".hasActivated(x, Register-patient(pat))) <-
    # canActivate(ra, Registration-authority())
    #
    return (
        canActivate(ra, Registration_authority())
    )

def canReqCred_canActivate_Register_patient_7(spine, pat): # P2.2.5
    #
    # canReqCred(spine, "PDS".hasActivated(x, Register-patient(pat))) <-
    # spine = "Spine"
    #
    return (
        spine == "Spine"
    )

