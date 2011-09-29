from cassandra import *
from datetime import datetime

class Spine_clinician(Role): 
    def __init__(self, ra, org, spcty):
        super().__init__('Spine-clinician', ['ra', 'org', 'spcty']) 
        self.ra, self.org, self.spcty = ra, org, spcty
    
    def canActivate(self, *params):
        multi_try(lambda: self.canActivate_1(*params), lambda: self.canActivate_2(*params))
    
    def canActivate_1(self, cli):
        ra, org, spcty = self.ra, self.org, self.spcty
        
        {(subject, role) for subject, role in hasActivated if role.name == "NHS-clinician-cert"  and role.org == self.org and role.spcty == self.spcty and Current_time() in vrange(role.start, role.end)}
        canActivate(ra, Registration_authority())
        no_main_role_active(cli)
    
    def canActivate_2(self, cli):
        ra, org, spcty = self.ra, self.org, self.spcty
        
        {(subject, role) for subject, role in hasActivated if role.name == "NHS-clinician-cert"  and role.org == self.org and role.spcty == self.spcty and Current_time() in vrange(role.start, role.end)}
        canActivate(ra, Registration_authority())
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
    
    def canActivate(self, adm):
        
        {(subject, role) for subject, role in hasActivated if role.name == "Register-spine-admin" }
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
    
    def canActivate(self, adm):
        adm2 = self.adm2
        
        {(subject, role) for subject, role in hasActivated if role.name == "Spine-admin" }
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
    
    def canActivate(self, pat):
        
        {(subject, role) for subject, role in hasActivated if role.name == "Register-patient" }
        no_main_role_active(pat)
        {(subject, role) for subject, role in hasActivated if role.name == "Register-patient" }
    
    #'S1.3.2'
    #canDeactivate(pat, pat, Patient()) <-
    #	

#'S1.3.4'
#count-patient-activations(count<u>, user) <-
#	hasActivated(u, Patient()), u = user

class Register_patient(Role): 
    def __init__(self, pat):
        super().__init__('Register-patient', ['pat']) 
        self.pat = pat
    
    def canActivate(self, adm):
        pat = self.pat
        
        {(subject, role) for subject, role in hasActivated if role.name == "Spine-admin" }
        patient_regs(n, pat)
    
    #'S1.3.6'
    #canDeactivate(adm, x, Register-patient(pat)) <-
    #	hasActivated(adm, Spine-admin())
    
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

#'S1.3.7'
#patient-regs(count<x>, pat) <-
#	hasActivated(x, Register-patient(pat))

class Agent(Role): 
    def __init__(self, pat):
        super().__init__('Agent', ['pat']) 
        self.pat = pat
    
    def canActivate(self, ag):
        pat = self.pat
        
        {(subject, role) for subject, role in hasActivated if role.name == "Register-agent"  and role.pat == self.pat}
        {(subject, role) for subject, role in hasActivated if role.name == "Register-patient" }
        no_main_role_active(ag)
    
    #'S1.4.2'
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
        multi_try(lambda: self.canActivate_1(*params), lambda: self.canActivate_2(*params))
    
    def canActivate_1(self, pat):
        agent, pat = self.agent, self.pat
        
        {(subject, role) for subject, role in hasActivated if role.name == "Patient" }
        agent_regs(n, pat)
    
    def canActivate_2(self, cli):
        agent, pat = self.agent, self.pat
        
        {(subject, role) for subject, role in hasActivated if role.name == "Spine-clinician" }
        canActivate(cli, General_practitioner(pat))
    
    #'S1.4.11'
    #canDeactivate(pat, pat, Register-agent(agent, pat)) <-
    #	hasActivated(pat, Patient())
    
    #'S1.4.12'
    #canDeactivate(cli, x, Register-agent(agent, pat)) <-
    #	hasActivated(cli, Spine-clinician(ra, org, spcty)), canActivate(cli, General-practitioner(pat))
    
    #'S1.4.3'
    #isDeactivated(ag, Agent(pat)) <-
    #	isDeactivated(x, Register-agent(ag, pat)), other-agent-regs(n, x, ag, pat), n = 0

#'S1.4.14'
#agent-regs(count<x>, pat) <-
#	hasActivated(pat, Register-agent(x, pat))

class Registration_authority(Role): 
    def __init__(self):
        super().__init__('Registration-authority', []) 
    
    def canActivate(self, *params):
        multi_try(lambda: self.canActivate_1(*params), lambda: self.canActivate_2(*params))
    
    def canActivate_1(self, ra):
        
        {(subject, role) for subject, role in hasActivated if role.name == "NHS-registration-authority"  and Current_time() in vrange(role.start, role.end)}
    
    def canActivate_2(self, ra):
        
        {(subject, role) for subject, role in hasActivated if role.name == "NHS-registration-authority"  and Current_time() in vrange(role.start, role.end)}

#'S1.5.3'
#no-main-role-active(user) <-
#	count-agent-activations(n, user), count-spine-clinician-activations(n, user), count-spine-admin-activations(n, user), count-patient-activations(n, user), count-third-party-activations(n, user), n = 0

class One_off_consent(Role): 
    def __init__(self, pat):
        super().__init__('One-off-consent', ['pat']) 
        self.pat = pat
    
    def canActivate(self, *params):
        multi_try(lambda: self.canActivate_1(*params), lambda: self.canActivate_2(*params), lambda: self.canActivate_3(*params))
    
    def canActivate_1(self, pat):
        pat = self.pat
        
        {(subject, role) for subject, role in hasActivated if role.name == "Patient" }
    
    def canActivate_2(self, ag):
        pat = self.pat
        
        {(subject, role) for subject, role in hasActivated if role.name == "Agent"  and role.pat == self.pat}
    
    def canActivate_3(self, cli):
        pat = self.pat
        
        {(subject, role) for subject, role in hasActivated if role.name == "Spine-clinician" }
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
        multi_try(lambda: self.canActivate_1(*params), lambda: self.canActivate_2(*params), lambda: self.canActivate_3(*params))
    
    def canActivate_1(self, pat):
        x, pat, id = self.x, self.pat, self.id
        #couldn't build constraints
        #hasActivated(pat, Patient())
        #x in Get-spine-record-third-parties(pat, id)
    
    def canActivate_2(self, ag):
        x, pat, id = self.x, self.pat, self.id
        #couldn't build constraints
        #hasActivated(ag, Agent(pat))
        #x in Get-spine-record-third-parties(pat, id)
    
    def canActivate_3(self, cli):
        x, pat, id = self.x, self.pat, self.id
        #couldn't build constraints
        #hasActivated(cli, Spine-clinician(ra, org, spcty))
        #canActivate(cli, Treating-clinician(pat, org, spcty))
        #x in Get-spine-record-third-parties(pat, id)
    
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
    
    #'S2.2.12'
    #isDeactivated(x, Third-party()) <-
    #	isDeactivated(y, Request-third-party-consent(x, pat, id)), other-third-party-consent-requests(n, y, x), n = 0
    
    #'S2.2.16'
    #isDeactivated(x, Third-party-consent(x, pat, id)) <-
    #	isDeactivated(y, Request-third-party-consent(x, pat, id)), other-third-party-consent-requests(n, y, x), n = 0

#'S2.2.9'
#other-third-party-consent-requests(count<x>, y, z) <-
#	hasActivated(x, Request-third-party-consent(z, pat, id)), x != y

class Third_party(Role): 
    def __init__(self):
        super().__init__('Third-party', []) 
    
    def canActivate(self, x):
        
        {(subject, role) for subject, role in hasActivated if role.name == "Request-third-party-consent" }
        no_main_role_active(x)
        {(subject, role) for subject, role in hasActivated if role.name == "Register-patient" }
    
    #'S2.2.11'
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
        multi_try(lambda: self.canActivate_1(*params), lambda: self.canActivate_2(*params))
    
    def canActivate_1(self, x):
        x, pat, id = self.x, self.pat, self.id
        
        {(subject, role) for subject, role in hasActivated if role.name == "Third-party" }
        {(subject, role) for subject, role in hasActivated if role.name == "Request-third-party-consent"  and role.x == self.x and role.pat == self.pat and role.id == self.id}
    
    def canActivate_2(self, cli):
        x, pat, id = self.x, self.pat, self.id
        
        {(subject, role) for subject, role in hasActivated if role.name == "Spine-clinician" }
        canActivate(cli, Treating_clinician(pat, org, spcty))
        {(subject, role) for subject, role in hasActivated if role.name == "Request-third-party-consent"  and role.x == self.x and role.pat == self.pat and role.id == self.id}

#'S2.2.17'
#third-party-consent(group<consenter>, pat, id) <-
#	hasActivated(x, Third-party-consent(consenter, pat, id))

class Request_consent_to_treatment(Role): 
    def __init__(self, pat, org2, cli2, spcty2):
        super().__init__('Request-consent-to-treatment', ['pat', 'org2', 'cli2', 'spcty2']) 
        self.pat, self.org2, self.cli2, self.spcty2 = pat, org2, cli2, spcty2
    
    def canActivate(self, cli1):
        pat, org2, cli2, spcty2 = self.pat, self.org2, self.cli2, self.spcty2
        
        {(subject, role) for subject, role in hasActivated if role.name == "Spine-clinician" }
        canActivate(cli2, Spine_clinician(ra2, org2, spcty2))
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
        multi_try(lambda: self.canActivate_1(*params), lambda: self.canActivate_2(*params), lambda: self.canActivate_3(*params))
    
    def canActivate_1(self, pat):
        pat, org, cli, spcty = self.pat, self.org, self.cli, self.spcty
        
        {(subject, role) for subject, role in hasActivated if role.name == "Patient" }
        {(subject, role) for subject, role in hasActivated if role.name == "Request-consent-to-treatment"  and role.pat == self.pat and role.org == self.org and role.cli == self.cli and role.spcty == self.spcty}
    
    def canActivate_2(self, ag):
        pat, org, cli, spcty = self.pat, self.org, self.cli, self.spcty
        
        {(subject, role) for subject, role in hasActivated if role.name == "Agent"  and role.pat == self.pat}
        {(subject, role) for subject, role in hasActivated if role.name == "Request-consent-to-treatment"  and role.pat == self.pat and role.org == self.org and role.cli == self.cli and role.spcty == self.spcty}
    
    def canActivate_3(self, cli1):
        pat, org, cli, spcty = self.pat, self.org, self.cli, self.spcty
        
        {(subject, role) for subject, role in hasActivated if role.name == "Spine-clinician"  and role.org == self.org and role.spcty == self.spcty}
        canActivate(cli1, Treating_clinician(pat, org, spcty))
        {(subject, role) for subject, role in hasActivated if role.name == "Request-consent-to-treatment"  and role.pat == self.pat and role.org == self.org and role.spcty == self.spcty}

class Request_consent_to_group_treatment(Role): 
    def __init__(self, pat, org, group):
        super().__init__('Request-consent-to-group-treatment', ['pat', 'org', 'group']) 
        self.pat, self.org, self.group = pat, org, group
    
    def canActivate(self, cli):
        pat, org, group = self.pat, self.org, self.group
        
        {(subject, role) for subject, role in hasActivated if role.name == "Spine-clinician"  and role.org == self.org}
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
        multi_try(lambda: self.canActivate_1(*params), lambda: self.canActivate_2(*params), lambda: self.canActivate_3(*params))
    
    def canActivate_1(self, pat):
        pat, org, group = self.pat, self.org, self.group
        
        {(subject, role) for subject, role in hasActivated if role.name == "Patient" }
        {(subject, role) for subject, role in hasActivated if role.name == "Request-consent-to-group-treatment"  and role.pat == self.pat and role.org == self.org and role.group == self.group}
    
    def canActivate_2(self, ag):
        pat, org, group = self.pat, self.org, self.group
        
        {(subject, role) for subject, role in hasActivated if role.name == "Agent"  and role.pat == self.pat}
        {(subject, role) for subject, role in hasActivated if role.name == "Request-consent-to-group-treatment"  and role.pat == self.pat and role.org == self.org and role.group == self.group}
    
    def canActivate_3(self, cli1):
        pat, org, group = self.pat, self.org, self.group
        
        {(subject, role) for subject, role in hasActivated if role.name == "Spine-clinician"  and role.org == self.org}
        canActivate(cli1, Treating_clinician(pat, org, spcty))
        {(subject, role) for subject, role in hasActivated if role.name == "Request-consent-to-group-treatment"  and role.pat == self.pat and role.org == self.org and role.group == self.group}

class Referrer(Role): 
    def __init__(self, pat, org, cli2, spcty1):
        super().__init__('Referrer', ['pat', 'org', 'cli2', 'spcty1']) 
        self.pat, self.org, self.cli2, self.spcty1 = pat, org, cli2, spcty1
    
    def canActivate(self, cli1):
        pat, org, cli2, spcty1 = self.pat, self.org, self.cli2, self.spcty1
        
        {(subject, role) for subject, role in hasActivated if role.name == "Spine-clinician"  and role.org == self.org}
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
    
    def canActivate(self, cli):
        org, pat = self.org, self.pat
        
        {(subject, role) for subject, role in hasActivated if role.name == "Spine-clinician"  and role.org == self.org}
        canActivate(pat, Patient())
    
    #'S3.2.2'
    #canDeactivate(cli, cli, Spine-emergency-clinician(org, pat)) <-
    #	

class Treating_clinician(Role): 
    def __init__(self, pat, org, spcty):
        super().__init__('Treating-clinician', ['pat', 'org', 'spcty']) 
        self.pat, self.org, self.spcty = pat, org, spcty
    
    def canActivate(self, *params):
        multi_try(lambda: self.canActivate_1(*params), lambda: self.canActivate_2(*params), lambda: self.canActivate_3(*params), lambda: self.canActivate_4(*params))
    
    def canActivate_1(self, cli):
        pat, org, spcty = self.pat, self.org, self.spcty
        
        {(subject, role) for subject, role in hasActivated if role.name == "Consent-to-treatment"  and role.pat == self.pat and role.org == self.org and role.spcty == self.spcty}
    
    def canActivate_2(self, cli):
        pat, org, spcty = self.pat, self.org, self.spcty
        
        {(subject, role) for subject, role in hasActivated if role.name == "Spine-emergency-clinician"  and role.pat == self.pat and role.org == self.org}
    
    def canActivate_3(self, cli):
        pat, org, spcty = self.pat, self.org, self.spcty
        
        canActivate(cli, Spine_clinician(ra, org, spcty))
        {(subject, role) for subject, role in hasActivated if role.name == "Referrer"  and role.pat == self.pat and role.org == self.org and role.spcty == self.spcty}
    
    def canActivate_4(self, cli):
        pat, org, spcty = self.pat, self.org, self.spcty
        
        canActivate(cli, Group_treating_clinician(pat, ra, org, group, spcty))

class General_practitioner(Role): 
    def __init__(self, pat):
        super().__init__('General-practitioner', ['pat']) 
        self.pat = pat
    
    def canActivate(self, cli):
        pat = self.pat
        
        canActivate(cli, Treating_clinician(pat, org, spcty))

class Group_treating_clinician(Role): 
    def __init__(self, pat, ra, org, group, spcty):
        super().__init__('Group-treating-clinician', ['pat', 'ra', 'org', 'group', 'spcty']) 
        self.pat, self.ra, self.org, self.group, self.spcty = pat, ra, org, group, spcty
    
    def canActivate(self, *params):
        multi_try(lambda: self.canActivate_1(*params), lambda: self.canActivate_2(*params))
    
    def canActivate_1(self, cli):
        pat, ra, org, group, spcty = self.pat, self.ra, self.org, self.group, self.spcty
        
        {(subject, role) for subject, role in hasActivated if role.name == "Consent-to-group-treatment"  and role.pat == self.pat and role.org == self.org and role.group == self.group}
        canActivate(cli, Workgroup_member(org, group, spcty))
        canActivate(ra, Registration_authority())
    
    def canActivate_2(self, cli):
        pat, ra, org, group, spcty = self.pat, self.ra, self.org, self.group, self.spcty
        
        {(subject, role) for subject, role in hasActivated if role.name == "Consent-to-group-treatment"  and role.pat == self.pat and role.org == self.org and role.group == self.group}
        canActivate(cli, Workgroup_member(org, group, spcty))
        canActivate(ra, Registration_authority())

class Concealed_by_spine_clinician(Role): 
    def __init__(self, pat, ids, start, end):
        super().__init__('Concealed-by-spine-clinician', ['pat', 'ids', 'start', 'end']) 
        self.pat, self.ids, self.start, self.end = pat, ids, start, end
    
    def canActivate(self, cli):
        pat, ids, start, end = self.pat, self.ids, self.start, self.end
        
        {(subject, role) for subject, role in hasActivated if role.name == "Spine-clinician" }
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
        multi_try(lambda: self.canActivate_1(*params), lambda: self.canActivate_2(*params))
    
    def canActivate_1(self, pat):
        what, who, start, end = self.what, self.who, self.start, self.end
        #couldn't build constraints
        #hasActivated(pat, Patient())
        #count-conceal-requests(n, pat)
        #(what,who) = ((pat,ids,orgs,authors,subjects,from-time,to-time),(orgs1,readers1,spctys1))
        #n < 100
    
    def canActivate_2(self, ag):
        what, who, start, end = self.what, self.who, self.start, self.end
        #couldn't build constraints
        #hasActivated(ag, Agent(pat))
        #count-conceal-requests(n, pat)
        #(what,who) = ((pat,ids,orgs,authors,subjects,from-time,to-time),(orgs1,readers1,spctys1))
        #n < 100
    
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
    
    def canActivate(self, cli):
        what, who, start, end = self.what, self.who, self.start, self.end
        
        {(subject, role) for subject, role in hasActivated if role.name == "Spine-clinician" }
        canActivate(cli, Treating_clinician(pat, org, spcty))
        {(subject, role) for subject, role in hasActivated if role.name == "Conceal-request"  and role.what == self.what and role.who == self.who and role.start == self.start and role.end == self.end}
    
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
        multi_try(lambda: self.canActivate_1(*params), lambda: self.canActivate_2(*params), lambda: self.canActivate_3(*params))
    
    def canActivate_1(self, pat):
        pat, cli = self.pat, self.cli
        
        {(subject, role) for subject, role in hasActivated if role.name == "Patient" }
        count_authenticated_express_consent(n, pat)
    
    def canActivate_2(self, ag):
        pat, cli = self.pat, self.cli
        
        {(subject, role) for subject, role in hasActivated if role.name == "Agent"  and role.pat == self.pat}
        count_authenticated_express_consent(n, pat)
    
    def canActivate_3(self, cli1):
        pat, cli = self.pat, self.cli
        
        {(subject, role) for subject, role in hasActivated if role.name == "Spine-clinician" }
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
