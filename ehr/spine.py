from cassandra import *
import ehr.hospital, ehr.pds, ehr.ra

hasActivated = list()  # Set of (subject, role) pairs representing currently active roles.

list_of_roles = ['Spine-clinician', 'Spine-admin', 'Register-spine-admin', 'Patient', 'Register-patient', 'Agent', 'Register-agent', 'Registration-authority', 'One-off-consent', 'Request-third-party-consent', 'Third-party', 'Third-party-consent', 'Request-consent-to-treatment', 'Consent-to-treatment', 'Request-consent-to-group-treatment', 'Consent-to-group-treatment', 'Referrer', 'Spine-emergency-clinician', 'Treating-clinician', 'General-practitioner', 'Group-treating-clinician', 'Concealed-by-spine-clinician', 'Conceal-request', 'Concealed-by-spine-patient', 'Authenticated-express-consent']

class Spine_clinician(Role):
    def __init__(self, ra, org, spcty):
        super().__init__('Spine-clinician', **{'ra':ra, 'org':org, 'spcty':spcty})
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params)
    
    def canActivate_1(self, cli): # S1.1.1
        return {
            True for subj, role in hasActivated if 
            role.name == "NHS-clinician-cert" and 
            role.spcty == self.spcty and 
            role.org == self.org and 
            role.cli == cli and 
            canActivate(self.ra, Registration_authority()) and 
            Current_time() in vrange(role.start, role.end) and 
            no_main_role_active(role.cli)
        }
    
    def canActivate_2(self, cli): # S1.1.2
        return {
            True for subj, role in ehr.ra.hasActivated if 
            role.name == "NHS-clinician-cert" and 
            role.spcty == self.spcty and 
            role.org == self.org and 
            role.cli == cli and 
            canActivate(self.ra, Registration_authority()) and 
            Current_time() in vrange(role.start, role.end) and 
            no_main_role_active(role.cli)
        }
    
    def canDeactivate(self, cli, cli_): # S1.1.3
        return (
            cli == cli_
        )
    
    def onDeactivate(self, subj):
        deactivate(hasActivated, subj, Spine_emergency_clinician(self.org, Wildcard()))  # S3.2.3
        

def count_spine_clinician_activations(user): # S1.1.4
    return len({
        True for subj, role in hasActivated if 
        role.name == "Spine-clinician" and 
        subj == user
    })

class Spine_admin(Role):
    def __init__(self, ):
        super().__init__('Spine-admin', **{})
    
    def canActivate(self, adm): # S1.2.1
        return {
            True for subj, role in hasActivated if 
            role.name == "Register-spine-admin" and 
            role.adm == adm and 
            no_main_role_active(role.adm)
        }
    
    def canDeactivate(self, adm, adm_): # S1.2.2
        return (
            adm == adm_
        )

def count_spine_admin_activations(user): # S1.2.4
    return len({
        True for subj, role in hasActivated if 
        role.name == "Spine-admin" and 
        subj == user
    })

class Register_spine_admin(Role):
    def __init__(self, adm2):
        super().__init__('Register-spine-admin', **{'adm2':adm2})
    
    def canActivate(self, adm): # S1.2.5
        return {
            True for subj, role in hasActivated if 
            role.name == "Spine-admin" and 
            subj == adm and 
            spine_admin_regs(self.adm2) == 0
        }
    
    def canDeactivate(self, adm, x): # S1.2.6
        return {
            True for subj, role in hasActivated if 
            role.name == "Spine-admin" and 
            subj == adm
        }
    
    def onDeactivate(self, subj):
        deactivate(hasActivated, self.adm2, Spine_admin())  # S1.2.3
        

def spine_admin_regs(adm): # S1.2.7
    return len({
        True for subj, role in hasActivated if 
        role.name == "Register-spine-admin" and 
        role.adm == adm
    })

class Patient(Role):
    def __init__(self, ):
        super().__init__('Patient', **{})
    
    def canActivate(self, pat): # S1.3.1
        return {
            True for (subj1, role1) in hasActivated for (subj2, role2) in ehr.pds.hasActivated if 
            role1.name == "Register-patient" and 
            role2.name == "Register-patient" and 
            role1.pat == pat and 
            role2.pat == pat and 
            no_main_role_active(role2.pat)
        }
    
    def canDeactivate(self, pat, pat_): # S1.3.2
        return (
            pat == pat_
        )

def count_patient_activations(user): # S1.3.4
    return len({
        True for subj, role in hasActivated if 
        role.name == "Patient" and 
        subj == user
    })

class Register_patient(Role):
    def __init__(self, pat):
        super().__init__('Register-patient', **{'pat':pat})
    
    def canActivate(self, adm): # S1.3.5
        return {
            True for subj, role in hasActivated if 
            role.name == "Spine-admin" and 
            subj == adm and 
            patient_regs(self.pat) == 0
        }
    
    def canDeactivate(self, adm, x): # S1.3.6
        return {
            True for subj, role in hasActivated if 
            role.name == "Spine-admin" and 
            subj == adm
        }
    
    def onDeactivate(self, subj):
        deactivate(hasActivated, self.pat, Patient())  # S1.3.3
        
        deactivate(hasActivated, Wildcard(), Register_agent(Wildcard(), self.pat))  # S1.4.13
        
        deactivate(hasActivated, Wildcard(), One_off_consent(self.pat))  # S2.1.7
        
        deactivate(hasActivated, Wildcard(), Request_third_party_consent(Wildcard(), self.pat, Wildcard()))  # S2.2.8
        
        deactivate(hasActivated, Wildcard(), Request_consent_to_treatment(self.pat, Wildcard(), Wildcard(), Wildcard()))  # S2.3.7
        
        deactivate(hasActivated, Wildcard(), Request_consent_to_group_treatment(self.pat, Wildcard(), Wildcard()))  # S2.4.7
        
        deactivate(hasActivated, self.pat, Referrer(self.pat, Wildcard(), Wildcard(), Wildcard()))  # S3.1.4
        
        deactivate(hasActivated, Wildcard(), Spine_emergency_clinician(Wildcard(), self.pat))  # S3.2.4
        
        deactivate(hasActivated, Wildcard(), Concealed_by_spine_clinician(self.pat, Wildcard(), Wildcard(), Wildcard()))  # S4.1.5
        
        #S4.2.6 todo: unable to bind vars {'what'} in constraint pi7_1(what) == self.pat
        #pi7_1(what) = pat
        deactivate(hasActivated, Wildcard(), Conceal_request(Wildcard(), Wildcard(), Wildcard(), Wildcard()))  # S4.2.6
        
        deactivate(hasActivated, Wildcard(), Authenticated_express_consent(self.pat, Wildcard()))  # S4.3.7
        

def patient_regs(pat): # S1.3.7
    return len({
        True for subj, role in hasActivated if 
        role.name == "Register-patient" and 
        role.pat == pat
    })

class Agent(Role):
    def __init__(self, pat):
        super().__init__('Agent', **{'pat':pat})
    
    def canActivate(self, ag): # S1.4.1
        return {
            True for (subj1, role1) in hasActivated for (subj2, role2) in ehr.pds.hasActivated if 
            role1.name == "Register-agent" and 
            role2.name == "Register-patient" and 
            role1.pat == self.pat and 
            role1.ag == ag and 
            role2.pat == self.pat and 
            role2.ag == ag and 
            no_main_role_active(role2.ag)
        }
    
    def canDeactivate(self, ag, ag_): # S1.4.2
        return (
            ag == ag_
        )

def other_agent_regs(x, ag, pat): # S1.4.4
    return len({
        True for subj, role in hasActivated if 
        role.name == "Register-agent" and 
        role.pat == pat and 
        role.ag == ag and 
        x != subj
    })

def count_agent_activations(user): # S1.4.5
    return len({
        True for subj, role in hasActivated if 
        role.name == "Agent" and 
        subj == user
    })

class Register_agent(Role):
    def __init__(self, agent, pat):
        super().__init__('Register-agent', **{'agent':agent, 'pat':pat})
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params)
    
    def canActivate_1(self, pat): # S1.4.9
        return {
            True for subj, role in hasActivated if 
            role.name == "Patient" and 
            subj == pat and 
            agent_regs(subj) < 3
        }
    
    def canActivate_2(self, cli): # S1.4.10
        return {
            True for subj, role in hasActivated if 
            role.name == "Spine-clinician" and 
            subj == cli and 
            canActivate(subj, General_practitioner(self.pat))
        }
    
    def canDeactivate(self, *params):
        return self.canDeactivate_1(*params) or self.canDeactivate_2(*params)
    
    def canDeactivate_1(self, pat, pat_): # S1.4.11
        return {
            True for subj, role in hasActivated if 
            pat == pat_ and 
            role.name == "Patient" and 
            subj == pat
        }
    
    def canDeactivate_2(self, cli, x): # S1.4.12
        return {
            True for subj, role in hasActivated if 
            role.name == "Spine-clinician" and 
            subj == cli and 
            canActivate(subj, General_practitioner(self.pat))
        }
    
    def onDeactivate(self, subj):
        if other_agent_regs(subj, self.agent, self.pat) == 0:
            deactivate(hasActivated, self.agent, Agent(self.pat))  # S1.4.3

def agent_regs(pat): # S1.4.14
    return len({
        True for subj, role in hasActivated if 
        role.name == "Register-agent" and 
        role.pat == pat and 
        subj == role.pat
    })

class Registration_authority(Role):
    def __init__(self, ):
        super().__init__('Registration-authority', **{})
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params)
    
    def canActivate_1(self, ra): # S1.5.1
        return {
            True for subj, role in hasActivated if 
            role.name == "NHS-registration-authority" and 
            role.ra == ra and 
            Current_time() in vrange(role.start, role.end)
        }
    
    def canActivate_2(self, ra): # S1.5.2
        return {
            True for subj, role in ehr.ra.hasActivated if 
            role.name == "NHS-registration-authority" and 
            role.ra == ra and 
            Current_time() in vrange(role.start, role.end)
        }

def no_main_role_active(user): # S1.5.3
    return  count_agent_activations(user) == 0 and \
            count_spine_clinician_activations(user) == 0 and \
            count_spine_admin_activations(user) == 0 and \
            count_patient_activations(user) == 0 and \
            count_third_party_activations(user) == 0

class One_off_consent(Role):
    def __init__(self, pat):
        super().__init__('One-off-consent', **{'pat':pat})
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params) or self.canActivate_3(*params)
    
    def canActivate_1(self, pat): # S2.1.1
        return {
            True for subj, role in hasActivated if 
            role.name == "Patient" and 
            subj == pat
        }
    
    def canActivate_2(self, ag): # S2.1.2
        return {
            True for subj, role in hasActivated if 
            role.name == "Agent" and 
            role.pat == self.pat and 
            subj == ag
        }
    
    def canActivate_3(self, cli): # S2.1.3
        return {
            True for subj, role in hasActivated if 
            role.name == "Spine-clinician" and 
            subj == cli and 
            canActivate(subj, Treating_clinician(self.pat, role.org, role.spcty))
        }
    
    def canDeactivate(self, *params):
        return self.canDeactivate_1(*params) or self.canDeactivate_2(*params) or self.canDeactivate_3(*params)
    
    def canDeactivate_1(self, pat, x): # S2.1.4
        return {
            True for subj, role in hasActivated if 
            role.name == "Patient" and 
            subj == pat
        }
    
    def canDeactivate_2(self, ag, x): # S2.1.5
        return {
            True for subj, role in hasActivated if 
            role.name == "Agent" and 
            role.pat == self.pat and 
            subj == ag
        }
    
    def canDeactivate_3(self, cli, x): # S2.1.6
        return {
            True for subj, role in hasActivated if 
            role.name == "Spine-clinician" and 
            subj == cli and 
            canActivate(subj, Treating_clinician(self.pat, role.org, role.spcty))
        }

class Request_third_party_consent(Role):
    def __init__(self, x, pat, id):
        super().__init__('Request-third-party-consent', **{'x':x, 'pat':pat, 'id':id})
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params) or self.canActivate_3(*params)
    
    def canActivate_1(self, pat): # S2.2.1
        return {
            True for subj, role in hasActivated if 
            role.name == "Patient" and 
            subj == pat and 
            self.x in Get_spine_record_third_parties(subj, self.id)
        }
    
    def canActivate_2(self, ag): # S2.2.2
        return {
            True for subj, role in hasActivated if 
            role.name == "Agent" and 
            role.pat == self.pat and 
            subj == ag and 
            self.x in Get_spine_record_third_parties(role.pat, self.id)
        }
    
    def canActivate_3(self, cli): # S2.2.3
        return {
            True for subj, role in hasActivated if 
            role.name == "Spine-clinician" and 
            subj == cli and 
            canActivate(subj, Treating_clinician(self.pat, role.org, role.spcty)) and 
            self.x in Get_spine_record_third_parties(self.pat, self.id)
        }
    
    def canDeactivate(self, *params):
        return self.canDeactivate_1(*params) or self.canDeactivate_2(*params) or self.canDeactivate_3(*params) or self.canDeactivate_4(*params)
    
    def canDeactivate_1(self, pat, y): # S2.2.4
        return {
            True for subj, role in hasActivated if 
            role.name == "Patient" and 
            subj == pat
        }
    
    def canDeactivate_2(self, ag, y): # S2.2.5
        return {
            True for subj, role in hasActivated if 
            role.name == "Agent" and 
            role.pat == self.pat and 
            subj == role.pat
        }
    
    def canDeactivate_3(self, cli, y): # S2.2.6
        return {
            True for subj, role in hasActivated if 
            role.name == "Spine-clinician" and 
            subj == cli
        }
    
    def canDeactivate_4(self, x, y): # S2.2.7
        return {
            True for subj, role in hasActivated if 
            role.name == "Third-party" and 
            subj == x
        }
    
    def onDeactivate(self, subj):
        if other_third_party_consent_requests(subj, self.x) == 0:
            deactivate(hasActivated, self.x, Third_party())  # S2.2.12
        if other_third_party_consent_requests(subj, self.x) == 0:
            deactivate(hasActivated, self.x, Third_party_consent(self.x, self.pat, self.id))  # S2.2.16

def other_third_party_consent_requests(y, z): # S2.2.9
    return len({
        True for subj, role in hasActivated if 
        role.name == "Request-third-party-consent" and 
        role.z == z and 
        subj != y
    })

class Third_party(Role):
    def __init__(self, ):
        super().__init__('Third-party', **{})
    
    def canActivate(self, x): # S2.2.10
        return {
            True for (subj1, role1) in hasActivated for (subj2, role2) in ehr.pds.hasActivated if 
            role1.name == "Request-third-party-consent" and 
            role2.name == "Register-patient" and 
            role1.x == x and 
            role2.x == x and 
            no_main_role_active(role2.x)
        }
    
    def canDeactivate(self, x, x_): # S2.2.11
        return (
            x == x_
        )

def count_third_party_activations(user): # S2.2.13
    return len({
        True for subj, role in hasActivated if 
        role.name == "Third-party" and 
        subj == user
    })

class Third_party_consent(Role):
    def __init__(self, x, pat, id):
        super().__init__('Third-party-consent', **{'x':x, 'pat':pat, 'id':id})
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params)
    
    def canActivate_1(self, x): # S2.2.14
        return {
            True for (subj1, role1) in hasActivated for (subj2, role2) in hasActivated if 
            role1.name == "Third-party" and 
            role2.name == "Request-third-party-consent" and 
            subj1 == x
        }
    
    def canActivate_2(self, cli): # S2.2.15
        return {
            True for (subj1, role1) in hasActivated for (subj2, role2) in hasActivated if 
            role1.name == "Spine-clinician" and 
            role2.name == "Request-third-party-consent" and 
            subj1 == cli and 
            canActivate(subj1, Treating_clinician(self.pat, role2.org, role2.spcty))
        }

def third_party_consent(pat, id): # S2.2.17
    return {
        role.consenter for subj, role in hasActivated if 
        role.name == "Third-party-consent" and 
        role.pat == pat and 
        role.id == id
    }

class Request_consent_to_treatment(Role):
    def __init__(self, pat, org2, cli2, spcty2):
        super().__init__('Request-consent-to-treatment', **{'pat':pat, 'org2':org2, 'cli2':cli2, 'spcty2':spcty2})
    
    def canActivate(self, cli1): # S2.3.1
        return {
            True for subj, role in hasActivated if 
            role.name == "Spine-clinician" and 
            subj == cli1 and 
            canActivate(self.cli2, Spine_clinician(Wildcard(), self.org2, self.spcty2)) and 
            canActivate(self.pat, Patient())
        }
    
    def canDeactivate(self, *params):
        return self.canDeactivate_1(*params) or self.canDeactivate_2(*params) or self.canDeactivate_3(*params) or self.canDeactivate_4(*params) or self.canDeactivate_5(*params)
    
    def canDeactivate_1(self, cli1, cli1_): # S2.3.2
        return {
            True for subj, role in hasActivated if 
            cli1 == cli1_ and 
            role.name == "Spine-clinician" and 
            subj == cli1
        }
    
    def canDeactivate_2(self, cli2, cli1): # S2.3.3
        return {
            True for subj, role in hasActivated if 
            role.name == "Spine-clinician" and 
            role.org2 == self.org2 and 
            role.spcty2 == self.spcty2 and 
            subj == cli2
        }
    
    def canDeactivate_3(self, pat, x): # S2.3.4
        return {
            True for subj, role in hasActivated if 
            role.name == "Patient" and 
            subj == pat
        }
    
    def canDeactivate_4(self, ag, x): # S2.3.5
        return {
            True for subj, role in hasActivated if 
            role.name == "Agent" and 
            role.pat == self.pat and 
            subj == ag
        }
    
    def canDeactivate_5(self, cli, x): # S2.3.6
        return {
            True for subj, role in hasActivated if 
            role.name == "Spine-clinician" and 
            subj == cli and 
            canActivate(subj, General_practitioner(self.pat))
        }
    
    def onDeactivate(self, subj):
        if other_consent_to_treatment_requests(subj, self.pat, self.org2, self.cli2, self.spcty2) == 0:
            deactivate(hasActivated, Wildcard(), Consent_to_treatment(self.pat, self.org2, self.cli2, self.spcty2))  # S2.3.12

def other_consent_to_treatment_requests(x, pat, org, cli, spcty): # S2.3.8
    return len({
        True for subj, role in hasActivated if 
        role.name == "Request-consent-to-treatment" and 
        role.spcty == spcty and 
        role.org == org and 
        role.pat == pat and 
        role.cli == cli and 
        x != subj
    })

class Consent_to_treatment(Role):
    def __init__(self, pat, org, cli, spcty):
        super().__init__('Consent-to-treatment', **{'pat':pat, 'org':org, 'cli':cli, 'spcty':spcty})
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params) or self.canActivate_3(*params)
    
    def canActivate_1(self, pat): # S2.3.9
        return {
            True for (subj1, role1) in hasActivated for (subj2, role2) in hasActivated if 
            role1.name == "Patient" and 
            role2.name == "Request-consent-to-treatment" and 
            subj1 == pat
        }
    
    def canActivate_2(self, ag): # S2.3.10
        return {
            True for (subj1, role1) in hasActivated for (subj2, role2) in hasActivated if 
            role1.name == "Agent" and 
            role2.name == "Request-consent-to-treatment" and 
            subj1 == ag and 
            role1.pat == self.pat and 
            role2.pat == self.pat
        }
    
    def canActivate_3(self, cli1): # S2.3.11
        return {
            True for (subj1, role1) in hasActivated for (subj2, role2) in hasActivated if 
            role1.name == "Spine-clinician" and 
            role2.name == "Request-consent-to-treatment" and 
            subj1 == cli1 and 
            role1.spcty == self.spcty and 
            role1.org == self.org and 
            role2.spcty == self.spcty and 
            role2.org == self.org and 
            canActivate(subj1, Treating_clinician(self.pat, role2.org, role2.spcty))
        }

class Request_consent_to_group_treatment(Role):
    def __init__(self, pat, org, group):
        super().__init__('Request-consent-to-group-treatment', **{'pat':pat, 'org':org, 'group':group})
    
    def canActivate(self, cli): # S2.4.1
        return {
            True for subj, role in hasActivated if 
            role.name == "Spine-clinician" and 
            role.org == self.org and 
            subj == cli and 
            canActivate(self.pat, Patient())
        }
    
    def canDeactivate(self, *params):
        return self.canDeactivate_1(*params) or self.canDeactivate_2(*params) or self.canDeactivate_3(*params) or self.canDeactivate_4(*params) or self.canDeactivate_5(*params)
    
    def canDeactivate_1(self, cli, cli_): # S2.4.2
        return {
            True for subj, role in hasActivated if 
            cli == cli_ and 
            role.name == "Spine-clinician" and 
            role.org == self.org and 
            subj == cli
        }
    
    def canDeactivate_2(self, pat, x): # S2.4.3
        return {
            True for subj, role in hasActivated if 
            role.name == "Patient" and 
            subj == pat
        }
    
    def canDeactivate_3(self, ag, x): # S2.4.4
        return {
            True for subj, role in hasActivated if 
            role.name == "Agent" and 
            role.pat == self.pat and 
            subj == ag
        }
    
    def canDeactivate_4(self, cli, x): # S2.4.5
        return {
            True for subj, role in hasActivated if 
            role.name == "Spine-clinician" and 
            role.org == self.org and 
            subj == cli and 
            canActivate(subj, General_practitioner(self.pat))
        }
    
    def canDeactivate_5(self, cli, x): # S2.4.6
        return {
            True for subj, role in hasActivated if 
            role.name == "Spine-clinician" and 
            role.org == self.org and 
            subj == cli and 
            canActivate(subj, ehr.ra.Workgroup_member(role.org, self.group, role.spcty))
        }
    
    def onDeactivate(self, subj):
        if other_consent_to_group_treatment_requests(subj, self.pat, self.org, self.group) == 0:
            deactivate(hasActivated, Wildcard(), Consent_to_group_treatment(self.pat, self.org, self.group))  # S2.4.12

def other_consent_to_group_treatment_requests(x, pat, org, group): # S2.4.8
    return len({
        True for subj, role in hasActivated if 
        role.name == "Request-consent-to-group-treatment" and 
        role.org == org and 
        role.pat == pat and 
        role.group == group and 
        x != subj
    })

class Consent_to_group_treatment(Role):
    def __init__(self, pat, org, group):
        super().__init__('Consent-to-group-treatment', **{'pat':pat, 'org':org, 'group':group})
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params) or self.canActivate_3(*params)
    
    def canActivate_1(self, pat): # S2.4.9
        return {
            True for (subj1, role1) in hasActivated for (subj2, role2) in hasActivated if 
            role1.name == "Patient" and 
            role2.name == "Request-consent-to-group-treatment" and 
            subj1 == pat
        }
    
    def canActivate_2(self, ag): # S2.4.10
        return {
            True for (subj1, role1) in hasActivated for (subj2, role2) in hasActivated if 
            role1.name == "Agent" and 
            role2.name == "Request-consent-to-group-treatment" and 
            subj1 == ag and 
            role1.pat == self.pat and 
            role2.pat == self.pat
        }
    
    def canActivate_3(self, cli1): # S2.4.11
        return {
            True for (subj1, role1) in hasActivated for (subj2, role2) in hasActivated if 
            role1.name == "Spine-clinician" and 
            role2.name == "Request-consent-to-group-treatment" and 
            subj1 == cli1 and 
            role1.org == self.org and 
            role2.org == self.org and 
            canActivate(subj1, Treating_clinician(self.pat, role2.org, role2.spcty))
        }

class Referrer(Role):
    def __init__(self, pat, org, cli2, spcty1):
        super().__init__('Referrer', **{'pat':pat, 'org':org, 'cli2':cli2, 'spcty1':spcty1})
    
    def canActivate(self, cli1): # S3.1.1
        return {
            True for subj, role in hasActivated if 
            role.name == "Spine-clinician" and 
            role.org == self.org and 
            subj == cli1 and 
            canActivate(subj, Treating_clinician(self.pat, role.org, role.spcty2))
        }
    
    def canDeactivate(self, *params):
        return self.canDeactivate_1(*params) or self.canDeactivate_2(*params)
    
    def canDeactivate_1(self, cli1, cli1_): # S3.1.2
        return (
            cli1 == cli1_
        )
    
    def canDeactivate_2(self, pat, cli1): # S3.1.3
        return (
            
        )

class Spine_emergency_clinician(Role):
    def __init__(self, org, pat):
        super().__init__('Spine-emergency-clinician', **{'org':org, 'pat':pat})
    
    def canActivate(self, cli): # S3.2.1
        return {
            True for subj, role in hasActivated if 
            role.name == "Spine-clinician" and 
            role.org == self.org and 
            subj == cli and 
            canActivate(self.pat, Patient())
        }
    
    def canDeactivate(self, cli, cli_): # S3.2.2
        return (
            cli == cli_
        )

class Treating_clinician(Role):
    def __init__(self, pat, org, spcty):
        super().__init__('Treating-clinician', **{'pat':pat, 'org':org, 'spcty':spcty})
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params) or self.canActivate_3(*params) or self.canActivate_4(*params)
    
    def canActivate_1(self, cli): # S3.3.1
        return {
            True for subj, role in hasActivated if 
            role.name == "Consent-to-treatment" and 
            role.spcty == self.spcty and 
            role.org == self.org and 
            role.pat == self.pat and 
            role.cli == cli
        }
    
    def canActivate_2(self, cli): # S3.3.2
        return {
            True for subj, role in hasActivated if 
            role.name == "Spine-emergency-clinician" and 
            role.org == self.org and 
            role.pat == self.pat and 
            subj == cli and 
            self.spcty == "A_and_E"
        }
    
    def canActivate_3(self, cli): # S3.3.3
        return {
            True for subj, role in hasActivated if 
            role.name == "Referrer" and 
            role.spcty == self.spcty and 
            role.org == self.org and 
            role.pat == self.pat and 
            role.cli == cli and 
            canActivate(role.cli, Spine_clinician(Wildcard(), role.org, role.spcty))
        }
    
    def canActivate_4(self, cli): # S3.3.4
        return (
            canActivate(cli, Group_treating_clinician(self.pat, Wildcard(), self.org, Wildcard(), self.spcty))
        )

class General_practitioner(Role):
    def __init__(self, pat):
        super().__init__('General-practitioner', **{'pat':pat})
    
    def canActivate(self, cli): # S3.3.5
        #S3.3.5 todo: unable to bind vars {'spcty'} in constraint spcty == "GP"
        #canActivate(cli, Treating-clinician(pat, org, spcty))
        #spcty = "GP"
        pass

class Group_treating_clinician(Role):
    def __init__(self, pat, ra, org, group, spcty):
        super().__init__('Group-treating-clinician', **{'pat':pat, 'ra':ra, 'org':org, 'group':group, 'spcty':spcty})
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params)
    
    def canActivate_1(self, cli): # S3.4.1
        return {
            True for subj, role in hasActivated if 
            role.name == "Consent-to-group-treatment" and 
            role.org == self.org and 
            role.pat == self.pat and 
            role.group == self.group and 
            canActivate(cli, ehr.ra.Workgroup_member(role.org, role.group, self.spcty)) and 
            canActivate(self.ra, Registration_authority())
        }
    
    def canActivate_2(self, cli): # S3.4.2
        return {
            True for subj, role in hasActivated if 
            role.name == "Consent-to-group-treatment" and 
            role.org == self.org and 
            role.pat == self.pat and 
            role.group == self.group and 
            canActivate(cli, ehr.ra.Workgroup_member(role.org, role.group, self.spcty)) and 
            canActivate(self.ra, Registration_authority())
        }

class Concealed_by_spine_clinician(Role):
    def __init__(self, pat, ids, start, end):
        super().__init__('Concealed-by-spine-clinician', **{'pat':pat, 'ids':ids, 'start':start, 'end':end})
    
    def canActivate(self, cli): # S4.1.1
        return {
            True for subj, role in hasActivated if 
            role.name == "Spine-clinician" and 
            subj == cli and 
            canActivate(subj, Treating_clinician(self.pat, role.org, role.spcty))
        }
    
    def canDeactivate(self, *params):
        return self.canDeactivate_1(*params) or self.canDeactivate_2(*params) or self.canDeactivate_3(*params)
    
    def canDeactivate_1(self, cli, cli_): # S4.1.2
        return {
            True for subj, role in hasActivated if 
            cli == cli_ and 
            role.name == "Spine-clinician" and 
            subj == cli
        }
    
    def canDeactivate_2(self, cli, cli2): # S4.1.3
        return {
            True for subj, role in hasActivated if 
            role.name == "Spine-clinician" and 
            subj == cli and 
            canActivate(subj, General_practitioner(self.pat))
        }
    
    def canDeactivate_3(self, cli1, cli2): # S4.1.4
        return {
            True for (subj1, role1) in hasActivated for (subj2, role2) in hasActivated if 
            role1.name == "Spine-clinician" and 
            role2.name == "Consent-to-group-treatment" and 
            subj1 == cli1 and 
            canActivate(subj1, Group_treating_clinician(self.pat, role2.ra, role2.org, Wildcard(), role2.spcty1)) and 
            canActivate(cli2, Group_treating_clinician(self.pat, role2.ra, role2.org, Wildcard(), Wildcard()))
        }

def count_concealed_by_spine_clinician(pat, id): # S4.1.6
    return len({
        True for subj, role in hasActivated if 
        role.name == "Concealed-by-spine-clinician" and 
        role.pat == pat and 
        id in role.ids and 
        Current_time() in vrange(role.start, role.end)
    })

class Conceal_request(Role):
    def __init__(self, what, who, start, end):
        super().__init__('Conceal-request', **{'what':what, 'who':who, 'start':start, 'end':end})
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params)
    
    def canActivate_1(self, pat): # S4.2.1
        #S4.2.1 todo: could not translate constraint: (what,who) = ((pat,ids,orgs,authors,subjects,from-time,to-time),(orgs1,readers1,spctys1))
        #hasActivated(pat, Patient())
        #count-conceal-requests(n, pat)
        #(what,who) = ((pat,ids,orgs,authors,subjects,from-time,to-time),(orgs1,readers1,spctys1))
        #n < 100
        pass
    
    def canActivate_2(self, ag): # S4.2.2
        #S4.2.2 todo: could not translate constraint: (what,who) = ((pat,ids,orgs,authors,subjects,from-time,to-time),(orgs1,readers1,spctys1))
        #hasActivated(ag, Agent(pat))
        #count-conceal-requests(n, pat)
        #(what,who) = ((pat,ids,orgs,authors,subjects,from-time,to-time),(orgs1,readers1,spctys1))
        #n < 100
        pass
    
    def canDeactivate(self, *params):
        return self.canDeactivate_1(*params) or self.canDeactivate_2(*params) or self.canDeactivate_3(*params)
    
    def canDeactivate_1(self, pat, x): # S4.2.3
        return {
            True for subj, role in hasActivated if 
            role.name == "Patient" and 
            subj == pat and 
            pi7_1(self.what) == subj
        }
    
    def canDeactivate_2(self, ag, x): # S4.2.4
        return {
            True for subj, role in hasActivated if 
            role.name == "Agent" and 
            subj == ag and 
            pi7_1(self.what) == role.pat
        }
    
    def canDeactivate_3(self, cli, x): # S4.2.5
        #S4.2.5 todo: unable to bind vars {'pat'} in constraint pi7_1(self.what) == pat
        #hasActivated(cli, Spine-clinician(ra, org, spcty))
        #canActivate(cli, General-practitioner(pat))
        #pi7_1(what) = pat
        pass
    
    def onDeactivate(self, subj):
        deactivate(hasActivated, Wildcard(), Concealed_by_spine_patient(self.what, self.who, self.start, self.end))  # S4.2.11
        

def count_conceal_requests(pat): # S4.2.7
    #S4.2.7 todo: could not translate constraint: (what,who) = ((pat,ids,orgs,authors,subjects,from-time,to-time),(orgs1,readers1,spctys1))
    #hasActivated(x, Conceal-request(y))
    #(what,who) = ((pat,ids,orgs,authors,subjects,from-time,to-time),(orgs1,readers1,spctys1))
    #y = (what,who,start,end)
    pass

class Concealed_by_spine_patient(Role):
    def __init__(self, what, who, start, end):
        super().__init__('Concealed-by-spine-patient', **{'what':what, 'who':who, 'start':start, 'end':end})
    
    def canActivate(self, cli): # S4.2.8
        return {
            True for (subj1, role1) in hasActivated for (subj2, role2) in hasActivated if 
            role1.name == "Spine-clinician" and 
            role2.name == "Conceal-request" and 
            subj1 == cli and 
            canActivate(subj1, Treating_clinician(Wildcard(), role2.org, role2.spcty))
        }
    
    def canDeactivate(self, *params):
        return self.canDeactivate_1(*params) or self.canDeactivate_2(*params)
    
    def canDeactivate_1(self, cli, cli_): # S4.2.9
        return {
            True for subj, role in hasActivated if 
            cli == cli_ and 
            role.name == "Spine-clinician" and 
            subj == cli
        }
    
    def canDeactivate_2(self, cli1, cli2): # S4.2.10
        return {
            True for subj, role in hasActivated if 
            role.name == "Spine-clinician" and 
            subj == cli1 and 
            canActivate(subj, ehr.ra.Group_treating_clinician(Wildcard(), role.ra, role.org, Wildcard(), role.spcty1)) and 
            canActivate(cli2, ehr.ra.Group_treating_clinician(Wildcard(), role.ra, role.org, Wildcard(), Wildcard()))
        }

def count_concealed_by_spine_patient(a, b): # S4.2.12
    #S4.2.12 todo: could not translate constraint: a = (pat,id)
    #hasActivated(x, Concealed-by-spine-patient(what, who, start, end))
    #a = (pat,id)
    #b = (org,reader,spcty)
    #what = (pat,ids,orgs,authors,subjects,from-time,to-time)
    #whom = (orgs1,readers1,spctys1)
    #Get-spine-record-org(pat, id) in orgs
    #Get-spine-record-author(pat, id) in authors
    #sub in Get-spine-record-subjects(pat, id)
    #sub in subjects
    #Get-spine-record-time(pat, id) in [from-time, to-time]
    #id in ids
    #org in orgs1
    #reader in readers1
    #spcty in spctys1
    #Current-time() in [start, end]
    #Get-spine-record-third-parties(pat, id) = emptyset
    #"non-clinical" notin Get-spine-record-subjects(pat, id)
    pass

class Authenticated_express_consent(Role):
    def __init__(self, pat, cli):
        super().__init__('Authenticated-express-consent', **{'pat':pat, 'cli':cli})
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params) or self.canActivate_3(*params)
    
    def canActivate_1(self, pat): # S4.3.1
        return {
            True for subj, role in hasActivated if 
            role.name == "Patient" and 
            subj == pat and 
            count_authenticated_express_consent(subj) < 100
        }
    
    def canActivate_2(self, ag): # S4.3.2
        return {
            True for subj, role in hasActivated if 
            role.name == "Agent" and 
            role.pat == self.pat and 
            subj == ag and 
            count_authenticated_express_consent(role.pat) < 100
        }
    
    def canActivate_3(self, cli1): # S4.3.3
        return {
            True for subj, role in hasActivated if 
            role.name == "Spine-clinician" and 
            subj == cli1 and 
            canActivate(subj, General_practitioner(self.pat))
        }
    
    def canDeactivate(self, *params):
        return self.canDeactivate_1(*params) or self.canDeactivate_2(*params) or self.canDeactivate_3(*params)
    
    def canDeactivate_1(self, pat, x): # S4.3.4
        return {
            True for subj, role in hasActivated if 
            role.name == "Patient" and 
            subj == pat
        }
    
    def canDeactivate_2(self, ag, x): # S4.3.5
        return {
            True for subj, role in hasActivated if 
            role.name == "Agent" and 
            role.pat == self.pat and 
            subj == ag
        }
    
    def canDeactivate_3(self, cli1, x): # S4.3.6
        return {
            True for subj, role in hasActivated if 
            role.name == "Spine-clinician" and 
            subj == cli1 and 
            canActivate(subj, General_practitioner(self.pat))
        }

def count_authenticated_express_consent(pat): # S4.3.8
    return len({
        True for subj, role in hasActivated if 
        role.name == "Authenticated-express-consent" and 
        role.pat == pat
    })

class Add_spine_record_item(Role):
    def __init__(self, pat):
        super().__init__('Add-spine-record-item', **{'pat':pat})
    
    def permits(self, cli): # S5.1.1
        return {
            True for subj, role in hasActivated if 
            role.name == "Spine-clinician" and 
            subj == cli and 
            canActivate(subj, Treating_clinician(self.pat, role.org, role.spcty))
        }


class Annotate_spine_record_item(Role):
    def __init__(self, pat, id):
        super().__init__('Annotate-spine-record-item', **{'pat':pat, 'id':id})
    
    def permits(self, subj):
        return self.permits_1(subj) or self.permits_2(subj) or self.permits_3(subj)
    
    def permits_1(self, pat): # S5.1.2
        return {
            True for subj, role in hasActivated if 
            role.name == "Patient" and 
            subj == pat
        }
    
    def permits_2(self, ag): # S5.1.3
        return {
            True for subj, role in hasActivated if 
            role.name == "Agent" and 
            role.pat == self.pat and 
            subj == ag
        }
    
    def permits_3(self, pat): # S5.1.4
        return {
            True for subj, role in hasActivated if 
            role.name == "Spine-clinician" and 
            canActivate(subj, Treating_clinician(pat, role.org, role.spcty))
        }


class Get_spine_record_item_ids(Role):
    def __init__(self, pat):
        super().__init__('Get-spine-record-item-ids', **{'pat':pat})
    
    def permits(self, subj):
        return self.permits_1(subj) or self.permits_2(subj) or self.permits_3(subj)
    
    def permits_1(self, pat): # S5.2.1
        return {
            True for subj, role in hasActivated if 
            role.name == "Patient" and 
            subj == pat
        }
    
    def permits_2(self, ag): # S5.2.2
        return {
            True for subj, role in hasActivated if 
            role.name == "Agent" and 
            role.pat == self.pat and 
            subj == ag
        }
    
    def permits_3(self, cli): # S5.2.3
        return {
            True for subj, role in hasActivated if 
            role.name == "Spine-clinician" and 
            subj == cli and 
            canActivate(subj, Treating_clinician(self.pat, role.org, role.spcty))
        }


class Read_spine_record_item(Role):
    def __init__(self, pat, id):
        super().__init__('Read-spine-record-item', **{'pat':pat, 'id':id})
    
    def permits(self, subj):
        return self.permits_1(subj) or self.permits_2(subj) or self.permits_3(subj) or self.permits_4(subj) or self.permits_5(subj)
    
    def permits_1(self, pat): # S5.3.1
        #S5.3.1 todo: unbound vars {'a', 'b'} in count-concealed-by-spine-patient(n, a, b)
        #hasActivated(pat, Patient())
        #hasActivated(x, One-off-consent(pat))
        #count-concealed-by-spine-patient(n, a, b)
        #count-concealed-by-spine-clinician(m, pat, id)
        #third-party-consent(consenters, pat, id)
        #n = 0
        #m = 0
        #a = (pat,id)
        #b = ("No-org",pat,"No-spcty")
        #Get-spine-record-third-parties(pat, id) subseteq consenters
        pass
    
    def permits_2(self, ag): # S5.3.2
        #S5.3.2 todo: unbound vars {'a', 'b'} in count-concealed-by-spine-patient(n, a, b)
        #hasActivated(ag, Agent(pat))
        #hasActivated(x, One-off-consent(pat))
        #count-concealed-by-spine-patient(n, a, b)
        #count-concealed-by-spine-clinician(m, pat, id)
        #third-party-consent(consenters, pat, id)
        #n = 0
        #m = 0
        #a = (pat,id)
        #b = ("No-org",ag,"No-spcty")
        #Get-spine-record-third-parties(pat, id) subseteq consenters
        pass
    
    def permits_3(self, cli): # S5.3.3
        return {
            True for (subj1, role1) in hasActivated for (subj2, role2) in hasActivated if 
            role1.name == "Spine-clinician" and 
            role2.name == "One-off-consent" and 
            subj1 == cli and 
            Get_spine_record_org(self.pat, self.id) == role2.org and 
            Get_spine_record_author(self.pat, self.id) == subj1
        }
    
    def permits_4(self, cli): # S5.3.4
        #S5.3.4 todo: unbound vars {'a', 'b'} in count-concealed-by-spine-patient(n, a, b)
        #hasActivated(cli, Spine-clinician(ra, org, spcty))
        #hasActivated(x, One-off-consent(pat))
        #canActivate(cli, Treating-clinician(pat, org, spcty))
        #count-concealed-by-spine-patient(n, a, b)
        #n = 0
        #a = (pat,id)
        #b = (org,cli,spcty)
        #Get-spine-record-subjects(pat, id) subseteq Permitted-subjects(spcty)
        pass
    
    def permits_5(self, cli): # S5.3.5
        #S5.3.5 todo: Not implemented: 3 hasAcs in a rule.
        #hasActivated(cli, Spine-clinician(ra, org, spcty))
        #hasActivated(x, One-off-consent(pat))
        #canActivate(cli, Treating-clinician(pat, org, spcty))
        #hasActivated(y, Authenticated-express-consent(pat, cli))
        #Get-spine-record-subjects(pat, id) subseteq Permitted-subjects(spcty)
        pass


class Force_read_spine_record_item(Role):
    def __init__(self, pat, id):
        super().__init__('Force-read-spine-record-item', **{'pat':pat, 'id':id})
    
    def permits(self, cli): # S5.3.6
        return {
            True for subj, role in hasActivated if 
            role.name == "Spine-clinician" and 
            subj == cli and 
            canActivate(subj, Treating_clinician(self.pat, role.org, role.spcty))
        }

# Credential Request Restrictions
# ===============================
# These rules determine if certain predicates can be 
# invoked, such as canActivate or hasActivated.

# They restrict who can invoke such predicates.
# These rules have not been translated.

# Restrictions on canActivate

# For the Role 'Agent'
# 
# 'S1.4.6'
# canReqCred(ag, "Spine".canActivate(ag, Agent(pat))) <-
# 	hasActivated(ag, Agent(pat))
# 
# 'S1.4.7'
# canReqCred(org, "Spine".canActivate(ag, Agent(pat))) <-
# 	ra.hasActivated(x, NHS-health-org-cert(org, start, end)), canActivate(ra, Registration-authority()), Current-time() in [start, end]
# 
# 'S1.4.8'
# canReqCred(org, "Spine".canActivate(ag, Agent(pat))) <-
# 	org@ra.hasActivated(x, NHS-health-org-cert(org, start, end)), canActivate(ra, Registration-authority()), Current-time() in [start, end]

# Restrictions on hasActivate

