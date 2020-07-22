# United Systems .dat File Tool

This tool combines a number of python scripts into one singular package that helps with easily parsing, testing, and modifying
download and upload files for use with both MVRS and FCS. 

## Features
Current features of this tool include:
- [x] Scan for specific records 
- [x] Identify missing meter numbers
- [x] Identify all read type codes
- [x] Print Office-Region-Zone fields for debugging
- [x] Check for malformed lat/long data
- [x] Perform full scans of download files
- [x] Graphical user interface for ease-of-use
- [x] Save any parsed data as .txt or .csv

Future improvements include:
- [ ] Modifying download files safely from the command line
- [ ] Standalone scripts for each operation included
- [ ] General UI improvements

## User Interface
Currently, the main focus of development is an easy-to-use UI that requires no external libraries. Written in pure python in the tkinter library. 

![GUI](https://imgur.com/eTnUivD.png)

## Dependencies
There are two included versions of the tool in the repo, one with third-party library dependencies and one without. The actively developed version is the one with dependencies, while the standalone version gets features added after they've been thoroughly tested.

Think of them as a beta and release build. 

## Installation and Usage
To use the tool, simply install the most recent version of Python (3.X) and ensure that Python exists in the PATH. 

By default, this tool only uses the download file in the current working directory. A future update will add the option to switch to upload files or change file name/paths from the command line. 

This problem can also be solved by using the UI, which will read the default 'download.dat' file in the same directory, or can alternatively open any .dat or .hdl file. 

## 

For feature requests/comments email christophers@united-systems.com
