#!/usr/bin/env python3

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
import argparse

def getArgs():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('-p',dest="toolspath",type=str,default="../test/",help='')
    parser.add_argument('-o',dest="csvfile",type=str,default="../test/Softwares.csv",help='')

    args = parser.parse_args()

    return args

def walklevel(directory, depth = 2):
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

def parseProperties(directories):
    # Regexes to detect each category
    regexes = {
    'name':          'NAME=',
    'description':   'DESCRIPTION=',
    'version':       'VERSION=',
    'cmdline':       'CMDLINE=',
    'galaxy':        'GALAXY=',
    'documentation': 'URLDOC=',
    'operation':     'KEYWORDS=',
    'environment':   'CMD_INSTALL=',
    'topic':         'TOPIC=',
    'date':          'DATE_INSTALL='
    }

    # Main dict with the result for each tool
    properties = {}
    # Retrive all tool.properties
    for root, dirs, files in directories:
        if 'tool.properties' in files:
            # print(os.path.join(root, 'tool.properties'))
            tool_infos = open(os.path.join(root, 'tool.properties'), 'r')
            parsed_data = {}
            parsed_data['path'] = root
            for l in tool_infos:
                # Use regex to ensure the correct recovery of each category
                # In case of wrong category order
                for k, v in regexes.items():
                    if v in l:
                        regex, value = re.split(r'=', l.rstrip('\n'))
                        parsed_data[k] = value
            # Create a uniq tool ID
            toolID = parsed_data['name'] +'-'+ parsed_data['version']
            # Transfert into the main dict
            properties[toolID] = parsed_data
    # Return the dict for printing
    return(properties)

def outputWriting(csvfile, dictData):
    txt = open(csvfile, 'w')
    txt.write('Name,Operation,Environment,Topic,Access,Doc,Description,Path,Date\n')
    # Iterate over each tool - sorted by name
    for tool in sorted(dictData.keys(), key=lambda x:x.lower()):
        # Get properties
        p = dictData[tool]
        # Print path in case of error
        print(p['path'])
        # Accesses
        if p['cmdline'] == 'true' and p['galaxy'] == 'true':
            p['access'] = 'Galaxy and cmdline'
        elif p['cmdline'] == 'true' and p['galaxy'] == 'false':
            p['access'] = 'Cmdline only'
        else:
            p['access'] = 'Galaxy only'
        # Write, ordered
        name = p['name'] + ' - ' + p['version']
        txt.write('"{0}","{1}","{2}","{3}","{4}","{5}","{6}","{7}","{8}"\n'.format(name,p['operation'],p['environment'],p['topic'],p['access'],p['documentation'],p['description'],p['path'],p['date']))
    # Close file
    txt.close()

def main(args):
    # 1 - Digging tool directory and explore at 2 level of depth
    directories = walklevel(args.toolspath)
    # 2 - parse all tool.properties
    parsedProperties = parseProperties(directories)
    # 3 - write csv file
    outputWriting(args.csvfile ,parsedProperties)

if __name__ == '__main__':
    args = getArgs()
    main(args)
