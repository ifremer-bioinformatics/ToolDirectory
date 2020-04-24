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
    parser.add_argument('-p',dest="path",type=str,default="../test/",help='')
    parser.add_argument('-s',dest="skipdir",type=lambda s: [str(item) for item in s.split(',')],help='Delimited list input')

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

# Collect properties files.
# Argument directory: root directory used to start collecting files
# Argument skipdir: a list of directory to ignore
# Return a list of file absolute paths
def getFiles(directory, skipdir):
    filesList=[]
    for dir in os.listdir(directory):
    	if not dir in skipdir:
            for root, dirs, files in os.walk(os.path.join(directory,dir)):
                for file in files:
                    if file.endswith('tool.properties'):
                        abs_f=os.path.join(root, file)
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
    for f in toolsPropertiesListFiles:
        print(f)
        current = f
        backup = f.replace('tool.properties','tool.properties.backup.'+daytime)
        # Make a copy of the original tool.properties with metadata
        shutil.copy2(current, backup)
        # Open backup file and update (rewrite) the original file
        backupToolProp = open(backup, 'r')
        # newToolProp = open(current, 'w')
        # Devel
        newToolProp = open(current+'.test', 'w')


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
    modifications = toolProperties2update('tools2update.test')
    # 2 - Collect all properties files
    toolsPropertiesListFiles = getFiles(args.path, args.skipdir)
    # 3 - Make the update
    updateToolProperties(toolsPropertiesListFiles, modifications)

if __name__ == '__main__':
    args = getArgs()
    main(args)
