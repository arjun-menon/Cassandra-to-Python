from . translator import *

ehr_path = "ehr/"

rule_sets = ['spine', 'pds', 'hospital', 'ra']
rules_collections = None

def parse_rules():
    global rules_collections, rule_sets
    rules_collections = [ ( rule_set, parse_one(ehr_path+"%s.txt" % rule_set) ) for rule_set in rule_sets ]
    with open(ehr_path+"parse_tree.pickle", "wb") as f:
        pickle.dump(rules_collections, f)

def unpickle_rules():
    global rules_collections
    with open(ehr_path+"parse_tree.pickle", "rb") as f:
        rules_collections = pickle.load(f)

def translate_all():
    global rules_collections
    
    def write(tr, rule_set):
        with open(ehr_path+"%s.py" % rule_set, 'w') as f:
            f.write(tr)
        print("Done. Wrote to %s.py\n" % rule_set)
        
    for (rule_set, rules) in rules_collections:
        tr = translate_rules(rules, rule_sets, rule_set)
        write(tr, rule_set)

def translate():
    unpickle_rules()
    translate_all()
