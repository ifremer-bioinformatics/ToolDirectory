from __future__ import print_function
import os
import json
import requests
import datetime
from requests.exceptions import HTTPError
from loguru import logger


def create_properties(name, bid, version, owner, cmd, galaxy, environment, workflow, date, properties):
    logger.info(f"Create properties file for {name}")
    search = name
    if bid:
        search = bid
    response, code = biotools_api_request(search)
    if code == 404:
        write_properties_default(name, version, owner, cmd, galaxy, environment, workflow, date, properties)
    else:
        logger.info(f"Load and parse JSON")
        biojson = json.loads(response)
        write_properties(name, version, date, owner, environment, cmd, galaxy, workflow, biojson, properties)
    logger.info(f"Done")


def add_version(name, version, date, owner, environment, cmd, galaxy, workflow, properties):
    logger.info(f"{name} already exist")
    logger.info(f"Adding the new version")
    with open(properties) as json_data:
        p = json.load(json_data)
    p_check = p['version'].keys()
    install_date = daytime()
    if date:
        install_date = date
    if version not in p_check:
        p['version'][version] = {
            "localInstallUser": owner,
            "environment": environment,
            "localInstallDate": install_date,
            "isCmdline": cmd,
            "isGalaxy": galaxy,
            "isWorkflow": workflow,
            "status": "active"
        }
        with open(properties, 'w') as o:
            json.dump(p, o, sort_keys=False, indent=2)
        o.close()
        logger.info(f"New version successfully added")
        logger.info(f"Done")
    else:
        logger.warning(f"Tool version already declared")
        logger.warning(f"Skip")


def update(jp, bid):
    with open(jp) as json_data:
        p = json.load(json_data)
    logger.info(f"Starting update metadata for {p['name']}")
    search = p['name']
    if p['bio.tools_id'] != '':
        search = p['bio.tools_id']
    if bid:
        search = bid
    response, code = biotools_api_request(search)
    if code == 404:
        logger.error(f"Enable to find {search} in Bio.tools")
        logger.error(f"Update aborded")
        if not bid:
            logger.error(f"Force search with --bid could solve this issue")
        exit(1)
    else:
        bio_update = json.loads(response)
        operation = []
        for i in bio_update['function']:
            operation.append(i['operation'][0]['term'].lower().replace(' ', '-'))
        operations = ','.join(list(set(operation)))
        topic = []
        for i in bio_update['topic']:
            topic.append(i['term'])
        topics = ','.join(list(set(topic)))
        p['description'] = bio_update['description'].split('\n')[0]
        p['homepage'] = bio_update['homepage']
        p['operation'] = operations
        p['topic'] = topics
        if bid:
            p['bio.tools_id'] = bid
        if len(p['description'].split('\n')[0]) > 400:
            logger.warning(f"Tool description longer than 400 characters")
        with open(jp, 'w') as out_json:
            json.dump(p, out_json, sort_keys=False, indent=2)
        out_json.close()
        logger.info(f"Properties successfully updated")
        logger.info(f"Done")


def set_status(properties, versions, status):
    with open(properties) as json_data:
        p = json.load(json_data)
    logger.info(f"Setting status for versions of {p['name']}")
    for version in versions:
        try:
            p['version'][version]['status'] = status
            logger.info(f"Status set to {status} for version: {version}")
        except KeyError:
            logger.warning(f"Invalid tool version: {version}")
            logger.warning(f"Skip...")
            pass
        with open(properties, 'w') as o:
            json.dump(p, o, sort_keys=False, indent=2)
        o.close()
        logger.info(f"Done")


def kcsv_writing(csv_out, json_lst):
    logger.info(f"Writing csv")
    txt = open(csv_out, 'w')
    txt.write('Name,Version,Operation,Topic,Doc,Description,Environment,Galaxy,Workflow\n')

    json_lst.sort(key=str.lower)

    for tool in json_lst:
        logger.info(f'Read {tool}')
        try:
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
                txt.write(
                    f'"{name}","{versions}","{operation}","{topic}","{homepage}","{description}","{environments}","{isGalaxy}","{isWorkflow}"\n')
        except Exception as error:
            logger.error(f"Error occurred: {error}")
            exit(1)
    txt.close()
    logger.info(f"CSV successfully written")
    logger.info(f"Done")


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


def daytime():
    now = datetime.datetime.now()
    time = now.strftime("%d-%m-%Y")
    return time


def biotools_api_request(search):
    logger.info(f"Collect metadata from Bio.tools for {search}")
    try:
        response = requests.get('https://bio.tools/api/tool/' + search + '/?format=json')
        response.raise_for_status()
        response_json = response.text
        code = response.status_code
        logger.info(f"Successfully retrieve metadata")

        return response_json, code

    except HTTPError as http_error:
        if response.status_code == 404:
            response_json = response.text
            code = response.status_code
            logger.warning(f"{search} is not described in Bio.tools")

            return response_json, code
        else:
            logger.error(f"HTTP error occurred: {http_error}")
            exit(1)
    except Exception as error:
        logger.error(f"Error occurred: {error}")
        exit(1)


def check_path(path, tool_name, tool_version):
    tool_path = os.path.join(path, tool_name)
    if not os.path.isdir(tool_path):
        logger.error(f"{tool_path} do not exist")
        exit(1)
    tool_version_path = os.path.join(path, tool_name, tool_version)
    if not os.path.isfile(tool_version_path) and not os.path.isdir(tool_version_path):
        logger.error(f"{tool_version_path} do not exist")
        exit(1)


def write_properties(name, version, date, owner, environment, cmd, galaxy, workflow, biojson, properties):
    logger.info(f"Writing properties file")

    operation = []
    for i in biojson['function']:
        operation.append(i['operation'][0]['term'].lower().replace(' ', '-'))
    operations = ','.join(list(set(operation)))
    if len(operation) == 0:
        logger.error(f"No operations EDAM terms found")
        exit(1)
    else:
        logger.info(f"{len(operation)} operations EDAM found")
    topic = []
    for i in biojson['topic']:
        topic.append(i['term'])
    topics = ','.join(list(set(topic)))
    if len(topic) == 0:
        logger.error(f"No topics EDAM terms found")
        exit(1)
    else:
        logger.info(f"{len(topic)} topics EDAM found")
    install_date = daytime()
    if date:
        install_date = date
    prop = {
        'name': name,
        'bio.tools_id': biojson['biotoolsID'],
        'description': biojson['description'].split('\n')[0],
        'homepage': biojson['homepage'],
        "operation": operations,
        "topic": topics,
        'version': {
            version: {
                "localInstallUser": owner,
                "environment": environment,
                "localInstallDate": install_date,
                "isCmdline": cmd,
                "isGalaxy": galaxy,
                "isWorkflow": workflow,
                "status": "active"
            }
        }
    }
    if len(biojson['description'].split('\n')[0]) > 400:
        logger.warning(f"Tool description longer than 400 characters")
    with open(properties, 'w') as out_json:
        json.dump(prop, out_json, sort_keys=False, indent=2)
    out_json.close()
    logger.info(f"Properties successfully written")


def write_properties_default(name, version, owner, cmd, galaxy, environment, workflow, date, properties):
    # eprint(f"\033[0;31;47m WARNING: writing empty properties file \033[0m")
    # eprint(f"\033[0;31;47m WARNING: please, fill it manual: {properties} \033[0m")
    logger.warning(f"Writing empty properties file")
    install_date = daytime()
    if date:
        install_date = datetime
    prop = {
        'name': name,
        'bio.tools_id': '',
        'description': '',
        'homepage': '',
        "operation": '',
        "topic": '',
        'version': {
            version: {
                "localInstallUser": owner,
                "environment": environment,
                "localInstallDate": install_date,
                "isCmdline": cmd,
                "isGalaxy": galaxy,
                "isWorkflow": workflow,
                "status": "active"
            }
        }
    }
    with open(properties, 'w') as out_json:
        json.dump(prop, out_json, sort_keys=False, indent=2)
    out_json.close()
    logger.info(f"Properties successfully written")
    logger.warning(f"Please, fill missing properties")
    logger.info(f"Don't hesitate to describe this tool in Bio.tools ;)")
