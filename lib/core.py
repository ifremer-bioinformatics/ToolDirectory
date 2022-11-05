from __future__ import print_function
import os
import sys
import json
import requests
import datetime
from requests.exceptions import HTTPError

environment = {
    "b": "bash",
    "c": "conda",
    "d": "docker",
    "s": "singularity",
    "o": "other"
}


def create_properties(args, properties):
    eprint(f"\033[0;37;46m LOG: Launch create for " + args.name + " \033[0m")
    if args.bid:
        eprint(f"\033[0;37;46m LOG: Search on Bio.tools for " + args.bid + " instead of " + args.name + "\033[0m")
    eprint(f"\033[0;37;46m LOG: Collect info. from Bio.tools \033[0m")
    response, code = biotools_api_request(args, properties)
    eprint(f"\033[0;37;46m LOG: Load and parse JSON \033[0m")
    bio_json = json.loads(response)
    eprint(f"\033[0;37;46m LOG: Create properties \033[0m")
    write_properties(args, bio_json, properties)
    eprint(f"\033[0;37;46m LOG: All done!\033[0m")


def add_version(args, properties):
    eprint(f"\033[0;37;46m LOG: " + args.name + " already exist. Adding new version number... \033[0m")
    with open(properties) as json_data:
        p = json.load(json_data)
    p_check = p['version'].keys()
    install_date = daytime()
    if args.datetime:
        install_date = args.datetime
    if args.version not in p_check:
        p['version'][args.version] = {
            "localInstallUser": args.installer,
            "environment": environment[args.environment],
            "localInstallDate": install_date,
            "isCmdline": args.cmdline,
            "isGalaxy": args.galaxy,
            "isWorkflow": args.workflow,
            "status": "active"
        }
        with open(properties, 'w') as o:
            json.dump(p, o, sort_keys=False, indent=2)
        o.close()
        eprint(f"\033[0;37;46m LOG: all done!\033[0m")
    else:
        eprint(f"\033[0;31;47m WARNING: tool version already declared. Skip.\033[0m")


def set_status(properties, versions, status):
    with open(properties) as json_data:
        p = json.load(json_data)
    for version in versions:
        try:
            p['version'][version]['status'] = status
        except KeyError:
            eprint(f"\033[0;31;47m WARNING: Invalid tool version: {versions}. Skip.\033[0m")
            pass
        with open(properties, 'w') as o:
            json.dump(p, o, sort_keys=False, indent=2)
        o.close()
        eprint(f"\033[0;37;46m LOG: All done!\033[0m")


def kcsv_writing(csv_out, json_lst):
    txt = open(csv_out, 'w')
    txt.write('Name,Version,Operation,Topic,Doc,Description,Environment,Galaxy,Workflow\n')

    json_lst.sort(key=str.lower)

    for tool in json_lst:
        with open(tool) as json_data:
            p = json.load(json_data)
            ver_env = []
            env = []
            name = p['name']
            operation = p['operation']
            topic = p['topic']
            homepage = p['homepage']
            description = p['description']
            for k in sorted(p['version'].keys(), reverse=True):
                if p['version'][k]['status'] == 'active':
                    ver_env.append(k + '-' + p['version'][k]['environment'])
                    if p['version'][k]['environment'] not in env:
                        env.append(p['version'][k]['environment'])
            versions = ','.join(ver_env)
            environments = ','.join(env)
            isGalaxy = p['version'][k]['isGalaxy']
            isWorkflow = p['version'][k]['isWorkflow']
            txt.write(f'"{name}","{versions}","{operation}","{topic}","{homepage}","{description}","{environments}","{isGalaxy}","{isWorkflow}"\n')
    txt.close()


def walk_level(directory, depth=2):
    if depth < 0:
        for root, dirs, files in os.walk(directory):
            yield root, dirs, files
    else:
        path = directory.rstrip(os.path.sep)
        num_sep = path.count(os.path.sep)
        for root, dirs, files in os.walk(path):
            yield root, dirs, files
            num_sep_this = root.count(os.path.sep)
            if num_sep + depth <= num_sep_this:
                del dirs[:]


def get_json(directories):
    json_lst = []
    for root, dirs, files in directories:
        if 'properties.json' in files:
            abs_f = os.path.join(root, 'properties.json')
            json_lst.append(abs_f)
    return json_lst


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def daytime():
    now = datetime.datetime.now()
    time = now.strftime("%d-%m-%Y")
    return time


def biotools_api_request(args, properties):
    name = args.name
    if args.bid:
        name = args.bid
    try:
        response = requests.get('https://bio.tools/api/tool/' + name + '/?format=json')
        response.raise_for_status()
    except HTTPError as http_error:
        if response.status_code == 404:
            # eprint(f"\033[0;31;47m WARNING: HTTP error occurred: {http_error} \033[0m")
            eprint(f"\033[0;31;47m WARNING: " + name + " is not described in Bio.tools \033[0m")
            eprint(f"\033[0;31;47m WARNING: writing empty properties file \033[0m")
            eprint(f"\033[0;31;47m WARNING: please, fill it manual: {properties} \033[0m")
            write_properties_default(args, properties)
            exit(0)
        else:
            eprint(f"\033[0;31;47m ERROR: HTTP error occurred: {http_error} \033[0m")
            exit(1)
    except Exception as error:
        eprint(f"\033[0;31;47m ERROR: Other error occurred: {error} \033[0m")
        exit(1)
    else:
        response_json = response.text
        code = response.status_code
        return response_json, code


def check_path(args):
    tool_path = os.path.join(args.path, args.name)
    if not os.path.isdir(tool_path):
        eprint(f"\033[0;31;47m ERROR:" + tool_path + " do not exist! \033[0m")
        eprint(f"\033[0;31;47m ERROR: processus killed \033[0m")
        exit(1)
    tool_version_path = os.path.join(args.path, args.name, args.version)
    if not os.path.isfile(tool_version_path) and not os.path.isdir(tool_version_path):
        eprint(f"\033[0;31;47m ERROR:" + tool_version_path + " do not exist! \033[0m")
        eprint(f"\033[0;31;47m ERROR: processus killed \033[0m")
        exit(1)


def write_properties(args, biojson, properties):
    operation = []
    for i in biojson['function']:
        operation.append(i['operation'][0]['term'].lower().replace(' ', '-'))
    operations = ','.join(list(set(operation)))
    if len(operation) == 0:
        eprint(f"\033[0;31;47m ERROR: No operations EDAM terms found\033[0m")
        eprint(f"\033[0;31;47m ERROR: Processus killed \033[0m")
        exit(1)
    else:
        eprint(f"\033[0;37;46m LOG: { len(operation) } operations EDAM found\033[0m")
    topic = []
    for i in biojson['topic']:
        topic.append(i['term'])
    topics = ','.join(list(set(topic)))
    if len(topic) == 0:
        eprint(f"\033[0;31;47m ERROR: No topics EDAM terms found\033[0m")
        eprint(f"\033[0;31;47m ERROR: Processus killed \033[0m")
        exit(1)
    else:
        eprint(f"\033[0;37;46m LOG: { len(topic) } topics EDAM found\033[0m")
    install_date = daytime()
    if args.datetime:
        install_date = args.datetime
    prop = {
        'name': args.name,
        'bio.tools_id': biojson['biotoolsID'],
        'description': biojson['description'].split('\n')[0],
        'homepage': biojson['homepage'],
        "operation": operations,
        "topic": topics,
        'version': {
            args.version: {
                "localInstallUser": args.installer,
                "environment": environment[args.environment],
                "localInstallDate": install_date,
                "isCmdline": args.cmdline,
                "isGalaxy": args.galaxy,
                "isWorkflow": args.workflow,
                "status": "active"
            }
        }
    }
    if len(biojson['description'].split('\n')[0]) > 400:
        eprint(f"\033[0;31;47m WARNING: tool description longer than 400 characters\033[0m")
    with open(properties, 'w') as out_json:
        json.dump(prop, out_json, sort_keys=False, indent=2)
    out_json.close()


def write_properties_default(args, properties):
    install_date = daytime()
    if args.datetime:
        install_date = args.datetime
    prop = {
        'name': args.name,
        'bio.tools_id': '',
        'description': '',
        'homepage': '',
        "operation": '',
        "topic": '',
        'version': {
            args.version: {
                "localInstallUser": args.installer,
                "environment": environment[args.environment],
                "localInstallDate": install_date,
                "isCmdline": args.cmdline,
                "isGalaxy": args.galaxy,
                "isWorkflow": args.workflow,
                "status": "active"
            }
        }
    }
    with open(properties, 'w') as out_json:
        json.dump(prop, out_json, sort_keys=False, indent=2)
    out_json.close()
