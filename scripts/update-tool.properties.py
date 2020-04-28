#!/usr/bin/env python3

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
        tool, keyUpdate = re.split(r'\t', l.rstrip('\n'))
        key, newVal = keyUpdate.split('=')
        modifTools[tool][key] = newVal
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
    # Read each file, make a backup file and create the new propertie file
    # TODO: read each file but only make a backup if needed
    # Parse and store all tool.properties and in a new function, only backup
    # and update listed files
    for f in toolsPropertiesListFiles:
        print(f)
        current = f
        backup = f.replace('tool.properties','tool.properties.backup.'+daytime)
        # Make a copy of the original tool.properties with metadata
        shutil.copy2(current, backup)
        # Open backup file and update (rewrite) the original file
        backupToolProp = open(backup, 'r')
        newToolProp = open(current, 'w')
        # Devel
        # newToolProp = open(current+'.test', 'w')
        for l in backupToolProp:
            keyword, propertie = re.split(r'=', l.rstrip('\n'))
            # Get the tool name and extract the data to update
            if keyword == 'NAME':
                toolUpdateProp = modifications[propertie]
                newToolProp.write('{0}={1}\n'.format(keyword, propertie))
            # If the keyword new to be update...
            elif keyword in toolUpdateProp:
                newToolProp.write('{0}={1}\n'.format(keyword, toolUpdateProp[keyword]))
                del toolUpdateProp[keyword]
            else:
                newToolProp.write('{0}={1}\n'.format(keyword, propertie))
        # Insertion of new key(s)
        if len(toolUpdateProp) > 0:
            for keyword, propertie in toolUpdateProp.items():
                newToolProp.write('{0}={1}\n'.format(keyword, propertie))

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
