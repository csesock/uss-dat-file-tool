# United Systems .dat File Tool

This tool combines a number of python scripts into one singular package that helps with easily parsing, testing, and modifying
download and upload files for use with both MVRS and FCS. 

## Features
Current features of this tool include:
- [x] Scan for specific records 
- [x] Export missing meters to both .txt and .csv
- [x] Export a specific meter type to .txt
- [x] Print Office-Region-Zone fields for debugging
- [x] Check for malformed lat/long data
- [x] Perform full scans of download files


Future improvements include:
- [ ] Modifying download files safely from the command line
- [ ] Standalone scripts for each operation included
- [ ] Dependency-free graphical user interface for the tool


## Dependencies
There are two included versions of the tool in the repo, one with third-party library dependencies and one without. The actively developed version is the one with dependencies, while the standalone version gets features added after they've been thoroughly tested.

Think of them as a beta and release build. 

## Installation and Usage
To use the tool, simply install the most recent version of Python (3.X) and ensure that Python exists in the PATH. 

By default, this tool only uses the download file in the current working directory. A future update will add the option to switch to upload files or change file name/paths from the command line. 

## 

For feature requests/comments email christophers@united-systems.com
