#!/usr/bin/python3

if __name__ == "__main__":
    from translate_all import parse, translate
    import argparse

    should_parse = True  # default parse mode
    
    argparser = argparse.ArgumentParser(description="Translate Cassandra rules to Python.")
    argparser.add_argument( '-p', '--parse', default=False, action='store_true', 
                            help='Parse & pickle rules. (Do this only once.)' )
    argparser.add_argument( '-P', '--noparse', default=False, action='store_true', 
                            help='Do not parse rules. (Use the old pickle.)' )
    args = argparser.parse_args()
    if args.noparse:
        should_parse = False
    if args.parse:
        should_parse = True
    
    if should_parse:
        parse()

    translate()
