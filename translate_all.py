# Copyright (C) 2011-2012 Arjun G. Menon
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

from translate_module import *

ehr_path = "ehr/"

rule_sets = ['spine', 'pds', 'hospital', 'ra']
rules_collections = None

def parse():
    global rules_collections, rule_sets
    from datetime import datetime
    from ehrparse import parse_ehr_file
    
    print("Parsing... ", end='')

    start_time = datetime.now()
    rules_collections = [ ( rule_set, parse_ehr_file(ehr_path+"%s.txt" % rule_set) ) for rule_set in rule_sets ]
    with open(ehr_path+"parse_tree.pickle", "wb") as f:
        pickle.dump(rules_collections, f)
    end_time = datetime.now()

    print("Done. (took %.2f seconds)\n" % (end_time - start_time).total_seconds())

def unpickle_rules():
    global rules_collections
    with open(ehr_path+"parse_tree.pickle", "rb") as f:
        rules_collections = pickle.load(f)

def translate_all():
    global rules_collections
    
    def write(tr, rule_set):
        with open(ehr_path+"%s.py" % rule_set, 'w') as f:
            f.write(tr)
        print("Done. Wrote to %s.py\n\n" % rule_set)
        
    for (rule_set, rules) in rules_collections:
        tr = translate_rules(rules, rule_sets, rule_set)
        StopTranslating.count = 0
        write(tr, rule_set)
        #interpreter.give(rules, rule_sets, rule_set)

def translate():
    unpickle_rules()
    translate_all()
