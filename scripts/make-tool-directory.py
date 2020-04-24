#!/usr/bin/env python

# =============================================================================
# Tool Directory - v1.0.0
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
# (c) 2017 Ifremer-Bioinformatics Team
# =============================================================================

import os
import pandas as pd
import collections
import string
from optparse import OptionParser
# Devel
import random

# ------------------------------------------------------------------
# --  DEFINITIONS  -------------------------------------------------
# ------------------------------------------------------------------

# Root directory containing tools; defualt is the test Directory
# You can use argument "-d" (see main, below)
TOOLS_DIR      = "../test/catalogue"

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
# --  FUNCTIONS    -------------------------------------------------
# ------------------------------------------------------------------

# def fileCompare(f1, f2):
#     props1 = readFile(f1)
#     props2 = readFile(f2)
#     if props1["NAME"].lower() < props2["NAME"].lower():
#         return -1
#     elif props1["NAME"].lower() == props2["NAME"].lower():
#         return 0
#     else:
#         return 1

# ------------------------------------------------------------------
# Collect properties files.
# argument directory: root directory used to start collecting files
# return a list of file absolute paths
def getFiles(directory="."):
    filesList=[]
    for root, dirs, files in os.walk(TOOLS_DIR):
        for file in files:
            if file.endswith(TOOL_EXT):
                abs_f=os.path.join(root, file)
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
def formatData(key, properties):
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
def orderProperties(properties):
    orderedProperties=collections.OrderedDict()
    for okey in ORDERED_KEYS:
        if okey in properties:
            orderedProperties[okey]=formatData(okey, properties)
    return orderedProperties

# ------------------------------------------------------------------
# Write csv file for keshif
# argument properties: dictionary with tool's properties
def writeCSV(properties):
    txt = open('Softwares.csv', 'w')
    txt.write('Name,Operation,Environment,Topic,Access,Doc,Description,Path\n')
    for tool in sorted(properties.keys(), key=lambda x:x.lower()):
        p = properties[tool]
        if p['CMDLINE'] == 'true' and p['GALAXY'] == 'true':
            p['ACCESS'] = 'Galaxy and cmdline'
        elif p['CMDLINE'] == 'true' and p['GALAXY'] == 'false':
            p['ACCESS'] = 'Cmdline only'
        else:
            p['ACCESS'] = 'Galaxy only'
        # Topic -> randomized for the dev
        p['TOPIC'] = random.choice(['Epigenetics','Multi-thematic','Genomics','Metabarcoding','Metagenomics','Transcriptomics','Other'])
        name = p['NAME'] + ' - ' + p['VERSION']
        txt.write('"{0}","{1}","{2}","{3}","{4}","{5}","{6}","{7}"\n'.format(name,
                                                                            p['KEYWORDS'],
                                                                            p['CMD_INSTALL'],
                                                                            p['TOPIC'],
                                                                            p['ACCESS'],
                                                                            p['URLDOC'],
                                                                            p['DESCRIPTION'],
                                                                            p['PATH']))
    #Close file
    txt.close()

# ------------------------------------------------------------------
# --  MAIN  --------------------------------------------------------
# ------------------------------------------------------------------
# Collect arguments if any provided
parser = OptionParser()
parser.add_option(
    "-d", "--directory",
    dest="directory",
    help="home directory of software properties",
    metavar="DIR")
(options, args) = parser.parse_args()
if options.directory!=None:
  TOOLS_DIR=options.directory

# step 1: collect all properties files
filesList=getFiles(TOOLS_DIR)

# step 2: read all tool's properties
data=[]
csv={}
for fl in filesList:
    # In case of problem with the input file
    print(fl)
    # Get and order properties
    props = readFile(fl)
    oprops = orderProperties(props)
    data.append(oprops)
    # Get the data for the csv file
    tool = props['NAME'] +'-'+ props['VERSION']
    csv[tool] = props

# step3: write csv file with informations from all tools
# will be used for Keshif visualisation
writeCSV(csv)

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
webhtml = open('clustertools.html', 'w')
webhtml.write("<html>\n<body>\n")
webhtml.write(s.render())
webhtml.write("\n</body>\n</html>\n")
