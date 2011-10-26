from cassandra import *
from datetime import datetime

class Register_clinician(Role):
    def __init__(self, cli, spcty):
        super().__init__('Register-clinician', ['cli', 'spcty']) 
        self.cli, self.spcty = cli, spcty
    
    def canActivate(self, mgr): # A1.1.1
        pass
    
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
        pass
    
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
        pass
    
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
        pass
    
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
        pass
    
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
        pass
    
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
        pass
    
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
        pass
    
    #'A1.4.5'
    #canDeactivate(rec, rec, Receptionist()) <-
    #	

#'A1.4.7'
#count-receptionist-activations(count<u>, user) <-
#	hasActivated(u, Receptionist()), u = user

class Register_patient(Role):
    def __init__(self, pat):
        super().__init__('Register-patient', ['pat']) 
        self.pat = pat
    
    def canActivate(self, rec): # A1.5.1
        pass
    
    #'A1.5.2'
    #canDeactivate(rec, x, Register-patient(pat)) <-
    #	hasActivated(rec, Receptionist())
    
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

#'A1.5.3'
#patient-regs(count<x>, pat) <-
#	hasActivated(x, Register-patient(pat))

class Patient(Role):
    def __init__(self):
        super().__init__('Patient', []) 
    
    def canActivate(self, pat): # A1.5.4
        #todo: Not implemented: 2 hasAcs in a rule.
        #hasActivated(x, Register-patient(pat))
        #no-main-role-active(pat)
        #"PDS"@"PDS".hasActivated(y, Register-patient(pat))
        pass
    
    #'A1.5.5'
    #canDeactivate(pat, pat, Patient()) <-
    #	

#'A1.5.7'
#count-patient-activations(count<u>, user) <-
#	hasActivated(u, Patient()), u = user

class Agent(Role):
    def __init__(self, pat):
        super().__init__('Agent', ['pat']) 
        self.pat = pat
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params)
    
    def canActivate_1(self, agent): # A1.6.1
        #todo: Not implemented: 2 hasAcs in a rule.
        #hasActivated(x, Register-agent(agent, pat))
        #"PDS"@"PDS".hasActivated(x, Register-patient(agent))
        #no-main-role-active(agent)
        pass
    
    def canActivate_2(self, agent): # A1.6.2
        pass

#'A1.6.4'
#count-agent-activations(count<u>, user) <-
#	hasActivated(u, Agent(pat)), u = user

class Register_agent(Role):
    def __init__(self, agent, pat):
        super().__init__('Register-agent', ['agent', 'pat']) 
        self.agent, self.pat = agent, pat
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params)
    
    def canActivate_1(self, pat): # A1.6.5
        pass
    
    def canActivate_2(self, cg): # A1.6.6
        pass
    
    #'A1.6.7'
    #canDeactivate(pat, pat, Register-agent(agent, pat)) <-
    #	hasActivated(pat, Patient())
    
    #'A1.6.8'
    #canDeactivate(cg, x, Register-agent(agent, pat)) <-
    #	hasActivated(cg, Caldicott-guardian())
    
    #'A1.6.3'
    #isDeactivated(ag, Agent(pat)) <-
    #	isDeactivated(x, Register-agent(ag, pat)), other-agent-regs(n, x, ag, pat), n = 0

#'A1.6.10'
#other-agent-regs(count<y>, x, ag, pat) <-
#	hasActivated(y, Register-agent(ag, pat)), x != y

#'A1.7.1'
#no-main-role-active(user) <-
#	count-agent-activations(n, user), count-caldicott-guardian-activations(n, user), count-clinician-activations(n, user), count-ext-treating-clinician-activations(n, user), count-hr-mgr-activations(n, user), count-patient-activations(n, user), count-receptionist-activations(n, user), count-third-party-activations(n, user), n = 0

class Registration_authority(Role):
    def __init__(self):
        super().__init__('Registration-authority', []) 
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params)
    
    def canActivate_1(self, ra): # A1.7.2
        pass
    
    def canActivate_2(self, ra): # A1.7.3
        pass

#'A1.7.4'
#canReqCred(x, "RA-ADB".hasActivated(y, NHS-health-org-cert(org, start, end))) <-
#	org = "ADB"

class Request_consent_to_referral(Role):
    def __init__(self, pat, ra, org, cli2, spcty2):
        super().__init__('Request-consent-to-referral', ['pat', 'ra', 'org', 'cli2', 'spcty2']) 
        self.pat, self.ra, self.org, self.cli2, self.spcty2 = pat, ra, org, cli2, spcty2
    
    def canActivate(self, cli1): # A2.1.1
        pass
    
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
        #todo: Not implemented: 2 hasAcs in a rule.
        #hasActivated(pat, Patient())
        #hasActivated(x, Request-consent-to-referral(pat, ra, org, cli, spcty))
        pass
    
    def canActivate_2(self, pat): # A2.1.9
        #todo: Not implemented: 2 hasAcs in a rule.
        #hasActivated(pat, Agent(pat))
        #hasActivated(x, Request-consent-to-referral(pat, ra, org, cli, spcty))
        pass
    
    def canActivate_3(self, cg): # A2.1.10
        #todo: Not implemented: 2 hasAcs in a rule.
        #hasActivated(cg, Caldicott-guardian())
        #hasActivated(x, Request-consent-to-referral(pat, ra, org, cli, spcty))
        pass
    
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
        #todo: Not implemented: 2 hasAcs in a rule.
        #hasActivated(x, Consent-to-referral(pat, ra, org, cli, spcty))
        #no-main-role-active(cli)
        #ra.hasActivated(y, NHS-clinician-cert(org, cli, spcty, start, end))
        #canActivate(ra, Registration-authority())
        pass
    
    def canActivate_2(self, cli): # A2.2.2
        #todo: Not implemented: 2 hasAcs in a rule.
        #hasActivated(ref, Consent-to-referral(pat, ra, org, cli, spcty))
        #no-main-role-active(cli)
        #ra@ra.hasActivated(y, NHS-clinician-cert(org, cli, spcty, start, end))
        #canActivate(ra, Registration-authority())
        pass
    
    #'A2.2.3'
    #canDeactivate(cli, cli, Ext-treating-clinician(pat, ra, org, spcty)) <-
    #	

#'A2.2.5'
#count-ext-treating-clinician-activations(count<u>, user) <-
#	hasActivated(u, Ext-treating-clinician(pat, ra, org, spcty)), u = user

class Request_third_party_consent(Role):
    def __init__(self, x, pat, id):
        super().__init__('Request-third-party-consent', ['x', 'pat', 'id']) 
        self.x, self.pat, self.id = x, pat, id
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params) or self.canActivate_3(*params) or self.canActivate_4(*params)
    
    def canActivate_1(self, pat): # A2.3.1
        pass
    
    def canActivate_2(self, ag): # A2.3.2
        pass
    
    def canActivate_3(self, cli): # A2.3.3
        pass
    
    def canActivate_4(self, cg): # A2.3.4
        pass
    
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
    
    #'A2.3.15'
    #isDeactivated(x, Third-party()) <-
    #	isDeactivated(y, Request-third-party-consent(x, pat, id)), other-third-party-requests(n, y, x), n = 0

#'A2.3.11'
#count-third-party-activations(count<u>, user) <-
#	hasActivated(u, Third-party()), u = user

class Third_party(Role):
    def __init__(self):
        super().__init__('Third-party', []) 
    
    def canActivate(self, x): # A2.3.12
        #todo: Not implemented: 2 hasAcs in a rule.
        #hasActivated(y, Request-third-party-consent(x, pat, id))
        #no-main-role-active(x)
        #"PDS"@"PDS".hasActivated(z, Register-patient(x))
        pass
    
    #'A2.3.13'
    #canDeactivate(x, x, Third-party()) <-
    #	

#'A2.3.14'
#other-third-party-requests(count<y>, x, third-party) <-
#	hasActivated(y, Request-third-party-consent(third-party, pat, id)), x != y

class Third_party_consent(Role):
    def __init__(self, x, pat, id):
        super().__init__('Third-party-consent', ['x', 'pat', 'id']) 
        self.x, self.pat, self.id = x, pat, id
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params)
    
    def canActivate_1(self, x): # A2.3.16
        #todo: Not implemented: 2 hasAcs in a rule.
        #hasActivated(x, Third-party())
        #hasActivated(y, Request-third-party-consent(x, pat, id))
        pass
    
    def canActivate_2(self, cg): # A2.3.17
        #todo: Not implemented: 2 hasAcs in a rule.
        #hasActivated(cg, Caldicott-guardian())
        #hasActivated(y, Request-third-party-consent(x, pat, id))
        pass
    
    #'A2.3.18'
    #canDeactivate(x, x, Third-party-consent(x, pat, id)) <-
    #	hasActivated(x, Third-party())
    
    #'A2.3.19'
    #canDeactivate(cg, x, Third-party-consent(x, pat, id)) <-
    #	hasActivated(cg, Caldicott-guardian())

#'A2.3.21'
#third-party-consent(group<consenter>, pat, id) <-
#	hasActivated(x, Third-party-consent(consenter, pat, id))

class Head_of_team(Role):
    def __init__(self, team):
        super().__init__('Head-of-team', ['team']) 
        self.team = team
    
    def canActivate(self, hd): # A3.1.1
        pass
    
    #'A3.1.2'
    #canDeactivate(hd, hd, Head-of-team(team)) <-
    #	

class Register_head_of_team(Role):
    def __init__(self, hd, team):
        super().__init__('Register-head-of-team', ['hd', 'team']) 
        self.hd, self.team = hd, team
    
    def canActivate(self, mgr): # A3.1.4
        #todo: Not implemented: 2 hasAcs in a rule.
        #hasActivated(mgr, HR-mgr())
        #hasActivated(x, Register-team-member(hd, team, spcty))
        #head-of-team-regs(n, hd, team)
        #n = 0
        pass
    
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
        pass
    
    def canActivate_2(self, hd): # A3.2.2
        pass
    
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
        pass
    
    def canActivate_2(self, cli): # A3.3.2
        #todo: Not implemented: 2 hasAcs in a rule.
        #hasActivated(cli, Clinician(spcty))
        #hasActivated(x, Register-team-member(cli, team, spcty))
        #canActivate(pat, Patient())
        #team-episode-regs(n, pat, team)
        #n = 0
        pass
    
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
        pass
    
    #'A3.4.2'
    #canDeactivate(cli, cli, Head-of-ward(ward)) <-
    #	

class Register_head_of_ward(Role):
    def __init__(self, cli, ward):
        super().__init__('Register-head-of-ward', ['cli', 'ward']) 
        self.cli, self.ward = cli, ward
    
    def canActivate(self, mgr): # A3.4.4
        #todo: Not implemented: 2 hasAcs in a rule.
        #hasActivated(mgr, HR-mgr())
        #hasActivated(x, Register-ward-member(cli, ward, spcty))
        #head-of-ward-regs(n, cli, ward)
        #n = 0
        pass
    
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
        pass
    
    def canActivate_2(self, hd): # A3.5.2
        pass
    
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
        pass
    
    def canActivate_2(self, hd): # A3.6.2
        pass
    
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
        pass
    
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
        #todo: Not implemented: 2 hasAcs in a rule.
        #canActivate(cli, Clinician(spcty))
        #hasActivated(x, Register-team-member(cli, team, spcty))
        #hasActivated(y, Register-team-episode(pat, team))
        #group = team
        pass
    
    def canActivate_2(self, cli): # A3.8.2
        #todo: Not implemented: 2 hasAcs in a rule.
        #canActivate(cli, Clinician(spcty))
        #hasActivated(x, Register-ward-member(cli, ward, spcty))
        #hasActivated(x, Register-ward-episode(pat, ward))
        #group = ward
        pass
    
    def canActivate_3(self, cli): # A3.8.3
        pass

class Concealed_by_clinician(Role):
    def __init__(self, pat, id, start, end):
        super().__init__('Concealed-by-clinician', ['pat', 'id', 'start', 'end']) 
        self.pat, self.id, self.start, self.end = pat, id, start, end
    
    def canActivate(self, cli): # A4.1.1
        pass
    
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
        pass
    
    def canActivate_2(self, ag): # A4.2.2
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
