
import cPickle as pickle
#import ehrparse

#rules = ehrparse.parse()
#pickle.dump(rules, open("parse_tree", "wb"))
rules = pickle.load(open("parse_tree"))


#p = ehrparse.EhrParser()
#ra = p( file("ra").read())


#r = rules[0]
#
##print r.concl.args[1].name
#
#all_canActivate_rules = (r for r in rules if r.concl.name == "canActivate")
#
#all_canActivate_Spineclinician_rules = (r for r in all_canActivate_rules if r.concl.args[1].name == "Spine-clinician")
#
#for r in all_canActivate_Spineclinician_rules:
#    print r
