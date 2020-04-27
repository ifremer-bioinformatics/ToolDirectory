#!/usr/bin/env python3

import os
import re
import argparse

def getArgs():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('-p',dest="toolspath",type=str,default="../test/",help='')
    parser.add_argument('-o',dest="outpath",type=str,default="../test/",help='')
    # parser.add_argument('-s',dest="skipdir", default=[], type=lambda s: [str(item) for item in s.split(',')],help='Delimited list of tool folder(s) to ignore')

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

# def parseProperties(directory, ignore):
#     # Regexes to detect each category
#     regexes = {
#     'name':          'NAME=',
#     'description':   'DESCRIPTION=',
#     'version':       'VERSION=',
#     'cmdline':       'CMDLINE=',
#     'galaxy':        'GALAXY=',
#     'documentation': 'URLDOC=',
#     'operation':     'KEYWORDS=',
#     'environment':   'CMD_INSTALL=',
#     'topic':         'TOPIC='
#     }
#
#     # Main dict with the result for each tool
#     properties = {}
#     # First, list level 1 dirs in order to not explore galaxy/ folder
#     for dir in os.listdir(directory):
#         # Ignore some dirs
#         if not dir in ignore:
#             # Second, list all files in all subdirectories
#             # WARNING: beware of "latest" symlinks. os.walk() do not explore symlink folders by default so it's ok
#             for root, dirs, files in os.walk(os.path.join(directory,dir)):
#                 for file in files:
#                     if file == "tool.properties":
#                         # In case of error, get the full path to the file
#                         # print(os.path.join(root, file))
#                         # Open the tool.properties
#                         tool_infos = open(os.path.join(root, file), 'r')
#                         # Create a tmp dict
#                         parsed_data = {}
#                         parsed_data['path'] = root
#                         for l in tool_infos:
#                             # Use regex to ensure the correct recovery of each category
#                             # In case of wrong category order
#                             for k, v in regexes.items():
#                                 if v in l:
#                                     regex, value = re.split(r'=', l.rstrip('\n'))
#                                     parsed_data[k] = value
#                         # Create a uniq tool ID
#                         toolID = parsed_data['name'] +'-'+ parsed_data['version']
#                         # Transfert into the main dict
#                         properties[toolID] = parsed_data
#     # Return the dict for printing
#     return(properties)

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
    'topic':         'TOPIC='
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







    # # First, list level 1 dirs in order to not explore galaxy/ folder
    # for dir in os.listdir(directory):
    #     # Ignore some dirs
    #     if not dir in ignore:
    #         # Second, list all files in all subdirectories
    #         # WARNING: beware of "latest" symlinks. os.walk() do not explore symlink folders by default so it's ok
    #         for root, dirs, files in os.walk(os.path.join(directory,dir)):
    #             for file in files:
    #                 if file == "tool.properties":
    #                     # In case of error, get the full path to the file
    #                     # print(os.path.join(root, file))
    #                     # Open the tool.properties
    #                     tool_infos = open(os.path.join(root, file), 'r')
    #                     # Create a tmp dict
    #                     parsed_data = {}
    #                     parsed_data['path'] = root
    #                     for l in tool_infos:
    #                         # Use regex to ensure the correct recovery of each category
    #                         # In case of wrong category order
    #                         for k, v in regexes.items():
    #                             if v in l:
    #                                 regex, value = re.split(r'=', l.rstrip('\n'))
    #                                 parsed_data[k] = value
    #                     # Create a uniq tool ID
    #                     toolID = parsed_data['name'] +'-'+ parsed_data['version']
    #                     # Transfert into the main dict
    #                     properties[toolID] = parsed_data
    # # Return the dict for printing
    # return(properties)

def outputWriting(outpath, dictData):
    txt = open(os.path.join(outpath, 'Softwares.csv'), 'w')
    txt.write('Name,Operation,Environment,Topic,Access,Doc,Description,Path\n')
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
        txt.write('"{0}","{1}","{2}","{3}","{4}","{5}","{6}","{7}"\n'.format(name,p['operation'],p['environment'],p['topic'],p['access'],p['documentation'],p['description'],p['path']))
    # Close file
    txt.close()

def main(args):
    # 1 - Digging tool directory and explore at 2 level
    directories = walklevel(args.toolspath)
    # 2 - parse all tool.properties
    parsedProperties = parseProperties(directories)
    # 3 - write csv file
    outputWriting(args.outpath ,parsedProperties)

if __name__ == '__main__':
    args = getArgs()
    main(args)
