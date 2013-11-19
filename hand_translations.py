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
    "S3.3.5" : r"""return canActivate(cli, Registration_authority(self.org, Wildcard(), "GP"))""",

}
