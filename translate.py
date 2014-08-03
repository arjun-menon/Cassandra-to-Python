#!/usr/bin/python3

from translator import *

def main():
    import argparse
    argparser = argparse.ArgumentParser(description="Translate Cassandra rules to Python.")
    argparser.add_argument( '-p', '--parse', default=False, action='store_true', help='Parse & pickle rules. (Do this only once.)' )
    argparser.add_argument( '-P', '--noparse', default=False, action='store_true', help='Do not parse rules. (Use previously pickled AST.)' )
    args = argparser.parse_args()

    if (parse_by_default or args.parse) and (not args.noparse):
        parse()

    translate_all()

if __name__ == "__main__":
    main()
