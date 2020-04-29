## Use of scripts to manage viewers

To generate the simple web page viewer, use:

```
./make-html-directory.py -p <directory> -o my-listing.html

where:
     directory: root directory of your software installation; considering our
                sample directory tree structure (see above), we will use:
                -d /appli/bioinfo
     my-listing.html: the list of your software, Html/Table formatted; use a
                file name as needed
```
To generate the CSV file required for the dynamic data viewer, use:

```
./make-csv-directory.py -p <directory> -o Softwares.csv

where:
     directory: root directory of your software installation; considering our
                sample directory tree structure (see above), we will use:
                -d /appli/bioinfo
     Softwares.csv: the list of your softwares, csv formatted; use a
                file name as needed
```
To generate the main web page for the the dynamic data viewer, use:

```
./generateWebPage.py -i ../template/template.html -p <directory>

where:
     directory: target directory to place generate HTML fil
```

## Use of script to manage project

To collect all "tool.properties" files of a software repository, use `collect-tool-properties.sh`. No arguments required, simply edit the script before use (very simple to do).


