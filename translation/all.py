from cassandra import *
from datetime import datetime

class Spine_clinician(Role):
    def __init__(self, ra, org, spcty):
        super().__init__('Spine-clinician', ['ra', 'org', 'spcty']) 
        self.ra, self.org, self.spcty = ra, org, spcty
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params)
    
    def canActivate_1(self, cli): # S1.1.1
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "NHS-clinician-cert" and role.org == self.org and role.spcty == self.spcty and Current_time() in vrange(role.start, role.end) } and\
        canActivate(ra, Registration_authority()) and\
        no_main_role_active(cli)
    
    def canActivate_2(self, cli): # S1.1.2
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "NHS-clinician-cert" and role.org == self.org and role.spcty == self.spcty and Current_time() in vrange(role.start, role.end) } and\
        canActivate(ra, Registration_authority()) and\
        no_main_role_active(cli)
    
    #'S1.1.3'
    #canDeactivate(cli, cli, Spine-clinician(ra, org, spcty)) <-
    #	
    
    #'S3.2.3'
    #isDeactivated(x, Spine-emergency-clinician(org, pat)) <-
    #	isDeactivated(x, Spine-clinician(ra, org, spcty))

#'S1.1.4'
#count-spine-clinician-activations(count<u>, user) <-
#	hasActivated(u, Spine-clinician(ra, org, spcty)), u = user

class Spine_admin(Role):
    def __init__(self):
        super().__init__('Spine-admin', []) 
    
    def canActivate(self, adm): # S1.2.1
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Register-spine-admin" } and\
        no_main_role_active(adm)
    
    #'S1.2.2'
    #canDeactivate(adm, adm, Spine-admin()) <-
    #	

#'S1.2.4'
#count-spine-admin-activations(count<u>, user) <-
#	hasActivated(u, Spine-admin()), u = user

class Register_spine_admin(Role):
    def __init__(self, adm2):
        super().__init__('Register-spine-admin', ['adm2']) 
        self.adm2 = adm2
    
    def canActivate(self, adm): # S1.2.5
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Spine-admin" } and\
        spine_admin_regs(n, adm2)
    
    #'S1.2.6'
    #canDeactivate(adm, x, Register-spine-admin(adm2)) <-
    #	hasActivated(adm, Spine-admin())
    
    #'S1.2.3'
    #isDeactivated(adm, Spine-admin()) <-
    #	isDeactivated(x, Register-spine-admin(adm))

#'S1.2.7'
#spine-admin-regs(count<x>, adm) <-
#	hasActivated(x, Register-spine-admin(adm))

class Patient(Role):
    def __init__(self):
        super().__init__('Patient', []) 
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params) or self.canActivate_3(*params)
    
    def canActivate_1(self, pat): # S1.3.1
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Register-patient" } and\
        no_main_role_active(pat) and\
        { (subject, role) for subject, role in hasActivated if role.name == "Register-patient" }
    
    def canActivate_2(self, pat): # P1.2.1
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Register-patient" } and\
        no_main_role_active(pat)
    
    def canActivate_3(self, pat): # A1.5.4
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Register-patient" } and\
        no_main_role_active(pat) and\
        { (subject, role) for subject, role in hasActivated if role.name == "Register-patient" }
    
    #'S1.3.2'
    #canDeactivate(pat, pat, Patient()) <-
    #	
    
    #'P1.2.2'
    #canDeactivate(pat, pat, Patient()) <-
    #	
    
    #'A1.5.5'
    #canDeactivate(pat, pat, Patient()) <-
    #	

#'S1.3.4'
#count-patient-activations(count<u>, user) <-
#	hasActivated(u, Patient()), u = user

class Register_patient(Role):
    def __init__(self, pat):
        super().__init__('Register-patient', ['pat']) 
        self.pat = pat
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params) or self.canActivate_3(*params)
    
    def canActivate_1(self, adm): # S1.3.5
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Spine-admin" } and\
        patient_regs(n, pat)
    
    def canActivate_2(self, adm): # P2.1.1
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "PDS-manager" } and\
        patient_regs(n, pat)
    
    def canActivate_3(self, rec): # A1.5.1
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Receptionist" } and\
        patient_regs(n, pat)
    
    #'S1.3.6'
    #canDeactivate(adm, x, Register-patient(pat)) <-
    #	hasActivated(adm, Spine-admin())
    
    #'P2.1.2'
    #canDeactivate(adm, x, Register-patient(pat)) <-
    #	hasActivated(adm, PDS-manager())
    
    #'A1.5.2'
    #canDeactivate(rec, x, Register-patient(pat)) <-
    #	hasActivated(rec, Receptionist())
    
    #'S1.3.3'
    #isDeactivated(pat, Patient()) <-
    #	isDeactivated(x, Register-patient(pat))
    
    #'S1.4.13'
    #isDeactivated(x, Register-agent(agent, pat)) <-
    #	isDeactivated(y, Register-patient(pat))
    
    #'S2.1.7'
    #isDeactivated(x, One-off-consent(pat)) <-
    #	isDeactivated(y, Register-patient(pat))
    
    #'S2.2.8'
    #isDeactivated(x, Request-third-party-consent(y, pat, id)) <-
    #	isDeactivated(z, Register-patient(pat))
    
    #'S2.3.7'
    #isDeactivated(x, Request-consent-to-treatment(pat, org, cli, spcty)) <-
    #	isDeactivated(y, Register-patient(pat))
    
    #'S2.4.7'
    #isDeactivated(x, Request-consent-to-group-treatment(pat, org, group)) <-
    #	isDeactivated(y, Register-patient(pat))
    
    #'S3.1.4'
    #isDeactivated(pat, Referrer(pat, org, cli2, spcty1)) <-
    #	isDeactivated(x, Register-patient(pat))
    
    #'S3.2.4'
    #isDeactivated(x, Spine-emergency-clinician(org, pat)) <-
    #	isDeactivated(y, Register-patient(pat))
    
    #'S4.1.5'
    #isDeactivated(x, Concealed-by-spine-clinician(pat, ids, start, end)) <-
    #	isDeactivated(y, Register-patient(pat))
    
    #'S4.2.6'
    #isDeactivated(x, Conceal-request(what, whom, start, end)) <-
    #	isDeactivated(y, Register-patient(pat)), pi7_1(what) = pat
    
    #'S4.3.7'
    #isDeactivated(x, Authenticated-express-consent(pat, cli)) <-
    #	isDeactivated(y, Register-patient(pat))
    
    #'P1.2.3'
    #isDeactivated(pat, Patient()) <-
    #	isDeactivated(x, Register-patient(pat))
    
    #'P1.3.3'
    #isDeactivated(ag, Agent(pat)) <-
    #	isDeactivated(x, Register-patient(ag))
    
    #'P1.3.4'
    #isDeactivated(ag, Agent(pat)) <-
    #	isDeactivated(x, Register-patient(pat))
    
    #'A1.5.6'
    #isDeactivated(pat, Patient()) <-
    #	isDeactivated(x, Register-patient(pat))
    
    #'A1.6.9'
    #isDeactivated(x, Register-agent(agent, pat)) <-
    #	isDeactivated(y, Register-patient(pat))
    
    #'A2.1.6'
    #isDeactivated(x, Request-consent-to-referral(pat, ra, org, cli, spcty)) <-
    #	isDeactivated(y, Register-patient(pat))
    
    #'A2.3.10'
    #isDeactivated(x, Request-third-party-consent(x2, pat, id)) <-
    #	isDeactivated(y, Register-patient(pat))
    
    #'A2.3.20'
    #isDeactivated(x, Third-party-consent(x, pat, id)) <-
    #	isDeactivated(y, Register-patient(pat))
    
    #'A3.3.6'
    #isDeactivated(x, Register-team-episode(pat, team)) <-
    #	isDeactivated(y, Register-patient(pat))
    
    #'A3.6.6'
    #isDeactivated(x, Register-ward-episode(pat, ward)) <-
    #	isDeactivated(y, Register-patient(pat))
    
    #'A3.7.4'
    #isDeactivated(x, Emergency-clinician(pat)) <-
    #	isDeactivated(y, Register-patient(pat))
    
    #'A4.1.5'
    #isDeactivated(x, Concealed-by-clinician(pat, id, start, end)) <-
    #	isDeactivated(y, Register-patient(pat))
    
    #'A4.2.6'
    #isDeactivated(x, Concealed-by-patient(what, whom, start, end)) <-
    #	isDeactivated(y, Register-patient(pat)), pi7_1(what) = pat

#'S1.3.7'
#patient-regs(count<x>, pat) <-
#	hasActivated(x, Register-patient(pat))

class Agent(Role):
    def __init__(self, pat):
        super().__init__('Agent', ['pat']) 
        self.pat = pat
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params) or self.canActivate_3(*params) or self.canActivate_4(*params)
    
    def canActivate_1(self, ag): # S1.4.1
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Register-agent" and role.pat == self.pat } and\
        { (subject, role) for subject, role in hasActivated if role.name == "Register-patient" } and\
        no_main_role_active(ag)
    
    def canActivate_2(self, ag): # P1.3.1
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Register-patient" } and\
        no_main_role_active(ag) and\
        canActivate(ag, Agent(pat))
    
    def canActivate_3(self, agent): # A1.6.1
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Register-agent" and role.pat == self.pat } and\
        { (subject, role) for subject, role in hasActivated if role.name == "Register-patient" } and\
        no_main_role_active(agent)
    
    def canActivate_4(self, agent): # A1.6.2
        return\
        canActivate(pat, Patient()) and\
        no_main_role_active(agent) and\
        { (subject, role) for subject, role in hasActivated if role.name == "Register-patient" } and\
        canActivate(agent, Agent(pat))
    
    #'S1.4.2'
    #canDeactivate(ag, ag, Agent(pat)) <-
    #	
    
    #'P1.3.2'
    #canDeactivate(ag, ag, Agent(pat)) <-
    #	

#'S1.4.4'
#other-agent-regs(count<y>, x, ag, pat) <-
#	hasActivated(y, Register-agent(ag, pat)), x != y

#'S1.4.5'
#count-agent-activations(count<u>, user) <-
#	hasActivated(u, Agent(pat)), u = user

#'S1.4.6'
#canReqCred(ag, "Spine".canActivate(ag, Agent(pat))) <-
#	hasActivated(ag, Agent(pat))

#'S1.4.7'
#canReqCred(org, "Spine".canActivate(ag, Agent(pat))) <-
#	ra.hasActivated(x, NHS-health-org-cert(org, start, end)), canActivate(ra, Registration-authority()), Current-time() in [start, end]

#'S1.4.8'
#canReqCred(org, "Spine".canActivate(ag, Agent(pat))) <-
#	org@ra.hasActivated(x, NHS-health-org-cert(org, start, end)), canActivate(ra, Registration-authority()), Current-time() in [start, end]

class Register_agent(Role):
    def __init__(self, agent, pat):
        super().__init__('Register-agent', ['agent', 'pat']) 
        self.agent, self.pat = agent, pat
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params) or self.canActivate_3(*params) or self.canActivate_4(*params)
    
    def canActivate_1(self, pat): # S1.4.9
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Patient" } and\
        agent_regs(n, pat)
    
    def canActivate_2(self, cli): # S1.4.10
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Spine-clinician" } and\
        canActivate(cli, General_practitioner(pat))
    
    def canActivate_3(self, pat): # A1.6.5
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Patient" }
    
    def canActivate_4(self, cg): # A1.6.6
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Caldicott-guardian" } and\
        canActivate(pat, Patient())
    
    #'S1.4.11'
    #canDeactivate(pat, pat, Register-agent(agent, pat)) <-
    #	hasActivated(pat, Patient())
    
    #'S1.4.12'
    #canDeactivate(cli, x, Register-agent(agent, pat)) <-
    #	hasActivated(cli, Spine-clinician(ra, org, spcty)), canActivate(cli, General-practitioner(pat))
    
    #'A1.6.7'
    #canDeactivate(pat, pat, Register-agent(agent, pat)) <-
    #	hasActivated(pat, Patient())
    
    #'A1.6.8'
    #canDeactivate(cg, x, Register-agent(agent, pat)) <-
    #	hasActivated(cg, Caldicott-guardian())
    
    #'S1.4.3'
    #isDeactivated(ag, Agent(pat)) <-
    #	isDeactivated(x, Register-agent(ag, pat)), other-agent-regs(n, x, ag, pat), n = 0
    
    #'A1.6.3'
    #isDeactivated(ag, Agent(pat)) <-
    #	isDeactivated(x, Register-agent(ag, pat)), other-agent-regs(n, x, ag, pat), n = 0

#'S1.4.14'
#agent-regs(count<x>, pat) <-
#	hasActivated(pat, Register-agent(x, pat))

class Registration_authority(Role):
    def __init__(self):
        super().__init__('Registration-authority', []) 
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params) or self.canActivate_3(*params) or self.canActivate_4(*params) or self.canActivate_5(*params) or self.canActivate_6(*params) or self.canActivate_7(*params) or self.canActivate_8(*params)
    
    def canActivate_1(self, ra): # S1.5.1
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "NHS-registration-authority" and Current_time() in vrange(role.start, role.end) }
    
    def canActivate_2(self, ra): # S1.5.2
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "NHS-registration-authority" and Current_time() in vrange(role.start, role.end) }
    
    def canActivate_3(self, ra): # P1.5.2
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "NHS-registration-authority" and Current_time() in vrange(role.start, role.end) }
    
    def canActivate_4(self, ra): # P1.5.3
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "NHS-registration-authority" and Current_time() in vrange(role.start, role.end) }
    
    def canActivate_5(self, ra): # A1.7.2
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "NHS-registration-authority" and Current_time() in vrange(role.start, role.end) }
    
    def canActivate_6(self, ra): # A1.7.3
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "NHS-registration-authority" and Current_time() in vrange(role.start, role.end) }
    
    def canActivate_7(self, ra): # R1.2.4
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "NHS-registration-authority" and Current_time() in vrange(role.start, role.end) }
    
    def canActivate_8(self, ra): # R1.2.5
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "NHS-registration-authority" and Current_time() in vrange(role.start, role.end) }

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
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Patient" }
    
    def canActivate_2(self, ag): # S2.1.2
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Agent" and role.pat == self.pat }
    
    def canActivate_3(self, cli): # S2.1.3
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Spine-clinician" } and\
        canActivate(cli, Treating_clinician(pat, org, spcty))
    
    #'S2.1.4'
    #canDeactivate(pat, x, One-off-consent(pat)) <-
    #	hasActivated(pat, Patient())
    
    #'S2.1.5'
    #canDeactivate(ag, x, One-off-consent(pat)) <-
    #	hasActivated(ag, Agent(pat))
    
    #'S2.1.6'
    #canDeactivate(cli, x, One-off-consent(pat)) <-
    #	hasActivated(cli, Spine-clinician(ra, org, spcty)), canActivate(cli, Treating-clinician(pat, org, spcty))

class Request_third_party_consent(Role):
    def __init__(self, x, pat, id):
        super().__init__('Request-third-party-consent', ['x', 'pat', 'id']) 
        self.x, self.pat, self.id = x, pat, id
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params) or self.canActivate_3(*params) or self.canActivate_4(*params) or self.canActivate_5(*params) or self.canActivate_6(*params) or self.canActivate_7(*params)
    
    def canActivate_1(self, pat): # S2.2.1
        #couldn't build constraints
        #hasActivated(pat, Patient())
        #x in Get-spine-record-third-parties(pat, id)
        pass
    
    def canActivate_2(self, ag): # S2.2.2
        #couldn't build constraints
        #hasActivated(ag, Agent(pat))
        #x in Get-spine-record-third-parties(pat, id)
        pass
    
    def canActivate_3(self, cli): # S2.2.3
        #couldn't build constraints
        #hasActivated(cli, Spine-clinician(ra, org, spcty))
        #canActivate(cli, Treating-clinician(pat, org, spcty))
        #x in Get-spine-record-third-parties(pat, id)
        pass
    
    def canActivate_4(self, pat): # A2.3.1
        #couldn't build constraints
        #hasActivated(pat, Patient())
        #x in Get-record-third-parties(pat, id)
        pass
    
    def canActivate_5(self, ag): # A2.3.2
        #couldn't build constraints
        #hasActivated(ag, Agent(pat))
        #x in Get-record-third-parties(pat, id)
        pass
    
    def canActivate_6(self, cli): # A2.3.3
        #couldn't build constraints
        #hasActivated(cli, Clinician(spcty))
        #x in Get-record-third-parties(pat, id)
        pass
    
    def canActivate_7(self, cg): # A2.3.4
        #couldn't build constraints
        #hasActivated(cg, Caldicott-guardian())
        #x in Get-record-third-parties(pat, id)
        pass
    
    #'S2.2.4'
    #canDeactivate(pat, y, Request-third-party-consent(x, pat, id)) <-
    #	hasActivated(pat, Patient())
    
    #'S2.2.5'
    #canDeactivate(ag, y, Request-third-party-consent(x, pat, id)) <-
    #	hasActivated(pat, Agent(pat))
    
    #'S2.2.6'
    #canDeactivate(cli, y, Request-third-party-consent(x, pat, id)) <-
    #	hasActivated(cli, Spine-clinician(ra, org, spcty))
    
    #'S2.2.7'
    #canDeactivate(x, y, Request-third-party-consent(x, pat, id)) <-
    #	hasActivated(x, Third-party())
    
    #'A2.3.5'
    #canDeactivate(pat, pat, Request-third-party-consent(x, pat, id)) <-
    #	hasActivated(pat, Patient())
    
    #'A2.3.6'
    #canDeactivate(ag, ag, Request-third-party-consent(x, pat, id)) <-
    #	hasActivated(pat, Agent(pat))
    
    #'A2.3.7'
    #canDeactivate(cli, cli, Request-third-party-consent(x, pat, id)) <-
    #	hasActivated(cli, Clinician(spcty))
    
    #'A2.3.8'
    #canDeactivate(cg, x, Request-third-party-consent(y, pat, id)) <-
    #	hasActivated(cg, Caldicott-guardian())
    
    #'A2.3.9'
    #canDeactivate(x, y, Request-third-party-consent(x, pat, id)) <-
    #	hasActivated(x, Third-party())
    
    #'S2.2.12'
    #isDeactivated(x, Third-party()) <-
    #	isDeactivated(y, Request-third-party-consent(x, pat, id)), other-third-party-consent-requests(n, y, x), n = 0
    
    #'S2.2.16'
    #isDeactivated(x, Third-party-consent(x, pat, id)) <-
    #	isDeactivated(y, Request-third-party-consent(x, pat, id)), other-third-party-consent-requests(n, y, x), n = 0
    
    #'A2.3.15'
    #isDeactivated(x, Third-party()) <-
    #	isDeactivated(y, Request-third-party-consent(x, pat, id)), other-third-party-requests(n, y, x), n = 0

#'S2.2.9'
#other-third-party-consent-requests(count<x>, y, z) <-
#	hasActivated(x, Request-third-party-consent(z, pat, id)), x != y

class Third_party(Role):
    def __init__(self):
        super().__init__('Third-party', []) 
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params)
    
    def canActivate_1(self, x): # S2.2.10
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Request-third-party-consent" } and\
        no_main_role_active(x) and\
        { (subject, role) for subject, role in hasActivated if role.name == "Register-patient" }
    
    def canActivate_2(self, x): # A2.3.12
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Request-third-party-consent" } and\
        no_main_role_active(x) and\
        { (subject, role) for subject, role in hasActivated if role.name == "Register-patient" }
    
    #'S2.2.11'
    #canDeactivate(x, x, Third-party()) <-
    #	
    
    #'A2.3.13'
    #canDeactivate(x, x, Third-party()) <-
    #	

#'S2.2.13'
#count-third-party-activations(count<u>, user) <-
#	hasActivated(u, Third-party()), u = user

class Third_party_consent(Role):
    def __init__(self, x, pat, id):
        super().__init__('Third-party-consent', ['x', 'pat', 'id']) 
        self.x, self.pat, self.id = x, pat, id
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params) or self.canActivate_3(*params) or self.canActivate_4(*params)
    
    def canActivate_1(self, x): # S2.2.14
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Third-party" } and\
        { (subject, role) for subject, role in hasActivated if role.name == "Request-third-party-consent" and role.x == self.x and role.pat == self.pat and role.id == self.id }
    
    def canActivate_2(self, cli): # S2.2.15
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Spine-clinician" } and\
        canActivate(cli, Treating_clinician(pat, org, spcty)) and\
        { (subject, role) for subject, role in hasActivated if role.name == "Request-third-party-consent" and role.x == self.x and role.pat == self.pat and role.id == self.id }
    
    def canActivate_3(self, x): # A2.3.16
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Third-party" } and\
        { (subject, role) for subject, role in hasActivated if role.name == "Request-third-party-consent" and role.x == self.x and role.pat == self.pat and role.id == self.id }
    
    def canActivate_4(self, cg): # A2.3.17
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Caldicott-guardian" } and\
        { (subject, role) for subject, role in hasActivated if role.name == "Request-third-party-consent" and role.x == self.x and role.pat == self.pat and role.id == self.id }
    
    #'A2.3.18'
    #canDeactivate(x, x, Third-party-consent(x, pat, id)) <-
    #	hasActivated(x, Third-party())
    
    #'A2.3.19'
    #canDeactivate(cg, x, Third-party-consent(x, pat, id)) <-
    #	hasActivated(cg, Caldicott-guardian())

#'S2.2.17'
#third-party-consent(group<consenter>, pat, id) <-
#	hasActivated(x, Third-party-consent(consenter, pat, id))

class Request_consent_to_treatment(Role):
    def __init__(self, pat, org2, cli2, spcty2):
        super().__init__('Request-consent-to-treatment', ['pat', 'org2', 'cli2', 'spcty2']) 
        self.pat, self.org2, self.cli2, self.spcty2 = pat, org2, cli2, spcty2
    
    def canActivate(self, cli1): # S2.3.1
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Spine-clinician" } and\
        canActivate(cli2, Spine_clinician(ra2, org2, spcty2)) and\
        canActivate(pat, Patient())
    
    #'S2.3.2'
    #canDeactivate(cli1, cli1, Request-consent-to-treatment(pat, org2, cli2, spcty2)) <-
    #	hasActivated(cli1, Spine-clinician(ra1, org1, spcty1))
    
    #'S2.3.3'
    #canDeactivate(cli2, cli1, Request-consent-to-treatment(pat, org2, cli2, spcty2)) <-
    #	hasActivated(cli2, Spine-clinician(ra2, org2, spcty2))
    
    #'S2.3.4'
    #canDeactivate(pat, x, Request-consent-to-treatment(pat, org, cli, spcty)) <-
    #	hasActivated(pat, Patient())
    
    #'S2.3.5'
    #canDeactivate(ag, x, Request-consent-to-treatment(pat, org, cli, spcty)) <-
    #	hasActivated(ag, Agent(pat))
    
    #'S2.3.6'
    #canDeactivate(cli, x, Request-consent-to-treatment(pat, org, cli2, spcty)) <-
    #	hasActivated(cli, Spine-clinician(ra, org, spcty)), canActivate(cli, General-practitioner(pat))
    
    #'S2.3.12'
    #isDeactivated(x, Consent-to-treatment(pat, org, cli, spcty)) <-
    #	isDeactivated(y, Request-consent-to-treatment(pat, org, cli, spcty)), other-consent-to-treatment-requests(n, y, pat, org, cli, spcty), n = 0

#'S2.3.8'
#other-consent-to-treatment-requests(count<y>, x, pat, org, cli, spcty) <-
#	hasActivated(y, Request-consent-to-treatment(pat, org, cli, spcty)), x != y

class Consent_to_treatment(Role):
    def __init__(self, pat, org, cli, spcty):
        super().__init__('Consent-to-treatment', ['pat', 'org', 'cli', 'spcty']) 
        self.pat, self.org, self.cli, self.spcty = pat, org, cli, spcty
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params) or self.canActivate_3(*params)
    
    def canActivate_1(self, pat): # S2.3.9
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Patient" } and\
        { (subject, role) for subject, role in hasActivated if role.name == "Request-consent-to-treatment" and role.pat == self.pat and role.org == self.org and role.cli == self.cli and role.spcty == self.spcty }
    
    def canActivate_2(self, ag): # S2.3.10
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Agent" and role.pat == self.pat } and\
        { (subject, role) for subject, role in hasActivated if role.name == "Request-consent-to-treatment" and role.pat == self.pat and role.org == self.org and role.cli == self.cli and role.spcty == self.spcty }
    
    def canActivate_3(self, cli1): # S2.3.11
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Spine-clinician" and role.org == self.org and role.spcty == self.spcty } and\
        canActivate(cli1, Treating_clinician(pat, org, spcty)) and\
        { (subject, role) for subject, role in hasActivated if role.name == "Request-consent-to-treatment" and role.pat == self.pat and role.org == self.org and role.spcty == self.spcty }

class Request_consent_to_group_treatment(Role):
    def __init__(self, pat, org, group):
        super().__init__('Request-consent-to-group-treatment', ['pat', 'org', 'group']) 
        self.pat, self.org, self.group = pat, org, group
    
    def canActivate(self, cli): # S2.4.1
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Spine-clinician" and role.org == self.org } and\
        canActivate(pat, Patient())
    
    #'S2.4.2'
    #canDeactivate(cli, cli, Request-consent-to-group-treatment(pat, org, group)) <-
    #	hasActivated(cli, Spine-clinician(ra, org, spcty))
    
    #'S2.4.3'
    #canDeactivate(pat, x, Request-consent-to-group-treatment(pat, org, group)) <-
    #	hasActivated(pat, Patient())
    
    #'S2.4.4'
    #canDeactivate(ag, x, Request-consent-to-group-treatment(pat, org, group)) <-
    #	hasActivated(ag, Agent(pat))
    
    #'S2.4.5'
    #canDeactivate(cli, x, Request-consent-to-group-treatment(pat, org, group)) <-
    #	hasActivated(cli, Spine-clinician(ra, org, spcty)), canActivate(cli, General-practitioner(pat))
    
    #'S2.4.6'
    #canDeactivate(cli, x, Request-consent-to-group-treatment(pat, org, group)) <-
    #	hasActivated(cli, Spine-clinician(ra, org, spcty)), ra@ra.canActivate(cli, Workgroup-member(org, group, spcty))
    
    #'S2.4.12'
    #isDeactivated(x, Consent-to-group-treatment(pat, org, group)) <-
    #	isDeactivated(y, Request-consent-to-group-treatment(pat, org, group)), other-consent-to-group-treatment-requests(n, y, pat, org, group), n = 0

#'S2.4.8'
#other-consent-to-group-treatment-requests(count<y>, x, pat, org, group) <-
#	hasActivated(y, Request-consent-to-group-treatment(pat, org, group)), x != y

class Consent_to_group_treatment(Role):
    def __init__(self, pat, org, group):
        super().__init__('Consent-to-group-treatment', ['pat', 'org', 'group']) 
        self.pat, self.org, self.group = pat, org, group
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params) or self.canActivate_3(*params)
    
    def canActivate_1(self, pat): # S2.4.9
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Patient" } and\
        { (subject, role) for subject, role in hasActivated if role.name == "Request-consent-to-group-treatment" and role.pat == self.pat and role.org == self.org and role.group == self.group }
    
    def canActivate_2(self, ag): # S2.4.10
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Agent" and role.pat == self.pat } and\
        { (subject, role) for subject, role in hasActivated if role.name == "Request-consent-to-group-treatment" and role.pat == self.pat and role.org == self.org and role.group == self.group }
    
    def canActivate_3(self, cli1): # S2.4.11
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Spine-clinician" and role.org == self.org } and\
        canActivate(cli1, Treating_clinician(pat, org, spcty)) and\
        { (subject, role) for subject, role in hasActivated if role.name == "Request-consent-to-group-treatment" and role.pat == self.pat and role.org == self.org and role.group == self.group }

class Referrer(Role):
    def __init__(self, pat, org, cli2, spcty1):
        super().__init__('Referrer', ['pat', 'org', 'cli2', 'spcty1']) 
        self.pat, self.org, self.cli2, self.spcty1 = pat, org, cli2, spcty1
    
    def canActivate(self, cli1): # S3.1.1
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Spine-clinician" and role.org == self.org } and\
        canActivate(cli1, Treating_clinician(pat, org, spcty2))
    
    #'S3.1.2'
    #canDeactivate(cli1, cli1, Referrer(pat, org, cli2, spcty1)) <-
    #	
    
    #'S3.1.3'
    #canDeactivate(pat, cli1, Referrer(pat, org, cli2, spcty1)) <-
    #	

class Spine_emergency_clinician(Role):
    def __init__(self, org, pat):
        super().__init__('Spine-emergency-clinician', ['org', 'pat']) 
        self.org, self.pat = org, pat
    
    def canActivate(self, cli): # S3.2.1
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Spine-clinician" and role.org == self.org } and\
        canActivate(pat, Patient())
    
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
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Consent-to-treatment" and role.pat == self.pat and role.org == self.org and role.spcty == self.spcty }
    
    def canActivate_2(self, cli): # S3.3.2
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Spine-emergency-clinician" and role.pat == self.pat and role.org == self.org }
    
    def canActivate_3(self, cli): # S3.3.3
        return\
        canActivate(cli, Spine_clinician(ra, org, spcty)) and\
        { (subject, role) for subject, role in hasActivated if role.name == "Referrer" and role.pat == self.pat and role.org == self.org and role.spcty == self.spcty }
    
    def canActivate_4(self, cli): # S3.3.4
        return\
        canActivate(cli, Group_treating_clinician(pat, ra, org, group, spcty))

class General_practitioner(Role):
    def __init__(self, pat):
        super().__init__('General-practitioner', ['pat']) 
        self.pat = pat
    
    def canActivate(self, cli): # S3.3.5
        return\
        canActivate(cli, Treating_clinician(pat, org, spcty))

class Group_treating_clinician(Role):
    def __init__(self, pat, ra, org, group, spcty):
        super().__init__('Group-treating-clinician', ['pat', 'ra', 'org', 'group', 'spcty']) 
        self.pat, self.ra, self.org, self.group, self.spcty = pat, ra, org, group, spcty
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params)
    
    def canActivate_1(self, cli): # S3.4.1
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Consent-to-group-treatment" and role.pat == self.pat and role.org == self.org and role.group == self.group } and\
        canActivate(cli, Workgroup_member(org, group, spcty)) and\
        canActivate(ra, Registration_authority())
    
    def canActivate_2(self, cli): # S3.4.2
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Consent-to-group-treatment" and role.pat == self.pat and role.org == self.org and role.group == self.group } and\
        canActivate(cli, Workgroup_member(org, group, spcty)) and\
        canActivate(ra, Registration_authority())

class Concealed_by_spine_clinician(Role):
    def __init__(self, pat, ids, start, end):
        super().__init__('Concealed-by-spine-clinician', ['pat', 'ids', 'start', 'end']) 
        self.pat, self.ids, self.start, self.end = pat, ids, start, end
    
    def canActivate(self, cli): # S4.1.1
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Spine-clinician" } and\
        canActivate(cli, Treating_clinician(pat, org, spcty))
    
    #'S4.1.2'
    #canDeactivate(cli, cli, Concealed-by-spine-clinician(pat, ids, start, end)) <-
    #	hasActivated(cli, Spine-clinician(ra, org, spcty))
    
    #'S4.1.3'
    #canDeactivate(cli, cli2, Concealed-by-spine-clinician(pat, ids, start, end)) <-
    #	hasActivated(cli, Spine-clinician(ra, org, spcty)), canActivate(cli, General-practitioner(pat))
    
    #'S4.1.4'
    #canDeactivate(cli1, cli2, Concealed-by-spine-clinician(pat, ids, start, end)) <-
    #	hasActivated(cli1, Spine-clinician(ra, org, spcty1)), canActivate(cli1, Group-treating-clinician(pat, ra, org, group, spcty1)), canActivate(cli2, Group-treating-clinician(pat, ra, org, group, spcty2)), hasActivated(x, Consent-to-group-treatment(pat, org, group))

#'S4.1.6'
#count-concealed-by-spine-clinician(count<x>, pat, id) <-
#	hasActivated(x, Concealed-by-spine-clinician(pat, ids, start, end)), id in ids, Current-time() in [start, end]

class Conceal_request(Role):
    def __init__(self, what, who, start, end):
        super().__init__('Conceal-request', ['what', 'who', 'start', 'end']) 
        self.what, self.who, self.start, self.end = what, who, start, end
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params)
    
    def canActivate_1(self, pat): # S4.2.1
        #couldn't build constraints
        #hasActivated(pat, Patient())
        #count-conceal-requests(n, pat)
        #(what,who) = ((pat,ids,orgs,authors,subjects,from-time,to-time),(orgs1,readers1,spctys1))
        #n < 100
        pass
    
    def canActivate_2(self, ag): # S4.2.2
        #couldn't build constraints
        #hasActivated(ag, Agent(pat))
        #count-conceal-requests(n, pat)
        #(what,who) = ((pat,ids,orgs,authors,subjects,from-time,to-time),(orgs1,readers1,spctys1))
        #n < 100
        pass
    
    #'S4.2.3'
    #canDeactivate(pat, x, Conceal-request(what, whom, start, end)) <-
    #	hasActivated(pat, Patient()), pi7_1(what) = pat
    
    #'S4.2.4'
    #canDeactivate(ag, x, Conceal-request(what, whom, start, end)) <-
    #	hasActivated(ag, Agent(pat)), pi7_1(what) = pat
    
    #'S4.2.5'
    #canDeactivate(cli, x, Conceal-request(what, whom, start, end)) <-
    #	hasActivated(cli, Spine-clinician(ra, org, spcty)), canActivate(cli, General-practitioner(pat)), pi7_1(what) = pat
    
    #'S4.2.11'
    #isDeactivated(cli, Concealed-by-spine-patient(what, who, start, end)) <-
    #	isDeactivated(x, Conceal-request(what, who, start, end))

#'S4.2.7'
#count-conceal-requests(count<y>, pat) <-
#	hasActivated(x, Conceal-request(y)), (what,who) = ((pat,ids,orgs,authors,subjects,from-time,to-time),(orgs1,readers1,spctys1)), y = (what,who,start,end)

class Concealed_by_spine_patient(Role):
    def __init__(self, what, who, start, end):
        super().__init__('Concealed-by-spine-patient', ['what', 'who', 'start', 'end']) 
        self.what, self.who, self.start, self.end = what, who, start, end
    
    def canActivate(self, cli): # S4.2.8
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Spine-clinician" } and\
        canActivate(cli, Treating_clinician(pat, org, spcty)) and\
        { (subject, role) for subject, role in hasActivated if role.name == "Conceal-request" and role.what == self.what and role.who == self.who and role.start == self.start and role.end == self.end }
    
    #'S4.2.9'
    #canDeactivate(cli, cli, Concealed-by-spine-patient(what, who, start, end)) <-
    #	hasActivated(cli, Spine-clinician(ra, org, spcty))
    
    #'S4.2.10'
    #canDeactivate(cli1, cli2, Concealed-by-spine-patient(what, who, start1, end1)) <-
    #	hasActivated(cli1, Spine-clinician(ra, org, spcty1)), ra@ra.canActivate(cli1, Group-treating-clinician(pat, ra, org, group, spcty1)), ra@ra.canActivate(cli2, Group-treating-clinician(pat, ra, org, group, spcty2))

#'S4.2.12'
#count-concealed-by-spine-patient(count<x>, a, b) <-
#	hasActivated(x, Concealed-by-spine-patient(what, who, start, end)), a = (pat,id), b = (org,reader,spcty), what = (pat,ids,orgs,authors,subjects,from-time,to-time), whom = (orgs1,readers1,spctys1), Get-spine-record-org(pat, id) in orgs, Get-spine-record-author(pat, id) in authors, sub in Get-spine-record-subjects(pat, id), sub in subjects, Get-spine-record-time(pat, id) in [from-time, to-time], id in ids, org in orgs1, reader in readers1, spcty in spctys1, Current-time() in [start, end], Get-spine-record-third-parties(pat, id) = emptyset, "non-clinical" notin Get-spine-record-subjects(pat, id)

class Authenticated_express_consent(Role):
    def __init__(self, pat, cli):
        super().__init__('Authenticated-express-consent', ['pat', 'cli']) 
        self.pat, self.cli = pat, cli
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params) or self.canActivate_3(*params)
    
    def canActivate_1(self, pat): # S4.3.1
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Patient" } and\
        count_authenticated_express_consent(n, pat)
    
    def canActivate_2(self, ag): # S4.3.2
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Agent" and role.pat == self.pat } and\
        count_authenticated_express_consent(n, pat)
    
    def canActivate_3(self, cli1): # S4.3.3
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Spine-clinician" } and\
        canActivate(cli1, General_practitioner(pat))
    
    #'S4.3.4'
    #canDeactivate(pat, x, Authenticated-express-consent(pat, cli)) <-
    #	hasActivated(pat, Patient())
    
    #'S4.3.5'
    #canDeactivate(ag, x, Authenticated-express-consent(pat, cli)) <-
    #	hasActivated(ag, Agent(pat))
    
    #'S4.3.6'
    #canDeactivate(cli1, x, Authenticated-express-consent(pat, cli2)) <-
    #	hasActivated(cli1, Spine-clinician(ra, org, spcty)), canActivate(cli1, General-practitioner(pat))

#'S4.3.8'
#count-authenticated-express-consent(count<cli>, pat) <-
#	hasActivated(x, Authenticated-express-consent(pat, cli))

#'S5.1.1'
#permits(cli, Add-spine-record-item(pat)) <-
#	hasActivated(cli, Spine-clinician(ra, org, spcty)), canActivate(cli, Treating-clinician(pat, org, spcty))

#'S5.1.2'
#permits(pat, Annotate-spine-record-item(pat, id)) <-
#	hasActivated(pat, Patient())

#'S5.1.3'
#permits(ag, Annotate-spine-record-item(pat, id)) <-
#	hasActivated(ag, Agent(pat))

#'S5.1.4'
#permits(pat, Annotate-spine-record-item(pat, id)) <-
#	hasActivated(cli, Spine-clinician(ra, org, spcty)), canActivate(cli, Treating-clinician(pat, org, spcty))

#'S5.2.1'
#permits(pat, Get-spine-record-item-ids(pat)) <-
#	hasActivated(pat, Patient())

#'S5.2.2'
#permits(ag, Get-spine-record-item-ids(pat)) <-
#	hasActivated(ag, Agent(pat))

#'S5.2.3'
#permits(cli, Get-spine-record-item-ids(pat)) <-
#	hasActivated(cli, Spine-clinician(ra, org, spcty)), canActivate(cli, Treating-clinician(pat, org, spcty))

#'S5.3.1'
#permits(pat, Read-spine-record-item(pat, id)) <-
#	hasActivated(pat, Patient()), hasActivated(x, One-off-consent(pat)), count-concealed-by-spine-patient(n, a, b), count-concealed-by-spine-clinician(m, pat, id), third-party-consent(consenters, pat, id), n = 0, m = 0, a = (pat,id), b = ("No-org",pat,"No-spcty"), Get-spine-record-third-parties(pat, id) subseteq consenters

#'S5.3.2'
#permits(ag, Read-spine-record-item(pat, id)) <-
#	hasActivated(ag, Agent(pat)), hasActivated(x, One-off-consent(pat)), count-concealed-by-spine-patient(n, a, b), count-concealed-by-spine-clinician(m, pat, id), third-party-consent(consenters, pat, id), n = 0, m = 0, a = (pat,id), b = ("No-org",ag,"No-spcty"), Get-spine-record-third-parties(pat, id) subseteq consenters

#'S5.3.3'
#permits(cli, Read-spine-record-item(pat, id)) <-
#	hasActivated(cli, Spine-clinician(ra, org, spcty)), hasActivated(x, One-off-consent(pat)), Get-spine-record-org(pat, id) = org, Get-spine-record-author(pat, id) = cli

#'S5.3.4'
#permits(cli, Read-spine-record-item(pat, id)) <-
#	hasActivated(cli, Spine-clinician(ra, org, spcty)), hasActivated(x, One-off-consent(pat)), canActivate(cli, Treating-clinician(pat, org, spcty)), count-concealed-by-spine-patient(n, a, b), n = 0, a = (pat,id), b = (org,cli,spcty), Get-spine-record-subjects(pat, id) subseteq Permitted-subjects(spcty)

#'S5.3.5'
#permits(cli, Read-spine-record-item(pat, id)) <-
#	hasActivated(cli, Spine-clinician(ra, org, spcty)), hasActivated(x, One-off-consent(pat)), canActivate(cli, Treating-clinician(pat, org, spcty)), hasActivated(y, Authenticated-express-consent(pat, cli)), Get-spine-record-subjects(pat, id) subseteq Permitted-subjects(spcty)

#'S5.3.6'
#permits(cli, Force-read-spine-record-item(pat, id)) <-
#	hasActivated(cli, Spine-clinician(ra, org, spcty)), canActivate(cli, Treating-clinician(pat, org, spcty))

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

#'P1.2.4'
#count-patient-activations(count<u>, user) <-
#	hasActivated(u, Patient()), u = user

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

class Register_clinician(Role):
    def __init__(self, cli, spcty):
        super().__init__('Register-clinician', ['cli', 'spcty']) 
        self.cli, self.spcty = cli, spcty
    
    def canActivate(self, mgr): # A1.1.1
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "HR-mgr" } and\
        clinician_regs(n, cli, spcty)
    
    #'A1.1.2'
    #canDeactivate(mgr, x, Register-clinician(cli, spcty)) <-
    #	hasActivated(mgr, HR-mgr())
    
    #'A1.1.6'
    #isDeactivated(cli, Clinician(spcty)) <-
    #	isDeactivated(x, Register-clinician(cli, spcty))
    
    #'A3.2.5'
    #isDeactivated(x, Register-team-member(mem, team, spcty)) <-
    #	isDeactivated(y, Register-clinician(mem, spcty))
    
    #'A3.5.6'
    #isDeactivated(x, Register-ward-member(cli, ward, spcty)) <-
    #	isDeactivated(y, Register-clinician(cli, spcty))

#'A1.1.3'
#clinician-regs(count<x>, cli, spcty) <-
#	hasActivated(x, Register-clinician(cli, spcty))

class Clinician(Role):
    def __init__(self, spcty):
        super().__init__('Clinician', ['spcty']) 
        self.spcty = spcty
    
    def canActivate(self, cli): # A1.1.4
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Register-clinician" and role.spcty == self.spcty } and\
        no_main_role_active(cli)
    
    #'A1.1.5'
    #canDeactivate(cli, cli, Clinician(spcty)) <-
    #	
    
    #'A3.7.5'
    #isDeactivated(x, Emergency-clinician(pat)) <-
    #	isDeactivated(x, Clinician(spcty))

#'A1.1.7'
#count-clinician-activations(count<u>, user) <-
#	hasActivated(u, Clinician(spcty)), u = user

class Register_Caldicott_guardian(Role):
    def __init__(self, cg):
        super().__init__('Register-Caldicott-guardian', ['cg']) 
        self.cg = cg
    
    def canActivate(self, mgr): # A1.2.1
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "HR-mgr" } and\
        cg_regs(n, cg)
    
    #'A1.2.2'
    #canDeactivate(mgr, x, Register-Caldicott-guardian(cg)) <-
    #	hasActivated(mgr, HR-mgr())
    
    #'A1.2.6'
    #isDeactivated(cg, Caldicott-guardian()) <-
    #	isDeactivated(x, Register-Caldicott-guardian(cg))

#'A1.2.3'
#cg-regs(count<x>, cg) <-
#	hasActivated(x, Register-Caldicott-guardian(cg))

class Caldicott_guardian(Role):
    def __init__(self):
        super().__init__('Caldicott-guardian', []) 
    
    def canActivate(self, cg): # A1.2.4
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Register-Caldicott-guardian" } and\
        no_main_role_active(cg)
    
    #'A1.2.5'
    #canDeactivate(cg, cg, Caldicott-guardian()) <-
    #	

#'A1.2.7'
#count-caldicott-guardian-activations(count<u>, user) <-
#	hasActivated(u, Caldicott-guardian()), u = user

class Register_HR_mgr(Role):
    def __init__(self, mgr2):
        super().__init__('Register-HR-mgr', ['mgr2']) 
        self.mgr2 = mgr2
    
    def canActivate(self, mgr): # A1.3.1
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "HR-mgr" } and\
        hr_manager_regs(n, mgr)
    
    #'A1.3.2'
    #canDeactivate(mgr, x, Register-HR-mgr(mgr2)) <-
    #	hasActivated(mgr, HR-mgr())
    
    #'A1.3.6'
    #isDeactivated(mgr, HR-mgr()) <-
    #	isDeactivated(x, Register-HR-mgr(mgr))

#'A1.3.3'
#hr-manager-regs(count<x>, mgr) <-
#	hasActivated(x, Register-HR-mgr(mgr))

class HR_mgr(Role):
    def __init__(self):
        super().__init__('HR-mgr', []) 
    
    def canActivate(self, mgr): # A1.3.4
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Register-HR-mgr" } and\
        no_main_role_active(mgr)
    
    #'A1.3.5'
    #canDeactivate(mgr, mgr, HR-mgr()) <-
    #	

#'A1.3.7'
#count-hr-mgr-activations(count<u>, user) <-
#	hasActivated(u, HR-mgr()), u = user

class Register_receptionist(Role):
    def __init__(self, rec):
        super().__init__('Register-receptionist', ['rec']) 
        self.rec = rec
    
    def canActivate(self, mgr): # A1.4.1
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "HR-mgr" } and\
        receptionist_regs(n, rec)
    
    #'A1.4.2'
    #canDeactivate(mgr, x, Register-receptionist(rec)) <-
    #	hasActivated(mgr, HR-mgr())
    
    #'A1.4.6'
    #isDeactivated(rec, Receptionist()) <-
    #	isDeactivated(x, Register-receptionist(rec)), no-main-role-active(rec)

#'A1.4.3'
#receptionist-regs(count<x>, rec) <-
#	hasActivated(x, Register-receptionist(rec))

class Receptionist(Role):
    def __init__(self):
        super().__init__('Receptionist', []) 
    
    def canActivate(self, rec): # A1.4.4
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Register-receptionist" }
    
    #'A1.4.5'
    #canDeactivate(rec, rec, Receptionist()) <-
    #	

#'A1.4.7'
#count-receptionist-activations(count<u>, user) <-
#	hasActivated(u, Receptionist()), u = user

#'A1.5.3'
#patient-regs(count<x>, pat) <-
#	hasActivated(x, Register-patient(pat))

#'A1.5.7'
#count-patient-activations(count<u>, user) <-
#	hasActivated(u, Patient()), u = user

#'A1.6.4'
#count-agent-activations(count<u>, user) <-
#	hasActivated(u, Agent(pat)), u = user

#'A1.6.10'
#other-agent-regs(count<y>, x, ag, pat) <-
#	hasActivated(y, Register-agent(ag, pat)), x != y

#'A1.7.1'
#no-main-role-active(user) <-
#	count-agent-activations(n, user), count-caldicott-guardian-activations(n, user), count-clinician-activations(n, user), count-ext-treating-clinician-activations(n, user), count-hr-mgr-activations(n, user), count-patient-activations(n, user), count-receptionist-activations(n, user), count-third-party-activations(n, user), n = 0

#'A1.7.4'
#canReqCred(x, "RA-ADB".hasActivated(y, NHS-health-org-cert(org, start, end))) <-
#	org = "ADB"

class Request_consent_to_referral(Role):
    def __init__(self, pat, ra, org, cli2, spcty2):
        super().__init__('Request-consent-to-referral', ['pat', 'ra', 'org', 'cli2', 'spcty2']) 
        self.pat, self.ra, self.org, self.cli2, self.spcty2 = pat, ra, org, cli2, spcty2
    
    def canActivate(self, cli1): # A2.1.1
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Clinician" } and\
        canActivate(cli1, ADB_treating_clinician(pat, team, spcty1))
    
    #'A2.1.2'
    #canDeactivate(cli, cli, Request-consent-to-referral(pat, ra, org, cli, spcty)) <-
    #	hasActivated(cli, Clinician(spcty))
    
    #'A2.1.3'
    #canDeactivate(pat, x, Request-consent-to-referral(pat, ra, org, cli, spcty)) <-
    #	hasActivated(pat, Patient())
    
    #'A2.1.4'
    #canDeactivate(ag, x, Request-consent-to-referral(pat, ra, org, cli, spcty)) <-
    #	hasActivated(ag, Agent(pat))
    
    #'A2.1.5'
    #canDeactivate(cg, x, Request-consent-to-referral(pat, ra, org, cli, spcty)) <-
    #	hasActivated(cg, Caldicott-guardian())
    
    #'A2.1.11'
    #isDeactivated(x, Consent-to-referral(pat, ra, org, cli, spcty)) <-
    #	isDeactivated(y, Request-consent-to-referral(pat, ra, org, cli, spcty)), other-consent-to-referral-requests(n, y, pat, ra, org, cli, spcty), n = 0

#'A2.1.7'
#other-consent-to-referral-requests(count<y>, x, pat, ra, org, cli, spcty) <-
#	hasActivated(y, Request-consent-to-referral(pat, ra, org, cli, spcty)), x != y

class Consent_to_referral(Role):
    def __init__(self, pat, ra, org, cli, spcty):
        super().__init__('Consent-to-referral', ['pat', 'ra', 'org', 'cli', 'spcty']) 
        self.pat, self.ra, self.org, self.cli, self.spcty = pat, ra, org, cli, spcty
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params) or self.canActivate_3(*params)
    
    def canActivate_1(self, pat): # A2.1.8
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Patient" } and\
        { (subject, role) for subject, role in hasActivated if role.name == "Request-consent-to-referral" and role.pat == self.pat and role.ra == self.ra and role.org == self.org and role.cli == self.cli and role.spcty == self.spcty }
    
    def canActivate_2(self, pat): # A2.1.9
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Agent" and role.pat == self.pat } and\
        { (subject, role) for subject, role in hasActivated if role.name == "Request-consent-to-referral" and role.pat == self.pat and role.ra == self.ra and role.org == self.org and role.cli == self.cli and role.spcty == self.spcty }
    
    def canActivate_3(self, cg): # A2.1.10
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Caldicott-guardian" } and\
        { (subject, role) for subject, role in hasActivated if role.name == "Request-consent-to-referral" and role.pat == self.pat and role.ra == self.ra and role.org == self.org and role.cli == self.cli and role.spcty == self.spcty }
    
    #'A2.2.4'
    #isDeactivated(cli, Ext-treating-clinician(pat, ra, org, spcty)) <-
    #	isDeactivated(x, Consent-to-referral(pat, ra, org, cli2, spcty)), other-referral-consents(n, x, pat, ra, org, cli, spcty), n = 0

#'A2.1.12'
#other-referral-consents(count<y>, x, pat, ra, org, cli, spcty) <-
#	hasActivated(y, Consent-to-referral(pat, ra, org, cli, spcty)), x != y

class Ext_treating_clinician(Role):
    def __init__(self, pat, ra, org, spcty):
        super().__init__('Ext-treating-clinician', ['pat', 'ra', 'org', 'spcty']) 
        self.pat, self.ra, self.org, self.spcty = pat, ra, org, spcty
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params)
    
    def canActivate_1(self, cli): # A2.2.1
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Consent-to-referral" and role.pat == self.pat and role.ra == self.ra and role.org == self.org and role.spcty == self.spcty } and\
        no_main_role_active(cli) and\
        { (subject, role) for subject, role in hasActivated if role.name == "NHS-clinician-cert" and role.org == self.org and role.spcty == self.spcty } and\
        canActivate(ra, Registration_authority())
    
    def canActivate_2(self, cli): # A2.2.2
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Consent-to-referral" and role.pat == self.pat and role.ra == self.ra and role.org == self.org and role.spcty == self.spcty } and\
        no_main_role_active(cli) and\
        { (subject, role) for subject, role in hasActivated if role.name == "NHS-clinician-cert" and role.org == self.org and role.spcty == self.spcty } and\
        canActivate(ra, Registration_authority())
    
    #'A2.2.3'
    #canDeactivate(cli, cli, Ext-treating-clinician(pat, ra, org, spcty)) <-
    #	

#'A2.2.5'
#count-ext-treating-clinician-activations(count<u>, user) <-
#	hasActivated(u, Ext-treating-clinician(pat, ra, org, spcty)), u = user

#'A2.3.11'
#count-third-party-activations(count<u>, user) <-
#	hasActivated(u, Third-party()), u = user

#'A2.3.14'
#other-third-party-requests(count<y>, x, third-party) <-
#	hasActivated(y, Request-third-party-consent(third-party, pat, id)), x != y

#'A2.3.21'
#third-party-consent(group<consenter>, pat, id) <-
#	hasActivated(x, Third-party-consent(consenter, pat, id))

class Head_of_team(Role):
    def __init__(self, team):
        super().__init__('Head-of-team', ['team']) 
        self.team = team
    
    def canActivate(self, hd): # A3.1.1
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Register-head-of-team" and role.team == self.team }
    
    #'A3.1.2'
    #canDeactivate(hd, hd, Head-of-team(team)) <-
    #	

class Register_head_of_team(Role):
    def __init__(self, hd, team):
        super().__init__('Register-head-of-team', ['hd', 'team']) 
        self.hd, self.team = hd, team
    
    def canActivate(self, mgr): # A3.1.4
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "HR-mgr" } and\
        { (subject, role) for subject, role in hasActivated if role.name == "Register-team-member" and role.hd == self.hd and role.team == self.team } and\
        head_of_team_regs(n, hd, team)
    
    #'A3.1.5'
    #canDeactivate(mgr, x, Register-head-of-team(hd, team)) <-
    #	hasActivated(mgr, HR-mgr())
    
    #'A3.1.3'
    #isDeactivated(hd, Head-of-team(team)) <-
    #	isDeactivated(x, Register-head-of-team(hd, team))

#'A3.1.7'
#head-of-team-regs(count<x>, hd, team) <-
#	hasActivated(x, Register-head-of-team(hd, team))

class Register_team_member(Role):
    def __init__(self, mem, team, spcty):
        super().__init__('Register-team-member', ['mem', 'team', 'spcty']) 
        self.mem, self.team, self.spcty = mem, team, spcty
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params)
    
    def canActivate_1(self, mgr): # A3.2.1
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "HR-mgr" } and\
        canActivate(mem, Clinician(spcty)) and\
        team_member_regs(n, mem, team, spcty)
    
    def canActivate_2(self, hd): # A3.2.2
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Clinician" } and\
        canActivate(hd, Head_of_team(team)) and\
        canActivate(mem, Clinician(spcty)) and\
        team_member_regs(n, mem, team, spcty)
    
    #'A3.2.3'
    #canDeactivate(mgr, x, Register-team-member(mem, team, spcty)) <-
    #	hasActivated(mgr, HR-mgr())
    
    #'A3.2.4'
    #canDeactivate(hd, x, Register-team-member(mem, team, spcty)) <-
    #	hasActivated(hd, Clinician(spcty2)), canActivate(hd, Head-of-team(team))
    
    #'A3.1.6'
    #isDeactivated(x, Register-head-of-team(hd, team)) <-
    #	isDeactivated(y, Register-team-member(hd, team, spcty))

#'A3.2.6'
#canReqCred(ra, "ADB".Register-team-member(cli, tea, spcty)) <-
#	ra = "RA-ADB"

#'A3.2.7'
#team-member-regs(count<x>, mem, team, spcty) <-
#	hasActivated(x, Register-team-member(mem, team, spcty))

class Register_team_episode(Role):
    def __init__(self, pat, team):
        super().__init__('Register-team-episode', ['pat', 'team']) 
        self.pat, self.team = pat, team
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params)
    
    def canActivate_1(self, rec): # A3.3.1
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Receptionist" } and\
        canActivate(pat, Patient()) and\
        team_episode_regs(n, pat, team)
    
    def canActivate_2(self, cli): # A3.3.2
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Clinician" } and\
        { (subject, role) for subject, role in hasActivated if role.name == "Register-team-member" and role.team == self.team } and\
        canActivate(pat, Patient()) and\
        team_episode_regs(n, pat, team)
    
    #'A3.3.3'
    #canDeactivate(cg, x, Register-team-episode(pat, team)) <-
    #	hasActivated(cg, Caldicott-guardian())
    
    #'A3.3.4'
    #canDeactivate(rec, x, Register-team-episode(pat, team)) <-
    #	hasActivated(rec, Receptionist())
    
    #'A3.3.5'
    #canDeactivate(cli, x, Register-team-episode(pat, team)) <-
    #	hasActivated(cli, Clinician(spcty)), hasActivated(x, Register-team-member(cli, team, spcty))

#'A3.3.7'
#team-episode-regs(count<x>, pat, team) <-
#	hasActivated(x, Register-team-episode(pat, team))

class Head_of_ward(Role):
    def __init__(self, ward):
        super().__init__('Head-of-ward', ['ward']) 
        self.ward = ward
    
    def canActivate(self, cli): # A3.4.1
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Register-head-of-ward" and role.ward == self.ward }
    
    #'A3.4.2'
    #canDeactivate(cli, cli, Head-of-ward(ward)) <-
    #	

class Register_head_of_ward(Role):
    def __init__(self, cli, ward):
        super().__init__('Register-head-of-ward', ['cli', 'ward']) 
        self.cli, self.ward = cli, ward
    
    def canActivate(self, mgr): # A3.4.4
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "HR-mgr" } and\
        { (subject, role) for subject, role in hasActivated if role.name == "Register-ward-member" and role.cli == self.cli and role.ward == self.ward } and\
        head_of_ward_regs(n, cli, ward)
    
    #'A3.4.5'
    #canDeactivate(mgr, x, Register-head-of-ward(cli, ward)) <-
    #	hasActivated(mgr, HR-mgr())
    
    #'A3.4.3'
    #isDeactivated(cli, Head-of-ward(ward)) <-
    #	isDeactivated(x, Register-head-of-ward(cli, ward))

#'A3.4.7'
#head-of-ward-regs(count<x>, cli, ward) <-
#	hasActivated(x, Register-head-of-ward(cli, ward))

class Register_ward_member(Role):
    def __init__(self, cli, ward, spcty):
        super().__init__('Register-ward-member', ['cli', 'ward', 'spcty']) 
        self.cli, self.ward, self.spcty = cli, ward, spcty
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params)
    
    def canActivate_1(self, mgr): # A3.5.1
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "HR-mgr" } and\
        canActivate(cli, Clinician(spcty)) and\
        ward_member_regs(n, cli, ward, spcty)
    
    def canActivate_2(self, hd): # A3.5.2
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Clinician" } and\
        canActivate(hd, Head_of_ward(ward)) and\
        canActivate(cli, Clinician(spcty)) and\
        ward_member_regs(n, cli, ward, spcty)
    
    #'A3.5.3'
    #canDeactivate(mgr, x, Register-ward-member(cli, ward, spcty)) <-
    #	hasActivated(mgr, HR-mgr())
    
    #'A3.5.4'
    #canDeactivate(hd, x, Register-ward-member(cli, ward, spcty)) <-
    #	hasActivated(hd, Clinician(spcty2)), canActivate(hd, Head-of-ward(ward))
    
    #'A3.4.6'
    #isDeactivated(x, Register-head-of-ward(cli, ward)) <-
    #	isDeactivated(y, Register-ward-member(cli, ward, spcty))

#'A3.5.5'
#canReqCred(ra, "ADB".Register-ward-member(cli, ward, spcty)) <-
#	ra = "RA-ADB"

#'A3.5.7'
#ward-member-regs(count<x>, cli, ward, spcty) <-
#	hasActivated(x, Register-ward-member(cli, ward, spcty))

class Register_ward_episode(Role):
    def __init__(self, pat, ward):
        super().__init__('Register-ward-episode', ['pat', 'ward']) 
        self.pat, self.ward = pat, ward
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params)
    
    def canActivate_1(self, rec): # A3.6.1
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Receptionist" } and\
        canActivate(pat, Patient()) and\
        ward_episode_regs(n, pat, ward)
    
    def canActivate_2(self, hd): # A3.6.2
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Clinician" } and\
        canActivate(hd, Head_of_ward(ward)) and\
        canActivate(pat, Patient()) and\
        ward_episode_regs(n, pat, ward)
    
    #'A3.6.3'
    #canDeactivate(cg, x, Register-ward-episode(pat, ward)) <-
    #	hasActivated(cg, Caldicott-guardian())
    
    #'A3.6.4'
    #canDeactivate(rec, x, Register-ward-episode(pat, ward)) <-
    #	hasActivated(rec, Receptionist())
    
    #'A3.6.5'
    #canDeactivate(hd, x, Register-ward-episode(pat, ward)) <-
    #	hasActivated(hd, Clinician(spcty)), canActivate(hd, Head-of-ward(ward))

#'A3.6.7'
#ward-episode-regs(count<x>, pat, ward) <-
#	hasActivated(x, Register-ward-episode(pat, ward))

class Emergency_clinician(Role):
    def __init__(self, pat):
        super().__init__('Emergency-clinician', ['pat']) 
        self.pat = pat
    
    def canActivate(self, cli): # A3.7.1
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Clinician" } and\
        canActivate(pat, Patient())
    
    #'A3.7.2'
    #canDeactivate(cli, cli, Emergency-clinician(pat)) <-
    #	
    
    #'A3.7.3'
    #canDeactivate(cg, cli, Emergency-clinician(pat)) <-
    #	hasActivated(cg, Caldicott-guardian())

#'A3.7.6'
#is-emergency-clinician(group<x>, pat) <-
#	hasActivated(x, Emergency-clinician(pat))

class ADB_treating_clinician(Role):
    def __init__(self, pat, group, spcty):
        super().__init__('ADB-treating-clinician', ['pat', 'group', 'spcty']) 
        self.pat, self.group, self.spcty = pat, group, spcty
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params) or self.canActivate_3(*params)
    
    def canActivate_1(self, cli): # A3.8.1
        #{'group', 'team'} variables in constraint: no match in {'spcty', 'cli', 'team'}
        #canActivate(cli, Clinician(spcty))
        #hasActivated(x, Register-team-member(cli, team, spcty))
        #hasActivated(y, Register-team-episode(pat, team))
        #group = team
        pass
    
    def canActivate_2(self, cli): # A3.8.2
        #{'ward', 'group'} variables in constraint: no match in {'spcty', 'ward', 'cli'}
        #canActivate(cli, Clinician(spcty))
        #hasActivated(x, Register-ward-member(cli, ward, spcty))
        #hasActivated(x, Register-ward-episode(pat, ward))
        #group = ward
        pass
    
    def canActivate_3(self, cli): # A3.8.3
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Emergency-clinician" and role.pat == self.pat }

class Concealed_by_clinician(Role):
    def __init__(self, pat, id, start, end):
        super().__init__('Concealed-by-clinician', ['pat', 'id', 'start', 'end']) 
        self.pat, self.id, self.start, self.end = pat, id, start, end
    
    def canActivate(self, cli): # A4.1.1
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Clinician" } and\
        canActivate(cli, ADB_treating_clinician(pat, group, spcty))
    
    #'A4.1.2'
    #canDeactivate(cli, cli, Concealed-by-clinician(pat, id, start, end)) <-
    #	hasActivated(cli, Clinician(spcty))
    
    #'A4.1.3'
    #canDeactivate(cli1, cli2, Concealed-by-clinician(pat, id, start, end)) <-
    #	hasActivated(cli1, Clinician(spcty1)), canActivate(cli1, ADB-treating-clinician(pat, group, spcty1)), canActivate(cli2, ADB-treating-clinician(pat, group, spcty2))
    
    #'A4.1.4'
    #canDeactivate(cg, cli, Concealed-by-clinician(pat, id, start, end)) <-
    #	hasActivated(cg, Caldicott-guardian())

#'A4.1.6'
#count-concealed-by-clinician(count<x>, pat, id) <-
#	hasActivated(x, Concealed-by-clinician(pat, id, start, end)), Current-time() in [start, end]

class Concealed_by_patient(Role):
    def __init__(self, what, who, start, end):
        super().__init__('Concealed-by-patient', ['what', 'who', 'start', 'end']) 
        self.what, self.who, self.start, self.end = what, who, start, end
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params)
    
    def canActivate_1(self, pat): # A4.2.1
        #couldn't build constraints
        #hasActivated(pat, Patient())
        #count-concealed-by-patient(n, pat)
        #what = (pat,ids,authors,groups,subjects,from-time,to-time)
        #who = (orgs1,readers1,groups1,spctys1)
        #n < 100
        pass
    
    def canActivate_2(self, ag): # A4.2.2
        #couldn't build constraints
        #hasActivated(ag, Agent(pat))
        #count-concealed-by-patient(n, pat)
        #what = (pat,ids,authors,groups,subjects,from-time,to-time)
        #who = (orgs1,readers1,groups1,spctys1)
        #n < 100
        pass
    
    #'A4.2.3'
    #canDeactivate(pat, x, Concealed-by-patient(what, whom, start, end)) <-
    #	hasActivated(pat, Patient()), pi7_1(what) = pat
    
    #'A4.2.4'
    #canDeactivate(ag, x, Concealed-by-patient(what, whom, start, end)) <-
    #	hasActivated(ag, Agent(pat)), pi7_1(what) = pat
    
    #'A4.2.5'
    #canDeactivate(cg, x, Concealed-by-patient(what, whom, start, end)) <-
    #	hasActivated(cg, Caldicott-guardian())

#'A4.2.7'
#count-concealed-by-patient(count<y>, pat) <-
#	hasActivated(x, Concealed-by-patient(y)), what = (pat,ids,authors,groups,subjects,from-time,to-time), who = (orgs1,readers1,groups1,spctys1), y = (what,who,start,end)

#'A4.2.8'
#count-concealed-by-patient2(count<x>, a, b) <-
#	hasActivated(x, Concealed-by-patient(what, whom, start, end)), a = (pat,id), b = (org,reader,group,spcty), what = (pat,ids,authors,groups,subjects,from-time,to-time), whom = (orgs1,readers1,groups1,spctys1), Get-record-author(pat, id) in authors, Get-record-group(pat, id) in groups, sub in Get-record-subjects(pat, id), sub in subjects, Get-record-time(pat, id) in [from-time, to-time], id in ids, org in orgs1, reader in readers1, group in groups1, spcty in spctys1, Current-time() in [start, end]

#'A5.1.1'
#permits(cli, Add-record-item(pat)) <-
#	hasActivated(cli, Clinician(spcty)), canActivate(cli, ADB-treating-clinician(pat, group, spcty))

#'A5.1.2'
#permits(cli, Add-record-item(pat)) <-
#	hasActivated(cli, Ext-treating-clinician(pat, ra, org, spcty))

#'A5.1.3'
#permits(ag, Annotate-record-item(pat, id)) <-
#	hasActivated(ag, Agent(pat))

#'A5.1.4'
#permits(pat, Annotate-record-item(pat, id)) <-
#	hasActivated(pat, Patient())

#'A5.1.5'
#permits(pat, Annotate-record-item(pat, id)) <-
#	hasActivated(cli, Clinician(spcty)), canActivate(cli, ADB-treating-clinician(pat, group, spcty))

#'A5.2.1'
#permits(pat, Get-record-item-ids(pat)) <-
#	hasActivated(pat, Patient())

#'A5.2.2'
#permits(ag, Get-record-item-ids(pat)) <-
#	hasActivated(ag, Agent(pat))

#'A5.2.3'
#permits(cli, Get-record-item-ids(pat)) <-
#	hasActivated(cli, Clinician(spcty)), canActivate(cli, ADB-treating-clinician(pat, group, spcty))

#'A5.3.1'
#permits(ag, Read-record-item(pat, id)) <-
#	hasActivated(ag, Agent(pat)), count-concealed-by-patient2(n, a, b), count-concealed-by-clinician(m, pat, id), third-party-consent(consenters, pat, id), a = (pat,id), b = ("No-org",ag,"No-group","No-spcty"), n = 0, m = 0, Get-record-third-parties(pat, id) subseteq consenters

#'A5.3.2'
#permits(cli, Read-record-item(pat, id)) <-
#	hasActivated(cli, Clinician(spcty)), Get-record-author(pat, id) = cli

#'A5.3.3'
#permits(cli, Read-record-item(pat, id)) <-
#	hasActivated(cli, Clinician(spcty)), hasActivated(x, Register-team-member(cli, team, spcty)), Get-record-group(pat, id) = team

#'A5.3.4'
#permits(cli, Read-record-item(pat, id)) <-
#	hasActivated(cli, Clinician(spcty)), canActivate(cli, ADB-treating-clinician(pat, group, spcty)), count-concealed-by-patient2(n, a, b), n = 0, a = (pat,id), b = ("ADB",cli,group,spcty), Get-record-subjects(pat, id) subseteq Permitted-subjects(spcty)

#'A5.3.5'
#permits(cli, Read-record-item(pat, id)) <-
#	hasActivated(cli, Ext-treating-clinician(pat, ra, org, spcty)), count-concealed-by-patient2(n, a, b), n = 0, a = (pat,id), b = (org,cli,"Ext-group",spcty), Get-record-subjects(pat, id) subseteq Permitted-subjects(spcty)

#'A5.3.6'
#permits(pat, Read-record-item(pat, id)) <-
#	hasActivated(pat, Patient()), count-concealed-by-patient2(n, a, b), count-concealed-by-clinician(m, pat, id), third-party-consent(consenters, pat, id), n = 0, m = 0, a = (pat,id), b = ("No-org",pat,"No-group","No-spcty"), Get-record-third-parties(pat, id) subseteq consenters

#'A5.3.7'
#permits(cg, Force-read-record-item(pat, id)) <-
#	hasActivated(cg, Caldicott-guardian())

#'A5.3.8'
#permits(cli, Force-read-record-item(pat, id)) <-
#	hasActivated(cli, Clinician(spcty)), canActivate(cli, ADB-treating-clinician(pat, group, spcty))

class Register_RA_manager(Role):
    def __init__(self, mgr2):
        super().__init__('Register-RA-manager', ['mgr2']) 
        self.mgr2 = mgr2
    
    def canActivate(self, mgr): # R1.1.1
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "RA-manager" } and\
        RA_manager_regs(n, mgr2)
    
    #'R1.1.2'
    #canDeactivate(mgr, x, Register-RA-manager(mgr2)) <-
    #	hasActivated(mgr, RA-manager())
    
    #'R1.1.6'
    #isDeactivated(mgr, RA-manager()) <-
    #	isDeactivated(x, Register-RA-manager(mgr))

#'R1.1.3'
#RA-manager-regs(count<x>, mgr) <-
#	hasActivated(x, Register-RA-manager(mgr))

class RA_manager(Role):
    def __init__(self):
        super().__init__('RA-manager', []) 
    
    def canActivate(self, mgr): # R1.1.4
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "Register-RA-manager" }
    
    #'R1.1.5'
    #canDeactivate(mgr, mgr, RA-manager()) <-
    #	

#'R1.2.1'
#canReqCred(x, "NHS".hasActivated(x, NHS-registration-authority(ra, start, end))) <-
#	ra = "RA-ADB"

class NHS_service(Role):
    def __init__(self):
        super().__init__('NHS-service', []) 
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params)
    
    def canActivate_1(self, srv): # R1.2.2
        return\
        canActivate(srv, Registration_authority())
    
    def canActivate_2(self, srv): # R1.2.3
        return\

class NHS_clinician_cert(Role):
    def __init__(self, org, cli, spcty, start, end):
        super().__init__('NHS-clinician-cert', ['org', 'cli', 'spcty', 'start', 'end']) 
        self.org, self.cli, self.spcty, self.start, self.end = org, cli, spcty, start, end
    
    def canActivate(self, mgr): # R2.1.1
        #{'start2', 'start', 'end2'} variables in constraint: no match in {'start2', 'org', 'end2'}
        #hasActivated(mgr, RA-manager())
        #hasActivated(y, NHS-health-org-cert(org, start2, end2))
        #start in [start2, end2]
        #end in [start2, end2]
        #start < end
        pass
    
    #'R2.1.2'
    #canDeactivate(mgr, x, NHS-clinician-cert(org, cli, spcty, start, end)) <-
    #	hasActivated(mgr, RA-manager())

#'R2.1.4'
#canReqCred(e, "RA-ADB".hasActivated(x, NHS-clinician-cert(org, cli, spcty, start, end))) <-
#	hasActivated(y, NHS-health-org-cert(org, start2, end2)), e = org, Current-time() in [start2, end2]

#'R2.1.5'
#canReqCred(e, "RA-ADB".hasActivated(x, NHS-clinician-cert(org, cli, spcty, start, end))) <-
#	canActivate(e, NHS-service())

#'R2.1.6'
#canReqCred(e, "RA-ADB".hasActivated(x, NHS-clinician-cert(org, cli, spcty, start, end))) <-
#	e = cli

class NHS_Caldicott_guardian_cert(Role):
    def __init__(self, org, cg, start, end):
        super().__init__('NHS-Caldicott-guardian-cert', ['org', 'cg', 'start', 'end']) 
        self.org, self.cg, self.start, self.end = org, cg, start, end
    
    def canActivate(self, mgr): # R2.2.1
        #{'start2', 'start', 'end2'} variables in constraint: no match in {'start2', 'org', 'end2'}
        #hasActivated(mgr, RA-manager())
        #hasActivated(x, NHS-health-org-cert(org, start2, end2))
        #start in [start2, end2]
        #end in [start2, end2]
        #start < end
        pass
    
    #'R2.2.2'
    #canDeactivate(mgr, x, NHS-Caldicott-guardian-cert(org, cg, start, end)) <-
    #	hasActivated(mgr, RA-manager())

#'R2.2.4'
#canReqCred(e, "RA-ADB".hasActivated(x, NHS-Caldicott-guardian-cert(org, cg, start, end))) <-
#	e = cg

#'R2.2.5'
#canReqCred(e, "RA-ADB".hasActivated(x, NHS-Caldicott-guardian-cert(org, cg, start, end))) <-
#	hasActivated(y, NHS-health-org-cert(org, start2, end2)), e = org, Current-time() in [start2, end2]

#'R2.2.6'
#canReqCred(e, "RA-ADB".hasActivated(x, NHS-Caldicott-guardian-cert(org, cg, start, end))) <-
#	canActivate(e, NHS-service())

class NHS_health_org_cert(Role):
    def __init__(self, org, start, end):
        super().__init__('NHS-health-org-cert', ['org', 'start', 'end']) 
        self.org, self.start, self.end = org, start, end
    
    def canActivate(self, mgr): # R2.3.1
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "RA-manager" }
    
    #'R2.3.2'
    #canDeactivate(mgr, x, NHS-health-org-cert(org, start, end)) <-
    #	hasActivated(mgr, RA-manager())
    
    #'R2.1.3'
    #isDeactivated(mgr, NHS-clinician-cert(org, cli, spcty, start, end)) <-
    #	isDeactivated(x, NHS-health-org-cert(org, start2, end2)), other-NHS-health-org-regs(n, x, org, start2, end2), n = 0, start in [start2, end2], end in [start2, end2], start < end
    
    #'R2.2.3'
    #isDeactivated(mgr, NHS-Caldicott-guardian-cert(org, cg, start, end)) <-
    #	isDeactivated(x, NHS-health-org-cert(org, start2, end2)), other-NHS-health-org-regs(n, x, org, start2, end2), start in [start2, end2], end in [start2, end2], start < end, n = 0

#'R2.3.3i'
#other-NHS-health-org-regs(count<y>, x, org, start, end) <-
#	hasActivated(y, NHS-health-org-cert(org, start2, end2)), start in [start2, end2], end in [start2, end2], start < end, x != y

#'R2.3.3ii'
#other-NHS-health-org-regs(count<y>, x, org, start, end) <-
#	hasActivated(y, NHS-health-org-cert(org, start2, end2)), start in [start2, end2], end in [start2, end2], start < end, start != start2

#'R2.3.3iii'
#other-NHS-health-org-regs(count<y>, x, org, start, end) <-
#	hasActivated(y, NHS-health-org-cert(org, start2, end2)), start in [start2, end2], end in [start2, end2], start < end, end != end2

#'R2.3.4'
#canReqCred(e, "RA-ADB".hasActivated(x, NHS-health-org-cert(org, start, end))) <-
#	hasActivated(y, NHS-Caldicott-guardian-cert(org, cg, start2, end2)), Current-time() in [start2, end2], e = cg

#'R2.3.5'
#canReqCred(e, "RA-ADB".hasActivated(x, NHS-health-org-cert(org, start, end))) <-
#	hasActivated(y, NHS-clinician-cert(org, cli, spcty, start2, end2)), Current-time() in [start2, end2], e = cli

#'R2.3.6'
#canReqCred(e, "RA-ADB".hasActivated(x, NHS-health-org-cert(org, start, end))) <-
#	e = org

#'R2.3.7'
#canReqCred(e, "RA-ADB".hasActivated(x, NHS-health-org-cert(org2, start, end))) <-
#	ra.hasActivated(y, NHS-health-org-cert(org, start2, end2)), canActivate(ra, Registration-authority()), e = org

#'R2.3.8'
#canReqCred(e, "RA-ADB".hasActivated(x, NHS-health-org-cert(org2, start, end))) <-
#	org@ra.hasActivated(y, NHS-health-org-cert(org, start2, end2)), canActivate(ra, Registration-authority()), e = org

#'R2.3.9'
#canReqCred(e, "RA-ADB".hasActivated(x, NHS-health-org-cert(org, start, end))) <-
#	canActivate(e, NHS-service())

class Workgroup_member(Role):
    def __init__(self, org, group, spcty):
        super().__init__('Workgroup-member', ['org', 'group', 'spcty']) 
        self.org, self.group, self.spcty = org, group, spcty
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params)
    
    def canActivate_1(self, cli): # R3.1.1
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "NHS-health-org-cert" and role.org == self.org and Current_time() in vrange(role.start, role.end) } and\
        { (subject, role) for subject, role in hasActivated if role.name == "Register-team-member" and role.group == self.group and role.spcty == self.spcty }
    
    def canActivate_2(self, cli): # R3.1.2
        return\
        { (subject, role) for subject, role in hasActivated if role.name == "NHS-health-org-cert" and role.org == self.org and Current_time() in vrange(role.start, role.end) } and\
        { (subject, role) for subject, role in hasActivated if role.name == "Register-ward-member" and role.group == self.group and role.spcty == self.spcty }

#'R3.1.3'
#canReqCred(spine, "RA-ADB".canActivate(cli, Workgroup-member(org, group, spcty))) <-
#	spine = "Spine"
