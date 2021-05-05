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
import json
import pandas as pd
import collections

def walk_level(directory, depth = 2):
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

def get_json(directories):
    json_list=[]
    for root, dirs, files in directories:
        if 'properties.json' in files:
            abs_f=os.path.join(root, 'properties.json')
            json_list.append(abs_f)
    return json_list

def format_data(key, properties, DATA_FORMATTER):
    if key in DATA_FORMATTER:
        new_value=str.replace(DATA_FORMATTER[key], "@DATA@", properties[key])
        if key=="CMDLINE" and "CMD_INSTALL" in properties:
            install_type=properties["CMD_INSTALL"]
            new_value+=("&nbsp;"+str.replace(DATA_FORMATTER["CMD_INSTALL"], "@DATA@", install_type))
        return new_value
    else:
        return properties[key]

def order_properties(properties, ORDERED_KEYS, DATA_FORMATTER):
    orderedProperties=collections.OrderedDict()
    for okey in ORDERED_KEYS:
        if okey in properties:
            orderedProperties[okey]= format_data(okey, properties, DATA_FORMATTER)
    return orderedProperties

def write_html(htmlfile, data, KEYS_TO_LABELS):
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

def html(args):
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
    # Step 1: digging tool directory and explore at 2 level of depth
    directories = walk_level(args.directory)
    # Step 2: collect all properties files
    json_list = get_json(directories)
    json_list.sort(key=str.lower)
    # Step 3: read all tool's properties
    data=[]
    for fl in json_list:
        # In case of problem with the input file
        print(fl)
        # Get and order properties
        # props = readFile(fl)
        with open(fl) as json_data:
            p = json.load(json_data)
        order_p = order_properties(p, ORDERED_KEYS, DATA_FORMATTER)
        data.append(order_p)

    # step4: write html file with informations from all tools
    # backup option if Keshif visualisation is problematic
    write_html(args.htmlfile, data, KEYS_TO_LABELS)