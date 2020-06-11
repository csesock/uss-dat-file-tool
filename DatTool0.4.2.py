# Current build: Version 0.4.2
# Current build written on 6-11-2020
#
# For information regarding this program, find the readme at github.com/csesock/SesockDatTool
# For feature requests or feedback, email christophers@united-systems.com
# Author: Chris Sesock on 6-5-2020

import time 
import csv, sys, re, os
from pyfiglet import Figlet
from clint.textui import colored, puts, indent
from os import system
from collections import deque
from datetime import datetime

# regular expression patterns
record_pattern = re.compile('[a-z][0-9]*\s*')
empty_pattern = re.compile('[^\S\n\t]+')
empty2_pattern = re.compile('[^\S\r\n]{2,}')

# file names with dynamic dates 
download_file_name = "download.dat"
missing_meter_filename = 'MissingMeters ' + str(datetime.today().strftime('%Y-%m-%d')) + '.txt'
missing_meter_csv_filename = 'MissingMeters ' + str(datetime.today().strftime('%Y-%m-%d')) + '.csv'
meter_type_filename = 'MeterType ' + str(datetime.today().strftime('%Y-%m-%d')) + '.txt'

# parameterized error handler for the file reader
def throwIOException(errorType):
    if errorType == 1:
        print("[ERROR 01]: File Not Found")
        print()
        main()
    elif errorType == 2:
        print("[ERROR 02]: File Already Exists")
        print()
        main()
    elif errorType == 3:
        print("[ERROR 03]: Unknown Input")
        print()
        main()
    else:
        print("[ERROR 00]: Unknown Error")
        print()
        sys.exit(0)

# main method -- responsible for IO menu/handling
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
    elif scan_type == 666:
        print(":^)")
        main()
    elif scan_type == 99:
        exportFullRecordMeterType()
    elif scan_type == 0:
        sys.exit(0)
    else:
        throwIOException(3)

# scan download file for number of instances of a single record
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
        throwIOException(1)
    total = time.time()-start
    print(f"{counter:,d}", "records found")
    print("time elapsed: %.2f" % (total), " seconds.")
    print()
    time.sleep(1)
    main()

# scan download file for number of each record
def scanAllRecords():
    count_cus = count_csx = count_mtr = count_mtx = count_mts = count_rdg = count_rff = 0
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
        throwIOException(1)

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

# print all of a single record type
def printSingleRecord():
    record_type = input("Enter the record type (ex. CUS or MTX): ")
    try:
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
    except FileNotFoundError:
        throwIOException(1)
    print()
    time.sleep(1)
    main()

# print all records -- functionally a print() for download.dat
def printAllRecords():
    try:
        with open(download_file_name, 'r') as openfile:
            counter = 0
            for line in openfile:
                print("{0}) {1}".format(counter, line))
                counter+=1
    except FileNotFoundError:
        throwIOException(1)
    print()
    time.sleep(1)
    main()

# exports a text file with all missing meter records in download file
def exportMissingMeters():
    try:
        with open(download_file_name, 'r') as openfile:
            try:
                with open(missing_meter_filename, 'x') as builtfile:
                    counter = 0
                    start = time.time()
                    previous_line = ''
                    for line in openfile:
                        if line.startswith('MTR'):
                            meter_record = line[45:58] # range 46-57
                            if empty_pattern.match(meter_record):
                                builtfile.write(previous_line)
                                counter+=1
                        previous_line = line
                    if counter == 0:
                        print("No missing meters found")
                        print()
                        main()
            except FileExistsError:
                throwIOException(2)
    except FileNotFoundError:
        throwIOException(1)
    total = time.time()-start
    print("Missing meters successfully exported.")
    print("time elapsed: %.2f" % (total), " seconds.")
    print()
    print("Export missing meters to .csv file? (Y or N)")
    answer = input()
    if answer == 'Y' or answer == 'y':
        convertMissingMetersToCSV()
    elif answer == 'N' or answer == 'n':
        main()
    else:
        throwIOException(3)

# post export function which converts list of missing meters to a .csv file
def convertMissingMetersToCSV():
    try: 
        with open(missing_meter_filename, 'r') as openfile:
            try:
                with open(missing_meter_csv_filename, 'x') as builtfile:
                    start = time.time()
                    for line in openfile:
                        line = re.sub('[^\S\r\n]{2,}', ',', line.strip())
                        builtfile.write(line)
                        if line.startswith('CUS'):
                            builtfile.write('\n')
                    total = time.time()-start
                    print(".csv file successfully exported.")
                    print("time elapsed: %.2f" % (total), " seconds.")
                    print()
            except FileExistsError:
                throwIOException(2)
    except FileNotFoundError:
        throwIOException(1)
    print()
    time.sleep(1)
    main()

# exports a text file of a specified meter translation code
def exportMeterType():
    try:
        with open(download_file_name, 'r') as openfile:
            try:
                user_meter_code = int(input("Enter the meter code to export (ex. 00 or 01): "))
                with open(meter_type_filename, 'x') as builtfile:
                    start = time.time()
                    previous_line = ''
                    for line in openfile:
                        if line.startswith('RDG'):
                            meter_code = line[76:78] #range 77-78
                            if int(meter_code) == user_meter_code:
                                builtfile.write(previous_line)
                                builtfile.write(line)
                        previous_line = line
                    total = time.time()-start
                    print("Meter type successfully exported")
                    print("time elapsed: %.2f" % (total), " seconds.")
            except FileExistsError:
                throwIOException(2)
    except FileNotFoundError:
        throwIOException(1)
    print()
    time.sleep(1)
    main()

# deque implementation to print entire customer record of translation code
# @TODO: return only post-customer records in deque
def exportFullRecordMeterType():
    lines = deque(maxlen=5)
    with open('download.dat', 'r') as openfile:
        for line in openfile:
            lines.append(line)
            if line.startswith('RDG'):
                searchDequeForCustomerRecord(lines)

# helper function for deque implementation of export meter translation
# @TODO: 
def searchDequeForCustomerRecord(deq):
    for rec in deq:
        if rec.startswith('CUS'):
            print(rec)
    main()

# sets import function calls
if __name__ == "__main__":
    f = Figlet(font='slant', width=120)
    print(f.renderText('Sesock\'s .dat Tool'))
    system('title'+'.dat Tool v0.4.2')
    main()