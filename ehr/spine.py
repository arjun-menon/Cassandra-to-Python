from auxiliary import *
import ehr.hospital, ehr.pds, ehr.ra

hasActivated = list()  # Set of (subject, role) pairs representing currently active roles.

list_of_roles = ['Spine-clinician', 'Spine-admin', 'Register-spine-admin', 'Patient', 'Register-patient', 'Agent', 'Register-agent', 'Registration-authority', 'One-off-consent', 'Request-third-party-consent', 'Third-party', 'Third-party-consent', 'Request-consent-to-treatment', 'Consent-to-treatment', 'Request-consent-to-group-treatment', 'Consent-to-group-treatment', 'Referrer', 'Spine-emergency-clinician', 'Treating-clinician', 'General-practitioner', 'Group-treating-clinician', 'Concealed-by-spine-clinician', 'Conceal-request', 'Concealed-by-spine-patient', 'Authenticated-express-consent']

class Spine_clinician(Role):
    def __init__(self, ra, org, spcty):
        super().__init__('Spine-clinician', ra = ra, org = org, spcty = spcty)
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params)
    
    def canActivate_1(self, cli): # S1.1.1
        #
        # canActivate(cli, Spine-clinician(ra, org, spcty)) <-
        # ra.hasActivated(x, NHS-clinician-cert(org, cli, spcty, start, end)), 
        # canActivate(ra, Registration-authority()), 
        # no-main-role-active(cli), 
        # Current-time() in [start, end]
        #
        return {
            True for subj, role in hasActivated if 
            Current_time() in vrange(role.start, role.end) and 
            canActivate(self.ra, Registration_authority()) and 
            no_main_role_active(role.cli) and 
            role.cli == cli and 
            role.name == "NHS-clinician-cert" and 
            role.org == self.org and 
            role.spcty == self.spcty
        }
    
    def canActivate_2(self, cli): # S1.1.2
        #
        # canActivate(cli, Spine-clinician(ra, org, spcty)) <-
        # ra@ra.hasActivated(x, NHS-clinician-cert(org, cli, spcty, start, end)), 
        # canActivate(ra, Registration-authority()), 
        # no-main-role-active(cli), 
        # Current-time() in [start, end]
        #
        return {
            True for subj, role in ehr.ra.hasActivated if 
            Current_time() in vrange(role.start, role.end) and 
            canActivate(self.ra, Registration_authority()) and 
            no_main_role_active(role.cli) and 
            role.cli == cli and 
            role.name == "NHS-clinician-cert" and 
            role.org == self.org and 
            role.spcty == self.spcty
        }
    
    def canDeactivate(self, cli, cli_): # S1.1.3
        #
        # canDeactivate(cli, cli, Spine-clinician(ra, org, spcty)) <-
        # 
        #
        return (
            cli == cli_
        )
    
    def onDeactivate(self, subject):
        # S3.2.3 -- deactive Spine-emergency-clinician(org, pat):
        hasActivated -= { (subj, role) for (subj, role) in hasActivated if subj == subject and role.name == 'Spine_emergency_clinician' and role.org == self.org }

def count_spine_clinician_activations(user): # S1.1.4
    #
    # count-spine-clinician-activations(count<u>, user) <-
    # hasActivated(u, Spine-clinician(ra, org, spcty)), 
    # u = user
    #
    return len([
        True for subj, role in hasActivated if 
        role.name == "Spine-clinician" and 
        subj == user
    ])

class Spine_admin(Role):
    def __init__(self):
        super().__init__('Spine-admin')
    
    def canActivate(self, adm): # S1.2.1
        #
        # canActivate(adm, Spine-admin()) <-
        # hasActivated(x, Register-spine-admin(adm)), 
        # no-main-role-active(adm)
        #
        return {
            True for subj, role in hasActivated if 
            no_main_role_active(role.adm) and 
            role.adm == adm and 
            role.name == "Register-spine-admin"
        }
    
    def canDeactivate(self, adm, adm_): # S1.2.2
        #
        # canDeactivate(adm, adm, Spine-admin()) <-
        # 
        #
        return (
            adm == adm_
        )

def count_spine_admin_activations(user): # S1.2.4
    #
    # count-spine-admin-activations(count<u>, user) <-
    # hasActivated(u, Spine-admin()), 
    # u = user
    #
    return len([
        True for subj, role in hasActivated if 
        role.name == "Spine-admin" and 
        subj == user
    ])

class Register_spine_admin(Role):
    def __init__(self, adm2):
        super().__init__('Register-spine-admin', adm2 = adm2)
    
    def canActivate(self, adm): # S1.2.5
        #
        # canActivate(adm, Register-spine-admin(adm2)) <-
        # hasActivated(adm, Spine-admin()), 
        # spine-admin-regs(n, adm2), 
        # n = 0
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Spine-admin" and 
            spine_admin_regs(self.adm2) == 0 and 
            subj == adm
        }
    
    def canDeactivate(self, adm, x): # S1.2.6
        #
        # canDeactivate(adm, x, Register-spine-admin(adm2)) <-
        # hasActivated(adm, Spine-admin())
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Spine-admin" and 
            subj == adm
        }
    
    def onDeactivate(self, subject):
        # S1.2.3 -- deactive Spine-admin():
        hasActivated -= { (subj, role) for (subj, role) in hasActivated if subj == self.adm2 and role.name == 'Spine_admin' }

def spine_admin_regs(adm): # S1.2.7
    #
    # spine-admin-regs(count<x>, adm) <-
    # hasActivated(x, Register-spine-admin(adm))
    #
    return len([
        True for subj, role in hasActivated if 
        role.adm == adm and 
        role.name == "Register-spine-admin"
    ])

class Patient(Role):
    def __init__(self):
        super().__init__('Patient')
    
    def canActivate(self, pat): # S1.3.1
        #
        # canActivate(pat, Patient()) <-
        # hasActivated(x, Register-patient(pat)), 
        # no-main-role-active(pat), 
        # "PDS"@"PDS".hasActivated(y, Register-patient(pat))
        #
        return {
            True for (subj1, role1) in hasActivated for (subj2, role2) in ehr.pds.hasActivated if 
            no_main_role_active(role2.pat) and 
            role1.name == "Register-patient" and 
            role1.pat == pat and 
            role2.name == "Register-patient" and 
            role2.pat == pat
        }
    
    def canDeactivate(self, pat, pat_): # S1.3.2
        #
        # canDeactivate(pat, pat, Patient()) <-
        # 
        #
        return (
            pat == pat_
        )

def count_patient_activations(user): # S1.3.4
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

class Register_patient(Role):
    def __init__(self, pat):
        super().__init__('Register-patient', pat = pat)
    
    def canActivate(self, adm): # S1.3.5
        #
        # canActivate(adm, Register-patient(pat)) <-
        # hasActivated(adm, Spine-admin()), 
        # patient-regs(n, pat), 
        # n = 0
        #
        return {
            True for subj, role in hasActivated if 
            patient_regs(self.pat) == 0 and 
            role.name == "Spine-admin" and 
            subj == adm
        }
    
    def canDeactivate(self, adm, x): # S1.3.6
        #
        # canDeactivate(adm, x, Register-patient(pat)) <-
        # hasActivated(adm, Spine-admin())
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Spine-admin" and 
            subj == adm
        }
    
    def onDeactivate(self, subject):
        # S1.3.3 -- deactive Patient():
        hasActivated -= { (subj, role) for (subj, role) in hasActivated if subj == self.pat and role.name == 'Patient' }
        
        # S1.4.13 -- deactive Register-agent(agent, pat):
        hasActivated -= { (subj, role) for (subj, role) in hasActivated if role.name == 'Register_agent' and role.pat == self.pat }
        
        # S2.1.7 -- deactive One-off-consent(pat):
        hasActivated -= { (subj, role) for (subj, role) in hasActivated if role.name == 'One_off_consent' and role.pat == self.pat }
        
        # S2.2.8 -- deactive Request-third-party-consent(y, pat, id):
        hasActivated -= { (subj, role) for (subj, role) in hasActivated if role.name == 'Request_third_party_consent' and role.pat == self.pat }
        
        # S2.3.7 -- deactive Request-consent-to-treatment(pat, org, cli, spcty):
        hasActivated -= { (subj, role) for (subj, role) in hasActivated if role.name == 'Request_consent_to_treatment' and role.pat == self.pat }
        
        # S2.4.7 -- deactive Request-consent-to-group-treatment(pat, org, group):
        hasActivated -= { (subj, role) for (subj, role) in hasActivated if role.name == 'Request_consent_to_group_treatment' and role.pat == self.pat }
        
        # S3.1.4 -- deactive Referrer(pat, org, cli2, spcty1):
        hasActivated -= { (subj, role) for (subj, role) in hasActivated if subj == self.pat and role.name == 'Referrer' and role.pat == self.pat }
        
        # S3.2.4 -- deactive Spine-emergency-clinician(org, pat):
        hasActivated -= { (subj, role) for (subj, role) in hasActivated if role.name == 'Spine_emergency_clinician' and role.pat == self.pat }
        
        # S4.1.5 -- deactive Concealed-by-spine-clinician(pat, ids, start, end):
        hasActivated -= { (subj, role) for (subj, role) in hasActivated if role.name == 'Concealed_by_spine_clinician' and role.pat == self.pat }
        
        # S4.2.6 -- deactive Conceal-request(what, whom, start, end):
        hasActivated -= { (subj, role) for (subj, role) in hasActivated if role.name == 'Conceal_request' }
        
        # S4.3.7 -- deactive Authenticated-express-consent(pat, cli):
        hasActivated -= { (subj, role) for (subj, role) in hasActivated if role.name == 'Authenticated_express_consent' and role.pat == self.pat }

def patient_regs(pat): # S1.3.7
    #
    # patient-regs(count<x>, pat) <-
    # hasActivated(x, Register-patient(pat))
    #
    return len([
        True for subj, role in hasActivated if 
        role.name == "Register-patient" and 
        role.pat == pat
    ])

class Agent(Role):
    def __init__(self, pat):
        super().__init__('Agent', pat = pat)
    
    def canActivate(self, ag): # S1.4.1
        #
        # canActivate(ag, Agent(pat)) <-
        # hasActivated(x, Register-agent(ag, pat)), 
        # "PDS"@"PDS".hasActivated(y, Register-patient(ag)), 
        # no-main-role-active(ag)
        #
        return {
            True for (subj1, role1) in hasActivated for (subj2, role2) in ehr.pds.hasActivated if 
            no_main_role_active(role2.ag) and 
            role1.ag == ag and 
            role1.name == "Register-agent" and 
            role1.pat == self.pat and 
            role2.ag == ag and 
            role2.name == "Register-patient"
        }
    
    def canDeactivate(self, ag, ag_): # S1.4.2
        #
        # canDeactivate(ag, ag, Agent(pat)) <-
        # 
        #
        return (
            ag == ag_
        )

def other_agent_regs(x, ag, pat): # S1.4.4
    #
    # other-agent-regs(count<y>, x, ag, pat) <-
    # hasActivated(y, Register-agent(ag, pat)), 
    # x != y
    #
    return len([
        True for subj, role in hasActivated if 
        role.ag == ag and 
        role.name == "Register-agent" and 
        role.pat == pat and 
        x != subj
    ])

def count_agent_activations(user): # S1.4.5
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

class Register_agent(Role):
    def __init__(self, agent, pat):
        super().__init__('Register-agent', agent = agent, pat = pat)
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params)
    
    def canActivate_1(self, pat): # S1.4.9
        #
        # canActivate(pat, Register-agent(agent, pat)) <-
        # hasActivated(pat, Patient()), 
        # agent-regs(n, pat), 
        # n < 3
        #
        return {
            True for subj, role in hasActivated if 
            agent_regs(subj) < 3 and 
            role.name == "Patient" and 
            subj == pat
        }
    
    def canActivate_2(self, cli): # S1.4.10
        #
        # canActivate(cli, Register-agent(agent, pat)) <-
        # hasActivated(cli, Spine-clinician(ra, org, spcty)), 
        # canActivate(cli, General-practitioner(pat))
        #
        return {
            True for subj, role in hasActivated if 
            canActivate(subj, General_practitioner(self.pat)) and 
            role.name == "Spine-clinician" and 
            subj == cli
        }
    
    def canDeactivate(self, *params):
        return self.canDeactivate_1(*params) or self.canDeactivate_2(*params)
    
    def canDeactivate_1(self, pat, pat_): # S1.4.11
        #
        # canDeactivate(pat, pat, Register-agent(agent, pat)) <-
        # hasActivated(pat, Patient())
        #
        return {
            True for subj, role in hasActivated if 
            pat == pat_ and 
            role.name == "Patient" and 
            subj == pat
        }
    
    def canDeactivate_2(self, cli, x): # S1.4.12
        #
        # canDeactivate(cli, x, Register-agent(agent, pat)) <-
        # hasActivated(cli, Spine-clinician(ra, org, spcty)), 
        # canActivate(cli, General-practitioner(pat))
        #
        return {
            True for subj, role in hasActivated if 
            canActivate(subj, General_practitioner(self.pat)) and 
            role.name == "Spine-clinician" and 
            subj == cli
        }
    
    def onDeactivate(self, subject):
        # S1.4.3 -- deactive Agent(pat):
        hasActivated -= { (subj, role) for (subj, role) in hasActivated if subj == self.agent and role.name == 'Agent' and role.pat == self.pat }

def agent_regs(pat): # S1.4.14
    #
    # agent-regs(count<x>, pat) <-
    # hasActivated(pat, Register-agent(x, pat))
    #
    return len([
        True for subj, role in hasActivated if 
        role.name == "Register-agent" and 
        role.pat == pat and 
        subj == role.pat
    ])

class Registration_authority(Role):
    def __init__(self):
        super().__init__('Registration-authority')
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params)
    
    def canActivate_1(self, ra): # S1.5.1
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
    
    def canActivate_2(self, ra): # S1.5.2
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

def no_main_role_active(user): # S1.5.3
    return  count_agent_activations(user) == 0 and \
            count_spine_clinician_activations(user) == 0 and \
            count_spine_admin_activations(user) == 0 and \
            count_patient_activations(user) == 0 and \
            count_third_party_activations(user) == 0

class One_off_consent(Role):
    def __init__(self, pat):
        super().__init__('One-off-consent', pat = pat)
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params) or self.canActivate_3(*params)
    
    def canActivate_1(self, pat): # S2.1.1
        #
        # canActivate(pat, One-off-consent(pat)) <-
        # hasActivated(pat, Patient())
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Patient" and 
            subj == pat
        }
    
    def canActivate_2(self, ag): # S2.1.2
        #
        # canActivate(ag, One-off-consent(pat)) <-
        # hasActivated(ag, Agent(pat))
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Agent" and 
            role.pat == self.pat and 
            subj == ag
        }
    
    def canActivate_3(self, cli): # S2.1.3
        #
        # canActivate(cli, One-off-consent(pat)) <-
        # hasActivated(cli, Spine-clinician(ra, org, spcty)), 
        # canActivate(cli, Treating-clinician(pat, org, spcty))
        #
        return {
            True for subj, role in hasActivated if 
            canActivate(subj, Treating_clinician(self.pat, role.org, role.spcty)) and 
            role.name == "Spine-clinician" and 
            subj == cli
        }
    
    def canDeactivate(self, *params):
        return self.canDeactivate_1(*params) or self.canDeactivate_2(*params) or self.canDeactivate_3(*params)
    
    def canDeactivate_1(self, pat, x): # S2.1.4
        #
        # canDeactivate(pat, x, One-off-consent(pat)) <-
        # hasActivated(pat, Patient())
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Patient" and 
            subj == pat
        }
    
    def canDeactivate_2(self, ag, x): # S2.1.5
        #
        # canDeactivate(ag, x, One-off-consent(pat)) <-
        # hasActivated(ag, Agent(pat))
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Agent" and 
            role.pat == self.pat and 
            subj == ag
        }
    
    def canDeactivate_3(self, cli, x): # S2.1.6
        #
        # canDeactivate(cli, x, One-off-consent(pat)) <-
        # hasActivated(cli, Spine-clinician(ra, org, spcty)), 
        # canActivate(cli, Treating-clinician(pat, org, spcty))
        #
        return {
            True for subj, role in hasActivated if 
            canActivate(subj, Treating_clinician(self.pat, role.org, role.spcty)) and 
            role.name == "Spine-clinician" and 
            subj == cli
        }

class Request_third_party_consent(Role):
    def __init__(self, x, pat, id):
        super().__init__('Request-third-party-consent', x = x, pat = pat, id = id)
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params) or self.canActivate_3(*params)
    
    def canActivate_1(self, pat): # S2.2.1
        #
        # canActivate(pat, Request-third-party-consent(x, pat, id)) <-
        # hasActivated(pat, Patient()), 
        # x in Get-spine-record-third-parties(pat, id)
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Patient" and 
            self.x in Get_spine_record_third_parties(subj, self.id) and 
            subj == pat
        }
    
    def canActivate_2(self, ag): # S2.2.2
        #
        # canActivate(ag, Request-third-party-consent(x, pat, id)) <-
        # hasActivated(ag, Agent(pat)), 
        # x in Get-spine-record-third-parties(pat, id)
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Agent" and 
            role.pat == self.pat and 
            self.x in Get_spine_record_third_parties(role.pat, self.id) and 
            subj == ag
        }
    
    def canActivate_3(self, cli): # S2.2.3
        #
        # canActivate(cli, Request-third-party-consent(x, pat, id)) <-
        # hasActivated(cli, Spine-clinician(ra, org, spcty)), 
        # canActivate(cli, Treating-clinician(pat, org, spcty)), 
        # x in Get-spine-record-third-parties(pat, id)
        #
        return {
            True for subj, role in hasActivated if 
            canActivate(subj, Treating_clinician(self.pat, role.org, role.spcty)) and 
            role.name == "Spine-clinician" and 
            self.x in Get_spine_record_third_parties(self.pat, self.id) and 
            subj == cli
        }
    
    def canDeactivate(self, *params):
        return self.canDeactivate_1(*params) or self.canDeactivate_2(*params) or self.canDeactivate_3(*params) or self.canDeactivate_4(*params)
    
    def canDeactivate_1(self, pat, y): # S2.2.4
        #
        # canDeactivate(pat, y, Request-third-party-consent(x, pat, id)) <-
        # hasActivated(pat, Patient())
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Patient" and 
            subj == pat
        }
    
    def canDeactivate_2(self, ag, y): # S2.2.5
        #
        # canDeactivate(ag, y, Request-third-party-consent(x, pat, id)) <-
        # hasActivated(pat, Agent(pat))
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Agent" and 
            role.pat == self.pat and 
            subj == role.pat
        }
    
    def canDeactivate_3(self, cli, y): # S2.2.6
        #
        # canDeactivate(cli, y, Request-third-party-consent(x, pat, id)) <-
        # hasActivated(cli, Spine-clinician(ra, org, spcty))
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Spine-clinician" and 
            subj == cli
        }
    
    def canDeactivate_4(self, x, y): # S2.2.7
        #
        # canDeactivate(x, y, Request-third-party-consent(x, pat, id)) <-
        # hasActivated(x, Third-party())
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Third-party" and 
            subj == x
        }
    
    def onDeactivate(self, subject):
        # S2.2.12 -- deactive Third-party():
        hasActivated -= { (subj, role) for (subj, role) in hasActivated if subj == self.x and role.name == 'Third_party' }
        
        # S2.2.16 -- deactive Third-party-consent(x, pat, id):
        hasActivated -= { (subj, role) for (subj, role) in hasActivated if subj == self.x and role.name == 'Third_party_consent' and role.x == self.x and role.pat == self.pat and role.id == self.id }

def other_third_party_consent_requests(y, z): # S2.2.9
    #
    # other-third-party-consent-requests(count<x>, y, z) <-
    # hasActivated(x, Request-third-party-consent(z, pat, id)), 
    # x != y
    #
    return len([
        True for subj, role in hasActivated if 
        role.name == "Request-third-party-consent" and 
        role.z == z and 
        subj != y
    ])

class Third_party(Role):
    def __init__(self):
        super().__init__('Third-party')
    
    def canActivate(self, x): # S2.2.10
        #
        # canActivate(x, Third-party()) <-
        # hasActivated(y, Request-third-party-consent(x, pat, id)), 
        # no-main-role-active(x), 
        # "PDS"@"PDS".hasActivated(z, Register-patient(x))
        #
        return {
            True for (subj1, role1) in hasActivated for (subj2, role2) in ehr.pds.hasActivated if 
            no_main_role_active(role2.x) and 
            role1.name == "Request-third-party-consent" and 
            role1.x == x and 
            role2.name == "Register-patient" and 
            role2.x == x
        }
    
    def canDeactivate(self, x, x_): # S2.2.11
        #
        # canDeactivate(x, x, Third-party()) <-
        # 
        #
        return (
            x == x_
        )

def count_third_party_activations(user): # S2.2.13
    #
    # count-third-party-activations(count<u>, user) <-
    # hasActivated(u, Third-party()), 
    # u = user
    #
    return len([
        True for subj, role in hasActivated if 
        role.name == "Third-party" and 
        subj == user
    ])

class Third_party_consent(Role):
    def __init__(self, x, pat, id):
        super().__init__('Third-party-consent', x = x, pat = pat, id = id)
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params)
    
    def canActivate_1(self, x): # S2.2.14
        #
        # canActivate(x, Third-party-consent(x, pat, id)) <-
        # hasActivated(x, Third-party()), 
        # hasActivated(y, Request-third-party-consent(x, pat, id))
        #
        return {
            True for (subj1, role1) in hasActivated for (subj2, role2) in hasActivated if 
            role1.name == "Third-party" and 
            role2.id == self.id and 
            role2.name == "Request-third-party-consent" and 
            role2.pat == self.pat and 
            role2.x == x and 
            subj1 == x
        }
    
    def canActivate_2(self, cli): # S2.2.15
        #
        # canActivate(cli, Third-party-consent(x, pat, id)) <-
        # hasActivated(cli, Spine-clinician(ra, org, spcty)), 
        # canActivate(cli, Treating-clinician(pat, org, spcty)), 
        # hasActivated(y, Request-third-party-consent(x, pat, id))
        #
        return {
            True for (subj1, role1) in hasActivated for (subj2, role2) in hasActivated if 
            canActivate(subj1, Treating_clinician(role2.pat, role1.org, role1.spcty)) and 
            role1.name == "Spine-clinician" and 
            role2.id == self.id and 
            role2.name == "Request-third-party-consent" and 
            role2.pat == self.pat and 
            role2.x == self.x and 
            subj1 == cli
        }

def third_party_consent(pat, id): # S2.2.17
    #
    # third-party-consent(group<consenter>, pat, id) <-
    # hasActivated(x, Third-party-consent(consenter, pat, id))
    #
    return {
        role.consenter for subj, role in hasActivated if 
        role.id == id and 
        role.name == "Third-party-consent" and 
        role.pat == pat
    }

class Request_consent_to_treatment(Role):
    def __init__(self, pat, org2, cli2, spcty2):
        super().__init__('Request-consent-to-treatment', pat = pat, org2 = org2, cli2 = cli2, spcty2 = spcty2)
    
    def canActivate(self, cli1): # S2.3.1
        #
        # canActivate(cli1, Request-consent-to-treatment(pat, org2, cli2, spcty2)) <-
        # hasActivated(cli1, Spine-clinician(ra1, org1, spcty1)), 
        # canActivate(cli2, Spine-clinician(ra2, org2, spcty2)), 
        # canActivate(pat, Patient())
        #
        return {
            True for subj, role in hasActivated if 
            canActivate(self.cli2, Spine_clinician(Wildcard(), self.org2, self.spcty2)) and 
            canActivate(self.pat, Patient()) and 
            role.name == "Spine-clinician" and 
            subj == cli1
        }
    
    def canDeactivate(self, *params):
        return self.canDeactivate_1(*params) or self.canDeactivate_2(*params) or self.canDeactivate_3(*params) or self.canDeactivate_4(*params) or self.canDeactivate_5(*params)
    
    def canDeactivate_1(self, cli1, cli1_): # S2.3.2
        #
        # canDeactivate(cli1, cli1, Request-consent-to-treatment(pat, org2, cli2, spcty2)) <-
        # hasActivated(cli1, Spine-clinician(ra1, org1, spcty1))
        #
        return {
            True for subj, role in hasActivated if 
            cli1 == cli1_ and 
            role.name == "Spine-clinician" and 
            subj == cli1
        }
    
    def canDeactivate_2(self, cli2, cli1): # S2.3.3
        #
        # canDeactivate(cli2, cli1, Request-consent-to-treatment(pat, org2, cli2, spcty2)) <-
        # hasActivated(cli2, Spine-clinician(ra2, org2, spcty2))
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Spine-clinician" and 
            role.org2 == self.org2 and 
            role.spcty2 == self.spcty2 and 
            subj == cli2
        }
    
    def canDeactivate_3(self, pat, x): # S2.3.4
        #
        # canDeactivate(pat, x, Request-consent-to-treatment(pat, org, cli, spcty)) <-
        # hasActivated(pat, Patient())
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Patient" and 
            subj == pat
        }
    
    def canDeactivate_4(self, ag, x): # S2.3.5
        #
        # canDeactivate(ag, x, Request-consent-to-treatment(pat, org, cli, spcty)) <-
        # hasActivated(ag, Agent(pat))
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Agent" and 
            role.pat == self.pat and 
            subj == ag
        }
    
    def canDeactivate_5(self, cli, x): # S2.3.6
        #
        # canDeactivate(cli, x, Request-consent-to-treatment(pat, org, cli2, spcty)) <-
        # hasActivated(cli, Spine-clinician(ra, org, spcty)), 
        # canActivate(cli, General-practitioner(pat))
        #
        return {
            True for subj, role in hasActivated if 
            canActivate(subj, General_practitioner(self.pat)) and 
            role.name == "Spine-clinician" and 
            subj == cli
        }
    
    def onDeactivate(self, subject):
        # S2.3.12 -- deactive Consent-to-treatment(pat, org, cli, spcty):
        hasActivated -= { (subj, role) for (subj, role) in hasActivated if role.name == 'Consent_to_treatment' and role.pat == self.pat and role.org == self.org2 and role.cli == self.cli2 and role.spcty == self.spcty2 }

def other_consent_to_treatment_requests(x, pat, org, cli, spcty): # S2.3.8
    #
    # other-consent-to-treatment-requests(count<y>, x, pat, org, cli, spcty) <-
    # hasActivated(y, Request-consent-to-treatment(pat, org, cli, spcty)), 
    # x != y
    #
    return len([
        True for subj, role in hasActivated if 
        role.cli == cli and 
        role.name == "Request-consent-to-treatment" and 
        role.org == org and 
        role.pat == pat and 
        role.spcty == spcty and 
        x != subj
    ])

class Consent_to_treatment(Role):
    def __init__(self, pat, org, cli, spcty):
        super().__init__('Consent-to-treatment', pat = pat, org = org, cli = cli, spcty = spcty)
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params) or self.canActivate_3(*params)
    
    def canActivate_1(self, pat): # S2.3.9
        #
        # canActivate(pat, Consent-to-treatment(pat, org, cli, spcty)) <-
        # hasActivated(pat, Patient()), 
        # hasActivated(x, Request-consent-to-treatment(pat, org, cli, spcty))
        #
        return {
            True for (subj1, role1) in hasActivated for (subj2, role2) in hasActivated if 
            role1.name == "Patient" and 
            role2.cli == self.cli and 
            role2.name == "Request-consent-to-treatment" and 
            role2.org == self.org and 
            role2.pat == pat and 
            role2.spcty == self.spcty and 
            subj1 == pat
        }
    
    def canActivate_2(self, ag): # S2.3.10
        #
        # canActivate(ag, Consent-to-treatment(pat, org, cli, spcty)) <-
        # hasActivated(ag, Agent(pat)), 
        # hasActivated(x, Request-consent-to-treatment(pat, org, cli, spcty))
        #
        return {
            True for (subj1, role1) in hasActivated for (subj2, role2) in hasActivated if 
            role1.name == "Agent" and 
            role1.pat == self.pat and 
            role2.cli == self.cli and 
            role2.name == "Request-consent-to-treatment" and 
            role2.org == self.org and 
            role2.pat == self.pat and 
            role2.spcty == self.spcty and 
            subj1 == ag
        }
    
    def canActivate_3(self, cli1): # S2.3.11
        #
        # canActivate(cli1, Consent-to-treatment(pat, org, cli2, spcty)) <-
        # hasActivated(cli1, Spine-clinician(ra, org, spcty)), 
        # canActivate(cli1, Treating-clinician(pat, org, spcty)), 
        # hasActivated(x, Request-consent-to-treatment(pat, org, cli2, spcty))
        #
        return {
            True for (subj1, role1) in hasActivated for (subj2, role2) in hasActivated if 
            canActivate(subj1, Treating_clinician(role2.pat, role2.org, role2.spcty)) and 
            role1.name == "Spine-clinician" and 
            role1.org == self.org and 
            role1.spcty == self.spcty and 
            role2.name == "Request-consent-to-treatment" and 
            role2.org == self.org and 
            role2.pat == self.pat and 
            role2.spcty == self.spcty and 
            subj1 == cli1
        }

class Request_consent_to_group_treatment(Role):
    def __init__(self, pat, org, group):
        super().__init__('Request-consent-to-group-treatment', pat = pat, org = org, group = group)
    
    def canActivate(self, cli): # S2.4.1
        #
        # canActivate(cli, Request-consent-to-group-treatment(pat, org, group)) <-
        # hasActivated(cli, Spine-clinician(ra, org, spcty)), 
        # canActivate(pat, Patient())
        #
        return {
            True for subj, role in hasActivated if 
            canActivate(self.pat, Patient()) and 
            role.name == "Spine-clinician" and 
            role.org == self.org and 
            subj == cli
        }
    
    def canDeactivate(self, *params):
        return self.canDeactivate_1(*params) or self.canDeactivate_2(*params) or self.canDeactivate_3(*params) or self.canDeactivate_4(*params) or self.canDeactivate_5(*params)
    
    def canDeactivate_1(self, cli, cli_): # S2.4.2
        #
        # canDeactivate(cli, cli, Request-consent-to-group-treatment(pat, org, group)) <-
        # hasActivated(cli, Spine-clinician(ra, org, spcty))
        #
        return {
            True for subj, role in hasActivated if 
            cli == cli_ and 
            role.name == "Spine-clinician" and 
            role.org == self.org and 
            subj == cli
        }
    
    def canDeactivate_2(self, pat, x): # S2.4.3
        #
        # canDeactivate(pat, x, Request-consent-to-group-treatment(pat, org, group)) <-
        # hasActivated(pat, Patient())
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Patient" and 
            subj == pat
        }
    
    def canDeactivate_3(self, ag, x): # S2.4.4
        #
        # canDeactivate(ag, x, Request-consent-to-group-treatment(pat, org, group)) <-
        # hasActivated(ag, Agent(pat))
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Agent" and 
            role.pat == self.pat and 
            subj == ag
        }
    
    def canDeactivate_4(self, cli, x): # S2.4.5
        #
        # canDeactivate(cli, x, Request-consent-to-group-treatment(pat, org, group)) <-
        # hasActivated(cli, Spine-clinician(ra, org, spcty)), 
        # canActivate(cli, General-practitioner(pat))
        #
        return {
            True for subj, role in hasActivated if 
            canActivate(subj, General_practitioner(self.pat)) and 
            role.name == "Spine-clinician" and 
            role.org == self.org and 
            subj == cli
        }
    
    def canDeactivate_5(self, cli, x): # S2.4.6
        #
        # canDeactivate(cli, x, Request-consent-to-group-treatment(pat, org, group)) <-
        # hasActivated(cli, Spine-clinician(ra, org, spcty)), 
        # ra@ra.canActivate(cli, Workgroup-member(org, group, spcty))
        #
        return {
            True for subj, role in hasActivated if 
            canActivate(subj, ehr.ra.Workgroup_member(role.org, self.group, role.spcty)) and 
            role.name == "Spine-clinician" and 
            role.org == self.org and 
            subj == cli
        }
    
    def onDeactivate(self, subject):
        # S2.4.12 -- deactive Consent-to-group-treatment(pat, org, group):
        hasActivated -= { (subj, role) for (subj, role) in hasActivated if role.name == 'Consent_to_group_treatment' and role.pat == self.pat and role.org == self.org and role.group == self.group }

def other_consent_to_group_treatment_requests(x, pat, org, group): # S2.4.8
    #
    # other-consent-to-group-treatment-requests(count<y>, x, pat, org, group) <-
    # hasActivated(y, Request-consent-to-group-treatment(pat, org, group)), 
    # x != y
    #
    return len([
        True for subj, role in hasActivated if 
        role.group == group and 
        role.name == "Request-consent-to-group-treatment" and 
        role.org == org and 
        role.pat == pat and 
        x != subj
    ])

class Consent_to_group_treatment(Role):
    def __init__(self, pat, org, group):
        super().__init__('Consent-to-group-treatment', pat = pat, org = org, group = group)
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params) or self.canActivate_3(*params)
    
    def canActivate_1(self, pat): # S2.4.9
        #
        # canActivate(pat, Consent-to-group-treatment(pat, org, group)) <-
        # hasActivated(pat, Patient()), 
        # hasActivated(x, Request-consent-to-group-treatment(pat, org, group))
        #
        return {
            True for (subj1, role1) in hasActivated for (subj2, role2) in hasActivated if 
            role1.name == "Patient" and 
            role2.group == self.group and 
            role2.name == "Request-consent-to-group-treatment" and 
            role2.org == self.org and 
            role2.pat == pat and 
            subj1 == pat
        }
    
    def canActivate_2(self, ag): # S2.4.10
        #
        # canActivate(ag, Consent-to-group-treatment(pat, org, group)) <-
        # hasActivated(ag, Agent(pat)), 
        # hasActivated(x, Request-consent-to-group-treatment(pat, org, group))
        #
        return {
            True for (subj1, role1) in hasActivated for (subj2, role2) in hasActivated if 
            role1.name == "Agent" and 
            role1.pat == self.pat and 
            role2.group == self.group and 
            role2.name == "Request-consent-to-group-treatment" and 
            role2.org == self.org and 
            role2.pat == self.pat and 
            subj1 == ag
        }
    
    def canActivate_3(self, cli1): # S2.4.11
        #
        # canActivate(cli1, Consent-to-group-treatment(pat, org, group)) <-
        # hasActivated(cli1, Spine-clinician(ra, org, spcty)), 
        # canActivate(cli1, Treating-clinician(pat, org, spcty)), 
        # hasActivated(x, Request-consent-to-group-treatment(pat, org, group))
        #
        return {
            True for (subj1, role1) in hasActivated for (subj2, role2) in hasActivated if 
            canActivate(subj1, Treating_clinician(role2.pat, role2.org, role1.spcty)) and 
            role1.name == "Spine-clinician" and 
            role1.org == self.org and 
            role2.group == self.group and 
            role2.name == "Request-consent-to-group-treatment" and 
            role2.org == self.org and 
            role2.pat == self.pat and 
            subj1 == cli1
        }

class Referrer(Role):
    def __init__(self, pat, org, cli2, spcty1):
        super().__init__('Referrer', pat = pat, org = org, cli2 = cli2, spcty1 = spcty1)
    
    def canActivate(self, cli1): # S3.1.1
        #
        # canActivate(cli1, Referrer(pat, org, cli2, spcty1)) <-
        # hasActivated(cli1, Spine-clinician(ra, org, spcty2)), 
        # canActivate(cli1, Treating-clinician(pat, org, spcty2))
        #
        return {
            True for subj, role in hasActivated if 
            canActivate(subj, Treating_clinician(self.pat, role.org, role.spcty2)) and 
            role.name == "Spine-clinician" and 
            role.org == self.org and 
            subj == cli1
        }
    
    def canDeactivate(self, *params):
        return self.canDeactivate_1(*params) or self.canDeactivate_2(*params)
    
    def canDeactivate_1(self, cli1, cli1_): # S3.1.2
        #
        # canDeactivate(cli1, cli1, Referrer(pat, org, cli2, spcty1)) <-
        # 
        #
        return (
            cli1 == cli1_
        )
    
    def canDeactivate_2(self, pat, cli1): # S3.1.3
        #
        # canDeactivate(pat, cli1, Referrer(pat, org, cli2, spcty1)) <-
        # 
        #
        return (
            
        )

class Spine_emergency_clinician(Role):
    def __init__(self, org, pat):
        super().__init__('Spine-emergency-clinician', org = org, pat = pat)
    
    def canActivate(self, cli): # S3.2.1
        #
        # canActivate(cli, Spine-emergency-clinician(org, pat)) <-
        # hasActivated(cli, Spine-clinician(ra, org, spcty)), 
        # canActivate(pat, Patient())
        #
        return {
            True for subj, role in hasActivated if 
            canActivate(self.pat, Patient()) and 
            role.name == "Spine-clinician" and 
            role.org == self.org and 
            subj == cli
        }
    
    def canDeactivate(self, cli, cli_): # S3.2.2
        #
        # canDeactivate(cli, cli, Spine-emergency-clinician(org, pat)) <-
        # 
        #
        return (
            cli == cli_
        )

class Treating_clinician(Role):
    def __init__(self, pat, org, spcty):
        super().__init__('Treating-clinician', pat = pat, org = org, spcty = spcty)
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params) or self.canActivate_3(*params) or self.canActivate_4(*params)
    
    def canActivate_1(self, cli): # S3.3.1
        #
        # canActivate(cli, Treating-clinician(pat, org, spcty)) <-
        # hasActivated(x, Consent-to-treatment(pat, org, cli, spcty))
        #
        return {
            True for subj, role in hasActivated if 
            role.cli == cli and 
            role.name == "Consent-to-treatment" and 
            role.org == self.org and 
            role.pat == self.pat and 
            role.spcty == self.spcty
        }
    
    def canActivate_2(self, cli): # S3.3.2
        #
        # canActivate(cli, Treating-clinician(pat, org, spcty)) <-
        # hasActivated(cli, Spine-emergency-clinician(org, pat)), 
        # spcty = "A-and-E"
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Spine-emergency-clinician" and 
            role.org == self.org and 
            role.pat == self.pat and 
            self.spcty == "A_and_E" and 
            subj == cli
        }
    
    def canActivate_3(self, cli): # S3.3.3
        #
        # canActivate(cli, Treating-clinician(pat, org, spcty)) <-
        # canActivate(cli, Spine-clinician(ra, org, spcty)), 
        # hasActivated(x, Referrer(pat, org, cli, spcty))
        #
        return {
            True for subj, role in hasActivated if 
            canActivate(role.cli, Spine_clinician(Wildcard(), role.org, role.spcty)) and 
            role.cli == cli and 
            role.name == "Referrer" and 
            role.org == self.org and 
            role.pat == self.pat and 
            role.spcty == self.spcty
        }
    
    def canActivate_4(self, cli): # S3.3.4
        #
        # canActivate(cli, Treating-clinician(pat, org, spcty)) <-
        # canActivate(cli, Group-treating-clinician(pat, ra, org, group, spcty))
        #
        return (
            canActivate(cli, Group_treating_clinician(self.pat, Wildcard(), self.org, Wildcard(), self.spcty))
        )

class General_practitioner(Role):
    def __init__(self, pat):
        super().__init__('General-practitioner', pat = pat)
    
    def canActivate(self, cli): # S3.3.5
        #
        # canActivate(cli, General-practitioner(pat)) <-
        # canActivate(cli, Treating-clinician(pat, org, spcty)), 
        # spcty = "GP"
        #
        # Using a hand translation, because this rule could not be translated automatically.
        # Reason: [1] unable to bind vars ['spcty'] in constraint spcty == "GP"
        #
        return canActivate(cli, Registration_authority(self.org, Wildcard(), "GP"))

class Group_treating_clinician(Role):
    def __init__(self, pat, ra, org, group, spcty):
        super().__init__('Group-treating-clinician', pat = pat, ra = ra, org = org, group = group, spcty = spcty)
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params)
    
    def canActivate_1(self, cli): # S3.4.1
        #
        # canActivate(cli, Group-treating-clinician(pat, ra, org, group, spcty)) <-
        # hasActivated(x, Consent-to-group-treatment(pat, org, group)), 
        # ra.canActivate(cli, Workgroup-member(org, group, spcty)), 
        # canActivate(ra, Registration-authority())
        #
        return {
            True for subj, role in hasActivated if 
            canActivate(cli, ehr.ra.Workgroup_member(role.org, role.group, self.spcty)) and 
            canActivate(self.ra, Registration_authority()) and 
            role.group == self.group and 
            role.name == "Consent-to-group-treatment" and 
            role.org == self.org and 
            role.pat == self.pat
        }
    
    def canActivate_2(self, cli): # S3.4.2
        #
        # canActivate(cli, Group-treating-clinician(pat, ra, org, group, spcty)) <-
        # hasActivated(x, Consent-to-group-treatment(pat, org, group)), 
        # ra@ra.canActivate(cli, Workgroup-member(org, group, spcty)), 
        # canActivate(ra, Registration-authority())
        #
        return {
            True for subj, role in hasActivated if 
            canActivate(cli, ehr.ra.Workgroup_member(role.org, role.group, self.spcty)) and 
            canActivate(self.ra, Registration_authority()) and 
            role.group == self.group and 
            role.name == "Consent-to-group-treatment" and 
            role.org == self.org and 
            role.pat == self.pat
        }

class Concealed_by_spine_clinician(Role):
    def __init__(self, pat, ids, start, end):
        super().__init__('Concealed-by-spine-clinician', pat = pat, ids = ids, start = start, end = end)
    
    def canActivate(self, cli): # S4.1.1
        #
        # canActivate(cli, Concealed-by-spine-clinician(pat, ids, start, end)) <-
        # hasActivated(cli, Spine-clinician(ra, org, spcty)), 
        # canActivate(cli, Treating-clinician(pat, org, spcty))
        #
        return {
            True for subj, role in hasActivated if 
            canActivate(subj, Treating_clinician(self.pat, role.org, role.spcty)) and 
            role.name == "Spine-clinician" and 
            subj == cli
        }
    
    def canDeactivate(self, *params):
        return self.canDeactivate_1(*params) or self.canDeactivate_2(*params) or self.canDeactivate_3(*params)
    
    def canDeactivate_1(self, cli, cli_): # S4.1.2
        #
        # canDeactivate(cli, cli, Concealed-by-spine-clinician(pat, ids, start, end)) <-
        # hasActivated(cli, Spine-clinician(ra, org, spcty))
        #
        return {
            True for subj, role in hasActivated if 
            cli == cli_ and 
            role.name == "Spine-clinician" and 
            subj == cli
        }
    
    def canDeactivate_2(self, cli, cli2): # S4.1.3
        #
        # canDeactivate(cli, cli2, Concealed-by-spine-clinician(pat, ids, start, end)) <-
        # hasActivated(cli, Spine-clinician(ra, org, spcty)), 
        # canActivate(cli, General-practitioner(pat))
        #
        return {
            True for subj, role in hasActivated if 
            canActivate(subj, General_practitioner(self.pat)) and 
            role.name == "Spine-clinician" and 
            subj == cli
        }
    
    def canDeactivate_3(self, cli1, cli2): # S4.1.4
        #
        # canDeactivate(cli1, cli2, Concealed-by-spine-clinician(pat, ids, start, end)) <-
        # hasActivated(cli1, Spine-clinician(ra, org, spcty1)), 
        # canActivate(cli1, Group-treating-clinician(pat, ra, org, group, spcty1)), 
        # canActivate(cli2, Group-treating-clinician(pat, ra, org, group, spcty2)), 
        # hasActivated(x, Consent-to-group-treatment(pat, org, group))
        #
        return {
            True for (subj1, role1) in hasActivated for (subj2, role2) in hasActivated if 
            canActivate(cli2, Group_treating_clinician(role2.pat, role1.ra, role2.org, role2.group, Wildcard())) and 
            canActivate(subj1, Group_treating_clinician(role2.pat, role1.ra, role2.org, role2.group, role1.spcty1)) and 
            role1.name == "Spine-clinician" and 
            role2.name == "Consent-to-group-treatment" and 
            role2.pat == self.pat and 
            subj1 == cli1
        }

def count_concealed_by_spine_clinician(pat, id): # S4.1.6
    #
    # count-concealed-by-spine-clinician(count<x>, pat, id) <-
    # hasActivated(x, Concealed-by-spine-clinician(pat, ids, start, end)), 
    # id in ids, 
    # Current-time() in [start, end]
    #
    return len([
        True for subj, role in hasActivated if 
        Current_time() in vrange(role.start, role.end) and 
        id in role.ids and 
        role.name == "Concealed-by-spine-clinician" and 
        role.pat == pat
    ])

class Conceal_request(Role):
    def __init__(self, what, who, start, end):
        super().__init__('Conceal-request', what = what, who = who, start = start, end = end)
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params)
    
    def canActivate_1(self, pat): # S4.2.1
        #
        # canActivate(pat, Conceal-request(what, who, start, end)) <-
        # hasActivated(pat, Patient()), 
        # count-conceal-requests(n, pat), 
        # what = (pat,ids,orgs,authors,subjects,from-time,to-time), 
        # who = (orgs1,readers1,spctys1), 
        # n < 100
        #
        # Using a hand translation, because this rule could not be translated automatically.
        # Reason: [2] unable to bind vars ['authors', 'from_time', 'ids', 'orgs', 'subjects', 'to_time'] in constraint compare_seq(self.what, (subj, ids, orgs, authors, subjects, from_time, to_time))
        #
        return {
                True for subj, role in hasActivated if 
                role.name == "Conceal-request" and 
                subj == pat and 
                compare_seq(self.what, (role.pat, Wildcard(), Wildcard(), Wildcard(), Wildcard(), Wildcard(), Wildcard())) and 
                compare_seq(self.who, (Wildcard(), Wildcard(), Wildcard())) and 
                count_conceal_requests(pat) < 100
        }
    
    def canActivate_2(self, ag): # S4.2.2
        #
        # canActivate(ag, Conceal-request(what, who, start, end)) <-
        # hasActivated(ag, Agent(pat)), 
        # count-conceal-requests(n, pat), 
        # what = (pat,ids,orgs,authors,subjects,from-time,to-time), 
        # who = (orgs1,readers1,spctys1), 
        # n < 100
        #
        # Using a hand translation, because this rule could not be translated automatically.
        # Reason: [3] unable to bind vars ['authors', 'from_time', 'ids', 'orgs', 'subjects', 'to_time'] in constraint compare_seq(self.what, (role.pat, ids, orgs, authors, subjects, from_time, to_time))
        #
        return {
                True for subj, role in hasActivated if 
                role.name == "Agent" and 
                subj == ag and 
                count_conceal_requests(role.pat) < 100 and 
                compare_seq(self.what, (role.pat, Wildcard(), Wildcard(), Wildcard(), Wildcard(), Wildcard(), Wildcard())) and 
                compare_seq(self.who, (Wildcard(), Wildcard(), Wildcard()))
        }
    
    def canDeactivate(self, *params):
        return self.canDeactivate_1(*params) or self.canDeactivate_2(*params) or self.canDeactivate_3(*params)
    
    def canDeactivate_1(self, pat, x): # S4.2.3
        #
        # canDeactivate(pat, x, Conceal-request(what, whom, start, end)) <-
        # hasActivated(pat, Patient()), 
        # pi7_1(what) = pat
        #
        return {
            True for subj, role in hasActivated if 
            pi7_1(self.what) == subj and 
            role.name == "Patient" and 
            subj == pat
        }
    
    def canDeactivate_2(self, ag, x): # S4.2.4
        #
        # canDeactivate(ag, x, Conceal-request(what, whom, start, end)) <-
        # hasActivated(ag, Agent(pat)), 
        # pi7_1(what) = pat
        #
        return {
            True for subj, role in hasActivated if 
            pi7_1(self.what) == role.pat and 
            role.name == "Agent" and 
            subj == ag
        }
    
    def canDeactivate_3(self, cli, x): # S4.2.5
        #
        # canDeactivate(cli, x, Conceal-request(what, whom, start, end)) <-
        # hasActivated(cli, Spine-clinician(ra, org, spcty)), 
        # canActivate(cli, General-practitioner(pat)), 
        # pi7_1(what) = pat
        #
        # Using a hand translation, because this rule could not be translated automatically.
        # Reason: [4] unable to bind vars ['pat'] in constraint pi7_1(self.what) == pat
        #
        return {
                True for subj, role in hasActivated if 
                role.name == "Spine-clinician" and 
                subj == cli and
                canActivate(cli, General_practitioner( pi7_1(self.what) ))
        }
    
    def onDeactivate(self, subject):
        # S4.2.11 -- deactive Concealed-by-spine-patient(what, who, start, end):
        hasActivated -= { (subj, role) for (subj, role) in hasActivated if role.name == 'Concealed_by_spine_patient' and role.what == self.what and role.who == self.who and role.start == self.start and role.end == self.end }

def count_conceal_requests(pat): # S4.2.7
    #
    # count-conceal-requests(count<y>, pat) <-
    # hasActivated(x, Conceal-request(y)), 
    # what = (pat,ids,orgs,authors,subjects,from-time,to-time), 
    # who = (orgs1,readers1,spctys1), 
    # y = (what,who,start,end)
    #
    # Using a hand translation, because this rule could not be translated automatically.
    # Reason: [5] unable to bind vars ['authors', 'from_time', 'ids', 'orgs', 'subjects', 'to_time', 'what'] in constraint compare_seq(what, (pat, ids, orgs, authors, subjects, from_time, to_time))
    #
    return len({
            True for subj, role in hasActivated if 
            role.name == "Conceal-request" and 
            compare_seq(role.what, (role.pat, Wildcard(), Wildcard(), Wildcard(), Wildcard(), Wildcard(), Wildcard())) and 
            compare_seq(role.who, (Wildcard(), Wildcard(), Wildcard()))
    })

class Concealed_by_spine_patient(Role):
    def __init__(self, what, who, start, end):
        super().__init__('Concealed-by-spine-patient', what = what, who = who, start = start, end = end)
    
    def canActivate(self, cli): # S4.2.8
        #
        # canActivate(cli, Concealed-by-spine-patient(what, who, start, end)) <-
        # hasActivated(cli, Spine-clinician(ra, org, spcty)), 
        # canActivate(cli, Treating-clinician(pat, org, spcty)), 
        # hasActivated(x, Conceal-request(what, who, start, end))
        #
        return {
            True for (subj1, role1) in hasActivated for (subj2, role2) in hasActivated if 
            canActivate(subj1, Treating_clinician(Wildcard(), role1.org, role1.spcty)) and 
            role1.name == "Spine-clinician" and 
            role2.end == self.end and 
            role2.name == "Conceal-request" and 
            role2.start == self.start and 
            role2.what == self.what and 
            role2.who == self.who and 
            subj1 == cli
        }
    
    def canDeactivate(self, *params):
        return self.canDeactivate_1(*params) or self.canDeactivate_2(*params)
    
    def canDeactivate_1(self, cli, cli_): # S4.2.9
        #
        # canDeactivate(cli, cli, Concealed-by-spine-patient(what, who, start, end)) <-
        # hasActivated(cli, Spine-clinician(ra, org, spcty))
        #
        return {
            True for subj, role in hasActivated if 
            cli == cli_ and 
            role.name == "Spine-clinician" and 
            subj == cli
        }
    
    def canDeactivate_2(self, cli1, cli2): # S4.2.10
        #
        # canDeactivate(cli1, cli2, Concealed-by-spine-patient(what, who, start1, end1)) <-
        # hasActivated(cli1, Spine-clinician(ra, org, spcty1)), 
        # ra@ra.canActivate(cli1, Group-treating-clinician(pat, ra, org, group, spcty1)), 
        # ra@ra.canActivate(cli2, Group-treating-clinician(pat, ra, org, group, spcty2))
        #
        return {
            True for subj, role in hasActivated if 
            canActivate(cli2, ehr.ra.Group_treating_clinician(Wildcard(), role.ra, role.org, Wildcard(), Wildcard())) and 
            canActivate(subj, ehr.ra.Group_treating_clinician(Wildcard(), role.ra, role.org, Wildcard(), role.spcty1)) and 
            role.name == "Spine-clinician" and 
            subj == cli1
        }

def count_concealed_by_spine_patient(a, b): # S4.2.12
    #
    # count-concealed-by-spine-patient(count<x>, a, b) <-
    # hasActivated(x, Concealed-by-spine-patient(what, who, start, end)), 
    # a = (pat,id), 
    # b = (org,reader,spcty), 
    # what = (pat,ids,orgs,authors,subjects,from-time,to-time), 
    # who = (orgs1,readers1,spctys1), 
    # Get-spine-record-org(pat, id) in orgs, 
    # Get-spine-record-author(pat, id) in authors, 
    # sub in Get-spine-record-subjects(pat, id), 
    # sub in subjects, 
    # Get-spine-record-time(pat, id) in [from-time, to-time], 
    # id in ids, 
    # org in orgs1, 
    # reader in readers1, 
    # spcty in spctys1, 
    # Current-time() in [start, end], 
    # Get-spine-record-third-parties(pat, id) = emptyset, 
    # "non-clinical" notin Get-spine-record-subjects(pat, id)
    #
    # Using a hand translation, because this rule could not be translated automatically.
    # Reason: [6] unable to bind vars ['id', 'pat'] in constraint compare_seq(a, (pat, id))
    #
    return len({
            True for subj, role in hasActivated if 
            role.name == "Concealed-by-spine-patient" and 
            compare_seq(role.what, (a.pat, Wildcard(), Wildcard(), Wildcard(), Wildcard(), Wildcard(), Wildcard())) and 
            compare_seq(role.who, (Wildcard(), Wildcard(), Wildcard())) and 
            Get_spine_record_org(a.pat, a.id) in role.what.orgs and 
            Get_spine_record_author(a.pat, a.id) in role.what.authors and 
            (True for sub in role.what.subjects if 
                sub in Get_spine_record_subjects(a.pat, a.id)) and 
            Get_spine_record_time(a.pat, a.id) in [role.what.from_time, role.what.to_time] and 
            a.id in role.what.ids and 
            b.org in role.who.orgs1 and 
            b.reader in role.who.readers1 and 
            b.spcty in role.who.spctys1 and 
            Current_time() in vrange(role.start, role.end) and 
            (not Get_spine_record_third_parties(a.pat, a.id)) and 
            "non-clinical" not in Get_spine_record_subjects(a.pat, a.id)
    })

class Authenticated_express_consent(Role):
    def __init__(self, pat, cli):
        super().__init__('Authenticated-express-consent', pat = pat, cli = cli)
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params) or self.canActivate_3(*params)
    
    def canActivate_1(self, pat): # S4.3.1
        #
        # canActivate(pat, Authenticated-express-consent(pat, cli)) <-
        # hasActivated(pat, Patient()), 
        # count-authenticated-express-consent(n, pat), 
        # n < 100
        #
        return {
            True for subj, role in hasActivated if 
            count_authenticated_express_consent(subj) < 100 and 
            role.name == "Patient" and 
            subj == pat
        }
    
    def canActivate_2(self, ag): # S4.3.2
        #
        # canActivate(ag, Authenticated-express-consent(pat, cli)) <-
        # hasActivated(ag, Agent(pat)), 
        # count-authenticated-express-consent(n, pat), 
        # n < 100
        #
        return {
            True for subj, role in hasActivated if 
            count_authenticated_express_consent(role.pat) < 100 and 
            role.name == "Agent" and 
            role.pat == self.pat and 
            subj == ag
        }
    
    def canActivate_3(self, cli1): # S4.3.3
        #
        # canActivate(cli1, Authenticated-express-consent(pat, cli2)) <-
        # hasActivated(cli1, Spine-clinician(ra, org, spcty)), 
        # canActivate(cli1, General-practitioner(pat))
        #
        return {
            True for subj, role in hasActivated if 
            canActivate(subj, General_practitioner(self.pat)) and 
            role.name == "Spine-clinician" and 
            subj == cli1
        }
    
    def canDeactivate(self, *params):
        return self.canDeactivate_1(*params) or self.canDeactivate_2(*params) or self.canDeactivate_3(*params)
    
    def canDeactivate_1(self, pat, x): # S4.3.4
        #
        # canDeactivate(pat, x, Authenticated-express-consent(pat, cli)) <-
        # hasActivated(pat, Patient())
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Patient" and 
            subj == pat
        }
    
    def canDeactivate_2(self, ag, x): # S4.3.5
        #
        # canDeactivate(ag, x, Authenticated-express-consent(pat, cli)) <-
        # hasActivated(ag, Agent(pat))
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Agent" and 
            role.pat == self.pat and 
            subj == ag
        }
    
    def canDeactivate_3(self, cli1, x): # S4.3.6
        #
        # canDeactivate(cli1, x, Authenticated-express-consent(pat, cli2)) <-
        # hasActivated(cli1, Spine-clinician(ra, org, spcty)), 
        # canActivate(cli1, General-practitioner(pat))
        #
        return {
            True for subj, role in hasActivated if 
            canActivate(subj, General_practitioner(self.pat)) and 
            role.name == "Spine-clinician" and 
            subj == cli1
        }

def count_authenticated_express_consent(pat): # S4.3.8
    #
    # count-authenticated-express-consent(count<cli>, pat) <-
    # hasActivated(x, Authenticated-express-consent(pat, cli))
    #
    return len([
        True for subj, role in hasActivated if 
        role.name == "Authenticated-express-consent" and 
        role.pat == pat
    ])

class Add_spine_record_item(Role): # Action
    def __init__(self, pat):
        super().__init__('Add-spine-record-item', pat = 'pat')
    
    def permits(self, cli): # S5.1.1
        #
        # permits(cli, Add-spine-record-item(pat)) <-
        # hasActivated(cli, Spine-clinician(ra, org, spcty)), 
        # canActivate(cli, Treating-clinician(pat, org, spcty))
        #
        return {
            True for subj, role in hasActivated if 
            canActivate(subj, Treating_clinician(self.pat, role.org, role.spcty)) and 
            role.name == "Spine-clinician" and 
            subj == cli
        }


class Annotate_spine_record_item(Role): # Action
    def __init__(self, pat, id):
        super().__init__('Annotate-spine-record-item', pat = 'pat', id = 'id')
    
    def permits(self, subj):
        return self.permits_1(subj) or self.permits_2(subj) or self.permits_3(subj)
    
    def permits_1(self, pat): # S5.1.2
        #
        # permits(pat, Annotate-spine-record-item(pat, id)) <-
        # hasActivated(pat, Patient())
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Patient" and 
            subj == pat
        }
    
    def permits_2(self, ag): # S5.1.3
        #
        # permits(ag, Annotate-spine-record-item(pat, id)) <-
        # hasActivated(ag, Agent(pat))
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Agent" and 
            role.pat == self.pat and 
            subj == ag
        }
    
    def permits_3(self, pat): # S5.1.4
        #
        # permits(pat, Annotate-spine-record-item(pat, id)) <-
        # hasActivated(cli, Spine-clinician(ra, org, spcty)), 
        # canActivate(cli, Treating-clinician(pat, org, spcty))
        #
        return {
            True for subj, role in hasActivated if 
            canActivate(subj, Treating_clinician(pat, role.org, role.spcty)) and 
            role.name == "Spine-clinician"
        }


class Get_spine_record_item_ids(Role): # Action
    def __init__(self, pat):
        super().__init__('Get-spine-record-item-ids', pat = 'pat')
    
    def permits(self, subj):
        return self.permits_1(subj) or self.permits_2(subj) or self.permits_3(subj)
    
    def permits_1(self, pat): # S5.2.1
        #
        # permits(pat, Get-spine-record-item-ids(pat)) <-
        # hasActivated(pat, Patient())
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Patient" and 
            subj == pat
        }
    
    def permits_2(self, ag): # S5.2.2
        #
        # permits(ag, Get-spine-record-item-ids(pat)) <-
        # hasActivated(ag, Agent(pat))
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Agent" and 
            role.pat == self.pat and 
            subj == ag
        }
    
    def permits_3(self, cli): # S5.2.3
        #
        # permits(cli, Get-spine-record-item-ids(pat)) <-
        # hasActivated(cli, Spine-clinician(ra, org, spcty)), 
        # canActivate(cli, Treating-clinician(pat, org, spcty))
        #
        return {
            True for subj, role in hasActivated if 
            canActivate(subj, Treating_clinician(self.pat, role.org, role.spcty)) and 
            role.name == "Spine-clinician" and 
            subj == cli
        }


class Read_spine_record_item(Role): # Action
    def __init__(self, pat, id):
        super().__init__('Read-spine-record-item', pat = 'pat', id = 'id')
    
    def permits(self, subj):
        return self.permits_1(subj) or self.permits_2(subj) or self.permits_3(subj) or self.permits_4(subj) or self.permits_5(subj)
    
    def permits_1(self, pat): # S5.3.1
        #
        # permits(pat, Read-spine-record-item(pat, id)) <-
        # hasActivated(pat, Patient()), 
        # hasActivated(x, One-off-consent(pat)), 
        # count-concealed-by-spine-patient(n, a, b), 
        # count-concealed-by-spine-clinician(m, pat, id), 
        # third-party-consent(consenters, pat, id), 
        # n = 0, 
        # m = 0, 
        # a = (pat,id), 
        # b = ("No-org",pat,"No-spcty"), 
        # Get-spine-record-third-parties(pat, id) subseteq consenters
        #
        # Using a hand translation, because this rule could not be translated automatically.
        # Reason: [7] unbound vars ['a', 'b'] in count-concealed-by-spine-patient(n, a, b)
        #
        return {
                True for (subj1, role1) in hasActivated for (subj2, role2) in hasActivated if
                pat == self.pat and 
                role1.name == "Patient" and 
                subj1 == self.pat and 
                role2.name == "One-off-consent" and 
                role2.pat == self.pat and 
                count_concealed_by_spine_patient((self.pat, self.id), ("No-org", self.pat, "No-spcty")) == 0 and 
                count_concealed_by_spine_clinician(self.pat, self.id) == 0 and 
                Get_spine_record_third_parties(self.pat, self.id) in third_party_consent(self.pat, self.id)
        }
    
    def permits_2(self, ag): # S5.3.2
        #
        # permits(ag, Read-spine-record-item(pat, id)) <-
        # hasActivated(ag, Agent(pat)), 
        # hasActivated(x, One-off-consent(pat)), 
        # count-concealed-by-spine-patient(n, a, b), 
        # count-concealed-by-spine-clinician(m, pat, id), 
        # third-party-consent(consenters, pat, id), 
        # n = 0, 
        # m = 0, 
        # a = (pat,id), 
        # b = ("No-org",ag,"No-spcty"), 
        # Get-spine-record-third-parties(pat, id) subseteq consenters
        #
        # Using a hand translation, because this rule could not be translated automatically.
        # Reason: [8] unbound vars ['a', 'b'] in count-concealed-by-spine-patient(n, a, b)
        #
        return {
                True for (subj1, role1) in hasActivated for (subj2, role2) in hasActivated if 
                role1.name == "Agent" and 
                subj1 == ag and 
                role2.name == "One-off-consent" and 
                role2.pat == self.pat and 
                count_concealed_by_spine_patient((self.pat, self.id), ("No-org", self.pat, "No-spcty")) == 0 and 
                count_concealed_by_spine_clinician(self.pat, self.id) == 0 and 
                Get_spine_record_third_parties(self.pat, self.id) in third_party_consent(self.pat, self.id)
        }
    
    def permits_3(self, cli): # S5.3.3
        #
        # permits(cli, Read-spine-record-item(pat, id)) <-
        # hasActivated(cli, Spine-clinician(ra, org, spcty)), 
        # hasActivated(x, One-off-consent(pat)), 
        # Get-spine-record-org(pat, id) = org, 
        # Get-spine-record-author(pat, id) = cli
        #
        return {
            True for (subj1, role1) in hasActivated for (subj2, role2) in hasActivated if 
            Get_spine_record_author(role2.pat, self.id) == subj1 and 
            Get_spine_record_org(role2.pat, self.id) == role1.org and 
            role1.name == "Spine-clinician" and 
            role2.name == "One-off-consent" and 
            role2.pat == self.pat and 
            subj1 == cli
        }
    
    def permits_4(self, cli): # S5.3.4
        #
        # permits(cli, Read-spine-record-item(pat, id)) <-
        # hasActivated(cli, Spine-clinician(ra, org, spcty)), 
        # hasActivated(x, One-off-consent(pat)), 
        # canActivate(cli, Treating-clinician(pat, org, spcty)), 
        # count-concealed-by-spine-patient(n, a, b), 
        # n = 0, 
        # a = (pat,id), 
        # b = (org,cli,spcty), 
        # Get-spine-record-subjects(pat, id) subseteq Permitted-subjects(spcty)
        #
        # Using a hand translation, because this rule could not be translated automatically.
        # Reason: [9] unbound vars ['a', 'b'] in count-concealed-by-spine-patient(n, a, b)
        #
        return {
                True for (subj1, role1) in hasActivated for (subj2, role2) in hasActivated if 
                subj1 == cli and 
                role1.name == "Spine-clinician" and 
                role2.name == "One-off-consent" and 
                role2.pat == self.pat and 
                canActivate(cli, Treating_clinician(self.pat, role1.org, role1.spcty) and 
                count_concealed_by_spine_patient((self.pat, self.id), (role1.org, cli, role1.spcty)) == 0 and 
                Get_spine_record_subjects(self.pat, self.id) in Permitted_subjects(role1.spcty)
        }
    
    def permits_5(self, cli): # S5.3.5
        #
        # permits(cli, Read-spine-record-item(pat, id)) <-
        # hasActivated(cli, Spine-clinician(ra, org, spcty)), 
        # hasActivated(x, One-off-consent(pat)), 
        # canActivate(cli, Treating-clinician(pat, org, spcty)), 
        # hasActivated(y, Authenticated-express-consent(pat, cli)), 
        # Get-spine-record-subjects(pat, id) subseteq Permitted-subjects(spcty)
        #
        # Using a hand translation, because this rule could not be translated automatically.
        # Reason: [10] Not implemented: 3 hasAcs in a rule.
        #
        return {
                True for (subj1, role1) in hasActivated for (subj2, role2) in hasActivated for (subj3, role3) in hasActivated if 
                role1.name == "Spine-clinician" and 
                role2.name == "One-off-consent" and 
                role3.name == "Authenticated-express-consent" and 
                role2.pat == self.pat and 
                role2.pat == role3.pat and 
                role1.org == role3.org and 
                role1.spcty == role3.spcty and 
                canActivate(subj1, Treating_clinician(role2.pat, role1.org, role1.spcty)) and 
                Get_spine_record_subjects(self.pat, self.id) in Permitted_subjects(role1.spcty)
        }


class Force_read_spine_record_item(Role): # Action
    def __init__(self, pat, id):
        super().__init__('Force-read-spine-record-item', pat = 'pat', id = 'id')
    
    def permits(self, cli): # S5.3.6
        #
        # permits(cli, Force-read-spine-record-item(pat, id)) <-
        # hasActivated(cli, Spine-clinician(ra, org, spcty)), 
        # canActivate(cli, Treating-clinician(pat, org, spcty))
        #
        return {
            True for subj, role in hasActivated if 
            canActivate(subj, Treating_clinician(self.pat, role.org, role.spcty)) and 
            role.name == "Spine-clinician" and 
            subj == cli
        }


# Credential Request Restrictions
# ===============================
# These rules place restrictions on access to certain canActivate and hasActivated predicates.

# Restrictions on canActivate
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~

# <<< For the Role 'Agent' >>>

def canReqCred_canActivate_Agent_1(ag): # S1.4.6
    #
    # canReqCred(ag, "Spine".canActivate(ag, Agent(pat))) <-
    # hasActivated(ag, Agent(pat))
    #
    return {
        True for subj, role in hasActivated if 
        role.name == "Agent" and 
        subj == ag
    }

def canReqCred_canActivate_Agent_2(org): # S1.4.7
    #
    # canReqCred(org, "Spine".canActivate(ag, Agent(pat))) <-
    # ra.hasActivated(x, NHS-health-org-cert(org, start, end)), 
    # canActivate(ra, Registration-authority()), 
    # Current-time() in [start, end]
    #
    return {
        True for subj, role in hasActivated if 
        Current_time() in vrange(role.start, role.end) and 
        canActivate(Wildcard(), Registration_authority()) and 
        role.name == "NHS-health-org-cert" and 
        role.org == org
    }

def canReqCred_canActivate_Agent_3(org): # S1.4.8
    #
    # canReqCred(org, "Spine".canActivate(ag, Agent(pat))) <-
    # org@ra.hasActivated(x, NHS-health-org-cert(org, start, end)), 
    # canActivate(ra, Registration-authority()), 
    # Current-time() in [start, end]
    #
    return {
        True for subj, role in ehr.org.hasActivated if 
        Current_time() in vrange(role.start, role.end) and 
        canActivate(Wildcard(), Registration_authority()) and 
        role.name == "NHS-health-org-cert" and 
        role.org == org
    }

# <<< No restrictions on hasActivated rules in this module. >>>

