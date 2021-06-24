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
import sys
import os
import requests
from requests.exceptions import HTTPError
import json
import datetime

# For errors / warnings
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def biotools_request(tool_id):
    # Try to get data from bio.tools API
    try:
        response = requests.get('https://bio.tools/api/tool/'+tool_id+'/?format=json')
        response.raise_for_status()
    except HTTPError as http_error:
        if response.status_code == 404:
            # eprint(f"\033[0;31;47m WARNING: HTTP error occurred: {http_error} \033[0m")
            eprint(f"\033[0;31;47m WARNING: "+tool_id+" is not described in Bio.tools \033[0m")
            eprint(f"\033[0;31;47m WARNING: Tool.properties will be created anyway \033[0m")
            response_dict = {
                            "description":"",
                            "homepage":"",
                            "biotoolsID":"",
                            "function":[
                                {
                                    "operation":[{"uri":"","term":""}]}],
                                    "topic":[{"uri":"","term":""}]
                            }
            response_json = json.dumps(response_dict)
            # Return empty json
            code = response.status_code
            #
            return response_json, code
        else:
            eprint(f"\033[0;31;47m ERROR: HTTP error occurred: {http_error} \033[0m")
            exit(1)
    except Exception as error:
        eprint(f"\033[0;31;47m ERROR: Other error occurred: {error} \033[0m")
        exit(1)
    else:
        # Return json as text file
        response_json = response.text
        code = response.status_code
        #
        return response_json, code

def write_properties(args, biojson, params):

    # Installation type
    install_values = {'c':'conda', 'b':'shell', 'd':'docker', 's':'singularity'}

    # Get the date
    now = datetime.datetime.now()
    daytime = now.strftime("%d/%m/%Y")

    # Store properties
    prop = {
        'NAME': biojson['biotoolsID'],
        'DESCRIPTION': biojson['description'].split('\n')[0],
        'VERSION': args.tool_version,
        'CMDLINE': args.cmdline,
        'GALAXY': args.galaxy,
        'URLDOC': biojson['homepage'],
        'CMD_INSTALL': install_values[args.install_type],
        'DATE_INSTALL':daytime,
        'OWNER': args.owner
    }

    # Get tool installation path
    install_dir = params['install_dir_path']
    tool_dir = os.path.join(args.tool_name, args.tool_version)
    tool_dir_path = os.path.join(install_dir, tool_dir)
    if not os.path.isdir(tool_dir_path):
        eprint(f"\033[0;31;47m ERROR:"+tool_dir_path+" do not exist! \033[0m")
        eprint(f"\033[0;31;47m ERROR: processus killed \033[0m")
        exit(1)

    # Format bio.tool data
    ## Operations
    function = []
    for i in biojson['function']:
        operation = i['operation'][0]['term'].lower().replace(' ','-')
        function.append(operation)
    prop['KEYWORDS'] = ','.join(list(set(function)))
    ## Topics
    topic = []
    for i in biojson['topic']:
        top = i['term']
        if top in params['topics']:
            topic.append(top)
    topic = list(set(topic))
    prop['TOPIC'] = ','.join(topic)
    if len(topic) == 0:
        eprint(f"\033[0;31;47m WARNING: no topic(s) matching allowed topics \033[0m")
    ## Description
    if len(biojson['description'].split('\n')[0]) > 200:
        eprint(f"\033[0;31;47m WARNING: tool description longer than 200 characters\033[0m")

    #Create and write tool.properties
    properties = os.path.join(tool_dir_path, 'properties.json')
    if os.path.isfile(properties) and not args.force:
        eprint(f"\033[0;31;47m WARNING: properties.json already exist \033[0m")
        eprint(f"\033[0;31;47m WARNING: create properties.json.tmp instead \033[0m")
        eprint(f"\033[0;31;47m WARNING: use -f to overwrite properties.json \033[0m")
        properties = os.path.join(tool_dir_path, 'properties.json.tmp')

    # Write
    with open(properties, 'w') as out_json:
        json.dump(prop, out_json, sort_keys=False, indent=2)
    out_json.close()

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
        eprint(f"\033[0;31;47m WARNING: file(s) inside will be overwritten \033[0m")
    else:
        eprint(f"\033[0;37;46m LOG: Create install folder at: " + path_tool + "\033[0m")
        os.makedirs(path_tool)

    return path_tool

def create(args):

    # 1 - Get params
    with open(os.path.expanduser(args.params)) as json_data:
        params = json.load(json_data)

    # 2 - Get tool name/id
    tool_name = args.tool_name
    eprint(f"\033[0;37;46m LOG: Launch create for " + tool_name + " \033[0m")

    # 3 - Create output tool directory
    path_tool = make_tool_dir(params, args)

    # 4 - For conda, create env.sh and delenv.sh
    if args.install_type == 'c':
        eprint(f"\033[0;37;46m LOG: Conda installation detected \033[0m")
        conda_tool(params, args)
        eprint(f"\033[0;37;46m LOG: Create env.sh and delenv.sh \033[0m")

    # 5 - Get json file from bio.tools
    eprint(f"\033[0;37;46m LOG: Collect info. from bio.tools \033[0m")
    response, code = biotools_request(tool_name)

    # 6 - Load the json
    eprint(f"\033[0;37;46m LOG: Load and parse JSON \033[0m")
    bio_json = json.loads(response)

    # 7 - Parse the json, collect infos and write properties
    eprint(f"\033[0;37;46m LOG: Create properties.json \033[0m")
    write_properties(args, bio_json, params)

    # 8 - Ending
    eprint(f"\033[0;37;46m LOG: " + tool_name + " installed at " + path_tool + "\033[0m")
    if code == 404:
        eprint(f"\033[0;31;47m WARNING: properties.json tags are empty\033[0m")
        eprint(f"\033[0;31;47m WARNING: Please, manually fill "+ path_tool +"/properties.json\033[0m")
    else:
        eprint(f"\033[0;37;46m LOG: Please check tool description\033[0m")