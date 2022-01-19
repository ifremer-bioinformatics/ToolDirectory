from __future__ import print_function
import os
import re
import sys
import json
import shutil
import requests
import datetime
from requests.exceptions import HTTPError


def walk_level(directory, depth=2):
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


# For errors / warnings
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def biotools_request(tool_id):
    # Try to get data from bio.tools API
    try:
        response = requests.get('https://bio.tools/api/tool/' + tool_id + '/?format=json')
        response.raise_for_status()
    except HTTPError as http_error:
        if response.status_code == 404:
            # eprint(f"\033[0;31;47m WARNING: HTTP error occurred: {http_error} \033[0m")
            core.eprint(f"\033[0;31;47m WARNING: " + tool_id + " is not described in Bio.tools \033[0m")
            exit(1)
            # core.eprint(f"\033[0;31;47m WARNING: Tool.properties will be created anyway but empty \033[0m")
            # response_dict = {
            #     "description": "",
            #     "homepage": "",
            #     "biotoolsID": "",
            #     "function": [
            #         {
            #             "operation": [{"uri": "", "term": ""}]}],
            #     "topic": [{"uri": "", "term": ""}]
            # }
            # response_json = json.dumps(response_dict)
            # # Return empty json
            # code = response.status_code
            # #
            # return response_json, code
        else:
            core.eprint(f"\033[0;31;47m ERROR: HTTP error occurred: {http_error} \033[0m")
            exit(1)
    except Exception as error:
        core.eprint(f"\033[0;31;47m ERROR: Other error occurred: {error} \033[0m")
        exit(1)
    else:
        # Return json as text file
        response_json = response.text
        code = response.status_code
        #
        return response_json, code


def write_properties(args, biojson, properties):
    now = datetime.datetime.now()
    daytime = now.strftime("%d/%m/%Y")
    prop = {
        'NAME': biojson['biotoolsID'],
        'DESCRIPTION': biojson['description'].split('\n')[0],
        'VERSION': args.tool_version,
        'URLDOC': biojson['homepage'],
        'DATE_INSTALL': daytime,
        'OWNER': args.owner
    }
    function = []
    for i in biojson['function']:
        operation = i['operation'][0]['term'].lower().replace(' ', '-')
        function.append(operation)
    prop['KEYWORDS'] = ','.join(list(set(function)))
    topic = []
    for i in biojson['topic']:
        topic.append(i['term'])
    prop['TOPIC'] = ','.join(list(set(topic)))
    if len(biojson['description'].split('\n')[0]) > 200:
        core.eprint(f"\033[0;31;47m WARNING: tool description longer than 200 characters\033[0m")
    with open(properties, 'w') as out_json:
        json.dump(prop, out_json, sort_keys=False, indent=2)
    out_json.close()


def check_modules(args):
    module_dir_path = os.path.join(args.path_modules, args.tool_name)
    if not os.path.isdir(module_dir_path):
        core.eprint(f"\033[0;31;47m ERROR:" + module_dir_path + " do not exist! \033[0m")
        core.eprint(f"\033[0;31;47m ERROR: processus killed \033[0m")
        exit(1)
    module_file_path = os.path.join(args.path_modules, args.tool_name, args.tool_version)
    if not os.path.isfile(module_file_path):
        core.eprint(f"\033[0;31;47m ERROR:" + module_file_path + " do not exist! \033[0m")
        core.eprint(f"\033[0;31;47m ERROR: processus killed \033[0m")
        exit(1)


def update_properties(args, properties):
    with open(properties) as json_data:
        p = json.load(json_data)
    p_check = p['VERSION'].split(',')
    if args.tool_version not in p_check:
        p['VERSION'] = p['VERSION'] + ',' + args.tool_version
        with open(properties, 'w') as o:
            json.dump(p, o, sort_keys=False, indent=2)
        o.close()
    else:
        core.eprint(f"\033[0;31;47m WARNING: tool version already declared. Skip.\033[0m")


def create_properties(args, properties):
    core.eprint(f"\033[0;37;46m LOG: Launch create for " + args.tool_name + " \033[0m")
    core.eprint(f"\033[0;37;46m LOG: Collect info. from bio.tools \033[0m")
    response, code = biotools_request(args.tool_name)
    core.eprint(f"\033[0;37;46m LOG: Load and parse JSON \033[0m")
    bio_json = json.loads(response)
    core.eprint(f"\033[0;37;46m LOG: Create properties.json \033[0m")
    write_properties(args, bio_json, properties)
    core.eprint(f"\033[0;37;46m LOG: all done!\033[0m")


def update_infos(modifications):
    updates = open(modifications, 'r')
    update_data = {}
    for l in updates:
        tool, version, key = re.split(r'\t', l.rstrip('\n'))
        key, val = key.split('=')
        if not tool in update_data:
            update_data[tool] = {version:{}}
        if not version in update_data[tool]:
            update_data[tool][version] = {}
        update_data[tool][version][key] = val
    return update_data


def get_json(directories):
    json_lst=[]
    for root, dirs, files in directories:
        if 'properties.json' in files:
            abs_f=os.path.join(root, 'properties.json')
            json_lst.append(abs_f)
    return json_lst


def update_tool_prop(json_list, modifications, backup=False):
    # Get the date of the modification
    now = datetime.datetime.now()
    daytime = now.strftime("%Y-%m-%d")
    # Parse and store all tool.properties and only backup
    # and update listed files
    for j in json_list:
        with open(j) as json_data:
            p = json.load(json_data)
        # 2a - Update all
        if "all" in modifications:
            for k,v in modifications["all"]["all"].items():
                p[k] = v
        # 2b - Update specific tools - Overwrite modifications apply to all
        ## First, check the tool
        if p['NAME'] in modifications:
            ## Second, check the version
            if p['VERSION'] in modifications[p['NAME']]:
                # Get the modifications
                for k, v in modifications[p['NAME']][p['VERSION']].items():
                    p[k] = v
        # 3 - Close
        json_data.close()
        # 4 - Write
        if "all" in modifications:
            if backup:
                backup = j.replace('properties.json', 'properties.' + daytime)
                shutil.copy2(j, backup)
            with open(j, 'w') as out_json:
                json.dump(p, out_json, sort_keys=False, indent=2)
            out_json.close()
        elif p['NAME'] in modifications and p['VERSION'] in modifications[p['NAME']]:
            if backup:
                backup = j.replace('properties.json', 'properties.' + daytime)
                shutil.copy2(j, backup)
            with open(j, 'w') as out_json:
                json.dump(p, out_json, sort_keys=False, indent=2)
            out_json.close()


def get_tool_prop(directories):
    tool_prop_files = []
    for root, dirs, files in directories:
        if 'properties.json' in files:
            abs_f = os.path.join(root, 'properties.json')
            tool_prop_files.append(abs_f)
    return tool_prop_files


def output_writing(csv_out, json_lst):
    txt = open(csv_out, 'w')
    txt.write('Name,Version,Operation,Topic,Doc,Description,Date\n')
    # Iterate over each tool - sorted by name
    # for tool in sorted(dictData.keys(), key=lambda x:x.lower()):

    json_lst.sort(key=str.lower)

    for tool in json_lst:
        # Load json
        with open(tool) as json_data:
            p = json.load(json_data)
        # Print path in case of error
        # Write, ordered
        name = p['NAME'] + ' - ' + p['VERSION']
        txt.write(
            '"{0}","{1}","{2}","{3}","{4}","{5}","{6}"\n'.format(p['NAME'],p['VERSION'],p['KEYWORDS'],p['TOPIC'],p['URLDOC'],p['DESCRIPTION'],p['DATE_INSTALL']))
    # Close file
    txt.close()
