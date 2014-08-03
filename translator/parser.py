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

import os, pickle, time

from grammar import parse_ehr

cache_file_name = '.cached_ast'

def parse(ehr_path, module_names, force=False):
    """
    Parse the EHR modules, and return the abstract syntax tree (AST).

    The AST is cached, and the cache is updated when the source files change.
    If force is true, the EHR is forcibly reparsed.
    """

    def should_parse():
        if force:
            return True

        if not os.path.exists(cache_file_name):
            return True

        cache_file_mtime = os.path.getmtime(cache_file_name)
        ehr_source_file_mtimes = [ os.path.getmtime(ehr_path + module_name + ".txt") for module_name in module_names ]

        if max(ehr_source_file_mtimes) > cache_file_mtime:
            return True

        return False

    def parse_module(file_name):
        with open(file_name) as f:
            return parse_ehr( f.read() )

    if should_parse():
        print("Parsing... ", end='')
        start_time = time.time()

        # Parse & pickle the EHRs' ASTs:
        ehr_ast = [ ( module_name, parse_module(ehr_path + module_name + ".txt") ) for module_name in module_names ]
        with open(cache_file_name, "wb") as f:
            pickle.dump(ehr_ast, f)

        end_time = time.time()
        print("Done. (took %.2f seconds)\n" % (end_time - start_time))

    else:
        with open(cache_file_name, "rb") as f:
            ehr_ast = pickle.load(f)

    return ehr_ast
