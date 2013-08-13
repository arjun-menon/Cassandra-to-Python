#!/usr/bin/python3

from translator import translate
import argparse

if __name__ == "__main__":
    parse_by_default = True
    
    argparser = argparse.ArgumentParser(description="Translate Cassandra rules to Python.")
    argparser.add_argument( '-p', '--parse', default=parse_by_default, action='store_true', 
                            help='Parse & pickle rules. (Do this only once.)' )
    args = argparser.parse_args()
    
    if args.parse:
        translate.parse_rules()
    
    translate.translate()
