from auxiliary import *
import ehr.spine, ehr.ra, ehr.pds

hasActivated = list()  # Set of (subject, role) pairs representing currently active roles.

list_of_roles = ['Register-clinician', 'Clinician', 'Register-Caldicott-guardian', 'Caldicott-guardian', 'Register-HR-mgr', 'HR-mgr', 'Register-receptionist', 'Receptionist', 'Register-patient', 'Patient', 'Agent', 'Register-agent', 'Registration-authority', 'Request-consent-to-referral', 'Consent-to-referral', 'Ext-treating-clinician', 'Request-third-party-consent', 'Third-party', 'Third-party-consent', 'Head-of-team', 'Register-head-of-team', 'Register-team-member', 'Register-team-episode', 'Head-of-ward', 'Register-head-of-ward', 'Register-ward-member', 'Register-ward-episode', 'Emergency-clinician', 'ADB-treating-clinician', 'Concealed-by-clinician', 'Concealed-by-patient']

class Register_clinician(Role):
    def __init__(self, cli, spcty):
        super().__init__('Register-clinician', cli = cli, spcty = spcty)
    
    def canActivate(self, mgr): # A1.1.1
        #
        # canActivate(mgr, Register-clinician(cli, spcty)) <-
        # hasActivated(mgr, HR-mgr()), 
        # clinician-regs(n, cli, spcty), 
        # n = 0
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "HR-mgr" and 
            subj == mgr and 
            clinician_regs(self.cli, self.spcty) == 0
        }
    
    def canDeactivate(self, mgr, x): # A1.1.2
        #
        # canDeactivate(mgr, x, Register-clinician(cli, spcty)) <-
        # hasActivated(mgr, HR-mgr())
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "HR-mgr" and 
            subj == mgr
        }
    
    def onDeactivate(self, subject):
        # A1.1.6 -- deactive Clinician(spcty):
        hasActivated -= { (subj, role) for (subj, role) in hasActivated if subj == self.cli and role.name == 'Clinician' and role.spcty == self.spcty }
        
        # A3.2.5 -- deactive Register-team-member(mem, team, spcty):
        hasActivated -= { (subj, role) for (subj, role) in hasActivated if role.name == 'Register_team_member' and role.mem == self.cli and role.spcty == self.spcty }
        
        # A3.5.6 -- deactive Register-ward-member(cli, ward, spcty):
        hasActivated -= { (subj, role) for (subj, role) in hasActivated if role.name == 'Register_ward_member' and role.cli == self.cli and role.spcty == self.spcty }

def clinician_regs(cli, spcty): # A1.1.3
    #
    # clinician-regs(count<x>, cli, spcty) <-
    # hasActivated(x, Register-clinician(cli, spcty))
    #
    return len([
        True for subj, role in hasActivated if 
        role.name == "Register-clinician" and 
        role.cli == cli and 
        role.spcty == spcty
    ]

class Clinician(Role):
    def __init__(self, spcty):
        super().__init__('Clinician', spcty = spcty)
    
    def canActivate(self, cli): # A1.1.4
        #
        # canActivate(cli, Clinician(spcty)) <-
        # hasActivated(x, Register-clinician(cli, spcty)), 
        # no-main-role-active(cli)
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Register-clinician" and 
            role.cli == cli and 
            role.spcty == self.spcty and 
            no_main_role_active(role.cli)
        }
    
    def canDeactivate(self, cli, cli_): # A1.1.5
        #
        # canDeactivate(cli, cli, Clinician(spcty)) <-
        # 
        #
        return (
            cli == cli_
        )
    
    def onDeactivate(self, subject):
        # A3.7.5 -- deactive Emergency-clinician(pat):
        hasActivated -= { (subj, role) for (subj, role) in hasActivated if subj == subject and role.name == 'Emergency_clinician' }

def count_clinician_activations(user): # A1.1.7
    #
    # count-clinician-activations(count<u>, user) <-
    # hasActivated(u, Clinician(spcty)), 
    # u = user
    #
    return len([
        True for subj, role in hasActivated if 
        role.name == "Clinician" and 
        subj == user
    ]

class Register_Caldicott_guardian(Role):
    def __init__(self, cg):
        super().__init__('Register-Caldicott-guardian', cg = cg)
    
    def canActivate(self, mgr): # A1.2.1
        #
        # canActivate(mgr, Register-Caldicott-guardian(cg)) <-
        # hasActivated(mgr, HR-mgr()), 
        # cg-regs(n, cg), 
        # n = 0
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "HR-mgr" and 
            subj == mgr and 
            cg_regs(self.cg) == 0
        }
    
    def canDeactivate(self, mgr, x): # A1.2.2
        #
        # canDeactivate(mgr, x, Register-Caldicott-guardian(cg)) <-
        # hasActivated(mgr, HR-mgr())
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "HR-mgr" and 
            subj == mgr
        }
    
    def onDeactivate(self, subject):
        # A1.2.6 -- deactive Caldicott-guardian():
        hasActivated -= { (subj, role) for (subj, role) in hasActivated if subj == self.cg and role.name == 'Caldicott_guardian' }

def cg_regs(cg): # A1.2.3
    #
    # cg-regs(count<x>, cg) <-
    # hasActivated(x, Register-Caldicott-guardian(cg))
    #
    return len([
        True for subj, role in hasActivated if 
        role.name == "Register-Caldicott-guardian" and 
        role.cg == cg
    ]

class Caldicott_guardian(Role):
    def __init__(self):
        super().__init__('Caldicott-guardian')
    
    def canActivate(self, cg): # A1.2.4
        #
        # canActivate(cg, Caldicott-guardian()) <-
        # hasActivated(x, Register-Caldicott-guardian(cg)), 
        # no-main-role-active(cg)
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Register-Caldicott-guardian" and 
            role.cg == cg and 
            no_main_role_active(role.cg)
        }
    
    def canDeactivate(self, cg, cg_): # A1.2.5
        #
        # canDeactivate(cg, cg, Caldicott-guardian()) <-
        # 
        #
        return (
            cg == cg_
        )

def count_caldicott_guardian_activations(user): # A1.2.7
    #
    # count-caldicott-guardian-activations(count<u>, user) <-
    # hasActivated(u, Caldicott-guardian()), 
    # u = user
    #
    return len([
        True for subj, role in hasActivated if 
        role.name == "Caldicott-guardian" and 
        subj == user
    ]

class Register_HR_mgr(Role):
    def __init__(self, mgr2):
        super().__init__('Register-HR-mgr', mgr2 = mgr2)
    
    def canActivate(self, mgr): # A1.3.1
        #
        # canActivate(mgr, Register-HR-mgr(mgr2)) <-
        # hasActivated(mgr, HR-mgr()), 
        # hr-manager-regs(n, mgr), 
        # n = 0
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "HR-mgr" and 
            subj == mgr and 
            hr_manager_regs(subj) == 0
        }
    
    def canDeactivate(self, mgr, x): # A1.3.2
        #
        # canDeactivate(mgr, x, Register-HR-mgr(mgr2)) <-
        # hasActivated(mgr, HR-mgr())
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "HR-mgr" and 
            subj == mgr
        }
    
    def onDeactivate(self, subject):
        # A1.3.6 -- deactive HR-mgr():
        hasActivated -= { (subj, role) for (subj, role) in hasActivated if subj == self.mgr2 and role.name == 'HR_mgr' }

def hr_manager_regs(mgr): # A1.3.3
    #
    # hr-manager-regs(count<x>, mgr) <-
    # hasActivated(x, Register-HR-mgr(mgr))
    #
    return len([
        True for subj, role in hasActivated if 
        role.name == "Register-HR-mgr" and 
        role.mgr == mgr
    ]

class HR_mgr(Role):
    def __init__(self):
        super().__init__('HR-mgr')
    
    def canActivate(self, mgr): # A1.3.4
        #
        # canActivate(mgr, HR-mgr()) <-
        # hasActivated(x, Register-HR-mgr(mgr)), 
        # no-main-role-active(mgr)
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Register-HR-mgr" and 
            role.mgr == mgr and 
            no_main_role_active(role.mgr)
        }
    
    def canDeactivate(self, mgr, mgr_): # A1.3.5
        #
        # canDeactivate(mgr, mgr, HR-mgr()) <-
        # 
        #
        return (
            mgr == mgr_
        )

def count_hr_mgr_activations(user): # A1.3.7
    #
    # count-hr-mgr-activations(count<u>, user) <-
    # hasActivated(u, HR-mgr()), 
    # u = user
    #
    return len([
        True for subj, role in hasActivated if 
        role.name == "HR-mgr" and 
        subj == user
    ]

class Register_receptionist(Role):
    def __init__(self, rec):
        super().__init__('Register-receptionist', rec = rec)
    
    def canActivate(self, mgr): # A1.4.1
        #
        # canActivate(mgr, Register-receptionist(rec)) <-
        # hasActivated(mgr, HR-mgr()), 
        # receptionist-regs(n, rec), 
        # n = 0
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "HR-mgr" and 
            subj == mgr and 
            receptionist_regs(self.rec) == 0
        }
    
    def canDeactivate(self, mgr, x): # A1.4.2
        #
        # canDeactivate(mgr, x, Register-receptionist(rec)) <-
        # hasActivated(mgr, HR-mgr())
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "HR-mgr" and 
            subj == mgr
        }
    
    def onDeactivate(self, subject):
        # A1.4.6 -- deactive Receptionist():
        hasActivated -= { (subj, role) for (subj, role) in hasActivated if subj == self.rec and role.name == 'Receptionist' }

def receptionist_regs(rec): # A1.4.3
    #
    # receptionist-regs(count<x>, rec) <-
    # hasActivated(x, Register-receptionist(rec))
    #
    return len([
        True for subj, role in hasActivated if 
        role.name == "Register-receptionist" and 
        role.rec == rec
    ]

class Receptionist(Role):
    def __init__(self):
        super().__init__('Receptionist')
    
    def canActivate(self, rec): # A1.4.4
        #
        # canActivate(rec, Receptionist()) <-
        # hasActivated(x, Register-receptionist(rec))
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Register-receptionist" and 
            role.rec == rec
        }
    
    def canDeactivate(self, rec, rec_): # A1.4.5
        #
        # canDeactivate(rec, rec, Receptionist()) <-
        # 
        #
        return (
            rec == rec_
        )

def count_receptionist_activations(user): # A1.4.7
    #
    # count-receptionist-activations(count<u>, user) <-
    # hasActivated(u, Receptionist()), 
    # u = user
    #
    return len([
        True for subj, role in hasActivated if 
        role.name == "Receptionist" and 
        subj == user
    ]

class Register_patient(Role):
    def __init__(self, pat):
        super().__init__('Register-patient', pat = pat)
    
    def canActivate(self, rec): # A1.5.1
        #
        # canActivate(rec, Register-patient(pat)) <-
        # hasActivated(rec, Receptionist()), 
        # patient-regs(n, pat), 
        # n = 0
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Receptionist" and 
            subj == rec and 
            patient_regs(self.pat) == 0
        }
    
    def canDeactivate(self, rec, x): # A1.5.2
        #
        # canDeactivate(rec, x, Register-patient(pat)) <-
        # hasActivated(rec, Receptionist())
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Receptionist" and 
            subj == rec
        }
    
    def onDeactivate(self, subject):
        # A1.5.6 -- deactive Patient():
        hasActivated -= { (subj, role) for (subj, role) in hasActivated if subj == self.pat and role.name == 'Patient' }
        
        # A1.6.9 -- deactive Register-agent(agent, pat):
        hasActivated -= { (subj, role) for (subj, role) in hasActivated if role.name == 'Register_agent' and role.pat == self.pat }
        
        # A2.1.6 -- deactive Request-consent-to-referral(pat, ra, org, cli, spcty):
        hasActivated -= { (subj, role) for (subj, role) in hasActivated if role.name == 'Request_consent_to_referral' and role.pat == self.pat }
        
        # A2.3.10 -- deactive Request-third-party-consent(x2, pat, id):
        hasActivated -= { (subj, role) for (subj, role) in hasActivated if role.name == 'Request_third_party_consent' and role.pat == self.pat }
        
        # A2.3.20 -- deactive Third-party-consent(x, pat, id):
        hasActivated -= { (subj, role) for (subj, role) in hasActivated if role.name == 'Third_party_consent' and role.pat == self.pat }
        
        # A3.3.6 -- deactive Register-team-episode(pat, team):
        hasActivated -= { (subj, role) for (subj, role) in hasActivated if role.name == 'Register_team_episode' and role.pat == self.pat }
        
        # A3.6.6 -- deactive Register-ward-episode(pat, ward):
        hasActivated -= { (subj, role) for (subj, role) in hasActivated if role.name == 'Register_ward_episode' and role.pat == self.pat }
        
        # A3.7.4 -- deactive Emergency-clinician(pat):
        hasActivated -= { (subj, role) for (subj, role) in hasActivated if role.name == 'Emergency_clinician' and role.pat == self.pat }
        
        # A4.1.5 -- deactive Concealed-by-clinician(pat, id, start, end):
        hasActivated -= { (subj, role) for (subj, role) in hasActivated if role.name == 'Concealed_by_clinician' and role.pat == self.pat }
        
        # A4.2.6 -- deactive Concealed-by-patient(what, whom, start, end):
        hasActivated -= { (subj, role) for (subj, role) in hasActivated if role.name == 'Concealed_by_patient' }

def patient_regs(pat): # A1.5.3
    #
    # patient-regs(count<x>, pat) <-
    # hasActivated(x, Register-patient(pat))
    #
    return len([
        True for subj, role in hasActivated if 
        role.name == "Register-patient" and 
        role.pat == pat
    ]

class Patient(Role):
    def __init__(self):
        super().__init__('Patient')
    
    def canActivate(self, pat): # A1.5.4
        #
        # canActivate(pat, Patient()) <-
        # hasActivated(x, Register-patient(pat)), 
        # no-main-role-active(pat), 
        # "PDS"@"PDS".hasActivated(y, Register-patient(pat))
        #
        return {
            True for (subj1, role1) in hasActivated for (subj2, role2) in ehr.pds.hasActivated if 
            role1.name == "Register-patient" and 
            role2.name == "Register-patient" and 
            role1.pat == pat and 
            role2.pat == pat and 
            no_main_role_active(role2.pat)
        }
    
    def canDeactivate(self, pat, pat_): # A1.5.5
        #
        # canDeactivate(pat, pat, Patient()) <-
        # 
        #
        return (
            pat == pat_
        )

def count_patient_activations(user): # A1.5.7
    #
    # count-patient-activations(count<u>, user) <-
    # hasActivated(u, Patient()), 
    # u = user
    #
    return len([
        True for subj, role in hasActivated if 
        role.name == "Patient" and 
        subj == user
    ]

class Agent(Role):
    def __init__(self, pat):
        super().__init__('Agent', pat = pat)
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params)
    
    def canActivate_1(self, agent): # A1.6.1
        #
        # canActivate(agent, Agent(pat)) <-
        # hasActivated(x, Register-agent(agent, pat)), 
        # "PDS"@"PDS".hasActivated(x, Register-patient(agent)), 
        # no-main-role-active(agent)
        #
        return {
            True for (subj1, role1) in hasActivated for (subj2, role2) in ehr.pds.hasActivated if 
            role1.name == "Register-agent" and 
            role2.name == "Register-patient" and 
            role1.pat == self.pat and 
            role1.agent == agent and 
            role2.agent == agent and 
            no_main_role_active(role2.agent)
        }
    
    def canActivate_2(self, agent): # A1.6.2
        #
        # canActivate(agent, Agent(pat)) <-
        # canActivate(pat, Patient()), 
        # no-main-role-active(agent), 
        # "PDS"@"PDS".hasActivated(x, Register-patient(agent)), 
        # "Spine"@"Spine".canActivate(agent, Agent(pat))
        #
        return {
            True for subj, role in ehr.pds.hasActivated if 
            role.name == "Register-patient" and 
            role.agent == agent and 
            canActivate(self.pat, Patient()) and 
            canActivate(role.agent, ehr.spine.Agent(self.pat)) and 
            no_main_role_active(role.agent)
        }

def count_agent_activations(user): # A1.6.4
    #
    # count-agent-activations(count<u>, user) <-
    # hasActivated(u, Agent(pat)), 
    # u = user
    #
    return len([
        True for subj, role in hasActivated if 
        role.name == "Agent" and 
        subj == user
    ]

class Register_agent(Role):
    def __init__(self, agent, pat):
        super().__init__('Register-agent', agent = agent, pat = pat)
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params)
    
    def canActivate_1(self, pat): # A1.6.5
        #
        # canActivate(pat, Register-agent(agent, pat)) <-
        # hasActivated(pat, Patient())
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Patient" and 
            subj == pat
        }
    
    def canActivate_2(self, cg): # A1.6.6
        #
        # canActivate(cg, Register-agent(agent, pat)) <-
        # hasActivated(cg, Caldicott-guardian()), 
        # canActivate(pat, Patient())
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Caldicott-guardian" and 
            subj == cg and 
            canActivate(self.pat, Patient())
        }
    
    def canDeactivate(self, *params):
        return self.canDeactivate_1(*params) or self.canDeactivate_2(*params)
    
    def canDeactivate_1(self, pat, pat_): # A1.6.7
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
    
    def canDeactivate_2(self, cg, x): # A1.6.8
        #
        # canDeactivate(cg, x, Register-agent(agent, pat)) <-
        # hasActivated(cg, Caldicott-guardian())
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Caldicott-guardian" and 
            subj == cg
        }
    
    def onDeactivate(self, subject):
        # A1.6.3 -- deactive Agent(pat):
        hasActivated -= { (subj, role) for (subj, role) in hasActivated if subj == self.agent and role.name == 'Agent' and role.pat == self.pat }

def other_agent_regs(x, ag, pat): # A1.6.10
    #
    # other-agent-regs(count<y>, x, ag, pat) <-
    # hasActivated(y, Register-agent(ag, pat)), 
    # x != y
    #
    return len([
        True for subj, role in hasActivated if 
        role.name == "Register-agent" and 
        role.pat == pat and 
        role.ag == ag and 
        x != subj
    ]

def no_main_role_active(user): # A1.7.1
    return  count_agent_activations(user) == 0 and \
            count_caldicott_guardian_activations(user) == 0 and \
            count_clinician_activations(user) == 0 and \
            count_ext_treating_clinician_activations(user) == 0 and \
            count_hr_mgr_activations(user) == 0 and \
            count_patient_activations(user) == 0 and \
            count_receptionist_activations(user) == 0 and \
            count_third_party_activations(user) == 0

class Registration_authority(Role):
    def __init__(self):
        super().__init__('Registration-authority')
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params)
    
    def canActivate_1(self, ra): # A1.7.2
        #
        # canActivate(ra, Registration-authority()) <-
        # "NHS".hasActivated(x, NHS-registration-authority(ra, start, end)), 
        # Current-time() in [start, end]
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "NHS-registration-authority" and 
            role.ra == ra and 
            Current_time() in vrange(role.start, role.end)
        }
    
    def canActivate_2(self, ra): # A1.7.3
        #
        # canActivate(ra, Registration-authority()) <-
        # ra@"NHS".hasActivated(x, NHS-registration-authority(ra, start, end)), 
        # Current-time() in [start, end]
        #
        return {
            True for subj, role in ehr.ra.hasActivated if 
            role.name == "NHS-registration-authority" and 
            role.ra == ra and 
            Current_time() in vrange(role.start, role.end)
        }

class Request_consent_to_referral(Role):
    def __init__(self, pat, ra, org, cli2, spcty2):
        super().__init__('Request-consent-to-referral', pat = pat, ra = ra, org = org, cli2 = cli2, spcty2 = spcty2)
    
    def canActivate(self, cli1): # A2.1.1
        #
        # canActivate(cli1, Request-consent-to-referral(pat, ra, org, cli2, spcty2)) <-
        # hasActivated(cli1, Clinician(spcty1)), 
        # canActivate(cli1, ADB-treating-clinician(pat, team, spcty1))
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Clinician" and 
            subj == cli1 and 
            canActivate(subj, ADB_treating_clinician(self.pat, Wildcard(), role.spcty1))
        }
    
    def canDeactivate(self, *params):
        return self.canDeactivate_1(*params) or self.canDeactivate_2(*params) or self.canDeactivate_3(*params) or self.canDeactivate_4(*params)
    
    def canDeactivate_1(self, cli, cli_): # A2.1.2
        #
        # canDeactivate(cli, cli, Request-consent-to-referral(pat, ra, org, cli, spcty)) <-
        # hasActivated(cli, Clinician(spcty))
        #
        return {
            True for subj, role in hasActivated if 
            cli == cli_ and 
            role.name == "Clinician" and 
            subj == cli
        }
    
    def canDeactivate_2(self, pat, x): # A2.1.3
        #
        # canDeactivate(pat, x, Request-consent-to-referral(pat, ra, org, cli, spcty)) <-
        # hasActivated(pat, Patient())
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Patient" and 
            subj == pat
        }
    
    def canDeactivate_3(self, ag, x): # A2.1.4
        #
        # canDeactivate(ag, x, Request-consent-to-referral(pat, ra, org, cli, spcty)) <-
        # hasActivated(ag, Agent(pat))
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Agent" and 
            role.pat == self.pat and 
            subj == ag
        }
    
    def canDeactivate_4(self, cg, x): # A2.1.5
        #
        # canDeactivate(cg, x, Request-consent-to-referral(pat, ra, org, cli, spcty)) <-
        # hasActivated(cg, Caldicott-guardian())
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Caldicott-guardian" and 
            subj == cg
        }
    
    def onDeactivate(self, subject):
        # A2.1.11 -- deactive Consent-to-referral(pat, ra, org, cli, spcty):
        hasActivated -= { (subj, role) for (subj, role) in hasActivated if role.name == 'Consent_to_referral' and role.pat == self.pat and role.ra == self.ra and role.org == self.org and role.cli == self.cli2 and role.spcty == self.spcty2 }

def other_consent_to_referral_requests(x, pat, ra, org, cli, spcty): # A2.1.7
    #
    # other-consent-to-referral-requests(count<y>, x, pat, ra, org, cli, spcty) <-
    # hasActivated(y, Request-consent-to-referral(pat, ra, org, cli, spcty)), 
    # x != y
    #
    return len([
        True for subj, role in hasActivated if 
        role.name == "Request-consent-to-referral" and 
        role.org == org and 
        role.pat == pat and 
        role.cli == cli and 
        role.spcty == spcty and 
        role.ra == ra and 
        x != subj
    ]

class Consent_to_referral(Role):
    def __init__(self, pat, ra, org, cli, spcty):
        super().__init__('Consent-to-referral', pat = pat, ra = ra, org = org, cli = cli, spcty = spcty)
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params) or self.canActivate_3(*params)
    
    def canActivate_1(self, pat): # A2.1.8
        #
        # canActivate(pat, Consent-to-referral(pat, ra, org, cli, spcty)) <-
        # hasActivated(pat, Patient()), 
        # hasActivated(x, Request-consent-to-referral(pat, ra, org, cli, spcty))
        #
        return {
            True for (subj1, role1) in hasActivated for (subj2, role2) in hasActivated if 
            role1.name == "Patient" and 
            role2.name == "Request-consent-to-referral" and 
            subj1 == pat and 
            role2.cli == self.cli and 
            role2.pat == pat and 
            role2.org == self.org and 
            role2.spcty == self.spcty and 
            role2.ra == self.ra
        }
    
    def canActivate_2(self, pat): # A2.1.9
        #
        # canActivate(pat, Consent-to-referral(pat, ra, org, cli, spcty)) <-
        # hasActivated(pat, Agent(pat)), 
        # hasActivated(x, Request-consent-to-referral(pat, ra, org, cli, spcty))
        #
        return {
            True for (subj1, role1) in hasActivated for (subj2, role2) in hasActivated if 
            role1.name == "Agent" and 
            role2.name == "Request-consent-to-referral" and 
            subj1 == pat and 
            role1.pat == pat and 
            role2.cli == self.cli and 
            role2.pat == pat and 
            role2.org == self.org and 
            role2.spcty == self.spcty and 
            role2.ra == self.ra
        }
    
    def canActivate_3(self, cg): # A2.1.10
        #
        # canActivate(cg, Consent-to-referral(pat, ra, org, cli, spcty)) <-
        # hasActivated(cg, Caldicott-guardian()), 
        # hasActivated(x, Request-consent-to-referral(pat, ra, org, cli, spcty))
        #
        return {
            True for (subj1, role1) in hasActivated for (subj2, role2) in hasActivated if 
            role1.name == "Caldicott-guardian" and 
            role2.name == "Request-consent-to-referral" and 
            subj1 == cg and 
            role2.org == self.org and 
            role2.pat == self.pat and 
            role2.cli == self.cli and 
            role2.spcty == self.spcty and 
            role2.ra == self.ra
        }
    
    def onDeactivate(self, subject):
        # A2.2.4 -- deactive Ext-treating-clinician(pat, ra, org, spcty):
        hasActivated -= { (subj, role) for (subj, role) in hasActivated if role.name == 'Ext_treating_clinician' and role.pat == self.pat and role.ra == self.ra and role.org == self.org and role.spcty == self.spcty }

def other_referral_consents(x, pat, ra, org, cli, spcty): # A2.1.12
    #
    # other-referral-consents(count<y>, x, pat, ra, org, cli, spcty) <-
    # hasActivated(y, Consent-to-referral(pat, ra, org, cli, spcty)), 
    # x != y
    #
    return len([
        True for subj, role in hasActivated if 
        role.name == "Consent-to-referral" and 
        role.org == org and 
        role.pat == pat and 
        role.cli == cli and 
        role.spcty == spcty and 
        role.ra == ra and 
        x != subj
    ]

class Ext_treating_clinician(Role):
    def __init__(self, pat, ra, org, spcty):
        super().__init__('Ext-treating-clinician', pat = pat, ra = ra, org = org, spcty = spcty)
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params)
    
    def canActivate_1(self, cli): # A2.2.1
        #
        # canActivate(cli, Ext-treating-clinician(pat, ra, org, spcty)) <-
        # hasActivated(x, Consent-to-referral(pat, ra, org, cli, spcty)), 
        # no-main-role-active(cli), 
        # ra.hasActivated(y, NHS-clinician-cert(org, cli, spcty, start, end)), 
        # canActivate(ra, Registration-authority())
        #
        return {
            True for (subj1, role1) in hasActivated for (subj2, role2) in hasActivated if 
            role1.name == "Consent-to-referral" and 
            role2.name == "NHS-clinician-cert" and 
            role1.org == self.org and 
            role1.pat == self.pat and 
            role1.cli == cli and 
            role1.spcty == self.spcty and 
            role1.ra == self.ra and 
            role2.org == self.org and 
            role2.cli == cli and 
            role2.spcty == self.spcty and 
            canActivate(role1.ra, Registration_authority()) and 
            no_main_role_active(role2.cli)
        }
    
    def canActivate_2(self, cli): # A2.2.2
        #
        # canActivate(cli, Ext-treating-clinician(pat, ra, org, spcty)) <-
        # hasActivated(ref, Consent-to-referral(pat, ra, org, cli, spcty)), 
        # no-main-role-active(cli), 
        # ra@ra.hasActivated(y, NHS-clinician-cert(org, cli, spcty, start, end)), 
        # canActivate(ra, Registration-authority())
        #
        return {
            True for (subj1, role1) in hasActivated for (subj2, role2) in ehr.ra.hasActivated if 
            role1.name == "Consent-to-referral" and 
            role2.name == "NHS-clinician-cert" and 
            role1.org == self.org and 
            role1.pat == self.pat and 
            role1.cli == cli and 
            role1.spcty == self.spcty and 
            role1.ra == self.ra and 
            role2.org == self.org and 
            role2.cli == cli and 
            role2.spcty == self.spcty and 
            canActivate(role1.ra, Registration_authority()) and 
            no_main_role_active(role2.cli)
        }
    
    def canDeactivate(self, cli, cli_): # A2.2.3
        #
        # canDeactivate(cli, cli, Ext-treating-clinician(pat, ra, org, spcty)) <-
        # 
        #
        return (
            cli == cli_
        )

def count_ext_treating_clinician_activations(user): # A2.2.5
    #
    # count-ext-treating-clinician-activations(count<u>, user) <-
    # hasActivated(u, Ext-treating-clinician(pat, ra, org, spcty)), 
    # u = user
    #
    return len([
        True for subj, role in hasActivated if 
        role.name == "Ext-treating-clinician" and 
        subj == user
    ]

class Request_third_party_consent(Role):
    def __init__(self, x, pat, id):
        super().__init__('Request-third-party-consent', x = x, pat = pat, id = id)
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params) or self.canActivate_3(*params) or self.canActivate_4(*params)
    
    def canActivate_1(self, pat): # A2.3.1
        #
        # canActivate(pat, Request-third-party-consent(x, pat, id)) <-
        # hasActivated(pat, Patient()), 
        # x in Get-record-third-parties(pat, id)
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Patient" and 
            subj == pat and 
            self.x in Get_record_third_parties(subj, self.id)
        }
    
    def canActivate_2(self, ag): # A2.3.2
        #
        # canActivate(ag, Request-third-party-consent(x, pat, id)) <-
        # hasActivated(ag, Agent(pat)), 
        # x in Get-record-third-parties(pat, id)
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Agent" and 
            role.pat == self.pat and 
            subj == ag and 
            self.x in Get_record_third_parties(role.pat, self.id)
        }
    
    def canActivate_3(self, cli): # A2.3.3
        #
        # canActivate(cli, Request-third-party-consent(x, pat, id)) <-
        # hasActivated(cli, Clinician(spcty)), 
        # x in Get-record-third-parties(pat, id)
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Clinician" and 
            subj == cli and 
            self.x in Get_record_third_parties(self.pat, self.id)
        }
    
    def canActivate_4(self, cg): # A2.3.4
        #
        # canActivate(cg, Request-third-party-consent(x, pat, id)) <-
        # hasActivated(cg, Caldicott-guardian()), 
        # x in Get-record-third-parties(pat, id)
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Caldicott-guardian" and 
            subj == cg and 
            self.x in Get_record_third_parties(self.pat, self.id)
        }
    
    def canDeactivate(self, *params):
        return self.canDeactivate_1(*params) or self.canDeactivate_2(*params) or self.canDeactivate_3(*params) or self.canDeactivate_4(*params) or self.canDeactivate_5(*params)
    
    def canDeactivate_1(self, pat, pat_): # A2.3.5
        #
        # canDeactivate(pat, pat, Request-third-party-consent(x, pat, id)) <-
        # hasActivated(pat, Patient())
        #
        return {
            True for subj, role in hasActivated if 
            pat == pat_ and 
            role.name == "Patient" and 
            subj == pat
        }
    
    def canDeactivate_2(self, ag, ag_): # A2.3.6
        #
        # canDeactivate(ag, ag, Request-third-party-consent(x, pat, id)) <-
        # hasActivated(pat, Agent(pat))
        #
        return {
            True for subj, role in hasActivated if 
            ag == ag_ and 
            role.name == "Agent" and 
            role.pat == self.pat and 
            subj == role.pat
        }
    
    def canDeactivate_3(self, cli, cli_): # A2.3.7
        #
        # canDeactivate(cli, cli, Request-third-party-consent(x, pat, id)) <-
        # hasActivated(cli, Clinician(spcty))
        #
        return {
            True for subj, role in hasActivated if 
            cli == cli_ and 
            role.name == "Clinician" and 
            subj == cli
        }
    
    def canDeactivate_4(self, cg, x): # A2.3.8
        #
        # canDeactivate(cg, x, Request-third-party-consent(y, pat, id)) <-
        # hasActivated(cg, Caldicott-guardian())
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Caldicott-guardian" and 
            subj == cg
        }
    
    def canDeactivate_5(self, x, y): # A2.3.9
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
        # A2.3.15 -- deactive Third-party():
        hasActivated -= { (subj, role) for (subj, role) in hasActivated if subj == self.x and role.name == 'Third_party' }

def count_third_party_activations(user): # A2.3.11
    #
    # count-third-party-activations(count<u>, user) <-
    # hasActivated(u, Third-party()), 
    # u = user
    #
    return len([
        True for subj, role in hasActivated if 
        role.name == "Third-party" and 
        subj == user
    ]

class Third_party(Role):
    def __init__(self):
        super().__init__('Third-party')
    
    def canActivate(self, x): # A2.3.12
        #
        # canActivate(x, Third-party()) <-
        # hasActivated(y, Request-third-party-consent(x, pat, id)), 
        # no-main-role-active(x), 
        # "PDS"@"PDS".hasActivated(z, Register-patient(x))
        #
        return {
            True for (subj1, role1) in hasActivated for (subj2, role2) in ehr.pds.hasActivated if 
            role1.name == "Request-third-party-consent" and 
            role2.name == "Register-patient" and 
            role1.x == x and 
            role2.x == x and 
            no_main_role_active(role2.x)
        }
    
    def canDeactivate(self, x, x_): # A2.3.13
        #
        # canDeactivate(x, x, Third-party()) <-
        # 
        #
        return (
            x == x_
        )

def other_third_party_requests(x, third_party): # A2.3.14
    #
    # other-third-party-requests(count<y>, x, third-party) <-
    # hasActivated(y, Request-third-party-consent(third-party, pat, id)), 
    # x != y
    #
    return len([
        True for subj, role in hasActivated if 
        role.name == "Request-third-party-consent" and 
        x != subj
    ]

class Third_party_consent(Role):
    def __init__(self, x, pat, id):
        super().__init__('Third-party-consent', x = x, pat = pat, id = id)
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params)
    
    def canActivate_1(self, x): # A2.3.16
        #
        # canActivate(x, Third-party-consent(x, pat, id)) <-
        # hasActivated(x, Third-party()), 
        # hasActivated(y, Request-third-party-consent(x, pat, id))
        #
        return {
            True for (subj1, role1) in hasActivated for (subj2, role2) in hasActivated if 
            role1.name == "Third-party" and 
            role2.name == "Request-third-party-consent" and 
            subj1 == x and 
            role2.pat == self.pat and 
            role2.x == x and 
            role2.id == self.id
        }
    
    def canActivate_2(self, cg): # A2.3.17
        #
        # canActivate(cg, Third-party-consent(x, pat, id)) <-
        # hasActivated(cg, Caldicott-guardian()), 
        # hasActivated(y, Request-third-party-consent(x, pat, id))
        #
        return {
            True for (subj1, role1) in hasActivated for (subj2, role2) in hasActivated if 
            role1.name == "Caldicott-guardian" and 
            role2.name == "Request-third-party-consent" and 
            subj1 == cg and 
            role2.pat == self.pat and 
            role2.x == self.x and 
            role2.id == self.id
        }
    
    def canDeactivate(self, *params):
        return self.canDeactivate_1(*params) or self.canDeactivate_2(*params)
    
    def canDeactivate_1(self, x, x_): # A2.3.18
        #
        # canDeactivate(x, x, Third-party-consent(x, pat, id)) <-
        # hasActivated(x, Third-party())
        #
        return {
            True for subj, role in hasActivated if 
            x == x_ and 
            role.name == "Third-party" and 
            subj == x
        }
    
    def canDeactivate_2(self, cg, x): # A2.3.19
        #
        # canDeactivate(cg, x, Third-party-consent(x, pat, id)) <-
        # hasActivated(cg, Caldicott-guardian())
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Caldicott-guardian" and 
            subj == cg
        }

def third_party_consent(pat, id): # A2.3.21
    #
    # third-party-consent(group<consenter>, pat, id) <-
    # hasActivated(x, Third-party-consent(consenter, pat, id))
    #
    return {
        role.consenter for subj, role in hasActivated if 
        role.name == "Third-party-consent" and 
        role.pat == pat and 
        role.id == id
    }

class Head_of_team(Role):
    def __init__(self, team):
        super().__init__('Head-of-team', team = team)
    
    def canActivate(self, hd): # A3.1.1
        #
        # canActivate(hd, Head-of-team(team)) <-
        # hasActivated(x, Register-head-of-team(hd, team))
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Register-head-of-team" and 
            role.hd == hd and 
            role.team == self.team
        }
    
    def canDeactivate(self, hd, hd_): # A3.1.2
        #
        # canDeactivate(hd, hd, Head-of-team(team)) <-
        # 
        #
        return (
            hd == hd_
        )

class Register_head_of_team(Role):
    def __init__(self, hd, team):
        super().__init__('Register-head-of-team', hd = hd, team = team)
    
    def canActivate(self, mgr): # A3.1.4
        #
        # canActivate(mgr, Register-head-of-team(hd, team)) <-
        # hasActivated(mgr, HR-mgr()), 
        # hasActivated(x, Register-team-member(hd, team, spcty)), 
        # head-of-team-regs(n, hd, team), 
        # n = 0
        #
        return {
            True for (subj1, role1) in hasActivated for (subj2, role2) in hasActivated if 
            role1.name == "HR-mgr" and 
            role2.name == "Register-team-member" and 
            subj1 == mgr and 
            role2.hd == self.hd and 
            role2.team == self.team and 
            head_of_team_regs(role2.hd, role2.team) == 0
        }
    
    def canDeactivate(self, mgr, x): # A3.1.5
        #
        # canDeactivate(mgr, x, Register-head-of-team(hd, team)) <-
        # hasActivated(mgr, HR-mgr())
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "HR-mgr" and 
            subj == mgr
        }
    
    def onDeactivate(self, subject):
        # A3.1.3 -- deactive Head-of-team(team):
        hasActivated -= { (subj, role) for (subj, role) in hasActivated if subj == self.hd and role.name == 'Head_of_team' and role.team == self.team }

def head_of_team_regs(hd, team): # A3.1.7
    #
    # head-of-team-regs(count<x>, hd, team) <-
    # hasActivated(x, Register-head-of-team(hd, team))
    #
    return len([
        True for subj, role in hasActivated if 
        role.name == "Register-head-of-team" and 
        role.hd == hd and 
        role.team == team
    ]

class Register_team_member(Role):
    def __init__(self, mem, team, spcty):
        super().__init__('Register-team-member', mem = mem, team = team, spcty = spcty)
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params)
    
    def canActivate_1(self, mgr): # A3.2.1
        #
        # canActivate(mgr, Register-team-member(mem, team, spcty)) <-
        # hasActivated(mgr, HR-mgr()), 
        # canActivate(mem, Clinician(spcty)), 
        # team-member-regs(n, mem, team, spcty), 
        # n = 0
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "HR-mgr" and 
            subj == mgr and 
            canActivate(self.mem, Clinician(self.spcty)) and 
            team_member_regs(self.mem, self.team, self.spcty) == 0
        }
    
    def canActivate_2(self, hd): # A3.2.2
        #
        # canActivate(hd, Register-team-member(mem, team, spcty)) <-
        # hasActivated(hd, Clinician(spcty2)), 
        # canActivate(hd, Head-of-team(team)), 
        # canActivate(mem, Clinician(spcty)), 
        # team-member-regs(n, mem, team, spcty), 
        # n = 0
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Clinician" and 
            subj == hd and 
            canActivate(subj, Head_of_team(self.team)) and 
            canActivate(self.mem, Clinician(self.spcty)) and 
            team_member_regs(self.mem, self.team, self.spcty) == 0
        }
    
    def canDeactivate(self, *params):
        return self.canDeactivate_1(*params) or self.canDeactivate_2(*params)
    
    def canDeactivate_1(self, mgr, x): # A3.2.3
        #
        # canDeactivate(mgr, x, Register-team-member(mem, team, spcty)) <-
        # hasActivated(mgr, HR-mgr())
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "HR-mgr" and 
            subj == mgr
        }
    
    def canDeactivate_2(self, hd, x): # A3.2.4
        #
        # canDeactivate(hd, x, Register-team-member(mem, team, spcty)) <-
        # hasActivated(hd, Clinician(spcty2)), 
        # canActivate(hd, Head-of-team(team))
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Clinician" and 
            subj == hd and 
            canActivate(subj, Head_of_team(self.team))
        }
    
    def onDeactivate(self, subject):
        # A3.1.6 -- deactive Register-head-of-team(hd, team):
        hasActivated -= { (subj, role) for (subj, role) in hasActivated if role.name == 'Register_head_of_team' and role.hd == self.mem and role.team == self.team }

def team_member_regs(mem, team, spcty): # A3.2.7
    #
    # team-member-regs(count<x>, mem, team, spcty) <-
    # hasActivated(x, Register-team-member(mem, team, spcty))
    #
    return len([
        True for subj, role in hasActivated if 
        role.name == "Register-team-member" and 
        role.team == team and 
        role.mem == mem and 
        role.spcty == spcty
    ]

class Register_team_episode(Role):
    def __init__(self, pat, team):
        super().__init__('Register-team-episode', pat = pat, team = team)
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params)
    
    def canActivate_1(self, rec): # A3.3.1
        #
        # canActivate(rec, Register-team-episode(pat, team)) <-
        # hasActivated(rec, Receptionist()), 
        # canActivate(pat, Patient()), 
        # team-episode-regs(n, pat, team), 
        # n = 0
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Receptionist" and 
            subj == rec and 
            canActivate(self.pat, Patient()) and 
            team_episode_regs(self.pat, self.team) == 0
        }
    
    def canActivate_2(self, cli): # A3.3.2
        #
        # canActivate(cli, Register-team-episode(pat, team)) <-
        # hasActivated(cli, Clinician(spcty)), 
        # hasActivated(x, Register-team-member(cli, team, spcty)), 
        # canActivate(pat, Patient()), 
        # team-episode-regs(n, pat, team), 
        # n = 0
        #
        return {
            True for (subj1, role1) in hasActivated for (subj2, role2) in hasActivated if 
            role1.name == "Clinician" and 
            role2.name == "Register-team-member" and 
            subj1 == cli and 
            role2.cli == cli and 
            role2.team == self.team and 
            canActivate(self.pat, Patient()) and 
            team_episode_regs(self.pat, role2.team) == 0
        }
    
    def canDeactivate(self, *params):
        return self.canDeactivate_1(*params) or self.canDeactivate_2(*params) or self.canDeactivate_3(*params)
    
    def canDeactivate_1(self, cg, x): # A3.3.3
        #
        # canDeactivate(cg, x, Register-team-episode(pat, team)) <-
        # hasActivated(cg, Caldicott-guardian())
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Caldicott-guardian" and 
            subj == cg
        }
    
    def canDeactivate_2(self, rec, x): # A3.3.4
        #
        # canDeactivate(rec, x, Register-team-episode(pat, team)) <-
        # hasActivated(rec, Receptionist())
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Receptionist" and 
            subj == rec
        }
    
    def canDeactivate_3(self, cli, x): # A3.3.5
        #
        # canDeactivate(cli, x, Register-team-episode(pat, team)) <-
        # hasActivated(cli, Clinician(spcty)), 
        # hasActivated(x, Register-team-member(cli, team, spcty))
        #
        return {
            True for (subj1, role1) in hasActivated for (subj2, role2) in hasActivated if 
            role1.name == "Clinician" and 
            role2.name == "Register-team-member" and 
            subj1 == cli and 
            subj2 == x and 
            role2.cli == cli and 
            role2.team == self.team
        }

def team_episode_regs(pat, team): # A3.3.7
    #
    # team-episode-regs(count<x>, pat, team) <-
    # hasActivated(x, Register-team-episode(pat, team))
    #
    return len([
        True for subj, role in hasActivated if 
        role.name == "Register-team-episode" and 
        role.pat == pat and 
        role.team == team
    ]

class Head_of_ward(Role):
    def __init__(self, ward):
        super().__init__('Head-of-ward', ward = ward)
    
    def canActivate(self, cli): # A3.4.1
        #
        # canActivate(cli, Head-of-ward(ward)) <-
        # hasActivated(x, Register-head-of-ward(cli, ward))
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Register-head-of-ward" and 
            role.cli == cli and 
            role.ward == self.ward
        }
    
    def canDeactivate(self, cli, cli_): # A3.4.2
        #
        # canDeactivate(cli, cli, Head-of-ward(ward)) <-
        # 
        #
        return (
            cli == cli_
        )

class Register_head_of_ward(Role):
    def __init__(self, cli, ward):
        super().__init__('Register-head-of-ward', cli = cli, ward = ward)
    
    def canActivate(self, mgr): # A3.4.4
        #
        # canActivate(mgr, Register-head-of-ward(cli, ward)) <-
        # hasActivated(mgr, HR-mgr()), 
        # hasActivated(x, Register-ward-member(cli, ward, spcty)), 
        # head-of-ward-regs(n, cli, ward), 
        # n = 0
        #
        return {
            True for (subj1, role1) in hasActivated for (subj2, role2) in hasActivated if 
            role1.name == "HR-mgr" and 
            role2.name == "Register-ward-member" and 
            subj1 == mgr and 
            role2.cli == self.cli and 
            role2.ward == self.ward and 
            head_of_ward_regs(role2.cli, role2.ward) == 0
        }
    
    def canDeactivate(self, mgr, x): # A3.4.5
        #
        # canDeactivate(mgr, x, Register-head-of-ward(cli, ward)) <-
        # hasActivated(mgr, HR-mgr())
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "HR-mgr" and 
            subj == mgr
        }
    
    def onDeactivate(self, subject):
        # A3.4.3 -- deactive Head-of-ward(ward):
        hasActivated -= { (subj, role) for (subj, role) in hasActivated if subj == self.cli and role.name == 'Head_of_ward' and role.ward == self.ward }

def head_of_ward_regs(cli, ward): # A3.4.7
    #
    # head-of-ward-regs(count<x>, cli, ward) <-
    # hasActivated(x, Register-head-of-ward(cli, ward))
    #
    return len([
        True for subj, role in hasActivated if 
        role.name == "Register-head-of-ward" and 
        role.cli == cli and 
        role.ward == ward
    ]

class Register_ward_member(Role):
    def __init__(self, cli, ward, spcty):
        super().__init__('Register-ward-member', cli = cli, ward = ward, spcty = spcty)
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params)
    
    def canActivate_1(self, mgr): # A3.5.1
        #
        # canActivate(mgr, Register-ward-member(cli, ward, spcty)) <-
        # hasActivated(mgr, HR-mgr()), 
        # canActivate(cli, Clinician(spcty)), 
        # ward-member-regs(n, cli, ward, spcty), 
        # n = 0
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "HR-mgr" and 
            subj == mgr and 
            canActivate(self.cli, Clinician(self.spcty)) and 
            ward_member_regs(self.cli, self.ward, self.spcty) == 0
        }
    
    def canActivate_2(self, hd): # A3.5.2
        #
        # canActivate(hd, Register-ward-member(cli, ward, spcty)) <-
        # hasActivated(cli, Clinician(spcty2)), 
        # canActivate(hd, Head-of-ward(ward)), 
        # canActivate(cli, Clinician(spcty)), 
        # ward-member-regs(n, cli, ward, spcty), 
        # n = 0
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Clinician" and 
            subj == self.cli and 
            canActivate(hd, Head_of_ward(self.ward)) and 
            canActivate(subj, Clinician(self.spcty)) and 
            ward_member_regs(subj, self.ward, self.spcty) == 0
        }
    
    def canDeactivate(self, *params):
        return self.canDeactivate_1(*params) or self.canDeactivate_2(*params)
    
    def canDeactivate_1(self, mgr, x): # A3.5.3
        #
        # canDeactivate(mgr, x, Register-ward-member(cli, ward, spcty)) <-
        # hasActivated(mgr, HR-mgr())
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "HR-mgr" and 
            subj == mgr
        }
    
    def canDeactivate_2(self, hd, x): # A3.5.4
        #
        # canDeactivate(hd, x, Register-ward-member(cli, ward, spcty)) <-
        # hasActivated(hd, Clinician(spcty2)), 
        # canActivate(hd, Head-of-ward(ward))
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Clinician" and 
            subj == hd and 
            canActivate(subj, Head_of_ward(self.ward))
        }
    
    def onDeactivate(self, subject):
        # A3.4.6 -- deactive Register-head-of-ward(cli, ward):
        hasActivated -= { (subj, role) for (subj, role) in hasActivated if role.name == 'Register_head_of_ward' and role.cli == self.cli and role.ward == self.ward }

def ward_member_regs(cli, ward, spcty): # A3.5.7
    #
    # ward-member-regs(count<x>, cli, ward, spcty) <-
    # hasActivated(x, Register-ward-member(cli, ward, spcty))
    #
    return len([
        True for subj, role in hasActivated if 
        role.name == "Register-ward-member" and 
        role.cli == cli and 
        role.ward == ward and 
        role.spcty == spcty
    ]

class Register_ward_episode(Role):
    def __init__(self, pat, ward):
        super().__init__('Register-ward-episode', pat = pat, ward = ward)
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params)
    
    def canActivate_1(self, rec): # A3.6.1
        #
        # canActivate(rec, Register-ward-episode(pat, ward)) <-
        # hasActivated(rec, Receptionist()), 
        # canActivate(pat, Patient()), 
        # ward-episode-regs(n, pat, ward), 
        # n = 0
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Receptionist" and 
            subj == rec and 
            canActivate(self.pat, Patient()) and 
            ward_episode_regs(self.pat, self.ward) == 0
        }
    
    def canActivate_2(self, hd): # A3.6.2
        #
        # canActivate(hd, Register-ward-episode(pat, ward)) <-
        # hasActivated(hd, Clinician(spcty)), 
        # canActivate(hd, Head-of-ward(ward)), 
        # canActivate(pat, Patient()), 
        # ward-episode-regs(n, pat, ward), 
        # n = 0
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Clinician" and 
            subj == hd and 
            canActivate(subj, Head_of_ward(self.ward)) and 
            canActivate(self.pat, Patient()) and 
            ward_episode_regs(self.pat, self.ward) == 0
        }
    
    def canDeactivate(self, *params):
        return self.canDeactivate_1(*params) or self.canDeactivate_2(*params) or self.canDeactivate_3(*params)
    
    def canDeactivate_1(self, cg, x): # A3.6.3
        #
        # canDeactivate(cg, x, Register-ward-episode(pat, ward)) <-
        # hasActivated(cg, Caldicott-guardian())
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Caldicott-guardian" and 
            subj == cg
        }
    
    def canDeactivate_2(self, rec, x): # A3.6.4
        #
        # canDeactivate(rec, x, Register-ward-episode(pat, ward)) <-
        # hasActivated(rec, Receptionist())
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Receptionist" and 
            subj == rec
        }
    
    def canDeactivate_3(self, hd, x): # A3.6.5
        #
        # canDeactivate(hd, x, Register-ward-episode(pat, ward)) <-
        # hasActivated(hd, Clinician(spcty)), 
        # canActivate(hd, Head-of-ward(ward))
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Clinician" and 
            subj == hd and 
            canActivate(subj, Head_of_ward(self.ward))
        }

def ward_episode_regs(pat, ward): # A3.6.7
    #
    # ward-episode-regs(count<x>, pat, ward) <-
    # hasActivated(x, Register-ward-episode(pat, ward))
    #
    return len([
        True for subj, role in hasActivated if 
        role.name == "Register-ward-episode" and 
        role.pat == pat and 
        role.ward == ward
    ]

class Emergency_clinician(Role):
    def __init__(self, pat):
        super().__init__('Emergency-clinician', pat = pat)
    
    def canActivate(self, cli): # A3.7.1
        #
        # canActivate(cli, Emergency-clinician(pat)) <-
        # hasActivated(cli, Clinician(spcty)), 
        # canActivate(pat, Patient())
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Clinician" and 
            subj == cli and 
            canActivate(self.pat, Patient())
        }
    
    def canDeactivate(self, *params):
        return self.canDeactivate_1(*params) or self.canDeactivate_2(*params)
    
    def canDeactivate_1(self, cli, cli_): # A3.7.2
        #
        # canDeactivate(cli, cli, Emergency-clinician(pat)) <-
        # 
        #
        return (
            cli == cli_
        )
    
    def canDeactivate_2(self, cg, cli): # A3.7.3
        #
        # canDeactivate(cg, cli, Emergency-clinician(pat)) <-
        # hasActivated(cg, Caldicott-guardian())
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Caldicott-guardian" and 
            subj == cg
        }

def is_emergency_clinician(pat): # A3.7.6
    #
    # is-emergency-clinician(group<x>, pat) <-
    # hasActivated(x, Emergency-clinician(pat))
    #
    return {
        subj for subj, role in hasActivated if 
        role.name == "Emergency-clinician" and 
        role.pat == pat
    }

class ADB_treating_clinician(Role):
    def __init__(self, pat, group, spcty):
        super().__init__('ADB-treating-clinician', pat = pat, group = group, spcty = spcty)
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params) or self.canActivate_3(*params)
    
    def canActivate_1(self, cli): # A3.8.1
        #
        # canActivate(cli, ADB-treating-clinician(pat, group, spcty)) <-
        # canActivate(cli, Clinician(spcty)), 
        # hasActivated(x, Register-team-member(cli, team, spcty)), 
        # hasActivated(y, Register-team-episode(pat, team)), 
        # group = team
        #
        return {
            True for (subj1, role1) in hasActivated for (subj2, role2) in hasActivated if 
            role1.name == "Register-team-member" and 
            role2.name == "Register-team-episode" and 
            role1.cli == cli and 
            role1.spcty == self.spcty and 
            role2.pat == self.pat and 
            canActivate(role1.cli, Clinician(role1.spcty)) and 
            self.group == role2.team
        }
    
    def canActivate_2(self, cli): # A3.8.2
        #
        # canActivate(cli, ADB-treating-clinician(pat, group, spcty)) <-
        # canActivate(cli, Clinician(spcty)), 
        # hasActivated(x, Register-ward-member(cli, ward, spcty)), 
        # hasActivated(x, Register-ward-episode(pat, ward)), 
        # group = ward
        #
        return {
            True for (subj1, role1) in hasActivated for (subj2, role2) in hasActivated if 
            role1.name == "Register-ward-member" and 
            role2.name == "Register-ward-episode" and 
            role1.cli == cli and 
            role1.spcty == self.spcty and 
            role2.pat == self.pat and 
            canActivate(role1.cli, Clinician(role1.spcty)) and 
            self.group == role2.ward
        }
    
    def canActivate_3(self, cli): # A3.8.3
        #
        # canActivate(cli, ADB-treating-clinician(pat, group, spcty)) <-
        # hasActivated(cli, Emergency-clinician(pat)), 
        # group = "A-and-E", 
        # spcty = "A-and-E"
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Emergency-clinician" and 
            role.pat == self.pat and 
            subj == cli and 
            self.group == "A_and_E" and 
            self.spcty == "A_and_E"
        }

class Concealed_by_clinician(Role):
    def __init__(self, pat, id, start, end):
        super().__init__('Concealed-by-clinician', pat = pat, id = id, start = start, end = end)
    
    def canActivate(self, cli): # A4.1.1
        #
        # canActivate(cli, Concealed-by-clinician(pat, id, start, end)) <-
        # hasActivated(cli, Clinician(spcty)), 
        # canActivate(cli, ADB-treating-clinician(pat, group, spcty))
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Clinician" and 
            subj == cli and 
            canActivate(subj, ADB_treating_clinician(self.pat, Wildcard(), role.spcty))
        }
    
    def canDeactivate(self, *params):
        return self.canDeactivate_1(*params) or self.canDeactivate_2(*params) or self.canDeactivate_3(*params)
    
    def canDeactivate_1(self, cli, cli_): # A4.1.2
        #
        # canDeactivate(cli, cli, Concealed-by-clinician(pat, id, start, end)) <-
        # hasActivated(cli, Clinician(spcty))
        #
        return {
            True for subj, role in hasActivated if 
            cli == cli_ and 
            role.name == "Clinician" and 
            subj == cli
        }
    
    def canDeactivate_2(self, cli1, cli2): # A4.1.3
        #
        # canDeactivate(cli1, cli2, Concealed-by-clinician(pat, id, start, end)) <-
        # hasActivated(cli1, Clinician(spcty1)), 
        # canActivate(cli1, ADB-treating-clinician(pat, group, spcty1)), 
        # canActivate(cli2, ADB-treating-clinician(pat, group, spcty2))
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Clinician" and 
            subj == cli1 and 
            canActivate(subj, ADB_treating_clinician(self.pat, Wildcard(), role.spcty1)) and 
            canActivate(cli2, ADB_treating_clinician(self.pat, Wildcard(), Wildcard()))
        }
    
    def canDeactivate_3(self, cg, cli): # A4.1.4
        #
        # canDeactivate(cg, cli, Concealed-by-clinician(pat, id, start, end)) <-
        # hasActivated(cg, Caldicott-guardian())
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Caldicott-guardian" and 
            subj == cg
        }

def count_concealed_by_clinician(pat, id): # A4.1.6
    #
    # count-concealed-by-clinician(count<x>, pat, id) <-
    # hasActivated(x, Concealed-by-clinician(pat, id, start, end)), 
    # Current-time() in [start, end]
    #
    return len([
        True for subj, role in hasActivated if 
        role.name == "Concealed-by-clinician" and 
        role.pat == pat and 
        role.id == id and 
        Current_time() in vrange(role.start, role.end)
    ]

class Concealed_by_patient(Role):
    def __init__(self, what, who, start, end):
        super().__init__('Concealed-by-patient', what = what, who = who, start = start, end = end)
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params)
    
    def canActivate_1(self, pat): # A4.2.1
        #
        # canActivate(pat, Concealed-by-patient(what, who, start, end)) <-
        # hasActivated(pat, Patient()), 
        # count-concealed-by-patient(n, pat), 
        # what = (pat,ids,authors,groups,subjects,from-time,to-time), 
        # who = (orgs1,readers1,groups1,spctys1), 
        # n < 100
        #
        # << AUTOMATIC TRANSLATION FAILURE >>
        # Reason: [11] unable to bind vars {'ids', 'from_time', 'authors', 'groups', 'subjects', 'to_time'} in constraint compare_seq(self.what, (subj, ids, authors, groups, subjects, from_time, to_time))
        #
        # !!! USING HAND TRANSLATION INSTEAD !!!
        #
        return {
                True for subj, role in hasActivated if 
                role.name == "Patient" and 
                subj == pat and 
                count_concealed_by_patient(subj) < 100 
                compare_seq(self.what, (pat, Wildcard(), Wildcard(), Wildcard(), Wildcard(), Wildcard(), Wildcard())) and
                compare_seq(self.who, (Wildcard(), Wildcard(), Wildcard(), Wildcard()))
        }
    
    def canActivate_2(self, ag): # A4.2.2
        #
        # canActivate(ag, Concealed-by-patient(what, who, start, end)) <-
        # hasActivated(ag, Agent(pat)), 
        # count-concealed-by-patient(n, pat), 
        # what = (pat,ids,authors,groups,subjects,from-time,to-time), 
        # who = (orgs1,readers1,groups1,spctys1), 
        # n < 100
        #
        # << AUTOMATIC TRANSLATION FAILURE >>
        # Reason: [12] unable to bind vars {'ids', 'from_time', 'authors', 'groups', 'subjects', 'to_time'} in constraint compare_seq(self.what, (role.pat, ids, authors, groups, subjects, from_time, to_time))
        #
        # !!! USING HAND TRANSLATION INSTEAD !!!
        #
        return {
                True for subj, role in hasActivated if 
                role.name == "Agent" and 
                subj == ag and 
                count_concealed_by_patient(role.pat) < 100 
                compare_seq(self.what, (role.pat, Wildcard(), Wildcard(), Wildcard(), Wildcard(), Wildcard(), Wildcard())) and
                compare_seq(self.who, (Wildcard(), Wildcard(), Wildcard(), Wildcard()))
        }
    
    def canDeactivate(self, *params):
        return self.canDeactivate_1(*params) or self.canDeactivate_2(*params) or self.canDeactivate_3(*params)
    
    def canDeactivate_1(self, pat, x): # A4.2.3
        #
        # canDeactivate(pat, x, Concealed-by-patient(what, whom, start, end)) <-
        # hasActivated(pat, Patient()), 
        # pi7_1(what) = pat
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Patient" and 
            subj == pat and 
            pi7_1(self.what) == subj
        }
    
    def canDeactivate_2(self, ag, x): # A4.2.4
        #
        # canDeactivate(ag, x, Concealed-by-patient(what, whom, start, end)) <-
        # hasActivated(ag, Agent(pat)), 
        # pi7_1(what) = pat
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Agent" and 
            subj == ag and 
            pi7_1(self.what) == role.pat
        }
    
    def canDeactivate_3(self, cg, x): # A4.2.5
        #
        # canDeactivate(cg, x, Concealed-by-patient(what, whom, start, end)) <-
        # hasActivated(cg, Caldicott-guardian())
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Caldicott-guardian" and 
            subj == cg
        }

def count_concealed_by_patient(pat): # A4.2.7
    #
    # count-concealed-by-patient(count<y>, pat) <-
    # hasActivated(x, Concealed-by-patient(y)), 
    # what = (pat,ids,authors,groups,subjects,from-time,to-time), 
    # who = (orgs1,readers1,groups1,spctys1), 
    # y = (what,who,start,end)
    #
    # << AUTOMATIC TRANSLATION FAILURE >>
    # Reason: [13] unable to bind vars {'ids', 'from_time', 'authors', 'groups', 'subjects', 'to_time', 'what'} in constraint compare_seq(what, (pat, ids, authors, groups, subjects, from_time, to_time))
    #
    # !!! USING HAND TRANSLATION INSTEAD !!!
    #
    return len({
            True for subj, role in hasActivated if 
            role.name == "Concealed-by-patient" and 
            compare_seq(role.what, (role.pat, Wildcard(), Wildcard(), Wildcard(), Wildcard(), Wildcard(), Wildcard())) and 
            compare_seq(role.who, (Wildcard(), Wildcard(), Wildcard()))
    })

def count_concealed_by_patient2(a, b): # A4.2.8
    #
    # count-concealed-by-patient2(count<x>, a, b) <-
    # hasActivated(x, Concealed-by-patient(what, whom, start, end)), 
    # a = (pat,id), 
    # b = (org,reader,group,spcty), 
    # what = (pat,ids,authors,groups,subjects,from-time,to-time), 
    # whom = (orgs1,readers1,groups1,spctys1), 
    # Get-record-author(pat, id) in authors, 
    # Get-record-group(pat, id) in groups, 
    # sub in Get-record-subjects(pat, id), 
    # sub in subjects, 
    # Get-record-time(pat, id) in [from-time, to-time], 
    # id in ids, 
    # org in orgs1, 
    # reader in readers1, 
    # group in groups1, 
    # spcty in spctys1, 
    # Current-time() in [start, end]
    #
    # << AUTOMATIC TRANSLATION FAILURE >>
    # Reason: [14] unable to bind vars {'pat', 'id'} in constraint compare_seq(a, (pat, id))
    #
    # !!! USING HAND TRANSLATION INSTEAD !!!
    #
    return {
            True for subj, role in hasActivated if 
            role.name == "Concealed-by-patient" and 
            compare_seq(role.what, (a.pat, Wildcard(), Wildcard(), Wildcard(), Wildcard(), Wildcard(), Wildcard())) and 
            compare_seq(role.who, (Wildcard(), Wildcard(), Wildcard(), Wildcard())) and 
            Get_record_author(a.pat, a.id) in role.what.authors and 
            Get_record_group(a.pat, a.id) in role.what.groups and 
            (True for sub in role.what.subjects if 
                sub in Get_record_subjects(a.pat, a.id)) and 
            Get_record_time(a.pat, a.id) in [role.what.from_time, role.what.to_time] and 
            a.id in role.what.ids and 
            b.org in role.who.orgs1 and 
            b.reader in role.who.readers1 and 
            b.group in role.who.groups1 and 
            b.spcty in role.who.spctys1 and 
            Current_time() in vrange(role.start, role.end)
    }

class Add_record_item(Role): # Action
    def __init__(self, pat):
        super().__init__('Add-record-item', pat = 'pat')
    
    def permits(self, subj):
        return self.permits_1(subj) or self.permits_2(subj)
    
    def permits_1(self, cli): # A5.1.1
        #
        # permits(cli, Add-record-item(pat)) <-
        # hasActivated(cli, Clinician(spcty)), 
        # canActivate(cli, ADB-treating-clinician(pat, group, spcty))
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Clinician" and 
            subj == cli and 
            canActivate(subj, ADB_treating_clinician(self.pat, Wildcard(), role.spcty))
        }
    
    def permits_2(self, cli): # A5.1.2
        #
        # permits(cli, Add-record-item(pat)) <-
        # hasActivated(cli, Ext-treating-clinician(pat, ra, org, spcty))
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Ext-treating-clinician" and 
            role.pat == self.pat and 
            subj == cli
        }


class Annotate_record_item(Role): # Action
    def __init__(self, pat, id):
        super().__init__('Annotate-record-item', pat = 'pat', id = 'id')
    
    def permits(self, subj):
        return self.permits_1(subj) or self.permits_2(subj) or self.permits_3(subj)
    
    def permits_1(self, ag): # A5.1.3
        #
        # permits(ag, Annotate-record-item(pat, id)) <-
        # hasActivated(ag, Agent(pat))
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Agent" and 
            role.pat == self.pat and 
            subj == ag
        }
    
    def permits_2(self, pat): # A5.1.4
        #
        # permits(pat, Annotate-record-item(pat, id)) <-
        # hasActivated(pat, Patient())
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Patient" and 
            subj == pat
        }
    
    def permits_3(self, pat): # A5.1.5
        #
        # permits(pat, Annotate-record-item(pat, id)) <-
        # hasActivated(cli, Clinician(spcty)), 
        # canActivate(cli, ADB-treating-clinician(pat, group, spcty))
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Clinician" and 
            canActivate(subj, ADB_treating_clinician(pat, Wildcard(), role.spcty))
        }


class Get_record_item_ids(Role): # Action
    def __init__(self, pat):
        super().__init__('Get-record-item-ids', pat = 'pat')
    
    def permits(self, subj):
        return self.permits_1(subj) or self.permits_2(subj) or self.permits_3(subj)
    
    def permits_1(self, pat): # A5.2.1
        #
        # permits(pat, Get-record-item-ids(pat)) <-
        # hasActivated(pat, Patient())
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Patient" and 
            subj == pat
        }
    
    def permits_2(self, ag): # A5.2.2
        #
        # permits(ag, Get-record-item-ids(pat)) <-
        # hasActivated(ag, Agent(pat))
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Agent" and 
            role.pat == self.pat and 
            subj == ag
        }
    
    def permits_3(self, cli): # A5.2.3
        #
        # permits(cli, Get-record-item-ids(pat)) <-
        # hasActivated(cli, Clinician(spcty)), 
        # canActivate(cli, ADB-treating-clinician(pat, group, spcty))
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Clinician" and 
            subj == cli and 
            canActivate(subj, ADB_treating_clinician(self.pat, Wildcard(), role.spcty))
        }


class Read_record_item(Role): # Action
    def __init__(self, pat, id):
        super().__init__('Read-record-item', pat = 'pat', id = 'id')
    
    def permits(self, subj):
        return self.permits_1(subj) or self.permits_2(subj) or self.permits_3(subj) or self.permits_4(subj) or self.permits_5(subj) or self.permits_6(subj)
    
    def permits_1(self, ag): # A5.3.1
        #
        # permits(ag, Read-record-item(pat, id)) <-
        # hasActivated(ag, Agent(pat)), 
        # count-concealed-by-patient2(n, a, b), 
        # count-concealed-by-clinician(m, pat, id), 
        # third-party-consent(consenters, pat, id), 
        # a = (pat,id), 
        # b = ("No-org",ag,"No-group","No-spcty"), 
        # n = 0, 
        # m = 0, 
        # Get-record-third-parties(pat, id) subseteq consenters
        #
        # << AUTOMATIC TRANSLATION FAILURE >>
        # Reason: [15] unbound vars {'a', 'b'} in count-concealed-by-patient2(n, a, b)
        #
        # !!! USING HAND TRANSLATION INSTEAD !!!
        #
        return {
                True for subj, role in hasActivated if 
                subj == ag and 
                role.name == "Agent" and 
                role.pat == self.pat and 
                count_concealed_by_patient2((self.pat, self.id), ("No-org", ag, "No-group", "No-spcty")) == 0 and 
                count_concealed_by_clinician(self.pat, self.id) == 0 and 
                Get_record_third_parties(self.pat, self.id) in third_party_consent(self.pat, self.id)
        }
    
    def permits_2(self, cli): # A5.3.2
        #
        # permits(cli, Read-record-item(pat, id)) <-
        # hasActivated(cli, Clinician(spcty)), 
        # Get-record-author(pat, id) = cli
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Clinician" and 
            subj == cli and 
            Get_record_author(self.pat, self.id) == subj
        }
    
    def permits_3(self, cli): # A5.3.3
        #
        # permits(cli, Read-record-item(pat, id)) <-
        # hasActivated(cli, Clinician(spcty)), 
        # hasActivated(x, Register-team-member(cli, team, spcty)), 
        # Get-record-group(pat, id) = team
        #
        return {
            True for (subj1, role1) in hasActivated for (subj2, role2) in hasActivated if 
            role1.name == "Clinician" and 
            role2.name == "Register-team-member" and 
            subj1 == cli and 
            role2.cli == cli and 
            Get_record_group(self.pat, self.id) == role2.team
        }
    
    def permits_4(self, cli): # A5.3.4
        #
        # permits(cli, Read-record-item(pat, id)) <-
        # hasActivated(cli, Clinician(spcty)), 
        # canActivate(cli, ADB-treating-clinician(pat, group, spcty)), 
        # count-concealed-by-patient2(n, a, b), 
        # n = 0, 
        # a = (pat,id), 
        # b = ("ADB",cli,group,spcty), 
        # Get-record-subjects(pat, id) subseteq Permitted-subjects(spcty)
        #
        # << AUTOMATIC TRANSLATION FAILURE >>
        # Reason: [16] unbound vars {'a', 'b'} in count-concealed-by-patient2(n, a, b)
        #
        # !!! USING HAND TRANSLATION INSTEAD !!!
        #
        return {
                True for subj, role in hasActivated if 
                subj == cli and 
                role.name == "Clinician" and
                # Hmm... 'group' must be somehow tied together in the rules below (using Wildcard() for now)
                canActivate(cli, ADB_treating_clinician(self.pat, Wildcard(), role.spcty)), 
                count_concealed_by_patient2((self.pat, self.id), ("ADB", cli, Wildcard(), role.spcty)) == 0 and 
                Get_record_subjects(self.pat, self.id) subseteq Permitted_subjects(role.spcty)
        }
    
    def permits_5(self, cli): # A5.3.5
        #
        # permits(cli, Read-record-item(pat, id)) <-
        # hasActivated(cli, Ext-treating-clinician(pat, ra, org, spcty)), 
        # count-concealed-by-patient2(n, a, b), 
        # n = 0, 
        # a = (pat,id), 
        # b = (org,cli,"Ext-group",spcty), 
        # Get-record-subjects(pat, id) subseteq Permitted-subjects(spcty)
        #
        # << AUTOMATIC TRANSLATION FAILURE >>
        # Reason: [17] unbound vars {'a', 'b'} in count-concealed-by-patient2(n, a, b)
        #
        # !!! USING HAND TRANSLATION INSTEAD !!!
        #
        return {
                True for subj, role in hasActivated if 
                subj == cli and 
                role.name == "Ext-treating-clinician" and 
                role.pat == self.pat and 
                count_concealed_by_patient2((self.pat, self.id), (role.org, Wildcard(), "Ext-group", role.spcty)) == 0 and 
                Get_record_subjects(self.pat, self.id) subseteq Permitted_subjects(role.spcty)
        }
    
    def permits_6(self, pat): # A5.3.6
        #
        # permits(pat, Read-record-item(pat, id)) <-
        # hasActivated(pat, Patient()), 
        # count-concealed-by-patient2(n, a, b), 
        # count-concealed-by-clinician(m, pat, id), 
        # third-party-consent(consenters, pat, id), 
        # n = 0, 
        # m = 0, 
        # a = (pat,id), 
        # b = ("No-org",pat,"No-group","No-spcty"), 
        # Get-record-third-parties(pat, id) subseteq consenters
        #
        # << AUTOMATIC TRANSLATION FAILURE >>
        # Reason: [18] unbound vars {'a', 'b'} in count-concealed-by-patient2(n, a, b)
        #
        # !!! USING HAND TRANSLATION INSTEAD !!!
        #
        return {
                True for subj, role in hasActivated if 
                subj == pat and 
                subj == self.pat and 
                role.name == "Patient" and 
                count_concealed_by_patient2((self.pat, self.id), ("No-org", self.pat, "No-group", "No-spcty")) == 0 and 
                count_concealed_by_clinician(self.pat, self.id) == 0 and 
                Get_record_third_parties(self.pat, self.id) in third_party_consent(self.pat, self.id)
        }


class Force_read_record_item(Role): # Action
    def __init__(self, pat, id):
        super().__init__('Force-read-record-item', pat = 'pat', id = 'id')
    
    def permits(self, subj):
        return self.permits_1(subj) or self.permits_2(subj)
    
    def permits_1(self, cg): # A5.3.7
        #
        # permits(cg, Force-read-record-item(pat, id)) <-
        # hasActivated(cg, Caldicott-guardian())
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Caldicott-guardian" and 
            subj == cg
        }
    
    def permits_2(self, cli): # A5.3.8
        #
        # permits(cli, Force-read-record-item(pat, id)) <-
        # hasActivated(cli, Clinician(spcty)), 
        # canActivate(cli, ADB-treating-clinician(pat, group, spcty))
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Clinician" and 
            subj == cli and 
            canActivate(subj, ADB_treating_clinician(self.pat, Wildcard(), role.spcty))
        }


# Credential Request Restrictions
# ===============================
# These rules determine if certain predicates can be 
# invoked, such as canActivate or hasActivated.

# They restrict who can invoke such predicates.
# These rules have not been translated.

# Restrictions on canActivate
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~


# Restrictions on hasActivate
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~

# <<< For the Role 'NHS-health-org-cert' >>>

# (A1.7.4)
# canReqCred(x, "RA-ADB".hasActivated(y, NHS-health-org-cert(org, start, end))) <-
# org = "ADB"

