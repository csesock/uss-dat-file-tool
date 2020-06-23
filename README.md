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

Future improvements include:

- [ ] Modifying download files safely from the command line
- [ ] Perform full scans of download files
- [ ] Standalone scripts for each operation included


## Dependencies
This project has been built from the start for ease of use and, consequently, to have no dependencies. The only requirement to run it is the current version of Python (3.8.X).

## Usage
By default, this tool only uses the download file in the current working directory. A future update will add the option to switch to upload files or change file name/paths from the command line. 

## 

For feature requests/comments email christophers@united-systems.com
