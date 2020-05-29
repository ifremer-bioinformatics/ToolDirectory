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
import shutil
import argparse
import datetime
from collections import defaultdict


# ------------------------------------------------------------------
# --  DEFINITIONS  -------------------------------------------------
# ------------------------------------------------------------------

def getArgs():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('-u',dest="update",type=str,required=True,help='')
    parser.add_argument('-p',dest="toolspath",type=str,default="../test/",help='')

    args = parser.parse_args()

    return args

# Collect modifications
# Argument modifications: a file containing the tool name and the modification
# Return a dictionary of tools as key, and subdictionary of keywords to update and the new value
def toolProperties2update(modifications):
    modifList = open(modifications, 'r')
    modifTools = defaultdict(dict)
    for l in modifList:
        tool, version, keyUpdate = re.split(r'\t', l.rstrip('\n'))
        modifTools[tool][version] = {}
        key, newVal = keyUpdate.split('=')
        modifTools[tool][version][key] = newVal
    return modifTools

# Collect all files at a certain depth
# Argument directory: root directory used to start collecting files
# Argument depth: depth level to digging - fixed at 2 as structure is ./toolName/version/
# Return an os.walk() object - path, dirs names, files into each dir
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

# Collect properties files.
# Argument directores: root, dirs and files from os.walk()
# Return a list of file absolute paths
def getFiles(directories):
    filesList=[]
    for root, dirs, files in directories:
        if 'tool.properties' in files:
            abs_f=os.path.join(root, 'tool.properties')
            filesList.append(abs_f)
    return filesList

# Update tool.properties files and save the original file.
# Argument toolsPropertiesListFiles: a list of file absolute paths
# Argument modifications: a dictionary of tools as key, and subdictionary of keywords to update and the new value
def updateToolProperties(toolsPropertiesListFiles, modifications):
    # Get the date of the modification
    now = datetime.datetime.now()
    daytime = now.strftime("%Y-%m-%d")
    # Parse and store all tool.properties and only backup
    # and update listed files
    for f in toolsPropertiesListFiles:
        # print(f)
        # 1 - read and store the file informations
        tool_infos = {}
        tool_prop = open(f, 'r')
        for l in tool_prop:
            keyword, propertie = re.split(r'=', l.rstrip('\n'))
            tool_infos[keyword] = propertie
        tool_prop.close()

        # 2 - Make the backup part if needed
        ## First, check the tool
        if tool_infos['NAME'] in modifications:
            ## Second, check the version
            if tool_infos['VERSION'] in modifications[tool_infos['NAME']]:
                # Get the modifications
                keys_to_update = modifications[tool_infos['NAME']][tool_infos['VERSION']]
                # Make a copy of the original tool.properties with metadata
                backup = f.replace('tool.properties', 'tool.properties.backup.' + daytime)
                shutil.copy2(f, backup)
                # Write the updated file
                tool_backup = open(backup, 'r')
                # tool_update = open(f, 'w')
                # Devel
                tool_update = open(f+'.test', 'w')

                # Update the file using backup as reference
                for l in tool_backup:
                    keyword, propertie = re.split(r'=', l.rstrip('\n'))
                    # Get the tool name and extract the data to update
                    if keyword == 'NAME':
                        tool_update.write('{0}={1}\n'.format(keyword, propertie))
                    # If the keyword need to be update...
                    elif keyword in keys_to_update:
                        tool_update.write('{0}={1}\n'.format(keyword, keys_to_update[keyword]))
                        del keys_to_update[keyword]
                    else:
                        tool_update.write('{0}={1}\n'.format(keyword, propertie))
                # Insertion of new key(s)
                if len(keys_to_update) > 0:
                    for keyword, propertie in keys_to_update.items():
                        tool_update.write('{0}={1}\n'.format(keyword, propertie))

# ------------------------------------------------------------------
# --  MAIN  --------------------------------------------------------
# ------------------------------------------------------------------
def main(args):
    # 1 - Get the tool and associated modification
    # Can be a modification of an existing key or insertion of a new key
    modifications = toolProperties2update(args.update)
    # 2 - Digging tool directory and explore at 2 level of depth
    directories = walklevel(args.toolspath)
    # 3 - Collect all properties files
    toolsPropertiesListFiles = getFiles(directories)
    # 4 - Make the update
    updateToolProperties(toolsPropertiesListFiles, modifications)

if __name__ == '__main__':
    args = getArgs()
    main(args)
