#!/usr/bin/env python3

import argparse
import re
from jinja2 import Template

def getArgs():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('-i',dest="info",type=argparse.FileType('r'),required=True,help='Info file to generate the web page')

    args = parser.parse_args()

    return args

def main(args):
    # Get data from args
    data = {'CLUSTERNAME': None,
            'TOOLDIRECTORYPATH': None,
            'PAGETITLE': None }

    # Read the file and get the infos
    for l in args.info:
        key, value = re.split(r'=', l.rstrip('\n'))
        data[key] = value

        if key == 'TEMPLATE':
            template = open(value, "r").read()
        elif key == 'WEBPAGEFILENAME':
            webpage = open(value, "w")

    #Load the template and make the rendering
    tm = Template(template)
    msg = tm.render(d=data)
    webpage.write(msg)

    # Close file
    webpage.close()

if __name__ == '__main__':
    args = getArgs()
    main(args)
