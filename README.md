# Tool Directory Software

## Introduction

This package provides an easy and convenient tool to display in a graphical way list softwares installed on a local system. 

Tool Directory was originally designed to provide a summary of all bioinformatics tools installed on the DATARMOR supercomputer at IFREMER.

**Two views are available**: either a simple web page or a data exploration viewer. 

**The simple web viewer** is a basic HTML Table aims at providing a clear overview of software name and version, software classification keywords and direct link to documentation. 

![Tool Directory](doc/test-page.png)

**The data exploration viewer** provides an extensive presentation of bioinformatics softwares along with data filtering features relying on [EDAM](https://ifb-elixirfr.github.io/edam-browser) Topic and Operation terms.

![Tool Directory](doc/facet-viewer.png)

In other words, ToolDirectory provides a convenient way to go from an "ugly" terminal listing:
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

to nice views to be presented as a web page for your users.

## Dependencies

This tool is a Python 2.7 program. It also requires the following packages used to build the HTML report:

* Pandas (tested with release 0.21)
* Jinja2 (tested with release 2.9.6)

Depending on your host configuration you can install these dependencies using either Python package manager or Conda. At IFREMER, we use conda and we had setup a Conda environment as follows:

```
conda create -n ToolDirectory-1.0
source activate ToolDirectory-1.0
conda install -c python=2.7 Jinja2 pandas
```
## Prepare your Directory

### What is a directory?

This is simply the place (*i.e.* a folder on your computing system) where your (bioinformatics) softwares are installed; while Tool Directory was designed to handle a catalog of bioinformatics tools, is can be used for any other software lisiting.

### Expected directory structure

Tool Directory expects a directory structure with the following constraints:

* **directory** is a folder on your computing system; let's call it *tool-home-dir*
* all softwares to be listed are located in sub-folders of *tool-home-dir*
* softwares having different releases are also organized using sub-folders

Here is an example of a simple *tool-home-dir*:

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

Now, to declare your softwares to Tool Directory you just have to setup Property files, one per software. Such a Property file contains the description of a single software (see below) and it has to follow these two constraints

* file must be called "tool.properties"
* file is located within home directory of a software

For instance, considering our PLAST 2.3.2 installation (see above directory tree structure), we have setup a file called "tool.properties" located in /appli/bioinfo/plast/2.3.2.

Here is the content of "tool.properties" for PLAST 2.3.2:

```
NAME=PLAST
DESCRIPTION=High Performance Parallel Local Alignment Search Tool
VERSION=2.3.2
CMDLINE=true
GALAXY=true
URLDOC=https://plast.inria.fr/user-guide/
KEYWORDS=pairwise-sequence-alignment
CMD_INSTALL=shell
```
As you can see this is basically a set of key=value pairs. Keys are reserved case-sentive words and values are set by you.

Here is such a Property file explained:

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

For a complete list of example of such 'tool.properties' files, look at ![catalogue directory](test/catalogue).

### Modifying keys in Property files

Maybe you could be interested in adding, removing or renaming the keys of a Property file. Of course, this is possible: just edit the Python source code of Tool Directory and adapt it to your needs. The source code is fully documented and it should be easy to modify it.

In a similar way, you can add more CMD_INSTALL values. If you do so, just ensure that you add the corresponding image in the images folder. For instance, the value docker is associated to images/docker.png file.

## Tool Directory use

### Testing the tool

You can test the tool as follows:

```
make-tool-directory.py > test.html
```
Then open "test.html" in your web browser. You should see sometjing like this:

![Tool Directory](doc/test-page.png)

### Using the tool with your software listing

You use Tool Directory in a very straightforward way:

```
make-tool-directory.py -d <directory> > my-listing.html

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

## Licenses

Tool Directory is released under the terms of the Apache 2 license.

Tool Directory data exploration viewer uses the open-source version version of [Keshif](https://github.com/adilyalcin/Keshif), a web-based data exploration environment for data analytics. Keshif open-source is released under the terms of the BSD-3 clause license.

