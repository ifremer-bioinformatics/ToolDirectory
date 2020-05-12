#!/usr/bin/env python3

from __future__ import print_function
import sys
import re
import requests
from requests.exceptions import HTTPError
import argparse
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
    parser.add_argument('-v',dest="version", type=str, required=True, help='Tool version. Ex: 2.6.3')
    parser.add_argument('-t', dest="topics", type=str, default='topics.allow.txt', help='List of topics allowed')
    parser.add_argument('-c',dest="cmdline", type=str, choices=['true','false'], default='true',help='Available in cmdline (true)')
    parser.add_argument('-g',dest="galaxy", type=str, choices=['true','false'], default='false',help='Available in Galaxy (false)')
    parser.add_argument('-i',dest="install", type=str, choices=['conda','shell','docker','singularity'], default='conda',help='Available using... (conda)')

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

    # Get arguments
    tool_id = args.tool_id
    version = args.version
    cmdline = args.cmdline
    galaxy = args.galaxy
    install_type = args.install

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
    tool_prop = open('tool.properties', 'w')
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
