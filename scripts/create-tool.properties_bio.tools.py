#!/usr/bin/env python3

from __future__ import print_function
import argparse
import sys
import os
import re
import requests
from requests.exceptions import HTTPError
import json

"""
NAME=Canu
DESCRIPTION=A single molecule sequence assembler for genomes large and small
VERSION=2.0
CMDLINE=true
GALAXY=false
URLDOC=http://canu.readthedocs.io
KEYWORDS=genome-assembly
CMD_INSTALL=conda
TOPIC=Sequence assembly
"""

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def getArgs():
    parser = argparse.ArgumentParser(description="", formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=80, width=130))
    parser.add_argument('-n',dest="tool_id", type=str, required=True, help='Tool Name. Ex: bowtie2')
    parser.add_argument('-v',dest="version", type=str, required=True, help='Tool version. Ex: 2.3.5')
    parser.add_argument('-t',dest="topics",  type=str, default='/home1/datahome/galaxy/tool-directory/ToolDirectory/scripts/topics.allow.txt', help='List of topics allowed [topics.allow.txt]')
    parser.add_argument('-c',dest="cmdline", type=str, default='true', choices=['true','false'], help='Available in cmdline [%(default)s]')
    parser.add_argument('-g',dest="galaxy",  type=str, default='false', choices=['true','false'], help='Available in Galaxy [%(default)s]')
    parser.add_argument('-i',dest="install", type=str, default='c', choices=['c','b','d','s'], help='[c]onda/[b]ash/[d]ocker/[s]ingularity [%(default)s]')
    parser.add_argument('-p',dest="path",    type=str, default='/appli/bioinfo/',help='ToolsDir path [%(default)s]')
    parser.add_argument('-f',dest="force",   action='store_true', help='Overwrite tool.properties')

    arg = parser.parse_args()

    return arg

def biotools_request(tool_id):

    try:
        response = requests.get('https://bio.tools/api/tool/'+tool_id+'/?format=json')
        response.raise_for_status()
    except HTTPError as http_error:
        eprint(f'HTTP error occurred: {http_error}')
        exit(1)
    except Exception as error:
        eprint(f'Other error occurred: {error}')
        exit(1)
    else:
        return response.text

def topics_allowed(topics_file):
    topics = []
    topics_read = open(topics_file, 'r')
    for l in topics_read:
        topic = l.rstrip('\n')
        topics.append(topic)
    return topics

def write_properties(args, json, topics):

    install_values = {'c':'conda', 'b':'shell', 'd':'docker', 's':'singularity'}

    # Get arguments
    tool_id = args.tool_id
    version = args.version
    cmdline = args.cmdline
    galaxy = args.galaxy
    install_type = install_values[args.install]

    # Get path
    main_dir = args.path
    sub_dir = os.path.join(args.tool_id, args.version)
    full_path = os.path.join(main_dir, sub_dir)

    # Check path exist
    if not os.path.isdir(full_path):
        eprint(f"\033[0;31;47m ERROR:"+full_path+" do not exist! \033[0m")
        eprint(f"\033[0;31;47m ERROR: processus killed \033[0m")
        exit(1)

    # Get infos when in a list and formatting
    ## Operations
    function = []
    for i in json['function']:
        operation = i['operation'][0]['term'].lower().replace(' ','-')
        function.append(operation)
    function = list(set(function))
    ## Topics
    topic = []
    for i in json['topic']:
        top = i['term']
        if top in topics:
            topic.append(top)
    topic = list(set(topic))
    if len(topic) == 0:
        eprint(f"\033[0;31;47m WARNING: no topic(s) matching allowed topics \033[0m")

    #Create and write tool.properties
    properties = os.path.join(full_path, 'tool.properties')

    # Before, check is file exist
    if os.path.isfile(properties) and not args.force:
        eprint(f"\033[0;31;47m WARNING: tool.properties already exist \033[0m")
        eprint(f"\033[0;31;47m WARNING: create tool.properties.tmp instead \033[0m")
        properties = os.path.join(full_path, 'tool.properties.tmp')

    tool_prop = open(properties, 'w')

    # Write
    tool_prop.write('NAME='+json['biotoolsID']+'\n')
    tool_prop.write('DESCRIPTION='+json['description'].split('\n')[0]+'\n')
    tool_prop.write('VERSION='+version+'\n')
    tool_prop.write('CMDLINE='+cmdline+'\n')
    tool_prop.write('GALAXY='+galaxy+'\n')
    tool_prop.write('URLDOC='+json['homepage']+'\n')
    tool_prop.write('KEYWORDS='+','.join(function)+'\n')
    tool_prop.write('CMD_INSTALL='+install_type+'\n')
    tool_prop.write('TOPIC='+','.join(topic))

def main(args):

    # 1 - Get tool name/id
    tool_id = args.tool_id
    # 2 - Get topics allowed
    topics = topics_allowed(args.topics)
    # 3 - Get json file from bio.tools
    response = biotools_request(tool_id)
    # 4 - Load the json
    json_read = json.loads(response)
    # 5 - Parse the json, collect infos and write properties
    write_properties(args, json_read, topics)

if __name__ == '__main__':
    args = getArgs()
    main(args)
