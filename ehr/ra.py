from auxiliary import *
import ehr.spine, ehr.hospital, ehr.pds

hasActivated = list()  # Set of (subject, role) pairs representing currently active roles.

list_of_roles = ['Register-RA-manager', 'RA-manager', 'NHS-service', 'Registration-authority', 'NHS-clinician-cert', 'NHS-Caldicott-guardian-cert', 'NHS-health-org-cert', 'Workgroup-member']

class Register_RA_manager(Role):
    def __init__(self, mgr2):
        super().__init__('Register-RA-manager', mgr2 = mgr2)
    
    def canActivate(self, mgr): # R1.1.1
        #
        # canActivate(mgr, Register-RA-manager(mgr2)) <-
        # hasActivated(mgr, RA-manager()), 
        # RA-manager-regs(n, mgr2), 
        # n = 0
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "RA-manager" and 
            subj == mgr and 
            RA_manager_regs(self.mgr2) == 0
        }
    
    def canDeactivate(self, mgr, x): # R1.1.2
        #
        # canDeactivate(mgr, x, Register-RA-manager(mgr2)) <-
        # hasActivated(mgr, RA-manager())
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "RA-manager" and 
            subj == mgr
        }
    
    def onDeactivate(self, subject):
        # R1.1.6 -- deactive RA-manager():
        hasActivated -= { (subj, role) for (subj, role) in hasActivated if subj == self.mgr2 and role.name == 'RA_manager' }

def RA_manager_regs(mgr): # R1.1.3
    #
    # RA-manager-regs(count<x>, mgr) <-
    # hasActivated(x, Register-RA-manager(mgr))
    #
    return len({
        True for subj, role in hasActivated if 
        role.name == "Register-RA-manager" and 
        role.mgr == mgr
    })

class RA_manager(Role):
    def __init__(self):
        super().__init__('RA-manager')
    
    def canActivate(self, mgr): # R1.1.4
        #
        # canActivate(mgr, RA-manager()) <-
        # hasActivated(x, Register-RA-manager(mgr))
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "Register-RA-manager" and 
            role.mgr == mgr
        }
    
    def canDeactivate(self, mgr, mgr_): # R1.1.5
        #
        # canDeactivate(mgr, mgr, RA-manager()) <-
        # 
        #
        return (
            mgr == mgr_
        )

class NHS_service(Role):
    def __init__(self):
        super().__init__('NHS-service')
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params)
    
    def canActivate_1(self, srv): # R1.2.2
        #
        # canActivate(srv, NHS-service()) <-
        # canActivate(srv, Registration-authority())
        #
        return (
            canActivate(srv, Registration_authority())
        )
    
    def canActivate_2(self, srv): # R1.2.3
        #
        # canActivate(srv, NHS-service()) <-
        # srv = "Spine"
        #
        return (
            srv == "Spine"
        )

class Registration_authority(Role):
    def __init__(self):
        super().__init__('Registration-authority')
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params)
    
    def canActivate_1(self, ra): # R1.2.4
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
    
    def canActivate_2(self, ra): # R1.2.5
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

class NHS_clinician_cert(Role):
    def __init__(self, org, cli, spcty, start, end):
        super().__init__('NHS-clinician-cert', org = org, cli = cli, spcty = spcty, start = start, end = end)
    
    def canActivate(self, mgr): # R2.1.1
        #
        # canActivate(mgr, NHS-clinician-cert(org, cli, spcty, start, end)) <-
        # hasActivated(mgr, RA-manager()), 
        # hasActivated(y, NHS-health-org-cert(org, start2, end2)), 
        # start in [start2, end2], 
        # end in [start2, end2], 
        # start < end
        #
        return {
            True for (subj1, role1) in hasActivated for (subj2, role2) in hasActivated if 
            role1.name == "RA-manager" and 
            role2.name == "NHS-health-org-cert" and 
            subj1 == mgr and 
            role2.org == self.org and 
            self.start in vrange(role2.start2, role2.end2) and 
            self.end in vrange(role2.start2, role2.end2) and 
            self.start < self.end
        }
    
    def canDeactivate(self, mgr, x): # R2.1.2
        #
        # canDeactivate(mgr, x, NHS-clinician-cert(org, cli, spcty, start, end)) <-
        # hasActivated(mgr, RA-manager())
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "RA-manager" and 
            subj == mgr
        }

class NHS_Caldicott_guardian_cert(Role):
    def __init__(self, org, cg, start, end):
        super().__init__('NHS-Caldicott-guardian-cert', org = org, cg = cg, start = start, end = end)
    
    def canActivate(self, mgr): # R2.2.1
        #
        # canActivate(mgr, NHS-Caldicott-guardian-cert(org, cg, start, end)) <-
        # hasActivated(mgr, RA-manager()), 
        # hasActivated(x, NHS-health-org-cert(org, start2, end2)), 
        # start in [start2, end2], 
        # end in [start2, end2], 
        # start < end
        #
        return {
            True for (subj1, role1) in hasActivated for (subj2, role2) in hasActivated if 
            role1.name == "RA-manager" and 
            role2.name == "NHS-health-org-cert" and 
            subj1 == mgr and 
            role2.org == self.org and 
            self.start in vrange(role2.start2, role2.end2) and 
            self.end in vrange(role2.start2, role2.end2) and 
            self.start < self.end
        }
    
    def canDeactivate(self, mgr, x): # R2.2.2
        #
        # canDeactivate(mgr, x, NHS-Caldicott-guardian-cert(org, cg, start, end)) <-
        # hasActivated(mgr, RA-manager())
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "RA-manager" and 
            subj == mgr
        }

class NHS_health_org_cert(Role):
    def __init__(self, org, start, end):
        super().__init__('NHS-health-org-cert', org = org, start = start, end = end)
    
    def canActivate(self, mgr): # R2.3.1
        #
        # canActivate(mgr, NHS-health-org-cert(org, start, end)) <-
        # hasActivated(mgr, RA-manager())
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "RA-manager" and 
            subj == mgr
        }
    
    def canDeactivate(self, mgr, x): # R2.3.2
        #
        # canDeactivate(mgr, x, NHS-health-org-cert(org, start, end)) <-
        # hasActivated(mgr, RA-manager())
        #
        return {
            True for subj, role in hasActivated if 
            role.name == "RA-manager" and 
            subj == mgr
        }
    
    def onDeactivate(self, subject):
        # R2.1.3 -- deactive NHS-clinician-cert(org, cli, spcty, start, end):
        hasActivated -= { (subj, role) for (subj, role) in hasActivated if role.name == 'NHS_clinician_cert' and role.org == self.org }
        
        # R2.2.3 -- deactive NHS-Caldicott-guardian-cert(org, cg, start, end):
        hasActivated -= { (subj, role) for (subj, role) in hasActivated if role.name == 'NHS_Caldicott_guardian_cert' and role.org == self.org }

def other_NHS_health_org_regs(x, org, start, end): # R2.3.3i
    #
    # other-NHS-health-org-regs(count<y>, x, org, start, end) <-
    # hasActivated(y, NHS-health-org-cert(org, start2, end2)), 
    # start in [start2, end2], 
    # end in [start2, end2], 
    # start < end, 
    # x != y
    #
    return len({
        True for subj, role in hasActivated if 
        role.name == "NHS-health-org-cert" and 
        role.org == org and 
        start in vrange(role.start2, role.end2) and 
        end in vrange(role.start2, role.end2) and 
        start < end and 
        x != subj
    })

def other_NHS_health_org_regs(x, org, start, end): # R2.3.3ii
    #
    # other-NHS-health-org-regs(count<y>, x, org, start, end) <-
    # hasActivated(y, NHS-health-org-cert(org, start2, end2)), 
    # start in [start2, end2], 
    # end in [start2, end2], 
    # start < end, 
    # start != start2
    #
    return len({
        True for subj, role in hasActivated if 
        role.name == "NHS-health-org-cert" and 
        role.org == org and 
        start in vrange(role.start2, role.end2) and 
        end in vrange(role.start2, role.end2) and 
        start < end and 
        start != role.start2
    })

def other_NHS_health_org_regs(x, org, start, end): # R2.3.3iii
    #
    # other-NHS-health-org-regs(count<y>, x, org, start, end) <-
    # hasActivated(y, NHS-health-org-cert(org, start2, end2)), 
    # start in [start2, end2], 
    # end in [start2, end2], 
    # start < end, 
    # end != end2
    #
    return len({
        True for subj, role in hasActivated if 
        role.name == "NHS-health-org-cert" and 
        role.org == org and 
        start in vrange(role.start2, role.end2) and 
        end in vrange(role.start2, role.end2) and 
        start < end and 
        end != role.end2
    })

class Workgroup_member(Role):
    def __init__(self, org, group, spcty):
        super().__init__('Workgroup-member', org = org, group = group, spcty = spcty)
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params)
    
    def canActivate_1(self, cli): # R3.1.1
        #
        # canActivate(cli, Workgroup-member(org, group, spcty)) <-
        # hasActivated(x, NHS-health-org-cert(org, start, end)), 
        # org@org.hasActivated(x, Register-team-member(cli, group, spcty)), 
        # Current-time() in [start, end]
        #
        return {
            True for (subj1, role1) in hasActivated for (subj2, role2) in ehr.org.hasActivated if 
            role1.name == "NHS-health-org-cert" and 
            role2.name == "Register-team-member" and 
            role1.org == self.org and 
            role2.group == self.group and 
            role2.cli == cli and 
            role2.spcty == self.spcty and 
            Current_time() in vrange(role1.start, role1.end)
        }
    
    def canActivate_2(self, cli): # R3.1.2
        #
        # canActivate(cli, Workgroup-member(org, group, spcty)) <-
        # hasActivated(x, NHS-health-org-cert(org, start, end)), 
        # org@org.hasActivated(x, Register-ward-member(cli, group, spcty)), 
        # Current-time() in [start, end]
        #
        return {
            True for (subj1, role1) in hasActivated for (subj2, role2) in ehr.org.hasActivated if 
            role1.name == "NHS-health-org-cert" and 
            role2.name == "Register-ward-member" and 
            role1.org == self.org and 
            role2.group == self.group and 
            role2.cli == cli and 
            role2.spcty == self.spcty and 
            Current_time() in vrange(role1.start, role1.end)
        }
# Credential Request Restrictions
# ===============================
# These rules determine if certain predicates can be 
# invoked, such as canActivate or hasActivated.

# They restrict who can invoke such predicates.
# These rules have not been translated.

# Restrictions on canActivate

# For the Role 'Workgroup-member'
# 
# (R3.1.3)
# canReqCred(spine, "RA-ADB".canActivate(cli, Workgroup-member(org, group, spcty))) <-
# spine = "Spine"

# Restrictions on hasActivate

# For the Role 'NHS-registration-authority'
# 
# (R1.2.1)
# canReqCred(x, "NHS".hasActivated(x, NHS-registration-authority(ra, start, end))) <-
# ra = "RA-ADB"
# For the Role 'NHS-Caldicott-guardian-cert'
# 
# (R2.2.4)
# canReqCred(e, "RA-ADB".hasActivated(x, NHS-Caldicott-guardian-cert(org, cg, start, end))) <-
# e = cg
# 
# (R2.2.5)
# canReqCred(e, "RA-ADB".hasActivated(x, NHS-Caldicott-guardian-cert(org, cg, start, end))) <-
# hasActivated(y, NHS-health-org-cert(org, start2, end2)), 
# e = org, 
# Current-time() in [start2, end2]
# 
# (R2.2.6)
# canReqCred(e, "RA-ADB".hasActivated(x, NHS-Caldicott-guardian-cert(org, cg, start, end))) <-
# canActivate(e, NHS-service())
# For the Role 'NHS-clinician-cert'
# 
# (R2.1.4)
# canReqCred(e, "RA-ADB".hasActivated(x, NHS-clinician-cert(org, cli, spcty, start, end))) <-
# hasActivated(y, NHS-health-org-cert(org, start2, end2)), 
# e = org, 
# Current-time() in [start2, end2]
# 
# (R2.1.5)
# canReqCred(e, "RA-ADB".hasActivated(x, NHS-clinician-cert(org, cli, spcty, start, end))) <-
# canActivate(e, NHS-service())
# 
# (R2.1.6)
# canReqCred(e, "RA-ADB".hasActivated(x, NHS-clinician-cert(org, cli, spcty, start, end))) <-
# e = cli
# For the Role 'NHS-health-org-cert'
# 
# (R2.3.4)
# canReqCred(e, "RA-ADB".hasActivated(x, NHS-health-org-cert(org, start, end))) <-
# hasActivated(y, NHS-Caldicott-guardian-cert(org, cg, start2, end2)), 
# Current-time() in [start2, end2], 
# e = cg
# 
# (R2.3.5)
# canReqCred(e, "RA-ADB".hasActivated(x, NHS-health-org-cert(org, start, end))) <-
# hasActivated(y, NHS-clinician-cert(org, cli, spcty, start2, end2)), 
# Current-time() in [start2, end2], 
# e = cli
# 
# (R2.3.6)
# canReqCred(e, "RA-ADB".hasActivated(x, NHS-health-org-cert(org, start, end))) <-
# e = org
# 
# (R2.3.7)
# canReqCred(e, "RA-ADB".hasActivated(x, NHS-health-org-cert(org2, start, end))) <-
# ra.hasActivated(y, NHS-health-org-cert(org, start2, end2)), 
# canActivate(ra, Registration-authority()), 
# e = org
# 
# (R2.3.8)
# canReqCred(e, "RA-ADB".hasActivated(x, NHS-health-org-cert(org2, start, end))) <-
# org@ra.hasActivated(y, NHS-health-org-cert(org, start2, end2)), 
# canActivate(ra, Registration-authority()), 
# e = org
# 
# (R2.3.9)
# canReqCred(e, "RA-ADB".hasActivated(x, NHS-health-org-cert(org, start, end))) <-
# canActivate(e, NHS-service())
