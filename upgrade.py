#!/usr/bin/env python3

import argparse
import json
import os
from lib import core_tool as cl


def getArgs():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('-p', dest="path", type=str, default='test/datarmor/', help='Path to properties files')

    arg = parser.parse_args()

    return arg


def extract_properties(jsons):
    tools_properties = {}
    for f in jsons:
        bio_json = json.load(open(f))
        tool_name = os.path.dirname(f).split(os.sep)[-2]
        if tool_name not in tools_properties:
            tools_properties[tool_name] = {'path': os.path.join(args.path, tool_name),
                                           'properties': {'name': bio_json['NAME'],
                                                          'description': bio_json['DESCRIPTION'],
                                                          'homepage': bio_json['URLDOC'],
                                                          "operation": bio_json['KEYWORDS'],
                                                          "topic": bio_json['TOPIC'],
                                                          'version': {
                                                              bio_json['VERSION']: {
                                                                  "localInstallUser": bio_json['OWNER'],
                                                                  "environment": bio_json['CMD_INSTALL'],
                                                                  "localInstallDate": bio_json['DATE_INSTALL'],
                                                                  "isCmdline": bio_json['CMDLINE'],
                                                                  "isGalaxy": bio_json['GALAXY']
                                                              }
                                                          }}}
        else:
            tools_properties[tool_name]['properties']['version'][bio_json['VERSION']] = {
                "localInstallUser": bio_json['OWNER'],
                "environment": bio_json['CMD_INSTALL'],
                "localInstallDate": bio_json['DATE_INSTALL'],
                "isCmdline": bio_json['CMDLINE'],
                "isGalaxy": bio_json['GALAXY']
                }
    return tools_properties


def update_from_biotools(properties):
    for tool_id, tool_property in properties.items():
        try:
            response, code = cl.biotools_api_request(tool_property['properties']['name'])
            bio_update = json.loads(response)
            operation = []
            for i in bio_update['function']:
                operation.append(i['operation'][0]['term'].lower().replace(' ', '-'))
            operations = ','.join(list(set(operation)))
            topic = []
            for i in bio_update['topic']:
                topic.append(i['term'])
            topics = ','.join(list(set(topic)))
            tool_property['properties']['description'] = bio_update['description'].split('\n')[0]
            tool_property['properties']['homepage'] = bio_update['homepage']
            tool_property['properties']['operation'] = operations
            tool_property['properties']['topic'] = topics
        except:
            pass

    return properties


def export_new_json_properties(properties):
    for tool_id in properties.keys():
        with open(os.path.join(properties[tool_id]['path'], 'properties.v2.json'), 'w') as out_json:
            json.dump(properties[tool_id]['properties'], out_json, sort_keys=False, indent=2)
        out_json.close()


def main(args):
    directories = cl.walk_level(args.path)
    jsons = cl.get_json(directories)
    old_properties = extract_properties(jsons)
    new_properties = update_from_biotools(old_properties)
    export_new_json_properties(new_properties)


if __name__ == '__main__':
    args = getArgs()
    main(args)
