from core import *
from datetime import datetime

class PDS_manager(Role):
    name = "PDS-manager"
    
    def __init__(self):
        super().__init__(PDS_manager.name, ())
        # no parameters 
    
    def canActivate(self, adm):
        #hasActivated(x,Register-PDS-manager(adm))
        #no-main-role-active(adm)
        pass
    
    #'P1.1.2'
    #canDeactivate(adm,adm,PDS-manager()) <-
    #	

#'P1.1.4'
#count-PDS-manager-activations(count<u>,user) <-
#	hasActivated(u,PDS-manager()),u = user

class Register_PDS_manager(Role):
    name = "Register-PDS-manager"
    
    def __init__(self, adm2):
        super().__init__(Register_PDS_manager.name, (adm2))
        self.adm2 =  adm2
    
    def canActivate(self, adm1):
        #hasActivated(adm1,PDS-manager())
        #pds-admin-regs(n,adm2)
        #n = 0
        pass
    
    #'P1.1.6'
    #canDeactivate(adm1,x,Register-PDS-manager(adm2)) <-
    #	hasActivated(adm1,PDS-manager())
    
    #'P1.1.3'
    #isDeactivated(adm,PDS-manager()) <-
    #	isDeactivated(x,Register-PDS-manager(adm))

#'P1.1.7'
#pds-admin-regs(count<x>,adm) <-
#	hasActivated(x,Register-PDS-manager(adm))

class Patient(Role):
    name = "Patient"
    
    def __init__(self):
        super().__init__(Patient.name, ())
        # no parameters 
    
    def canActivate(self, pat):
        #hasActivated(x,Register-patient(pat))
        #no-main-role-active(pat)
        pass
    
    #'P1.2.2'
    #canDeactivate(pat,pat,Patient()) <-
    #	

#'P1.2.4'
#count-patient-activations(count<u>,user) <-
#	hasActivated(u,Patient()),u = user

class Agent(Role):
    name = "Agent"
    
    def __init__(self, pat):
        super().__init__(Agent.name, (pat))
        self.pat =  pat
    
    def canActivate(self, ag):
        #hasActivated(x,Register-patient(ag))
        #no-main-role-active(ag)
        #"Spine"@"Spine".canActivate(ag,Agent(pat))
        pass
    
    #'P1.3.2'
    #canDeactivate(ag,ag,Agent(pat)) <-
    #	

#'P1.3.5'
#count-agent-activations(count<u>,user) <-
#	hasActivated(u,Agent(pat)),u = user

class Professional_user(Role):
    name = "Professional-user"
    
    def __init__(self, ra, org):
        super().__init__(Professional_user.name, (ra, org))
        self.ra, self.org =  ra, org
    
    def canActivate(self, *params):
        multi_try(lambda: self.canActivate_1(*params), lambda: self.canActivate_2(*params), lambda: self.canActivate_3(*params), lambda: self.canActivate_4(*params))
    
    def canActivate_1(self, x):
        #no-main-role-active(cli)
        #ra.hasActivated(x,NHS-clinician-cert(org,cli,spcty,start,end))
        #canActivate(ra,Registration-authority())
        #Current-time() in [start,end]
        pass
    
    def canActivate_2(self, x):
        #no-main-role-active(cli)
        #ra@ra.hasActivated(x,NHS-clinician-cert(org,cli,spcty,start,end))
        #canActivate(ra,Registration-authority())
        #Current-time() in [start,end]
        pass
    
    def canActivate_3(self, x):
        #no-main-role-active(cg)
        #ra.hasActivated(x,NHS-Caldicott-guardian-cert(org,cg,start,end))
        #canActivate(ra,Registration-authority())
        #Current-time() in [start,end]
        pass
    
    def canActivate_4(self, x):
        #no-main-role-active(cg)
        #ra@ra.hasActivated(x,NHS-Caldicott-guardian-cert(org,cg,start,end))
        #canActivate(ra,Registration-authority())
        #Current-time() in [start,end]
        pass
    
    #'P1.4.5'
    #canDeactivate(x,x,Professional-user(ra,org)) <-
    #	

#'P1.4.6'
#count-professional-user-activations(count<u>,user) <-
#	hasActivated(u,Professional-user(ra,org)),u = user

#'P1.5.1'
#no-main-role-active(user) <-
#	count-agent-activations(n,user),count-patient-activations(n,user),count-PDS-manager-activations(n,user),count-professional-user-activations(n,user),n = 0

class Registration_authority(Role):
    name = "Registration-authority"
    
    def __init__(self):
        super().__init__(Registration_authority.name, ())
        # no parameters 
    
    def canActivate(self, *params):
        multi_try(lambda: self.canActivate_1(*params), lambda: self.canActivate_2(*params))
    
    def canActivate_1(self, ra):
        #"NHS".hasActivated(x,NHS-registration-authority(ra,start,end))
        #Current-time() in [start,end]
        pass
    
    def canActivate_2(self, ra):
        #ra@"NHS".hasActivated(x,NHS-registration-authority(ra,start,end))
        #Current-time() in [start,end]
        pass

class Register_patient(Role):
    name = "Register-patient"
    
    def __init__(self, pat):
        super().__init__(Register_patient.name, (pat))
        self.pat =  pat
    
    def canActivate(self, adm):
        #hasActivated(adm,PDS-manager())
        #patient-regs(n,pat)
        #n = 0
        pass
    
    #'P2.1.2'
    #canDeactivate(adm,x,Register-patient(pat)) <-
    #	hasActivated(adm,PDS-manager())
    
    #'P1.2.3'
    #isDeactivated(pat,Patient()) <-
    #	isDeactivated(x,Register-patient(pat))
    
    #'P1.3.3'
    #isDeactivated(ag,Agent(pat)) <-
    #	isDeactivated(x,Register-patient(ag))
    
    #'P1.3.4'
    #isDeactivated(ag,Agent(pat)) <-
    #	isDeactivated(x,Register-patient(pat))

#'P2.1.3'
#patient-regs(count<x>,pat) <-
#	hasActivated(x,Register-patient(pat))

#'P2.2.1'
#canReqCred(pat,"PDS".hasActivated(x,Register-patient(pat))) <-
#	hasActivated(pat,Patient())

#'P2.2.2'
#canReqCred(ag,"PDS".hasActivated(x,Register-patient(pat))) <-
#	hasActivated(ag,Agent(pat))

#'P2.2.3'
#canReqCred(usr,"PDS".hasActivated(x,Register-patient(pat))) <-
#	hasActivated(usr,Professional-user(ra,org))

#'P2.2.4'
#canReqCred(org,"PDS".hasActivated(x,Register-patient(pat))) <-
#	ra.hasActivated(x,NHS-health-org-cert(org,start,end)),canActivate(ra,Registration-authority())

#'P2.2.5'
#canReqCred(org,"PDS".hasActivated(x,Register-patient(pat))) <-
#	org@ra.hasActivated(x,NHS-health-org-cert(org,start,end)),canActivate(ra,Registration-authority())

#'P2.2.5'
#canReqCred(ra,"PDS".hasActivated(x,Register-patient(pat))) <-
#	canActivate(ra,Registration-authority())

#'P2.2.5'
#canReqCred(spine,"PDS".hasActivated(x,Register-patient(pat))) <-
#	spine = "Spine"
