#!/usr/bin/python3

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
module_names = ['spine', 'pds', 'hospital', 'ra']

def parse():
    from datetime import datetime
    from grammar import parse_ehr_file
    
    print("Parsing... ", end='')
    start_time = datetime.now()

    # Parse & pickle the EHRs' ASTs:
    ehr_ast = [ ( rule_set, parse_ehr_file(ehr_path+"%s.txt" % rule_set) ) for rule_set in module_names ]
    with open(ehr_path+"parse_tree.pickle", "wb") as f:
        pickle.dump(ehr_ast, f)

    end_time = datetime.now()
    print("Done. (took %.2f seconds)\n" % (end_time - start_time).total_seconds())

def translate():
    with open(ehr_path+"parse_tree.pickle", "rb") as f:
        ehr_ast = pickle.load(f)

    for (module_name, ast) in ehr_ast:
        StopTranslating.count = 0
        translation = translate_module(ast, module_names, module_name)

        file_name = "%s.py" % module_name
        with open(ehr_path + file_name, 'w') as f:
            f.write(translation)
        print("Done. Wrote to %s\n\n" % file_name)

if __name__ == "__main__":
    import argparse
    argparser = argparse.ArgumentParser(description="Translate Cassandra rules to Python.")
    argparser.add_argument( '-p', '--parse', default=False, action='store_true', help='Parse & pickle rules. (Do this only once.)' )
    argparser.add_argument( '-P', '--noparse', default=False, action='store_true', help='Do not parse rules. (Use previously pickled AST.)' )
    args = argparser.parse_args()

    parse_by_default = True  # default parse mode
    if (parse_by_default or args.parse) and (not args.noparse):
        parse()

    translate()
