#!/usr/bin/python3

ehr_path = "ehr/"
module_names = ['spine', 'pds', 'hospital', 'ra']

from translator import translate_all

def main():
    import argparse
    argparser = argparse.ArgumentParser(description="Translate Cassandra rules to Python.")
    argparser.add_argument( '-p', '--parse', default=False, action='store_true', help='Forcibly reparse the EHR.' )
    args = argparser.parse_args()

    translate_all(ehr_path, module_names, args.parse)

if __name__ == "__main__":
    main()
