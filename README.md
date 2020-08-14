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
Currently, the main focus of development is an easy-to-use UI that requires no external libraries. Written in pure python using the tkinter library. 

![GUI](https://imgur.com/TcvyKQH.png)

## Dependencies
Currently, the tool has moved away from a command-line collection of scripts and towards a UI-based tool which allows for a number of more practical features. Despite this move towards verbosity, there are still no third-party depenencies within the tool; simply install Python and double click 'USSdatFileTool.py' to get started using the tool. 

This will be the focus moving forward, and any iteration of the tool that includes third-party libraries will be clearly delineated. 

## Installation and Usage
To use the tool, simply install the most recent version of Python (3.X) from https://www.python.org/downloads/ and ensure that Python exists in the PATH. 

##

By default, the tool does not restrict which types of files can be imported and tested. This can be changed in the 'Settings' tab, by checking 'Enforce filetype imports'. Doing so will only allow .dat and .hdl files to be read by the tool. 

##

The tool also has a logging system to help identify errors in both the tool and files read by the tool. By default, the tool never deletes these files, but these log files can be manually purged in the menu, and the number of maximum log files can be configured in the 'Settings' tab. 

## 

Currently, the tool support saving any information currently in the console as a .txt, .csv, and .py file. To request additional filetypes be added, contact me at the email address below or make a pull request. 

##

For additional feature requests/comments email: christophers@united-systems.com
