# Standalone script to export missing meters to a .txt file
# with the option for exporting as a .csv as well
# Written by: Chris Sesock on 6-19-2020
import sys, re
from datetime import datetime
download_file_name = 'download.dat'
missing_meter_filename = 'MissingMeters ' + str(datetime.today().strftime('%Y-%m-%d_%H-%M')) + '.txt'
empty_pattern = re.compile('[^\S\n\t]+')

def exportMissingMeters():
    counter=0
    current_line=1
    total_line = getFileLineCount(download_file_name)
    try:
        with open(download_file_name, 'r') as openfile:
            try:
                with open(missing_meter_filename, 'x') as builtfile:
                    previous_line = ''
                    for line in openfile:
                        progressBarComplex(current_line, total_line)
                        if line.startswith('MTR'):
                            meter_record = line[45:57]
                            if empty_pattern.match(meter_record):
                                builtfile.write(previous_line)
                                counter+=1
                        previous_line=line
                        current_line+=1
                    if counter == 0: # these few lines fix the problem of making a blank file if there are no missing meters
                        builtfile.close()
                        removeFile(missing_meter_filename)
            except FileExistsError:
                throwIOException(2)
    except FileNotFoundError:
        throwIOException(1)
    print("The operation was successful.")
    print()
    print("Export missing meters to .csv file (Y or N)")
    answer = input(">>")
    if answer.upper() == 'Y':
        convertMissingMetersToCSV() # create a .csv file with the same data
    elif answer.upper() == 'N':
        sys.exit(0)
    else:
        throwIOException(3)

# post export function which converts list of missing meters to a .csv file
def convertMissingMetersToCSV():
    try: 
        with open(missing_meter_filename, 'r') as openfile:
            try:
                with open(missing_meter_csv_filename, 'x') as builtfile:
                    for line in openfile:
                        line = re.sub('[^\S\r\n]{2,}', ',', line.strip())
                        builtfile.write(line)
                        if line.startswith('CUS'):
                            builtfile.write('\n')
            except FileExistsError:
                throwIOException(2)
    except FileNotFoundError:
        throwIOException(1)
    sys.exit(0)

def getFileLineCount(filename):
    try:
        with open(filename, 'r') as openfile:
            counter = 0
            for line in openfile:
                counter+=1
        return counter
    except FileNotFoundError:
        throwIOException(1)

def progressBarComplex(current, total, barLength = 20):
    percent = float(current) * 100 / total
    arrow   = '-' * int(percent/100 * barLength - 1) + '>'
    spaces  = ' ' * (barLength - len(arrow))
    print('Progress: [%s%s] %d %%' % (arrow, spaces, percent), end='\r')

if __name__ == '__main__':
    exportMissingMeters()
