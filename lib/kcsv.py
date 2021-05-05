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
import json

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

def get_tool_prop(directories):
    tool_prop_files = []
    for root, dirs, files in directories:
        if 'properties.json' in files:
            abs_f=os.path.join(root, 'properties.json')
            tool_prop_files.append(abs_f)
    return tool_prop_files

def output_writing(csv_out, json_lst):
    txt = open(csv_out, 'w')
    txt.write('Name,Operation,Environment,Topic,Access,Doc,Description,Path,Date\n')
    # Iterate over each tool - sorted by name
    # for tool in sorted(dictData.keys(), key=lambda x:x.lower()):
    for tool in json_lst:
        # Load json
        with open(tool) as json_data:
            p = json.load(json_data)
        # Print path in case of error
        print(os.path.split(tool)[0])
        p['PATH'] = str(os.path.split(tool)[0])
        # Accesses
        if p['CMDLINE'] == 'true' and p['GALAXY'] == 'true':
            p['ACCESS'] = 'Galaxy and cmdline'
        elif p['CMDLINE'] == 'true' and p['GALAXY'] == 'false':
            p['ACCESS'] = 'Cmdline only'
        else:
            p['ACCESS'] = 'Galaxy only'
        # Write, ordered
        name = p['NAME'] + ' - ' + p['VERSION']
        txt.write('"{0}","{1}","{2}","{3}","{4}","{5}","{6}","{7}","{8}"\n'.format(name,p['KEYWORDS'],p['CMD_INSTALL'],p['TOPIC'],p['ACCESS'],p['URLDOC'],p['DESCRIPTION'],p['PATH'],p['DATE_INSTAL']))
    # Close file
    txt.close()

def kcsv(args):
    # 1 - Digging tool directory and explore at 2 level of depth
    directories = walk_level(args.toolspath)
    # 2 - Filter for properties.json
    prop_json = get_tool_prop(directories)
    # 3 - write csv file
    output_writing(args.csvfile, prop_json)