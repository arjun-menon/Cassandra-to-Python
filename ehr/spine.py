from cassandra import *
from datetime import datetime

class Spine_clinician(Role):
    def __init__(self, ra, org, spcty):
        super().__init__('Spine-clinician', ['ra', 'org', 'spcty']) 
        self.ra, self.org, self.spcty = ra, org, spcty
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params)
    
    def canActivate_1(self, cli): # S1.1.1
        return {
        	1 for subj, role in hasActivated if 
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
        	1 for subj, role in hasActivated if 
        	role.name == "NHS-clinician-cert" and 
        	role.spcty == self.spcty and 
        	role.org == self.org and 
        	role.cli == cli and 
        	canActivate(self.ra, Registration_authority()) and 
        	Current_time() in vrange(role.start, role.end) and 
        	no_main_role_active(role.cli)
        }
    
    #untranslated:
    #'S1.1.3'
    #canDeactivate(cli, cli, Spine-clinician(ra, org, spcty)) <-
    #	
    
    #untranslated:
    #'S3.2.3'
    #isDeactivated(x, Spine-emergency-clinician(org, pat)) <-
    #	isDeactivated(x, Spine-clinician(ra, org, spcty))

def count_spine_clinician_activations(user): # S1.1.4
    return len({
    	1 for subj, role in hasActivated if 
    	role.name == "Spine-clinician" and 
    	subj == user
    })

class Spine_admin(Role):
    def __init__(self):
        super().__init__('Spine-admin', []) 
    
    def canActivate(self, adm): # S1.2.1
        return {
        	1 for subj, role in hasActivated if 
        	role.name == "Register-spine-admin" and 
        	role.adm == adm and 
        	no_main_role_active(role.adm)
        }
    
    #untranslated:
    #'S1.2.2'
    #canDeactivate(adm, adm, Spine-admin()) <-
    #	

def count_spine_admin_activations(user): # S1.2.4
    return len({
    	1 for subj, role in hasActivated if 
    	role.name == "Spine-admin" and 
    	subj == user
    })

class Register_spine_admin(Role):
    def __init__(self, adm2):
        super().__init__('Register-spine-admin', ['adm2']) 
        self.adm2 = adm2
    
    def canActivate(self, adm): # S1.2.5
        return {
        	1 for subj, role in hasActivated if 
        	role.name == "Spine-admin" and 
        	subj == adm and 
        	spine_admin_regs(self.adm2) == 0
        }
    
    #untranslated:
    #'S1.2.6'
    #canDeactivate(adm, x, Register-spine-admin(adm2)) <-
    #	hasActivated(adm, Spine-admin())
    
    #untranslated:
    #'S1.2.3'
    #isDeactivated(adm, Spine-admin()) <-
    #	isDeactivated(x, Register-spine-admin(adm))

def spine_admin_regs(adm): # S1.2.7
    return len({
    	1 for subj, role in hasActivated if 
    	role.name == "Register-spine-admin" and 
    	role.adm == adm
    })

class Patient(Role):
    def __init__(self):
        super().__init__('Patient', []) 
    
    def canActivate(self, pat): # S1.3.1
        #todo: Not implemented: 2 hasAcs in a rule.
        #hasActivated(x, Register-patient(pat))
        #no-main-role-active(pat)
        #"PDS"@"PDS".hasActivated(y, Register-patient(pat))
        pass
    
    #untranslated:
    #'S1.3.2'
    #canDeactivate(pat, pat, Patient()) <-
    #	

def count_patient_activations(user): # S1.3.4
    return len({
    	1 for subj, role in hasActivated if 
    	role.name == "Patient" and 
    	subj == user
    })

class Register_patient(Role):
    def __init__(self, pat):
        super().__init__('Register-patient', ['pat']) 
        self.pat = pat
    
    def canActivate(self, adm): # S1.3.5
        return {
        	1 for subj, role in hasActivated if 
        	role.name == "Spine-admin" and 
        	subj == adm and 
        	patient_regs(self.pat) == 0
        }
    
    #untranslated:
    #'S1.3.6'
    #canDeactivate(adm, x, Register-patient(pat)) <-
    #	hasActivated(adm, Spine-admin())
    
    #untranslated:
    #'S1.3.3'
    #isDeactivated(pat, Patient()) <-
    #	isDeactivated(x, Register-patient(pat))
    
    #untranslated:
    #'S1.4.13'
    #isDeactivated(x, Register-agent(agent, pat)) <-
    #	isDeactivated(y, Register-patient(pat))
    
    #untranslated:
    #'S2.1.7'
    #isDeactivated(x, One-off-consent(pat)) <-
    #	isDeactivated(y, Register-patient(pat))
    
    #untranslated:
    #'S2.2.8'
    #isDeactivated(x, Request-third-party-consent(y, pat, id)) <-
    #	isDeactivated(z, Register-patient(pat))
    
    #untranslated:
    #'S2.3.7'
    #isDeactivated(x, Request-consent-to-treatment(pat, org, cli, spcty)) <-
    #	isDeactivated(y, Register-patient(pat))
    
    #untranslated:
    #'S2.4.7'
    #isDeactivated(x, Request-consent-to-group-treatment(pat, org, group)) <-
    #	isDeactivated(y, Register-patient(pat))
    
    #untranslated:
    #'S3.1.4'
    #isDeactivated(pat, Referrer(pat, org, cli2, spcty1)) <-
    #	isDeactivated(x, Register-patient(pat))
    
    #untranslated:
    #'S3.2.4'
    #isDeactivated(x, Spine-emergency-clinician(org, pat)) <-
    #	isDeactivated(y, Register-patient(pat))
    
    #untranslated:
    #'S4.1.5'
    #isDeactivated(x, Concealed-by-spine-clinician(pat, ids, start, end)) <-
    #	isDeactivated(y, Register-patient(pat))
    
    #untranslated:
    #'S4.2.6'
    #isDeactivated(x, Conceal-request(what, whom, start, end)) <-
    #	isDeactivated(y, Register-patient(pat)), pi7_1(what) = pat
    
    #untranslated:
    #'S4.3.7'
    #isDeactivated(x, Authenticated-express-consent(pat, cli)) <-
    #	isDeactivated(y, Register-patient(pat))

def patient_regs(pat): # S1.3.7
    return len({
    	1 for subj, role in hasActivated if 
    	role.name == "Register-patient" and 
    	role.pat == pat
    })

class Agent(Role):
    def __init__(self, pat):
        super().__init__('Agent', ['pat']) 
        self.pat = pat
    
    def canActivate(self, ag): # S1.4.1
        #todo: Not implemented: 2 hasAcs in a rule.
        #hasActivated(x, Register-agent(ag, pat))
        #"PDS"@"PDS".hasActivated(y, Register-patient(ag))
        #no-main-role-active(ag)
        pass
    
    #untranslated:
    #'S1.4.2'
    #canDeactivate(ag, ag, Agent(pat)) <-
    #	

def other_agent_regs(x, ag, pat): # S1.4.4
    return len({
    	1 for subj, role in hasActivated if 
    	role.name == "Register-agent" and 
    	role.pat == pat and 
    	role.ag == ag and 
    	x != subj
    })

def count_agent_activations(user): # S1.4.5
    return len({
    	1 for subj, role in hasActivated if 
    	role.name == "Agent" and 
    	subj == user
    })

#untranslated:
#'S1.4.6'
#canReqCred(ag, "Spine".canActivate(ag, Agent(pat))) <-
#	hasActivated(ag, Agent(pat))

#untranslated:
#'S1.4.7'
#canReqCred(org, "Spine".canActivate(ag, Agent(pat))) <-
#	ra.hasActivated(x, NHS-health-org-cert(org, start, end)), canActivate(ra, Registration-authority()), Current-time() in [start, end]

#untranslated:
#'S1.4.8'
#canReqCred(org, "Spine".canActivate(ag, Agent(pat))) <-
#	org@ra.hasActivated(x, NHS-health-org-cert(org, start, end)), canActivate(ra, Registration-authority()), Current-time() in [start, end]

class Register_agent(Role):
    def __init__(self, agent, pat):
        super().__init__('Register-agent', ['agent', 'pat']) 
        self.agent, self.pat = agent, pat
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params)
    
    def canActivate_1(self, pat): # S1.4.9
        return {
        	1 for subj, role in hasActivated if 
        	role.name == "Patient" and 
        	subj == pat and 
        	agent_regs(subj) < 3
        }
    
    def canActivate_2(self, cli): # S1.4.10
        return {
        	1 for subj, role in hasActivated if 
        	role.name == "Spine-clinician" and 
        	subj == cli and 
        	canActivate(subj, General_practitioner(self.pat))
        }
    
    #untranslated:
    #'S1.4.11'
    #canDeactivate(pat, pat, Register-agent(agent, pat)) <-
    #	hasActivated(pat, Patient())
    
    #untranslated:
    #'S1.4.12'
    #canDeactivate(cli, x, Register-agent(agent, pat)) <-
    #	hasActivated(cli, Spine-clinician(ra, org, spcty)), canActivate(cli, General-practitioner(pat))
    
    #untranslated:
    #'S1.4.3'
    #isDeactivated(ag, Agent(pat)) <-
    #	isDeactivated(x, Register-agent(ag, pat)), other-agent-regs(n, x, ag, pat), n = 0

def agent_regs(pat): # S1.4.14
    return len({
    	1 for subj, role in hasActivated if 
    	role.name == "Register-agent" and 
    	role.pat == pat and 
    	subj == role.pat
    })

class Registration_authority(Role):
    def __init__(self):
        super().__init__('Registration-authority', []) 
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params)
    
    def canActivate_1(self, ra): # S1.5.1
        return {
        	1 for subj, role in hasActivated if 
        	role.name == "NHS-registration-authority" and 
        	role.ra == ra and 
        	Current_time() in vrange(role.start, role.end)
        }
    
    def canActivate_2(self, ra): # S1.5.2
        return {
        	1 for subj, role in hasActivated if 
        	role.name == "NHS-registration-authority" and 
        	role.ra == ra and 
        	Current_time() in vrange(role.start, role.end)
        }

#untranslated:
#'S1.5.3'
#no-main-role-active(user) <-
#	count-agent-activations(n, user), count-spine-clinician-activations(n, user), count-spine-admin-activations(n, user), count-patient-activations(n, user), count-third-party-activations(n, user), n = 0

class One_off_consent(Role):
    def __init__(self, pat):
        super().__init__('One-off-consent', ['pat']) 
        self.pat = pat
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params) or self.canActivate_3(*params)
    
    def canActivate_1(self, pat): # S2.1.1
        return {
        	1 for subj, role in hasActivated if 
        	role.name == "Patient" and 
        	subj == pat
        }
    
    def canActivate_2(self, ag): # S2.1.2
        return {
        	1 for subj, role in hasActivated if 
        	role.name == "Agent" and 
        	role.pat == self.pat and 
        	subj == ag
        }
    
    def canActivate_3(self, cli): # S2.1.3
        return {
        	1 for subj, role in hasActivated if 
        	role.name == "Spine-clinician" and 
        	subj == cli and 
        	canActivate(subj, Treating_clinician(self.pat, role.org, role.spcty))
        }
    
    #untranslated:
    #'S2.1.4'
    #canDeactivate(pat, x, One-off-consent(pat)) <-
    #	hasActivated(pat, Patient())
    
    #untranslated:
    #'S2.1.5'
    #canDeactivate(ag, x, One-off-consent(pat)) <-
    #	hasActivated(ag, Agent(pat))
    
    #untranslated:
    #'S2.1.6'
    #canDeactivate(cli, x, One-off-consent(pat)) <-
    #	hasActivated(cli, Spine-clinician(ra, org, spcty)), canActivate(cli, Treating-clinician(pat, org, spcty))

class Request_third_party_consent(Role):
    def __init__(self, x, pat, id):
        super().__init__('Request-third-party-consent', ['x', 'pat', 'id']) 
        self.x, self.pat, self.id = x, pat, id
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params) or self.canActivate_3(*params)
    
    def canActivate_1(self, pat): # S2.2.1
        return {
        	1 for subj, role in hasActivated if 
        	role.name == "Patient" and 
        	subj == pat and 
        	self.x in Get_spine_record_third_parties(subj, self.id)
        }
    
    def canActivate_2(self, ag): # S2.2.2
        return {
        	1 for subj, role in hasActivated if 
        	role.name == "Agent" and 
        	role.pat == self.pat and 
        	subj == ag and 
        	self.x in Get_spine_record_third_parties(role.pat, self.id)
        }
    
    def canActivate_3(self, cli): # S2.2.3
        return {
        	1 for subj, role in hasActivated if 
        	role.name == "Spine-clinician" and 
        	subj == cli and 
        	canActivate(subj, Treating_clinician(self.pat, role.org, role.spcty)) and 
        	self.x in Get_spine_record_third_parties(self.pat, self.id)
        }
    
    #untranslated:
    #'S2.2.4'
    #canDeactivate(pat, y, Request-third-party-consent(x, pat, id)) <-
    #	hasActivated(pat, Patient())
    
    #untranslated:
    #'S2.2.5'
    #canDeactivate(ag, y, Request-third-party-consent(x, pat, id)) <-
    #	hasActivated(pat, Agent(pat))
    
    #untranslated:
    #'S2.2.6'
    #canDeactivate(cli, y, Request-third-party-consent(x, pat, id)) <-
    #	hasActivated(cli, Spine-clinician(ra, org, spcty))
    
    #untranslated:
    #'S2.2.7'
    #canDeactivate(x, y, Request-third-party-consent(x, pat, id)) <-
    #	hasActivated(x, Third-party())
    
    #untranslated:
    #'S2.2.12'
    #isDeactivated(x, Third-party()) <-
    #	isDeactivated(y, Request-third-party-consent(x, pat, id)), other-third-party-consent-requests(n, y, x), n = 0
    
    #untranslated:
    #'S2.2.16'
    #isDeactivated(x, Third-party-consent(x, pat, id)) <-
    #	isDeactivated(y, Request-third-party-consent(x, pat, id)), other-third-party-consent-requests(n, y, x), n = 0

def other_third_party_consent_requests(y, z): # S2.2.9
    return len({
    	1 for subj, role in hasActivated if 
    	role.name == "Request-third-party-consent" and 
    	role.z == z and 
    	subj != y
    })

class Third_party(Role):
    def __init__(self):
        super().__init__('Third-party', []) 
    
    def canActivate(self, x): # S2.2.10
        #todo: Not implemented: 2 hasAcs in a rule.
        #hasActivated(y, Request-third-party-consent(x, pat, id))
        #no-main-role-active(x)
        #"PDS"@"PDS".hasActivated(z, Register-patient(x))
        pass
    
    #untranslated:
    #'S2.2.11'
    #canDeactivate(x, x, Third-party()) <-
    #	

def count_third_party_activations(user): # S2.2.13
    return len({
    	1 for subj, role in hasActivated if 
    	role.name == "Third-party" and 
    	subj == user
    })

class Third_party_consent(Role):
    def __init__(self, x, pat, id):
        super().__init__('Third-party-consent', ['x', 'pat', 'id']) 
        self.x, self.pat, self.id = x, pat, id
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params)
    
    def canActivate_1(self, x): # S2.2.14
        #todo: Not implemented: 2 hasAcs in a rule.
        #hasActivated(x, Third-party())
        #hasActivated(y, Request-third-party-consent(x, pat, id))
        pass
    
    def canActivate_2(self, cli): # S2.2.15
        #todo: Not implemented: 2 hasAcs in a rule.
        #hasActivated(cli, Spine-clinician(ra, org, spcty))
        #canActivate(cli, Treating-clinician(pat, org, spcty))
        #hasActivated(y, Request-third-party-consent(x, pat, id))
        pass

#untranslated:
#'S2.2.17'
#third-party-consent(group<consenter>, pat, id) <-
#	hasActivated(x, Third-party-consent(consenter, pat, id))

class Request_consent_to_treatment(Role):
    def __init__(self, pat, org2, cli2, spcty2):
        super().__init__('Request-consent-to-treatment', ['pat', 'org2', 'cli2', 'spcty2']) 
        self.pat, self.org2, self.cli2, self.spcty2 = pat, org2, cli2, spcty2
    
    def canActivate(self, cli1): # S2.3.1
        return {
        	1 for subj, role in hasActivated if 
        	role.name == "Spine-clinician" and 
        	subj == cli1 and 
        	canActivate(self.cli2, Spine_clinician(Wildcard(), self.org2, self.spcty2)) and 
        	canActivate(self.pat, Patient())
        }
    
    #untranslated:
    #'S2.3.2'
    #canDeactivate(cli1, cli1, Request-consent-to-treatment(pat, org2, cli2, spcty2)) <-
    #	hasActivated(cli1, Spine-clinician(ra1, org1, spcty1))
    
    #untranslated:
    #'S2.3.3'
    #canDeactivate(cli2, cli1, Request-consent-to-treatment(pat, org2, cli2, spcty2)) <-
    #	hasActivated(cli2, Spine-clinician(ra2, org2, spcty2))
    
    #untranslated:
    #'S2.3.4'
    #canDeactivate(pat, x, Request-consent-to-treatment(pat, org, cli, spcty)) <-
    #	hasActivated(pat, Patient())
    
    #untranslated:
    #'S2.3.5'
    #canDeactivate(ag, x, Request-consent-to-treatment(pat, org, cli, spcty)) <-
    #	hasActivated(ag, Agent(pat))
    
    #untranslated:
    #'S2.3.6'
    #canDeactivate(cli, x, Request-consent-to-treatment(pat, org, cli2, spcty)) <-
    #	hasActivated(cli, Spine-clinician(ra, org, spcty)), canActivate(cli, General-practitioner(pat))
    
    #untranslated:
    #'S2.3.12'
    #isDeactivated(x, Consent-to-treatment(pat, org, cli, spcty)) <-
    #	isDeactivated(y, Request-consent-to-treatment(pat, org, cli, spcty)), other-consent-to-treatment-requests(n, y, pat, org, cli, spcty), n = 0

def other_consent_to_treatment_requests(x, pat, org, cli, spcty): # S2.3.8
    return len({
    	1 for subj, role in hasActivated if 
    	role.name == "Request-consent-to-treatment" and 
    	role.spcty == spcty and 
    	role.org == org and 
    	role.pat == pat and 
    	role.cli == cli and 
    	x != subj
    })

class Consent_to_treatment(Role):
    def __init__(self, pat, org, cli, spcty):
        super().__init__('Consent-to-treatment', ['pat', 'org', 'cli', 'spcty']) 
        self.pat, self.org, self.cli, self.spcty = pat, org, cli, spcty
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params) or self.canActivate_3(*params)
    
    def canActivate_1(self, pat): # S2.3.9
        #todo: Not implemented: 2 hasAcs in a rule.
        #hasActivated(pat, Patient())
        #hasActivated(x, Request-consent-to-treatment(pat, org, cli, spcty))
        pass
    
    def canActivate_2(self, ag): # S2.3.10
        #todo: Not implemented: 2 hasAcs in a rule.
        #hasActivated(ag, Agent(pat))
        #hasActivated(x, Request-consent-to-treatment(pat, org, cli, spcty))
        pass
    
    def canActivate_3(self, cli1): # S2.3.11
        #todo: Not implemented: 2 hasAcs in a rule.
        #hasActivated(cli1, Spine-clinician(ra, org, spcty))
        #canActivate(cli1, Treating-clinician(pat, org, spcty))
        #hasActivated(x, Request-consent-to-treatment(pat, org, cli2, spcty))
        pass

class Request_consent_to_group_treatment(Role):
    def __init__(self, pat, org, group):
        super().__init__('Request-consent-to-group-treatment', ['pat', 'org', 'group']) 
        self.pat, self.org, self.group = pat, org, group
    
    def canActivate(self, cli): # S2.4.1
        return {
        	1 for subj, role in hasActivated if 
        	role.name == "Spine-clinician" and 
        	role.org == self.org and 
        	subj == cli and 
        	canActivate(self.pat, Patient())
        }
    
    #untranslated:
    #'S2.4.2'
    #canDeactivate(cli, cli, Request-consent-to-group-treatment(pat, org, group)) <-
    #	hasActivated(cli, Spine-clinician(ra, org, spcty))
    
    #untranslated:
    #'S2.4.3'
    #canDeactivate(pat, x, Request-consent-to-group-treatment(pat, org, group)) <-
    #	hasActivated(pat, Patient())
    
    #untranslated:
    #'S2.4.4'
    #canDeactivate(ag, x, Request-consent-to-group-treatment(pat, org, group)) <-
    #	hasActivated(ag, Agent(pat))
    
    #untranslated:
    #'S2.4.5'
    #canDeactivate(cli, x, Request-consent-to-group-treatment(pat, org, group)) <-
    #	hasActivated(cli, Spine-clinician(ra, org, spcty)), canActivate(cli, General-practitioner(pat))
    
    #untranslated:
    #'S2.4.6'
    #canDeactivate(cli, x, Request-consent-to-group-treatment(pat, org, group)) <-
    #	hasActivated(cli, Spine-clinician(ra, org, spcty)), ra@ra.canActivate(cli, Workgroup-member(org, group, spcty))
    
    #untranslated:
    #'S2.4.12'
    #isDeactivated(x, Consent-to-group-treatment(pat, org, group)) <-
    #	isDeactivated(y, Request-consent-to-group-treatment(pat, org, group)), other-consent-to-group-treatment-requests(n, y, pat, org, group), n = 0

def other_consent_to_group_treatment_requests(x, pat, org, group): # S2.4.8
    return len({
    	1 for subj, role in hasActivated if 
    	role.name == "Request-consent-to-group-treatment" and 
    	role.org == org and 
    	role.pat == pat and 
    	role.group == group and 
    	x != subj
    })

class Consent_to_group_treatment(Role):
    def __init__(self, pat, org, group):
        super().__init__('Consent-to-group-treatment', ['pat', 'org', 'group']) 
        self.pat, self.org, self.group = pat, org, group
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params) or self.canActivate_3(*params)
    
    def canActivate_1(self, pat): # S2.4.9
        #todo: Not implemented: 2 hasAcs in a rule.
        #hasActivated(pat, Patient())
        #hasActivated(x, Request-consent-to-group-treatment(pat, org, group))
        pass
    
    def canActivate_2(self, ag): # S2.4.10
        #todo: Not implemented: 2 hasAcs in a rule.
        #hasActivated(ag, Agent(pat))
        #hasActivated(x, Request-consent-to-group-treatment(pat, org, group))
        pass
    
    def canActivate_3(self, cli1): # S2.4.11
        #todo: Not implemented: 2 hasAcs in a rule.
        #hasActivated(cli1, Spine-clinician(ra, org, spcty))
        #canActivate(cli1, Treating-clinician(pat, org, spcty))
        #hasActivated(x, Request-consent-to-group-treatment(pat, org, group))
        pass

class Referrer(Role):
    def __init__(self, pat, org, cli2, spcty1):
        super().__init__('Referrer', ['pat', 'org', 'cli2', 'spcty1']) 
        self.pat, self.org, self.cli2, self.spcty1 = pat, org, cli2, spcty1
    
    def canActivate(self, cli1): # S3.1.1
        return {
        	1 for subj, role in hasActivated if 
        	role.name == "Spine-clinician" and 
        	role.org == self.org and 
        	subj == cli1 and 
        	canActivate(subj, Treating_clinician(self.pat, role.org, role.spcty2))
        }
    
    #untranslated:
    #'S3.1.2'
    #canDeactivate(cli1, cli1, Referrer(pat, org, cli2, spcty1)) <-
    #	
    
    #untranslated:
    #'S3.1.3'
    #canDeactivate(pat, cli1, Referrer(pat, org, cli2, spcty1)) <-
    #	

class Spine_emergency_clinician(Role):
    def __init__(self, org, pat):
        super().__init__('Spine-emergency-clinician', ['org', 'pat']) 
        self.org, self.pat = org, pat
    
    def canActivate(self, cli): # S3.2.1
        return {
        	1 for subj, role in hasActivated if 
        	role.name == "Spine-clinician" and 
        	role.org == self.org and 
        	subj == cli and 
        	canActivate(self.pat, Patient())
        }
    
    #untranslated:
    #'S3.2.2'
    #canDeactivate(cli, cli, Spine-emergency-clinician(org, pat)) <-
    #	

class Treating_clinician(Role):
    def __init__(self, pat, org, spcty):
        super().__init__('Treating-clinician', ['pat', 'org', 'spcty']) 
        self.pat, self.org, self.spcty = pat, org, spcty
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params) or self.canActivate_3(*params) or self.canActivate_4(*params)
    
    def canActivate_1(self, cli): # S3.3.1
        return {
        	1 for subj, role in hasActivated if 
        	role.name == "Consent-to-treatment" and 
        	role.spcty == self.spcty and 
        	role.org == self.org and 
        	role.pat == self.pat and 
        	role.cli == cli
        }
    
    def canActivate_2(self, cli): # S3.3.2
        return {
        	1 for subj, role in hasActivated if 
        	role.name == "Spine-emergency-clinician" and 
        	role.org == self.org and 
        	role.pat == self.pat and 
        	subj == cli and 
        	self.spcty == "A_and_E"
        }
    
    def canActivate_3(self, cli): # S3.3.3
        return {
        	1 for subj, role in hasActivated if 
        	role.name == "Referrer" and 
        	role.spcty == self.spcty and 
        	role.org == self.org and 
        	role.pat == self.pat and 
        	role.cli == cli and 
        	canActivate(role.cli, Spine_clinician(Wildcard(), role.org, role.spcty))
        }
    
    def canActivate_4(self, cli): # S3.3.4
        #todo: Not implemented: 0 hasAcs in a rule.
        #canActivate(cli, Group-treating-clinician(pat, ra, org, group, spcty))
        pass

class General_practitioner(Role):
    def __init__(self, pat):
        super().__init__('General-practitioner', ['pat']) 
        self.pat = pat
    
    def canActivate(self, cli): # S3.3.5
        #todo: Not implemented: 0 hasAcs in a rule.
        #canActivate(cli, Treating-clinician(pat, org, spcty))
        #spcty = "GP"
        pass

class Group_treating_clinician(Role):
    def __init__(self, pat, ra, org, group, spcty):
        super().__init__('Group-treating-clinician', ['pat', 'ra', 'org', 'group', 'spcty']) 
        self.pat, self.ra, self.org, self.group, self.spcty = pat, ra, org, group, spcty
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params)
    
    def canActivate_1(self, cli): # S3.4.1
        return {
        	1 for subj, role in hasActivated if 
        	role.name == "Consent-to-group-treatment" and 
        	role.org == self.org and 
        	role.pat == self.pat and 
        	role.group == self.group and 
        	canActivate(cli, Workgroup_member(role.org, role.group, self.spcty)) and 
        	canActivate(self.ra, Registration_authority())
        }
    
    def canActivate_2(self, cli): # S3.4.2
        return {
        	1 for subj, role in hasActivated if 
        	role.name == "Consent-to-group-treatment" and 
        	role.org == self.org and 
        	role.pat == self.pat and 
        	role.group == self.group and 
        	canActivate(cli, Workgroup_member(role.org, role.group, self.spcty)) and 
        	canActivate(self.ra, Registration_authority())
        }

class Concealed_by_spine_clinician(Role):
    def __init__(self, pat, ids, start, end):
        super().__init__('Concealed-by-spine-clinician', ['pat', 'ids', 'start', 'end']) 
        self.pat, self.ids, self.start, self.end = pat, ids, start, end
    
    def canActivate(self, cli): # S4.1.1
        return {
        	1 for subj, role in hasActivated if 
        	role.name == "Spine-clinician" and 
        	subj == cli and 
        	canActivate(subj, Treating_clinician(self.pat, role.org, role.spcty))
        }
    
    #untranslated:
    #'S4.1.2'
    #canDeactivate(cli, cli, Concealed-by-spine-clinician(pat, ids, start, end)) <-
    #	hasActivated(cli, Spine-clinician(ra, org, spcty))
    
    #untranslated:
    #'S4.1.3'
    #canDeactivate(cli, cli2, Concealed-by-spine-clinician(pat, ids, start, end)) <-
    #	hasActivated(cli, Spine-clinician(ra, org, spcty)), canActivate(cli, General-practitioner(pat))
    
    #untranslated:
    #'S4.1.4'
    #canDeactivate(cli1, cli2, Concealed-by-spine-clinician(pat, ids, start, end)) <-
    #	hasActivated(cli1, Spine-clinician(ra, org, spcty1)), canActivate(cli1, Group-treating-clinician(pat, ra, org, group, spcty1)), canActivate(cli2, Group-treating-clinician(pat, ra, org, group, spcty2)), hasActivated(x, Consent-to-group-treatment(pat, org, group))

def count_concealed_by_spine_clinician(pat, id): # S4.1.6
    return len({
    	1 for subj, role in hasActivated if 
    	role.name == "Concealed-by-spine-clinician" and 
    	role.pat == pat and 
    	id in role.ids and 
    	Current_time() in vrange(role.start, role.end)
    })

class Conceal_request(Role):
    def __init__(self, what, who, start, end):
        super().__init__('Conceal-request', ['what', 'who', 'start', 'end']) 
        self.what, self.who, self.start, self.end = what, who, start, end
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params)
    
    def canActivate_1(self, pat): # S4.2.1
        #todo: could not translate constraint: (what,who) = ((pat,ids,orgs,authors,subjects,from-time,to-time),(orgs1,readers1,spctys1))
        #hasActivated(pat, Patient())
        #count-conceal-requests(n, pat)
        #(what,who) = ((pat,ids,orgs,authors,subjects,from-time,to-time),(orgs1,readers1,spctys1))
        #n < 100
        pass
    
    def canActivate_2(self, ag): # S4.2.2
        #todo: could not translate constraint: (what,who) = ((pat,ids,orgs,authors,subjects,from-time,to-time),(orgs1,readers1,spctys1))
        #hasActivated(ag, Agent(pat))
        #count-conceal-requests(n, pat)
        #(what,who) = ((pat,ids,orgs,authors,subjects,from-time,to-time),(orgs1,readers1,spctys1))
        #n < 100
        pass
    
    #untranslated:
    #'S4.2.3'
    #canDeactivate(pat, x, Conceal-request(what, whom, start, end)) <-
    #	hasActivated(pat, Patient()), pi7_1(what) = pat
    
    #untranslated:
    #'S4.2.4'
    #canDeactivate(ag, x, Conceal-request(what, whom, start, end)) <-
    #	hasActivated(ag, Agent(pat)), pi7_1(what) = pat
    
    #untranslated:
    #'S4.2.5'
    #canDeactivate(cli, x, Conceal-request(what, whom, start, end)) <-
    #	hasActivated(cli, Spine-clinician(ra, org, spcty)), canActivate(cli, General-practitioner(pat)), pi7_1(what) = pat
    
    #untranslated:
    #'S4.2.11'
    #isDeactivated(cli, Concealed-by-spine-patient(what, who, start, end)) <-
    #	isDeactivated(x, Conceal-request(what, who, start, end))

def count_conceal_requests(pat): # S4.2.7
    #todo: could not translate constraint: (what,who) = ((pat,ids,orgs,authors,subjects,from-time,to-time),(orgs1,readers1,spctys1))
    #hasActivated(x, Conceal-request(y))
    #(what,who) = ((pat,ids,orgs,authors,subjects,from-time,to-time),(orgs1,readers1,spctys1))
    #y = (what,who,start,end)
    pass

class Concealed_by_spine_patient(Role):
    def __init__(self, what, who, start, end):
        super().__init__('Concealed-by-spine-patient', ['what', 'who', 'start', 'end']) 
        self.what, self.who, self.start, self.end = what, who, start, end
    
    def canActivate(self, cli): # S4.2.8
        #todo: Not implemented: 2 hasAcs in a rule.
        #hasActivated(cli, Spine-clinician(ra, org, spcty))
        #canActivate(cli, Treating-clinician(pat, org, spcty))
        #hasActivated(x, Conceal-request(what, who, start, end))
        pass
    
    #untranslated:
    #'S4.2.9'
    #canDeactivate(cli, cli, Concealed-by-spine-patient(what, who, start, end)) <-
    #	hasActivated(cli, Spine-clinician(ra, org, spcty))
    
    #untranslated:
    #'S4.2.10'
    #canDeactivate(cli1, cli2, Concealed-by-spine-patient(what, who, start1, end1)) <-
    #	hasActivated(cli1, Spine-clinician(ra, org, spcty1)), ra@ra.canActivate(cli1, Group-treating-clinician(pat, ra, org, group, spcty1)), ra@ra.canActivate(cli2, Group-treating-clinician(pat, ra, org, group, spcty2))

def count_concealed_by_spine_patient(a, b): # S4.2.12
    #todo: could not translate constraint: a = (pat,id)
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
        super().__init__('Authenticated-express-consent', ['pat', 'cli']) 
        self.pat, self.cli = pat, cli
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params) or self.canActivate_3(*params)
    
    def canActivate_1(self, pat): # S4.3.1
        return {
        	1 for subj, role in hasActivated if 
        	role.name == "Patient" and 
        	subj == pat and 
        	count_authenticated_express_consent(subj) < 100
        }
    
    def canActivate_2(self, ag): # S4.3.2
        return {
        	1 for subj, role in hasActivated if 
        	role.name == "Agent" and 
        	role.pat == self.pat and 
        	subj == ag and 
        	count_authenticated_express_consent(role.pat) < 100
        }
    
    def canActivate_3(self, cli1): # S4.3.3
        return {
        	1 for subj, role in hasActivated if 
        	role.name == "Spine-clinician" and 
        	subj == cli1 and 
        	canActivate(subj, General_practitioner(self.pat))
        }
    
    #untranslated:
    #'S4.3.4'
    #canDeactivate(pat, x, Authenticated-express-consent(pat, cli)) <-
    #	hasActivated(pat, Patient())
    
    #untranslated:
    #'S4.3.5'
    #canDeactivate(ag, x, Authenticated-express-consent(pat, cli)) <-
    #	hasActivated(ag, Agent(pat))
    
    #untranslated:
    #'S4.3.6'
    #canDeactivate(cli1, x, Authenticated-express-consent(pat, cli2)) <-
    #	hasActivated(cli1, Spine-clinician(ra, org, spcty)), canActivate(cli1, General-practitioner(pat))

def count_authenticated_express_consent(pat): # S4.3.8
    return len({
    	1 for subj, role in hasActivated if 
    	role.name == "Authenticated-express-consent" and 
    	role.pat == pat
    })

#untranslated:
#'S5.1.1'
#permits(cli, Add-spine-record-item(pat)) <-
#	hasActivated(cli, Spine-clinician(ra, org, spcty)), canActivate(cli, Treating-clinician(pat, org, spcty))

#untranslated:
#'S5.1.2'
#permits(pat, Annotate-spine-record-item(pat, id)) <-
#	hasActivated(pat, Patient())

#untranslated:
#'S5.1.3'
#permits(ag, Annotate-spine-record-item(pat, id)) <-
#	hasActivated(ag, Agent(pat))

#untranslated:
#'S5.1.4'
#permits(pat, Annotate-spine-record-item(pat, id)) <-
#	hasActivated(cli, Spine-clinician(ra, org, spcty)), canActivate(cli, Treating-clinician(pat, org, spcty))

#untranslated:
#'S5.2.1'
#permits(pat, Get-spine-record-item-ids(pat)) <-
#	hasActivated(pat, Patient())

#untranslated:
#'S5.2.2'
#permits(ag, Get-spine-record-item-ids(pat)) <-
#	hasActivated(ag, Agent(pat))

#untranslated:
#'S5.2.3'
#permits(cli, Get-spine-record-item-ids(pat)) <-
#	hasActivated(cli, Spine-clinician(ra, org, spcty)), canActivate(cli, Treating-clinician(pat, org, spcty))

#untranslated:
#'S5.3.1'
#permits(pat, Read-spine-record-item(pat, id)) <-
#	hasActivated(pat, Patient()), hasActivated(x, One-off-consent(pat)), count-concealed-by-spine-patient(n, a, b), count-concealed-by-spine-clinician(m, pat, id), third-party-consent(consenters, pat, id), n = 0, m = 0, a = (pat,id), b = ("No-org",pat,"No-spcty"), Get-spine-record-third-parties(pat, id) subseteq consenters

#untranslated:
#'S5.3.2'
#permits(ag, Read-spine-record-item(pat, id)) <-
#	hasActivated(ag, Agent(pat)), hasActivated(x, One-off-consent(pat)), count-concealed-by-spine-patient(n, a, b), count-concealed-by-spine-clinician(m, pat, id), third-party-consent(consenters, pat, id), n = 0, m = 0, a = (pat,id), b = ("No-org",ag,"No-spcty"), Get-spine-record-third-parties(pat, id) subseteq consenters

#untranslated:
#'S5.3.3'
#permits(cli, Read-spine-record-item(pat, id)) <-
#	hasActivated(cli, Spine-clinician(ra, org, spcty)), hasActivated(x, One-off-consent(pat)), Get-spine-record-org(pat, id) = org, Get-spine-record-author(pat, id) = cli

#untranslated:
#'S5.3.4'
#permits(cli, Read-spine-record-item(pat, id)) <-
#	hasActivated(cli, Spine-clinician(ra, org, spcty)), hasActivated(x, One-off-consent(pat)), canActivate(cli, Treating-clinician(pat, org, spcty)), count-concealed-by-spine-patient(n, a, b), n = 0, a = (pat,id), b = (org,cli,spcty), Get-spine-record-subjects(pat, id) subseteq Permitted-subjects(spcty)

#untranslated:
#'S5.3.5'
#permits(cli, Read-spine-record-item(pat, id)) <-
#	hasActivated(cli, Spine-clinician(ra, org, spcty)), hasActivated(x, One-off-consent(pat)), canActivate(cli, Treating-clinician(pat, org, spcty)), hasActivated(y, Authenticated-express-consent(pat, cli)), Get-spine-record-subjects(pat, id) subseteq Permitted-subjects(spcty)

#untranslated:
#'S5.3.6'
#permits(cli, Force-read-spine-record-item(pat, id)) <-
#	hasActivated(cli, Spine-clinician(ra, org, spcty)), canActivate(cli, Treating-clinician(pat, org, spcty))
