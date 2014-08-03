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

from . parser import parse
from . L1_ModuleTranslator import *

def translate_all(ehr_path, module_names, force_parse=False):
    ehr_ast = parse(ehr_path, module_names, force_parse)

    for (module_name, ast) in ehr_ast:
        translation = translate_module(ast, module_names, module_name)

        file_name = "%s.py" % module_name
        with open(ehr_path + file_name, 'w') as f:
            f.write(translation)
        print("Done. Wrote to %s\n\n" % file_name)
