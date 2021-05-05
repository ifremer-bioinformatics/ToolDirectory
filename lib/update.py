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
import shutil
import datetime

"""
all     all     OWNER=galaxy
all     all     TEAM=SEBIMER
bowtie2 2.3.0   OWNER=acormier
bowtie2 2.3.0   TEAM=SEBIMER
bowtie2 2.3.1   OWNER=acormier
bowtie2 2.3.1   TEAM=SEBIMER
bowtie2 2.3.2   OWNER=acormier
"""

def update_infos(modifications):
    updates = open(modifications, 'r')
    update_data = {}
    for l in updates:
        tool, version, key = re.split(r'\t', l.rstrip('\n'))
        key, val = key.split('=')
        if not tool in update_data:
            update_data[tool] = {version:{}}
        if not version in update_data[tool]:
            update_data[tool][version] = {}
        update_data[tool][version][key] = val
    return update_data

def walk_level(directory, depth = 2):
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

def get_json(directories):
    json_lst=[]
    for root, dirs, files in directories:
        if 'properties.json' in files:
            abs_f=os.path.join(root, 'properties.json')
            json_lst.append(abs_f)
    return json_lst

def update_tool_prop(json_list, modifications, backup=False):
    # Get the date of the modification
    now = datetime.datetime.now()
    daytime = now.strftime("%Y-%m-%d")
    # Parse and store all tool.properties and only backup
    # and update listed files
    for j in json_list:
        with open(j) as json_data:
            p = json.load(json_data)
        # 2a - Update all
        if "all" in modifications:
            for k,v in modifications["all"]["all"].items():
                p[k] = v
        # 2b - Update specific tools - Overwrite modifications apply to all
        ## First, check the tool
        if p['NAME'] in modifications:
            ## Second, check the version
            if p['VERSION'] in modifications[p['NAME']]:
                # Get the modifications
                for k, v in modifications[p['NAME']][p['VERSION']].items():
                    p[k] = v
        # 3 - Close
        json_data.close()
        # 4 - Write
        if "all" in modifications:
            if backup:
                backup = j.replace('properties.json', 'properties.' + daytime)
                shutil.copy2(j, backup)
            with open(j, 'w') as out_json:
                json.dump(p, out_json, sort_keys=False, indent=2)
            out_json.close()
        elif p['NAME'] in modifications and p['VERSION'] in modifications[p['NAME']]:
            if backup:
                backup = j.replace('properties.json', 'properties.' + daytime)
                shutil.copy2(j, backup)
            with open(j, 'w') as out_json:
                json.dump(p, out_json, sort_keys=False, indent=2)
            out_json.close()

def update(args):
    # 1 - Get the tool and associated modification
    # Can be a modification of an existing key or insertion of a new key
    modifications = update_infos(args.update)
    # 2 - Digging tool directory and explore at 2 level of depth
    directories = walk_level(args.toolspath)
    # 3 - Collect all properties files
    tools_json = get_json(directories)
    # 4 - Make the update
    update_tool_prop(tools_json, modifications, backup=args.backup)
