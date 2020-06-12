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

from __future__ import print_function
import argparse
import sys
import os
import requests
from requests.exceptions import HTTPError
import json
import datetime

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
# For errors / warnings
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def getArgs():
    parser = argparse.ArgumentParser(description="", formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=80, width=130))
    parser.add_argument('-n',dest="tool_name", type=str, required=True, help='Tool Name. Ex: bowtie2')
    parser.add_argument('-v',dest="tool_version", type=str, required=True, help='Tool version. Ex: 2.3.5')
    parser.add_argument('-c',dest="cmdline", type=str, default='true', choices=['true','false'], help='Available in cmdline [%(default)s]')
    parser.add_argument('-g',dest="galaxy",  type=str, default='false', choices=['true','false'], help='Available in Galaxy [%(default)s]')
    parser.add_argument('-i',dest="install_type", type=str, default='c', choices=['c','b','d','s'], help='[c]onda/[b]ash/[d]ocker/[s]ingularity [%(default)s]')
    parser.add_argument('-p',dest="params", type=str, default='~/.tooldir.params', help='Params file')
    parser.add_argument('-f',dest="force",   action='store_true', help='Overwrite tool.properties')

    arg = parser.parse_args()

    return arg

def biotools_request(tool_id):
    # Try to get data from bio.tools API
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
        # Return json as text file
        return response.text

def write_properties(args, json, params):

    install_values = {'c':'conda', 'b':'shell', 'd':'docker', 's':'singularity'}

    # Get arguments
    tool_name = args.tool_name
    tool_version = args.tool_version
    cmdline = args.cmdline
    galaxy = args.galaxy
    install_type = install_values[args.install_type]

    # Get path
    install_dir = params['install_dir_path']
    tool_dir = os.path.join(tool_name, tool_version)
    tool_dir_path = os.path.join(install_dir, tool_dir)

    # Check path exist
    if not os.path.isdir(tool_dir_path):
        eprint(f"\033[0;31;47m ERROR:"+tool_dir_path+" do not exist! \033[0m")
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
        if top in params['topics']:
            topic.append(top)
    topic = list(set(topic))
    if len(topic) == 0:
        eprint(f"\033[0;31;47m WARNING: no topic(s) matching allowed topics \033[0m")

    # Get the date
    now = datetime.datetime.now()
    # daytime = now.strftime("%Y-%m-%d")
    daytime = now.strftime("%d-%m-%Y")

    #Create and write tool.properties
    properties = os.path.join(tool_dir_path, 'tool.properties')

    # Before, check is file exist
    if os.path.isfile(properties) and not args.force:
        eprint(f"\033[0;31;47m WARNING: tool.properties already exist \033[0m")
        eprint(f"\033[0;31;47m WARNING: create tool.properties.tmp instead \033[0m")
        eprint(f"\033[0;31;47m WARNING: use -f to overwrite tool.properties \033[0m")
        properties = os.path.join(tool_dir_path, 'tool.properties.tmp')

    tool_prop = open(properties, 'w')

    # Write
    tool_prop.write('NAME='+json['biotoolsID']+'\n')
    tool_prop.write('DESCRIPTION='+json['description'].split('\n')[0]+'\n')
    if len(json['description'].split('\n')[0]) > 200:
        eprint(f"\033[0;31;47m WARNING: tool description longer than 200 characters\033[0m")
    tool_prop.write('VERSION='+tool_version+'\n')
    tool_prop.write('CMDLINE='+cmdline+'\n')
    tool_prop.write('GALAXY='+galaxy+'\n')
    tool_prop.write('URLDOC='+json['homepage']+'\n')
    tool_prop.write('KEYWORDS='+','.join(function)+'\n')
    tool_prop.write('CMD_INSTALL='+install_type+'\n')
    tool_prop.write('TOPIC='+','.join(topic)+'\n')
    tool_prop.write('DATE_INSTALL=' + daytime)

def conda_tool(params, args):

    # Get arguments
    tool_name = args.tool_name
    tool_version = args.tool_version
    install_conda = params['conda_envs_path']
    install_dir = params['install_dir_path']

    # Path to tool folder and env
    path_tool = os.path.join(install_dir, tool_name, tool_version)
    env_tool = tool_name + '-' + tool_version
    path_env = os.path.join(install_conda, env_tool)

    # Check if conda env exist
    if not os.path.isdir(path_env):
        eprint(f"\033[0;31;47m ERROR:"+ path_env +" do not exist! \033[0m")
        eprint(f"\033[0;31;47m ERROR: Was conda environment has been created? \033[0m")
        eprint(f"\033[0;31;47m ERROR: Processus killed \033[0m")
        exit(1)

    # Write env.sh and delenv.sh
    env_sh = open(os.path.join(path_tool, 'env.sh'), 'w')
    env_sh.write('#!/usr/bin/env bash\n')
    env_sh.write('. '+ params['anaconda_profile_d'] +'\n')
    env_sh.write('conda activate '+ path_env +'\n')
    env_sh.close()

    delenv_sh = open(os.path.join(path_tool, 'delenv.sh'), 'w')
    delenv_sh.write('#!/usr/bin/env bash\n')
    delenv_sh.write('conda deactivate\n')
    delenv_sh.write('PATH=$(echo "$PATH" | sed -e "s@'+ params['anaconda_dir_path'] +'.*/condabin:@@g")\n')
    delenv_sh.write('unset CONDA_EXE CONDA_PYTHON_EXE\n')
    delenv_sh.close()

def make_tool_dir(params, args):

    # Get arguments
    install_dir_path = params['install_dir_path']
    tool_name = args.tool_name
    tool_version = args.tool_version

    # Create tool folder
    path_tool = os.path.join(install_dir_path, tool_name, tool_version)
    if os.path.isdir(path_tool):
        eprint(f"\033[0;31;47m WARNING:"+path_tool+" already exist! \033[0m")
        eprint(f"\033[0;31;47m WARNING: files inside will be overwritten \033[0m")
    else:
        os.makedirs(path_tool)

    return path_tool

def main(args):

    # 1 - Get params
    with open(os.path.expanduser(args.params)) as json_data:
        params = json.load(json_data)

    # 2 - Get tool name/id
    tool_name = args.tool_name
    eprint(f"\033[0;37;46m LOG: Launch create for " + tool_name + " \033[0m")

    # 3 - Get json file from bio.tools
    eprint(f"\033[0;37;46m LOG: Collect info. from bio.tools \033[0m")
    response = biotools_request(tool_name)

    # 4 - Load the json
    eprint(f"\033[0;37;46m LOG: Load and parse JSON \033[0m")
    json_read = json.loads(response)

    # 5 - Create output tool directory
    eprint(f"\033[0;37;46m LOG: Create install folder at ... \033[0m")
    path_tool = make_tool_dir(params, args)
    eprint(f"\033[0;37;46m LOG: " + path_tool + "\033[0m")

    # 5b - For conda, create env.sh and delenv.sh
    eprint(f"\033[0;37;46m LOG: Conda installation detected\033[0m")
    eprint(f"\033[0;37;46m LOG: Create env.sh and delenv.sh \033[0m")
    if args.install_type == 'c':
        conda_tool(params, args)

    # 6 - Parse the json, collect infos and write properties
    eprint(f"\033[0;37;46m LOG: Create tool.properties \033[0m")
    write_properties(args, json_read, params)

    # 7 - Ending
    eprint(f"\033[0;37;46m LOG: " + tool_name + " installed at " + path_tool + "\033[0m")
    eprint(f"\033[0;37;46m LOG: Please check tool description\033[0m")

if __name__ == '__main__':
    args = getArgs()
    main(args)
