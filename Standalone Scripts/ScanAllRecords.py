# Standalone script to print all important records from a download file
#
import sys, os
# scan download file for number of each record
def scanAllRecords():
    count_rhd = count_cus = count_csx = count_mtr = count_mtx = count_mts = count_rdg = count_rff = 0
    current_line = 1
    total_lines = getFileLineCount('download.dat')
    try:
        with open('download.dat', 'r') as openfile:
                for line in openfile:
                    progressBarComplex(current_line, total_lines)
                    if line.startswith('RHD'):
                        count_rhd+=1
                    elif line.startswith('CUS'):
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
                    current_line+=1
    except FileNotFoundError:
        print("ERROR: File Not Found")
        
    print()
    print("File scan successful.")
    print("-----------------------------------------")
    print(f"{count_rhd:,d}", "\t (RHD) Route header records found.")
    print(f"{count_cus:,d}", "\t (CUS) Customer records found.")
    print(f"{count_csx:,d}", "\t (CSX) Customer extra records found.")
    print(f"{count_mtr:,d}", "\t (MTR) Meter records found.")
    print(f"{count_mtx:,d}" "\t (MTX) Meter extra records found.")
    print(f"{count_mts:,d}" "\t (MTS) Meter special records found.")
    print(f"{count_rdg:,d}" "\t (RDG) Reading records found.")
    print(f"{count_rff:,d}" "\t (RFF) Radio records found.")
    print("-----------------------------------------")
    os.system('pause')


def getFileLineCount(filename):
    try:
        with open(filename, 'r') as openfile:
            counter = 0
            for line in openfile:
                counter+=1
        return counter
    except FileNotFoundError:
        print("ERROR: File Not Found")

def progressBarComplex(current, total, barLength = 20):
    percent = float(current) * 100 / total
    arrow   = '-' * int(percent/100 * barLength - 1) + '>'
    spaces  = ' ' * (barLength - len(arrow))
    print('Progress: [%s%s] %d %%' % (arrow, spaces, percent), end='\r')


if __name__ == '__main__':
    scanAllRecords()