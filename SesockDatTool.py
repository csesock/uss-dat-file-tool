# The convention in this program is to measure elapsed time by using
# time.time() when an execution begins, and then again when it ends.
# 
# for feature requests or feedback, email christophers@united-systems.com
# Author: Chris Sesock on 6-5-2020

import time 
import csv, sys, re, os
from pyfiglet import Figlet
from clint.textui import colored, puts, indent

# regular expression patterns
record_pattern = re.compile('MTX[0-9]*\s*')
empty_pattern = re.compile('[^\S\n\t]+')
empty2_pattern = re.compile('[^\S\r\n]{2,}')

# name of the download file
download_file_name = "download.dat"

def throwFileException(errorType):
    if errorType == 1:
        print("ERROR 01: File Not Found")
        print()
        main()
    elif errorType == 2:
        print("ERROR 02: File Already Exists")
        print()
        main()

def main():
    puts(colored.green("Enter operation to perform (0 to quit)"))
    with indent(4, quote=' >'):
        puts('1. Single record scan')
        puts('2. Verbose record scan')
        puts('3. Print single record type')
        puts('4. Print all records')
        puts('5. Export missing meters')
        puts('6. Export meter type')

    scan_type = int(input())
    if scan_type == 1:
        scanForRecord()
    elif scan_type == 2:
        scanAllRecords()
    elif scan_type == 3:
        printSingleRecord()
    elif scan_type == 4:
        print("This will print the entire download file")
        answer = input("Are you sure? (Y or N):")
        if answer == 'Y' or answer == 'y':
            printAllRecords()
        else:
            main()
    elif scan_type == 5:
        exportMissingMeters()
    elif scan_type == 6:
        exportMeterType()
    elif scan_type == 0:
        sys.exit(0)
    else:
        print("ERROR: Unknown Option Entered")
        print()
        main()

def scanForRecord():
    counter = 0
    record_type = input("Enter the record type: (ex. CUS or MTX) ").upper()
    try:
        with open(download_file_name, 'r') as openfile:
            start = time.time()
            for line in openfile:
                if line.startswith(record_type):
                    counter+=1
    except FileNotFoundError:
        throwFileException(1)
    total = time.time()-start
    print(f"{counter:,d}", "records found")
    print("time elapsed: %.2f" % (total), " seconds.")
    print()
    time.sleep(1)
    main()

def scanAllRecords():
    count_cus = 0
    count_csx = 0
    count_mtr = 0
    count_mtx = 0
    count_mts = 0
    count_rdg = 0
    count_rff = 0
    try:
        with open(download_file_name, 'r') as openfile:
                start = time.time()
                for line in openfile:
                    if line.startswith('CUS'):
                        count_cus+=1
                    elif line.startswith('CSX'):
                        count_csx+=1
                    elif line.startswith('MTR'):
                        count_mtr+=1
                    elif line.startswith('MTX'):
                        count_mtx+=1
                    elif line.startswith('MTS'):
                        count_mts+=1
                    elif line.startswith('RDG'):
                        count_rdg+=1
                    elif line.startswith('RFF'):
                        count_rff+=1
    except FileNotFoundError:
        throwFileException(1)

    total = time.time()-start 
    print("File scan successful.")
    print("-----------------------------------------")
    print(f"{count_cus:,d}", "\t (CUS) Customer records found.")
    print(f"{count_csx:,d}", "\t (CSX) Customer extra records found.")
    print(f"{count_mtr:,d}", "\t (MTR) Meter records found.")
    print(f"{count_mtx:,d}" "\t (MTX) Meter extra records found.")
    print(f"{count_mts:,d}" "\t (MTS) Meter special records found.")
    print(f"{count_rdg:,d}" "\t (RDG) Reading records found.")
    print(f"{count_rff:,d}" "\t (RFF) Radio records found.")
    print("-----------------------------------------")
    print("time elapsed: %.2f" % (total), " seconds.")
    print()
    time.sleep(1)
    main()
    
def printSingleRecord():
    record_type = input("Enter the record type: (ex. CUS or MTX) ")
    with open(download_file_name, 'r') as openfile:
        counter = 0
        start = time.time()
        for line in openfile:
            if record_type in line or record_type.lower() in line:
                counter+=1
                print("{0}) {1}".format(counter, line))
    total = time.time()-start
    print(counter, "records printed.")
    print("time elapsed: %.2f" % (total), " seconds.")
    print()
    time.sleep(1)
    main()

def printAllRecords():
    with open(download_file_name, 'r') as openfile:
        counter = 0
        for line in openfile:
            print("{0}) {1}".format(counter, line))
            counter+=1
    print()
    time.sleep(1)
    main()

def exportMissingMeters():
    try:
        with open(download_file_name, 'r') as openfile:
            try:
                with open('MissingMeters.txt', 'x') as builtfile:
                    start = time.time()
                    previous_line = ''
                    for line in openfile:
                        if line.startswith('MTR'):
                            meter_record = line[45:58]
                            if empty_pattern.match(meter_record):
                                builtfile.write(previous_line)
                        previous_line = line
            except FileExistsError:
                throwFileException(2)
    except FileNotFoundError:
        throwFileException(1)
    total = time.time()-start
    print("Missing meters successfully exported.")
    print("time elapsed: %.2f" % (total), " seconds.")
    print()
    print("Export missing meters to .csv file? (Y or N)")
    answer = input()
    if answer == 'Y' or answer == 'y':
        convertMissingMetersToCSV()
    else:
        main()

def convertMissingMetersToCSV():
    try: 
        with open('MissingMeters.txt', 'r') as openfile:
            try:
                with open('MissingMeters.csv', 'x') as builtfile:
                    start = time.time()
                    for line in openfile:
                        line = re.sub(empty2_pattern, ',', line.strip())
                        builtfile.write(line)
                        if line.startswith('CUS'):
                            builtfile.write('\n')
                    total = time.time()-start
                    print(".csv file successfully exported.")
                    print("time elapsed: %.2f" % (total), " seconds.")
                    print()
                    main()
            except FileExistsError:
                throwFileException(2)
    except FileNotFoundError:
        throwFileException(1)
    print()
    time.sleep(1)
    main()

def exportMeterType():
    try:
        with open(download_file_name, 'r') as openfile:
            try:
                user_meter_code = int(input("Enter the meter code to export: "))
                with open('MeterType.txt', 'x') as builtfile:
                    start = time.time()
                    for line in openfile:
                        if line.startswith('RDG'):
                            meter_code = line[76:78]
                            if meter_code == user_meter_code: #failing to write somewhere in here
                                builtfile.write(line)
                                print(line)
                    total = time.time()-start
                    print("Meter type successfully exported")
                    print("time elapsed: %.2f" % (total), " seconds.")
                    print()
                    main()
            except FileExistsError:
                throwFileException(2)
    except FileNotFoundError:
        throwFileException(1)
    print()
    time.sleep(1)
    main()
        


if __name__ == "__main__":
    f = Figlet(font='slant')
    print(f.renderText('Sesock .dat Tool'))
    main()

