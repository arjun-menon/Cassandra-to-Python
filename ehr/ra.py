from cassandra import *
import spine, hospital, pds

hasActivated = set()  # Set of (subject, role) pairs representing currently active roles.

list_of_roles = ['Register-RA-manager', 'RA-manager', 'NHS-service', 'Registration-authority', 'NHS-clinician-cert', 'NHS-Caldicott-guardian-cert', 'NHS-health-org-cert', 'Workgroup-member']

class Register_RA_manager(Role):
    def __init__(self, mgr2):
        super().__init__('Register-RA-manager', ['mgr2']) 
        self.mgr2 = mgr2
    
    def canActivate(self, mgr): # R1.1.1
        return {
            1 for subj, role in hasActivated if 
            role.name == "RA-manager" and 
            subj == mgr and 
            RA_manager_regs(self.mgr2) == 0
        }
    
    def canDeactivate(self, mgr, x): # R1.1.2
        return {
            1 for subj, role in hasActivated if 
            role.name == "RA-manager" and 
            subj == mgr
        }
    
    def onDeactivate(self, subj):
        deactivate(hasActivated, self.mgr2, RA_manager())  # R1.1.6
        

def RA_manager_regs(mgr): # R1.1.3
    return len({
        1 for subj, role in hasActivated if 
        role.name == "Register-RA-manager" and 
        role.mgr == mgr
    })

class RA_manager(Role):
    def __init__(self):
        super().__init__('RA-manager', []) 
    
    def canActivate(self, mgr): # R1.1.4
        return {
            1 for subj, role in hasActivated if 
            role.name == "Register-RA-manager" and 
            role.mgr == mgr
        }
    
    def canDeactivate(self, mgr, mgr_): # R1.1.5
        return (
            mgr == mgr_
        )

class NHS_service(Role):
    def __init__(self):
        super().__init__('NHS-service', []) 
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params)
    
    def canActivate_1(self, srv): # R1.2.2
        return (
            canActivate(srv, Registration_authority())
        )
    
    def canActivate_2(self, srv): # R1.2.3
        return (
            srv == "Spine"
        )

class Registration_authority(Role):
    def __init__(self):
        super().__init__('Registration-authority', []) 
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params)
    
    def canActivate_1(self, ra): # R1.2.4
        return {
            1 for subj, role in hasActivated if 
            role.name == "NHS-registration-authority" and 
            role.ra == ra and 
            Current_time() in vrange(role.start, role.end)
        }
    
    def canActivate_2(self, ra): # R1.2.5
        return {
            1 for subj, role in ra.hasActivated if 
            role.name == "NHS-registration-authority" and 
            role.ra == ra and 
            Current_time() in vrange(role.start, role.end)
        }

class NHS_clinician_cert(Role):
    def __init__(self, org, cli, spcty, start, end):
        super().__init__('NHS-clinician-cert', ['org', 'cli', 'spcty', 'start', 'end']) 
        self.org, self.cli, self.spcty, self.start, self.end = org, cli, spcty, start, end
    
    def canActivate(self, mgr): # R2.1.1
        #todo: unable to bind vars {'start2', 'end2'} in constraint self.start in vrange(start2, end2)
        #hasActivated(mgr, RA-manager())
        #hasActivated(y, NHS-health-org-cert(org, start2, end2))
        #start in [start2, end2]
        #end in [start2, end2]
        #start < end
        pass
    
    def canDeactivate(self, mgr, x): # R2.1.2
        return {
            1 for subj, role in hasActivated if 
            role.name == "RA-manager" and 
            subj == mgr
        }

class NHS_Caldicott_guardian_cert(Role):
    def __init__(self, org, cg, start, end):
        super().__init__('NHS-Caldicott-guardian-cert', ['org', 'cg', 'start', 'end']) 
        self.org, self.cg, self.start, self.end = org, cg, start, end
    
    def canActivate(self, mgr): # R2.2.1
        #todo: unable to bind vars {'start2', 'end2'} in constraint self.start in vrange(start2, end2)
        #hasActivated(mgr, RA-manager())
        #hasActivated(x, NHS-health-org-cert(org, start2, end2))
        #start in [start2, end2]
        #end in [start2, end2]
        #start < end
        pass
    
    def canDeactivate(self, mgr, x): # R2.2.2
        return {
            1 for subj, role in hasActivated if 
            role.name == "RA-manager" and 
            subj == mgr
        }

class NHS_health_org_cert(Role):
    def __init__(self, org, start, end):
        super().__init__('NHS-health-org-cert', ['org', 'start', 'end']) 
        self.org, self.start, self.end = org, start, end
    
    def canActivate(self, mgr): # R2.3.1
        return {
            1 for subj, role in hasActivated if 
            role.name == "RA-manager" and 
            subj == mgr
        }
    
    def canDeactivate(self, mgr, x): # R2.3.2
        return {
            1 for subj, role in hasActivated if 
            role.name == "RA-manager" and 
            subj == mgr
        }
    
    def onDeactivate(self, subj):
        #todo: unable to bind vars {'start'} in constraint start in vrange(self.start, self.end)
        #other-NHS-health-org-regs(n, x, org, start2, end2)
        #n = 0
        #start in [start2, end2]
        #end in [start2, end2]
        #start < end
        deactivate(hasActivated, Wildcard(), NHS_clinician_cert(self.org, Wildcard(), Wildcard(), Wildcard(), Wildcard()))  # R2.1.3
        
        #todo: unable to bind vars {'start'} in constraint start in vrange(self.start, self.end)
        #other-NHS-health-org-regs(n, x, org, start2, end2)
        #start in [start2, end2]
        #end in [start2, end2]
        #start < end
        #n = 0
        deactivate(hasActivated, Wildcard(), NHS_Caldicott_guardian_cert(self.org, Wildcard(), Wildcard(), Wildcard()))  # R2.2.3
        

def other_NHS_health_org_regs(x, org, start, end): # R2.3.3i
    return len({
        1 for subj, role in hasActivated if 
        role.name == "NHS-health-org-cert" and 
        role.org == org and 
        start in vrange(role.start2, role.end2) and 
        end in vrange(role.start2, role.end2) and 
        start < end and 
        x != subj
    })

def other_NHS_health_org_regs(x, org, start, end): # R2.3.3ii
    return len({
        1 for subj, role in hasActivated if 
        role.name == "NHS-health-org-cert" and 
        role.org == org and 
        start in vrange(role.start2, role.end2) and 
        end in vrange(role.start2, role.end2) and 
        start < end and 
        start != role.start2
    })

def other_NHS_health_org_regs(x, org, start, end): # R2.3.3iii
    return len({
        1 for subj, role in hasActivated if 
        role.name == "NHS-health-org-cert" and 
        role.org == org and 
        start in vrange(role.start2, role.end2) and 
        end in vrange(role.start2, role.end2) and 
        start < end and 
        end != role.end2
    })

class Workgroup_member(Role):
    def __init__(self, org, group, spcty):
        super().__init__('Workgroup-member', ['org', 'group', 'spcty']) 
        self.org, self.group, self.spcty = org, group, spcty
    
    def canActivate(self, *params):
        return self.canActivate_1(*params) or self.canActivate_2(*params)
    
    def canActivate_1(self, cli): # R3.1.1
        return {
            1 for (subj1, role1) in hasActivated for (subj2, role2) in org.hasActivated if 
            role1.name == "NHS-health-org-cert" and 
            role2.name == "Register-team-member" and 
            role1.org == self.org and 
            role2.org == self.org and 
            Current_time() in vrange(role2.start, role2.end)
        }
    
    def canActivate_2(self, cli): # R3.1.2
        return {
            1 for (subj1, role1) in hasActivated for (subj2, role2) in org.hasActivated if 
            role1.name == "NHS-health-org-cert" and 
            role2.name == "Register-ward-member" and 
            role1.org == self.org and 
            role2.org == self.org and 
            Current_time() in vrange(role2.start, role2.end)
        }
