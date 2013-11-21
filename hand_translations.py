# Copyright (C) 2011-2013 Arjun G. Menon
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""
Hand Translations of Selected Rules
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Some rules are difficult to translate automatically. Or rather, 
the translator would have to be seriously augmented to be capable 
of translating such rules. It is not worth investing such effort 
into this translator, as we probably will not be using this translator
for anything besides Becker's NHS EHR specification in Cassandra.

As such, the translations for those specific rules are provided for here.
Whenever a rule has a hand-translation, the translator will simply output 
it, instead of trying to automatically translate the rule itself.
"""

hand_translations = {

    # (S3.3.5)
    # canActivate(cli, General-practitioner(pat)) <-
    # canActivate(cli, Treating-clinician(pat, org, spcty)), 
    # spcty = "GP" 
    #
    # Hand Translation Reason: unable to bind vars {'spcty'} in constraint spcty == "GP"
    #
    "S3.3.5" : r"""return canActivate(cli, Registration_authority(self.org, Wildcard(), "GP"))""",

    # (S4.2.1)
    # canActivate(pat, Conceal-request(what, who, start, end)) <-
    # hasActivated(pat, Patient()), 
    # count-conceal-requests(n, pat), 
    # (what,who) = ((pat,ids,orgs,authors,subjects,from-time,to-time),(orgs1,readers1,spctys1)), 
    # n < 100 
    #
    # Hand Translation Reason: could not translate constraint: (what,who) = ((pat,ids,orgs,authors,subjects,from-time,to-time),(orgs1,readers1,spctys1))
    #
    "S4.2.1" : r"""return {
        True for subj, role in hasActivated if 
        role.name == "Conceal-request" and 
        subj == pat and 
        compare_seq(self.what, (role.pat, Wildcard(), Wildcard(), Wildcard(), Wildcard(), Wildcard(), Wildcard())) and 
        compare_seq(self.who, (Wildcard(), Wildcard(), Wildcard())) and 
        count_conceal_requests(pat) < 100
}""",

    # (S4.2.2)
    # canActivate(ag, Conceal-request(what, who, start, end)) <-
    # hasActivated(ag, Agent(pat)), 
    # count-conceal-requests(n, pat), 
    # (what,who) = ((pat,ids,orgs,authors,subjects,from-time,to-time),(orgs1,readers1,spctys1)), 
    # n < 100
    #
    # Hand Translation Reason: could not translate constraint: (what,who) = ((pat,ids,orgs,authors,subjects,from-time,to-time),(orgs1,readers1,spctys1)) 
    # 
    "S4.2.2" : r"""return {
        True for subj, role in hasActivated if 
        role.name == "Agent" and 
        subj == ag and 
        count_conceal_requests(role.pat) < 100 and 
        compare_seq(self.what, (role.pat, Wildcard(), Wildcard(), Wildcard(), Wildcard(), Wildcard(), Wildcard())) and 
        compare_seq(self.who, (Wildcard(), Wildcard(), Wildcard()))
}""",

    # (S4.2.5)
    # canDeactivate(cli, x, Conceal-request(what, whom, start, end)) <-
    # hasActivated(cli, Spine-clinician(ra, org, spcty)), 
    # canActivate(cli, General-practitioner(pat)), 
    # pi7_1(what) = pat 
    #
    # Hand Translation Reason: unable to bind vars {'pat'} in constraint pi7_1(self.what) == pat 
    #
    "S4.2.5" : r"""return {
        True for subj, role in hasActivated if 
        role.name == "Spine-clinician" and 
        subj == cli and
        canActivate(cli, General_practitioner( pi7_1(self.what) ))
}""",

    # (S4.2.7)
    # count-conceal-requests(count<y>, pat) <-
    # hasActivated(x, Conceal-request(y)), 
    # what = (pat, ids, orgs, authors, subjects, from-time, to-time),
    # who = (orgs1, readers1, spctys1), 
    # y = (what,who,start,end) 
    #
    # Hand Translation Reason: could not translate constraint: (what,who) = ((pat,ids,orgs,authors,subjects,from-time,to-time),(orgs1,readers1,spctys1)) 
    #
    "S4.2.7" : r"""return len({
        True for subj, role in hasActivated if 
        role.name == "Conceal-request" and 
        compare_seq(role.what, (role.pat, Wildcard(), Wildcard(), Wildcard(), Wildcard(), Wildcard(), Wildcard())) and 
        compare_seq(role.who, (Wildcard(), Wildcard(), Wildcard()))
})""",

    # (S4.2.12)
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
    # Hand Translation Reason: unable to bind vars {'id', 'pat'} in constraint compare_seq(a, (pat, id)) 
    #
    "S4.2.12" : r"""return len({
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
})""",

    # (S5.3.1)
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
    # Hand Translation Reason: unbound vars {'a', 'b'} in count-concealed-by-spine-patient(n, a, b) 
    #
    "S5.3.1" : r"""return {
        True for (subj1, role1) in hasActivated for (subj2, role2) in hasActivated if
        self.pat == pat and  
        role1.name == "Patient" and 
        subj1 == pat and 
        role2.name == "One-off-consent" and 
        role2.pat == pat and 
        count_concealed_by_spine_patient((pat, self.id), ("No-org", pat, "No-spcty")) == 0 and 
        count_concealed_by_spine_clinician(pat, self.id) == 0 and 
        Get_spine_record_third_parties(pat, self.id) in consenters
}""",

    # (S5.3.2)
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
    # Hand Translation Reason: unbound vars {'a', 'b'} in count-concealed-by-spine-patient(n, a, b) 
    #
#     "S5.3.2" : r"""return {
#     # TODO
# }""",

    # (S5.3.4)
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
    # Hand Translation Reason: unbound vars {'a', 'b'} in count-concealed-by-spine-patient(n, a, b) 
    #
#     "S5.3.4" : r"""return {
#     # TODO
# }""",

    # (S5.3.5)
    # permits(cli, Read-spine-record-item(pat, id)) <-
    # hasActivated(cli, Spine-clinician(ra, org, spcty)), 
    # hasActivated(x, One-off-consent(pat)), 
    # canActivate(cli, Treating-clinician(pat, org, spcty)), 
    # hasActivated(y, Authenticated-express-consent(pat, cli)), 
    # Get-spine-record-subjects(pat, id) subseteq Permitted-subjects(spcty) 
    #
    # Hand Translation Reason: Not implemented: 3 hasAcs in a rule. 
    #
#     "S5.3.5" : r"""return {
#     # TODO
# }""",

    # (A4.2.1)
    # canActivate(pat, Concealed-by-patient(what, who, start, end)) <-
    # hasActivated(pat, Patient()), 
    # count-concealed-by-patient(n, pat), 
    # what = (pat,ids,authors,groups,subjects,from-time,to-time), 
    # who = (orgs1,readers1,groups1,spctys1), 
    # n < 100 
    #
    # Hand Translation Reason: unable to bind vars {'from_time', 'to_time', 'authors', 'groups', 'subjects', 'ids'} in constraint compare_seq(self.what, (subj, ids, authors, groups, subjects, from_time, to_time)) 
    #
    "A4.2.1" : r"""return {
        True for subj, role in hasActivated if 
        role.name == "Patient" and 
        subj == pat and 
        count_concealed_by_patient(subj) < 100 
        compare_seq(self.what, (pat, Wildcard(), Wildcard(), Wildcard(), Wildcard(), Wildcard(), Wildcard())) and
        compare_seq(self.who, (Wildcard(), Wildcard(), Wildcard(), Wildcard()))
}""",

    # (A4.2.2)
    # canActivate(ag, Concealed-by-patient(what, who, start, end)) <-
    # hasActivated(ag, Agent(pat)), 
    # count-concealed-by-patient(n, pat), 
    # what = (pat,ids,authors,groups,subjects,from-time,to-time), 
    # who = (orgs1,readers1,groups1,spctys1), 
    # n < 100 
    #
    # Hand Translation Reason: unable to bind vars {'from_time', 'to_time', 'authors', 'groups', 'subjects', 'ids'} in constraint compare_seq(self.what, (role.pat, ids, authors, groups, subjects, from_time, to_time)) 
    #
    "A4.2.2" : r"""return {
        True for subj, role in hasActivated if 
        role.name == "Agent" and 
        subj == ag and 
        count_concealed_by_patient(role.pat) < 100 
        compare_seq(self.what, (role.pat, Wildcard(), Wildcard(), Wildcard(), Wildcard(), Wildcard(), Wildcard())) and
        compare_seq(self.who, (Wildcard(), Wildcard(), Wildcard(), Wildcard()))
}""",

    # (A4.2.7)
    # count-concealed-by-patient(count<y>, pat) <-
    # hasActivated(x, Concealed-by-patient(y)), 
    # what = (pat,ids,authors,groups,subjects,from-time,to-time), 
    # who = (orgs1,readers1,groups1,spctys1), 
    # y = (what,who,start,end) 
    #
    # Hand Translation Reason: unable to bind vars {'from_time', 'to_time', 'authors', 'groups', 'subjects', 'ids', 'what'} in constraint compare_seq(what, (pat, ids, authors, groups, subjects, from_time, to_time)) 
    #
#     "A4.2.7" : r"""return {
#     # TODO
# }""",

    # (A4.2.8)
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
    # Hand Translation Reason: unable to bind vars {'id', 'pat'} in constraint compare_seq(a, (pat, id)) 
    #
#     "A4.2.8" : r"""return {
#     # TODO
# }""",

    # (A5.3.1)
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
    # Hand Translation Reason: unbound vars {'a', 'b'} in count-concealed-by-patient2(n, a, b) 
    #
#     "A5.3.1" : r"""return {
#     # TODO
# }""",

    # (A5.3.4)
    # permits(cli, Read-record-item(pat, id)) <-
    # hasActivated(cli, Clinician(spcty)), 
    # canActivate(cli, ADB-treating-clinician(pat, group, spcty)), 
    # count-concealed-by-patient2(n, a, b), 
    # n = 0, 
    # a = (pat,id), 
    # b = ("ADB",cli,group,spcty), 
    # Get-record-subjects(pat, id) subseteq Permitted-subjects(spcty) 
    #
    # Hand Translation Reason: unbound vars {'a', 'b'} in count-concealed-by-patient2(n, a, b) 
    #
#     "A5.3.4" : r"""return {
#     # TODO
# }""",

    # (A5.3.5)
    # permits(cli, Read-record-item(pat, id)) <-
    # hasActivated(cli, Ext-treating-clinician(pat, ra, org, spcty)), 
    # count-concealed-by-patient2(n, a, b), 
    # n = 0, 
    # a = (pat,id), 
    # b = (org,cli,"Ext-group",spcty), 
    # Get-record-subjects(pat, id) subseteq Permitted-subjects(spcty) 
    #
    # Hand Translation Reason: unbound vars {'a', 'b'} in count-concealed-by-patient2(n, a, b) 
    #
#     "A5.3.5" : r"""return {
#     # TODO
# }""",

    # (A5.3.6)
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
    # Hand Translation Reason: unbound vars {'a', 'b'} in count-concealed-by-patient2(n, a, b) 
    #
#     "A5.3.6" : r"""return {
#     # TODO
# }""",

}
