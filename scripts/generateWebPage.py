#!/usr/bin/env python3

import argparse
import re
import os
from jinja2 import Template

def getArgs():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('-i',dest="info",type=argparse.FileType('r'),required=True,help='File with informations to generate the web page')
    parser.add_argument('-p',dest="path",type=str,required=True,help='Destination for html file')

    args = parser.parse_args()

    return args

def main(args):
    data = {}
    # Read the file and get the infos
    for l in args.info:
        key, value = re.split(r'=', l.rstrip('\n'))
        data[key] = value

    template = open('../template/template.html', "r").read()
    webpage = open(os.path.join(args.path, 'index.html'), "w")

    #Load the template and make the rendering
    tm = Template(template)
    msg = tm.render(d=data)
    webpage.write(msg)

    # Close file
    webpage.close()

if __name__ == '__main__':
    args = getArgs()
    main(args)
