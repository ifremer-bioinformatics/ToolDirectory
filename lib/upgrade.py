# =============================================================================
# Tool Directory 
#
# A program to prepare an HTML table listing softwares available on
# a file system.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# (c) 2017-20 Ifremer-Bioinformatics Team
# =============================================================================

import os
import re
import json

def walk_level(directory, depth = 2):
    # Argument depth: depth level to digging - fixed at 2 as structure is ./toolName/version/
    # If depth is negative, just walk
    # Unsed in the project
    if depth < 0:
        for root, dirs, files in os.walk(directory):
            yield root, dirs, files
    # path.count works because is a file has a "/" it will show up in the list as a ":"
    else:
        path = directory.rstrip(os.path.sep)
        num_sep = path.count(os.path.sep)
        for root, dirs, files in os.walk(path):
            yield root, dirs, files
            num_sep_this = root.count(os.path.sep)
            if num_sep + depth <= num_sep_this:
                del dirs[:]

def get_tool_prop(directories):
    tool_prop_files = []
    for root, dirs, files in directories:
        if 'tool.properties' in files:
            abs_f=os.path.join(root, 'tool.properties')
            tool_prop_files.append(abs_f)
    return tool_prop_files

def upgrade_to_json(tool_properties_files):
    # Parse and store all tool.properties
    for f in tool_properties_files:
        path = os.path.dirname(f)
        # 1 - read and store the file informations
        print(f)
        infos = {}
        prop = open(f, 'r')
        for l in prop:
            k, v = re.split(r'=', l.rstrip('\n'))
            infos[k] = v
        prop.close()
        # 2 - write JSON
        with open('data.json', 'w') as outjson:
            json.dump(infos, outjson, sort_keys=False, indent=2)
        outjson.close()

def upgrade(args):
    # 1 - Digging tool directory and explore at 2 level of depth
    directories = walk_level(args.toolspath)
    # 2 - Collect all properties files
    tool_properties_files = get_tool_prop(directories)
    # 3 - Upgrade to JSON
    upgrade_to_json(tool_properties_files)