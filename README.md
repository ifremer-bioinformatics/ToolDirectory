# Tool Directory Software

## Introduction

ToolDirectory provides a convenient tool to display list of softwares in a graphical way along with dynamic data filtering capabilities. It was primarily designed to help end users find their way among several hundred of bioinformatics tools installed on our supercomputer DATARMOR at IFREMER. The tool relies on a standard way of describing softwares: EDAM Topic and Operation terms, installation types, supported platforms, packaging, etc. These description "facets" are available for dynamic software filtering directly in the viewer.

ToolDirectory provides a way to go from an "ugly" terminal listing:
```
/path/to/bioinfo-softwares
  ├── blast
  │    ├── 2.2.31
  │    └── 2.6.0
  ├── plast
  │    └── 2.3.2
  ├── beedeem
  │    └── 4.3.0
  .../...
```

Two views are available:
- a simple web page (since ToolDirectory v1)
- a dynamic data exploration viewer (introduced with ToolDirectory v2).

### The simple web viewer

This is a basic HTML Table aims at providing a clear overview of software name and version, software classification keywords and direct link to documentation. It is available since Tool Directory first release.

![Tool Directory](doc/test-page.png)

### The dynamic data exploration viewer

It provides an extensive presentation of bioinformatics softwares along with data filtering features relying on [EDAM](https://ifb-elixirfr.github.io/edam-browser) Topic and Operation terms. It was introduced with Tool Directory release 2.0. Check out a working viewer [here](https://ifremer-bioinformatics.github.io/ToolDirectorySample/).

![Tool Directory](doc/facet-viewer.png)

[Check out by yourself](https://ifremer-bioinformatics.github.io/ToolDirectorySample/)

## Installation

This tool is a Python 3.x program. It also requires the following packages used to build the HTML report:

* Pandas (tested with release 0.21)
* Jinja2 (tested with release 2.9.6)
* Requests (tested with release 2.25.1)

```
conda create -p tooldir-v3.0 -c jinja2 pandas requests
```

Tool Directory also relies on the open-source version of [Keshif](https://github.com/adilyalcin/Keshif) data visualisation, included in this package, i.e. you do not have to install it.

## Basic usage

```bash
$ tooldir -h
usage: tooldir <command> [<args>]
            The available commands are:
            create   Create tool properties
            update   Update tool properties (add new key(s), change values)
            upgrade  Upgrade tool properties to JSON (v2 -> v3)
            kcsv     Create csv for Keshif visualisation
            khtml    Create core webpage for Keshif
            html     Create a basic html view
```

## Prepare your Directory

### Expected directory structure

Tool Directory expects a directory structure with the following constraints:

- \<install-dir>/\<tool>/\<version>/

Here is an example:

```
/appli/bioinfo
  ├── blast
  │    ├── 2.2.31
  │    └── 2.6.0
  ├── plast
  │    └── 2.3.2
  ├── beedeem
  │    └── 4.3.0
  .../...
```
### Declaring your softwares

To declare your softwares to Tool Directory you just have to setup a propertie file, one per software. It contains the description of a single software and it has to follow these two constraints

* file must be called ```properties.json```
* file is located within home directory of a software

For instance, considering our PLAST 2.3.2 installation, we have setup a file called ```properties.json``` located in /appli/bioinfo/plast/2.3.2:

```
{
  "NAME": "PLAST",
  "DESCRIPTION": "High Performance Parallel Local Alignment Search Tool",
  "VERSION": "2.3.3",
  "CMDLINE": "true",
  "GALAXY": "true",
  "URLDOC": "https://plast.inria.fr/user-guide/",
  "KEYWORDS": "sequence-similarity-search",
  "CMD_INSTALL": "shell",
  "TOPIC": "Biological databases",
  "DATE_INSTALL": "11/07/2018",
  "OWNER": "galaxy"
}
```
Keys explanation:

```
NAME: the name of the software
DESCRIPTION: a short one line description of the software
VERSION: the release tag of the software
CMDLINE: software available on the command-line? (only use one of: true, false)
GALAXY: software available on GALAXY Workflow platform? (only use one of: true, false)
URLDOC: URL to the user manual
KEYWORDS: one or several keywords to classify your software using EDAM Operation terms
TOPIC: one or several keywords to classify your software using EDAM Topic terms
CMD_INSTALL: the way a tool is installed. (one of: conda, docker, shell)
```
All but GALAXY keys are valid to describe your softwares, whatever their field of application. Then, regarding KEYWORDS values, we rely on the EDAM-operation names (see http://edamontology.org/page). It is up to you to choose whatever naming system appropriate to classify your tools.

For a complete list of example of such 'properties.json' files, look at ![catalogue directory](test/catalogue).

### Automatic creation of properties using Bio.tools API

To be consistent between the descriptions of your softwares, we strongly recommend to use the Bio.tools database.

To do such job, you can use ```tooldir create``` which will automatically create the ```properties.json``` as follows:

```bash
tooldir create -n bowtie2 -v 2.3.5 -o username
```
By default, it will search for the parameter file into  ```~/.tooldir.params``` which contains the structure of your install environment, as follow:

```
{
    "install_dir_path": "/foo/bar/",
    "conda_envs_path": "/foo/tools_env/",
    "anaconda_dir_path": "/foo/anaconda/<versions>/",
    "anaconda_profile_d": "/foo/anaconda/<versions>/etc/profile.d/conda.sh",
    "topics":
        [
            "Bioimaging",
            "Bioinformatics",
            "Biological databases",
            "Comparative genomics",
            "Data visualisation",
            "Statistics and probability",
            "Structure analysis",
            "Transcriptomics"
        ]
}
```

And you can indicate a restrictive list of allowed topics.

## Tool Directory use

### Testing the tool

You can test the tool as follows:

```
tooldir html -o test.html
```
Then open "test.html" in your web browser. You should see sometjing like this:

![Tool Directory](doc/test-page.png)

### Using the tool with your software listing

You use Tool Directory in a very straightforward way:

```
tooldir khtml -p <directory> -o my-listing.html

where:
     directory: root directory of your software installation; considering our
                sample directory tree structure (see above), we will use:
                -d /appli/bioinfo
     my-listing.html: the list of your software, Html/Table formatted; use a
                file name as needed
```

## Setup the simple HTML based view

Simply uses the procedure described in the Testing section, above.

## Setup the data exploration view

### Prepare the dynamic viewer basic files

Steps to execute one time  are
- On your web server, locate the 'www' directory, then create a sub-folder, e.g. 'tool-directory' ;
- Copy content of 'thirdparty/Keshif/*' into 'www/tool-directory' ;
- Copy file 'css/software_browser.css' into 'www/tool-directory' ;
- Edit file 'template/example.lst' and update field values to match your system ;
- Run script 'scripts/generateWebPage.py' to generate html template into 'www/tool-directory' ;

### Prepare the CSV file required by the viewer

- Run script 'scripts/make-csv-directory.py' to prepare CSV file' and place it into 'www/tool-directory'.

That step has to be executed each time yout install a new software into your repository of tools; at Ifremer, we use a cron task.

## Licenses

Tool Directory is released under the terms of the Apache 2 license.

Tool Directory data exploration viewer uses the open-source version of [Keshif](https://github.com/adilyalcin/Keshif), a web-based data exploration environment for data analytics. Keshif open-source is released under the terms of the BSD-3 clause license.
