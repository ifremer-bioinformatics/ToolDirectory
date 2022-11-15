# ToolDirectory
## Introduction

ToolDirectory provides a convenient tool to display list of softwares in a webpage along with dynamic data filtering capabilities.

![Tool Directory](images/tooldirectory.png)

You can test our [public demo](https://ifremer-bioinformatics.github.io/ToolDirectorySample/)

## Direct use of ToolDirectory Viewer

ToolDirectory is a Python 3.x program. It also requires the following package:

* requests >=2.25.1
* rich-click >=1.5.2
* loguru >=0.6.0

```
conda create -p tooldir -c anaconda requests=2.25.1 rich-click=1.5.2 loguru=0.6.0
```

Web rendering relies on the open-source version of [Keshif](https://github.com/adilyalcin/Keshif) data visualisation. We provided [Katalog](https://gitlab.ifremer.fr/bioinfo/katalog), a lightweight version specifically designed for ToolDirectory and DataDirectory.

## Basic usage

```bash
$ tooldir -h
 Usage: tooldir [OPTIONS] COMMAND [ARGS]...                              
                                                                         
 ToolDirectory: A dynamic visualization of pieces of software managed by 
 a Bioinformatics Core Facility                                          
                                                                         
╭─ Options ─────────────────────────────────────────────────────────────╮
│ --version        Show the version and exit.                           │
│ --help     -h    Show this message and exit.                          │
╰───────────────────────────────────────────────────────────────────────╯
╭─ Main usage ──────────────────────────────────────────────────────────╮
│ create     Create tool properties or add a new version                │
│ update     Update metadata of a tool                                  │
│ status     Set installation status of a tool's version                │
╰───────────────────────────────────────────────────────────────────────╯
╭─ Visualization ───────────────────────────────────────────────────────╮
│ kcsv      Create csv for Keshif visualisation                         │
╰───────────────────────────────────────────────────────────────────────╯
```

## Data structure

ToolDirectory expects a directory structure with the following constraints:
- /path/to/tools/tool-name/tool-version/

Or, with [modules](http://modules.sourceforge.net/) architecture:
- /path/to/tools/tool-name/modulefile

Or, with [modules](http://modules.sourceforge.net/) architecture:
- \<install-dir>/\<tool>/<version-module>

Here is an example:

```
/path/to/tools/
  ├── blast
  │    ├── 2.2.31 #Folder or modulefile
  │    └── 2.6.0
  ├── plast
  │    └── 2.3.2
  ├── beedeem
  │    └── 4.3.0
  .../...
```

## Usage
#### Creation a tool description

```bash
tooldir create -n <tool-name> -v <tool-version> -o <username> -p /path/to/tools/
```
Sometimes the processus fails: it happens when the tool is not referenced yet in [Bio.tools](https://bio.tools/). You can manually fill the missing fields  but we strongly encourage you to create the tool description on [Bio.tools](https://bio.tools/) and recreate or update the json.

In the case of the installation of an addition of a new version, the json is modified to add the associated information without changing the metadata of the tool.

#### Update tool metadata
```bash
tooldir update -j /appli/bioinfo/spades/properties.json
```

#### Force metadata search based on Bio.tools ID

It may happen that the name you gave for the tool differs from the identifier given in Bio.tools. In this case, it is possible to force the search to retrieve the metadata.

```bash
tooldir create -n interproscan -v 5.48-83.0 -o acormier -b interproscan_ebi
```
```bash
tooldir update -j /appli/bioinfo/interproscan/properties.json -b interproscan_ebi
```

## Setup visualisation

You will need [Katalog](https://gitlab.ifremer.fr/bioinfo/katalog), a lightweight version of [Keshif](https://github.com/adilyalcin/Keshif) specifically designed for ToolDirectory and DataDirectory.


```bash
git clone https://gitlab.ifremer.fr/bioinfo/katalog.git /foo/bar/www/tooldirectory
```

Then, generate the software list:
```bash
tooldir kcsv -p /path/to/tools/ -c /foo/bar/www/tooldirectory/Softwares.csv

```

You can use a crontab to automatically update the software listing.

## Licenses

Tool Directory is released under the terms of the Apache 2 license.
