#!/usr/bin/env python

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

import os
import pandas as pd
import collections
import string
import argparse

# ------------------------------------------------------------------
# --  FUNCTIONS    -------------------------------------------------
# ------------------------------------------------------------------

# ------------------------------------------------------------------
# Collect all files at a certain depth
# Argument directory: root directory used to start collecting files
# Argument depth: depth level to digging - fixed at 2 as structure is ./toolName/version/
# Return an os.walk() object - path, dirs names, files into each dir
def walklevel(directory=".", depth = 2):
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

# ------------------------------------------------------------------
# Collect properties files.
# Argument directores: root, dirs and files from os.walk()
# Return a list of file absolute paths
def getFiles(directories):
    filesList=[]
    for root, dirs, files in directories:
        if 'tool.properties' in files:
            abs_f=os.path.join(root, 'tool.properties')
            filesList.append(abs_f)
    return filesList

# ------------------------------------------------------------------
# Read properties from file as they are provided
# argument: a file containing tool's properties
# return: a dictionary with tool's properties
def readFile(propertiesFile):
    properties = {}
    properties['PATH'] = os.path.dirname(propertiesFile)
    with open(propertiesFile) as myfile:
        for line in myfile:
            cleanedLine=line.strip()
            if cleanedLine and cleanedLine[0]!='#':
                name,value=cleanedLine.partition("=")[::2]
                properties[name.strip()]=value.strip()
    return properties

# ------------------------------------------------------------------
# Format a particular value for HTML presentation
# argument key: key of property to format
# argument value: the value to format
# return a formatted value as a string
def formatData(key, properties, DATA_FORMATTER):
    if key in DATA_FORMATTER:
        new_value=str.replace(DATA_FORMATTER[key], "@DATA@", properties[key])
        if key=="CMDLINE" and "CMD_INSTALL" in properties:
            install_type=properties["CMD_INSTALL"]
            new_value+=("&nbsp;"+str.replace(DATA_FORMATTER["CMD_INSTALL"], "@DATA@", install_type))
        return new_value
    else:
        return properties[key]

# ------------------------------------------------------------------
# Order properties
# argument properties: dictionary with tool's properties
# return an OrderedDict
def orderProperties(properties, ORDERED_KEYS, DATA_FORMATTER):
    orderedProperties=collections.OrderedDict()
    for okey in ORDERED_KEYS:
        if okey in properties:
            orderedProperties[okey]=formatData(okey, properties, DATA_FORMATTER)
    return orderedProperties

# ------------------------------------------------------------------
# Write html file for direct visualisation
# argument properties: data with properties and key to visualize
def writeHTML(htmlfile, data, KEYS_TO_LABELS):
    # step 4: use Pandas to prepare HTML output
    #pd.set_option('display.max_colwidth', -1)
    # convert our data to a Pandas' data frame
    df = pd.DataFrame.from_dict(data)
    df.rename(columns=lambda x: KEYS_TO_LABELS[x], inplace=True)

    # Dict used to setup table styles
    cellpadding = '10px'
    linestyle = '1px solid #ddd'
    d = [
        {'selector':'th','props':[('text-align', 'center'),('border-bottom', linestyle),('padding-left',cellpadding)]},
        {'selector':'tr:hover','props': [('background-color', '#F0F8FF')]}
      ]

    all_labels = list(KEYS_TO_LABELS.values())
    firstColLabel = all_labels.pop(0)

    # format the data as an HTML table
    s = df.style.set_properties(
            subset=[firstColLabel],
            **{'text-align': 'left','border-bottom': linestyle,'padding-left': cellpadding})\
          .set_properties(
            subset=all_labels,
            **{'text-align': 'center','border-bottom': linestyle,'padding-left': cellpadding})\
          .set_table_styles(d)

    # write output html files
    webhtml = open(htmlfile, 'w')
    webhtml.write("<html>\n<body>\n")
    webhtml.write(s.render())
    webhtml.write("\n</body>\n</html>\n")

# ------------------------------------------------------------------
def getArgs():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('-p',dest="directory",type=str,default="../test/catalogue/",help='home directory of software properties')
    parser.add_argument('-o',dest="htmlfile",type=str,default="tool-directory.html",help='HTML file containing list of tools')

    args = parser.parse_args()

    return args

def main(args):
    # ------------------------------------------------------------------
    # --  DEFINITIONS  -------------------------------------------------
    # ------------------------------------------------------------------
    # Extension of files containing tool's descriptions
    TOOL_EXT       = "tool.properties"
    # Property keys used to build HTML table:
    #  1- colum order to use in the table
    ORDERED_KEYS   = ["NAME","VERSION","CMDLINE","GALAXY","KEYWORDS","URLDOC"]
    #  2- column labels
    KEYS_TO_LABELS = {
            'NAME'    : 'Tool name',
            'VERSION' : 'release',
            'CMDLINE' : 'cmd-line',
            'GALAXY'  : 'Galaxy',
            'KEYWORDS': 'Available for',
            'URLDOC'  : 'Manual'
            }
    # Which keys have to be reformatted
    # @DATA@ is a reverved keyword used to introduce value into formatted string
    # Accepted values for @DATA@ for CMDLINE and GALAXY: true, false (lower case!)
    DATA_FORMATTER = {
        'URLDOC'      : '<a href="@DATA@"><img src="./images/document.png" border="0"></a>',
        'CMDLINE'     : '<img src="./images/@DATA@.png" border="0">',
        'CMD_INSTALL' : '<img src="./images/@DATA@.png" border="0">',
        'GALAXY'      : '<img src="./images/@DATA@.png" border="0">'
    }

    # ------------------------------------------------------------------
    # --  MAIN  --------------------------------------------------------
    # ------------------------------------------------------------------
    # step 1: digging tool directory and explore at 2 level of depth
    directories = walklevel(args.directory)

    # step 2: collect all properties files
    filesList=getFiles(directories)
    filesList.sort(key=str.lower)

    # step 3: read all tool's properties
    data=[]
    for fl in filesList:
        # In case of problem with the input file
        print(fl)
        # Get and order properties
        props = readFile(fl)
        oprops = orderProperties(props, ORDERED_KEYS, DATA_FORMATTER)
        data.append(oprops)

    # step4: write html file with informations from all tools
    # backup option if Keshif visualisation is problematic
    writeHTML(args.htmlfile, data, KEYS_TO_LABELS)

if __name__ == '__main__':
    args = getArgs()
    main(args)
