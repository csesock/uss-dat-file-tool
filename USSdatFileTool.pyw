import tkinter as tk
from tkinter import *
from tkinter import messagebox, simpledialog, ttk
from tkinter.filedialog import asksaveasfile
from tkinter.font import Font

from collections import deque
from datetime import datetime
import sys, os, re, time, csv
try:
    import Logging
except:
    print("Logging system files not found -- to enable logging please place Logging.py in the default directory")
    pass

#regex
pattern_missing_meters = re.compile(r'[^\S\n\t]{11}')
pattern_lat_long = re.compile(r'-?[0-9]{2}\.\d{1,13}$')
pattern_space_nonewline = re.compile(r'\t|[ ]{2,}') #test


#file configurations
download_filename = 'download.dat'
defaut_file_extension = '.txt'
window = tk.Tk()
s = ttk.Style()
s.theme_use('clam')

#default UI sizes
DEFAULT_FONT_SIZE = 10
CONSOLE_WIDTH = 76
CONSOLE_HEIGHT = 15
BUTTON_WIDTH = 22

#default tkk configuration
consoleFont = Font(family="Consolas", size=DEFAULT_FONT_SIZE)
labelFont = Font(size=10, weight='bold')
window.title("United System .dat File Tool")
window.resizable(False, False)
height = window.winfo_screenheight()/3
width = window.winfo_screenwidth()/3
window.geometry('780x350+%d+%d' %(width, height))

#build window icons
try:
    dirp = os.path.dirname(__file__)
    photo = PhotoImage(file="assets\\IconSmall.png")
    window.iconphoto(False, photo)
except:
    pass

#hotkey bindings
window.bind('2', lambda event: scanAllRecordsVerbose())
window.bind('3', lambda event: searchRecords())
window.bind('4', lambda event: officeRegionZone())
window.bind('5', lambda event: missingMeters())
window.bind('6', lambda event: printReadType())
window.bind('7', lambda event: checkMalformedLatLong())

#menu bindings
window.bind('<Control-o>', lambda event: openFile())
window.bind('<Control-s>', lambda event: save())
window.bind('<Control-Alt-s>', lambda event: saveAs())
window.bind('<Control-c>', lambda event: bocConsole.delete(1.0, "end"))
window.bind('<F1>', lambda event: aboutDialog())
window.bind('<F10>', lambda event: resetWindow())
window.bind('<F11>', lambda event: resizeWindow())

###################
##File Functions###
###################

def disallowedCharacters(event=None):
    Logging.writeToLogs('Start Function Call - disallowedCharacters()')
    counter = 0
    line_number = 1
    index = 1.0
    try:
        with open(download_filename, 'r') as openfile:
            bocConsole.delete(1.0, 'end')
            for line in openfile:
                if line.startswith('MTR'):
                    meter_number = line[45:57] #46-57
                    if '*' in meter_number or '/' in meter_number or '\\' in meter_number or ':' in meter_number or '<' in meter_number or '>' in meter_number:
                        bocConsole.insert(index, str(line_number) + " " + line + "\n")
                        counter+=1
                        index+=1
                line_number+=1
            if counter == 0:
                bocConsole.delete(1.0, 'end')
                bocConsole.insert(1.0, 'No disallowed characters found in download file.')
                bocConsole.insert('end', '\n')
                bocConsole.insert('end', "Disallowed characters include: * < > \\ / \"")
        Logging.writeToLogs('End Function Call - disallowedCharacters()')
    except FileNotFoundError:
        fileNotFoundError()

def searchRecords(event=None):
    Logging.writeToLogs('Start Function Call - searchRecords()')
    records = []
    record_type = simpledialog.askstring("Record Search", '    Enter the record types to search \n\n (Separate record types by comma) \n               (ex. cus, mtr, rff)  ', parent=window)
    if record_type is None:
        return
    record_type = record_type.upper()
    if ',' in record_type:
        #multiple records to search
        records = record_type.split(',')
        records = [x.strip(' ') for x in records]
    counter = 1.0
    try:
        with open(download_filename, 'r') as openfile:
            bocConsole.delete(1.0, "end")
            if not records:
                for line in openfile:
                    if line.startswith(record_type):
                        bocConsole.insert(counter, line + "\n")
                        counter+=1
            else:
                for line in openfile:
                    for record in records:
                        if line.startswith(record):
                            bocConsole.insert(counter, line+ "\n")
                            counter+=1
        Logging.writeToLogs('End Function Call - searchRecords()')
    except FileNotFoundError:
        fileNotFoundError()
        
def officeRegionZone(event=None):
    Logging.writeToLogs('Start Function Call - officeRegionZone()')
    try:
        with open(download_filename, 'r') as openfile:
            for line in openfile:
                if line.startswith('RHD'):
                    office = line[71:73]
                    if office == "  ":
                        office = "BLANK"
                    region = line[73:75]
                    if region == "  ":
                        region = "BLANK"
                    zone = line[75:77]
                    if zone == "  ":
                        zone = "BLANK"
                if line.startswith('ERH'):
                    office = line[81:83]
                    if office == "  ":
                        office = "BLANK"
                    region = line[83:85]
                    if region == "  ":
                        region = "BLANK"
                    zone = line[85:87]
                    if zone == "  ":
                        zone = "BLANK" 
                    bocConsole.delete(1.0, "end")
                    bocConsole.insert(1.0, "Office-Region-Zone Fields")
                    bocConsole.insert(2.0, "\n")
                    bocConsole.insert(2.0, "------------------------")
                    bocConsole.insert(3.0, "\n")
                    bocConsole.insert(3.0, "Office . . . . : \t" + str(office))
                    bocConsole.insert(4.0, "\n")
                    bocConsole.insert(4.0, "Region . . . . : \t" + str(region))
                    bocConsole.insert(5.0, "\n")
                    bocConsole.insert(5.0, "Zone . . . . . : \t" + str(zone))
                    bocConsole.insert(6.0, "\n")
                    bocConsole.insert(6.0, "------------------------")
                    return
        Logging.writeToLogs('End Function Call - officeRegionZone()')
    except FileNotFoundError:
        fileNotFoundError()
        
def scanAllRecordsVerbose(event=None):
    Logging.writeToLogs('Start Function Call - scanAllRecordsVerbose()')
    all_records = {}
    counter = 1.0
    try:
        with open(download_filename, 'r') as openfile:
            for line in openfile:
                x = line[0:3]
                if x not in all_records:
                    all_records[x] = 1
                else:
                    all_records[x]+=1
            bocConsole.delete(counter, "end")
            bocConsole.insert(counter, "Records")
            counter+=1
            bocConsole.insert(counter, "\n")
            bocConsole.insert(counter, "----------------------")
            counter+=1
            bocConsole.insert(counter, "\n")
            for record in all_records:
                bocConsole.insert(counter, str(record) + " . . . :\t" + f"{all_records[record]:,d} ")
                counter+=1
                bocConsole.insert(counter, "\n")
            bocConsole.insert(counter, "----------------------")
        Logging.writeToLogs('End Function Call - scanAllRecordsVerbose()')
    except FileNotFoundError:
        fileNotFoundError()

def missingMeters(event=None):
    Logging.writeToLogs('Start Function Call - missingMeters()')
    counter = 0
    line_number = 1
    try:
        with open(download_filename, 'r') as openfile:
            previous_line = ''
            bocConsole.delete(1.0, "end")
            for line in openfile:
                        if line.startswith('MTR'):
                            meter_record = line[45:57] #46-57
                            if pattern_missing_meters.match(meter_record):
                                bocConsole.insert("end", str(line_number) + " " + previous_line)
                                bocConsole.insert("end", "\n")
                                counter+=1
                        previous_line=line
                        line_number +=1
            if counter == 0:
                bocConsole.delete(1.0, "end")
                bocConsole.insert(1.0, "No missing meters found in ["+os.path.basename(download_filename)+"]")
                return
        Logging.writeToLogs('End Function Call - missingMeters()')
    except FileNotFoundError:
        fileNotFoundError()

def printReadType(event=None):
    Logging.writeToLogs('Start Function Call - printReadType()')
    user_meter_code = simpledialog.askstring("Enter Record", "Enter the record type to search:", parent=window)
    if user_meter_code is None:
        return
    user_meter_code = user_meter_code.upper()
    counter = 0
    current_record = deque(maxlen=getCustomerRecordLength()+1)
    try:
        with open(download_filename, 'r') as openfile:
            bocConsole.delete(1.0, "end")
            for line in openfile:
                if line.startswith('RDG'):
                    meter_code = line[76:78]
                    if meter_code == user_meter_code:
                        for record in current_record:
                            if record.startswith('CUS'):
                                bocConsole.insert("end", "{0} {1}".format(counter, record))
                                counter+=1
                current_record.append(line)
            if counter == 0:
                bocConsole.insert("end", "No meters of that type found.")
            elif counter != 0:
                bocConsole.insert("end", counter)
        Logging.writeToLogs('End Function Call - printReadType()')
    except FileNotFoundError:
        fileNotFoundError()

def printReadTypeVerbose(event=None):
    Logging.writeToLogs("Start Function Call - printReadTypeVerbose()")
    all_reads = {}
    counter = 1.0
    try:
        with open(download_filename, 'r') as openfile:
            for line in openfile:
                if line.startswith('RDG'):
                    x = line[76:78]
                    if x not in all_reads:
                        all_reads[x] = 1
                    else:
                        all_reads[x]+=1
            bocConsole.delete(counter, "end")
            bocConsole.insert(counter, "Read Type Codes")
            counter+=1
            bocConsole.insert(counter, "\n")
            bocConsole.insert(counter, "----------------------")
            counter+=1
            bocConsole.insert(counter, "\n")
            for record in all_reads:
                bocConsole.insert(counter, str(record) + " . . . :\t" + f"{all_reads[record]:,d} ")
                counter+=1
                bocConsole.insert(counter, "\n")
            bocConsole.insert(counter, "----------------------")
        Logging.writeToLogs("End Function Call - printReadTypeVerbose()")
    except FileNotFoundError:
        fileNotFoundError()

def checkMalformedLatLong(event=None):
    Logging.writeToLogs("Start Function Call - checkMalformedLatLong()")
    line_number = 1
    try:
        with open(download_filename, 'r') as openfile:
            for line in openfile:
                if line.startswith('MTX'):
                    lat_data = line[23:40].rstrip()
                    long_data = line[40:57].rstrip()
                    if not pattern_lat_long.match(lat_data) and not pattern_lat_long.match(long_data):
                        latLongConsole.delete(1.0, "end")
                        latLongConsole.insert(1.0, "Malformed lat/long data at line: " + str(line_number))
                        latLongConsole.insert(2.0, "\n")
                        latLongConsole.insert(2.0, "Line: " + line)
                        return
                line_number+=1
            latLongConsole.delete(1.0, "end")
            latLongConsole.insert(1.0, "No malformation within lat/long data detected.")
        Logging.writeToLogs("End Function Call - checkMalformedLatLong()")
    except FileNotFoundError:
        fileNotFoundError2()

def checkLatLongSigns(event=None):
    Logging.writeToLogs("Start Function Call - checkLatLongSigns()")
    try:
        with open(download_filename, 'r') as openfile:
            for line in openfile:
                if line.startswith('MTX'):
                    lat_data = float(line[23:40].rstrip())
                    long_data = float(line[40:57].rstrip())
                    if lat_data < 27 or lat_data > 50 or long_data < -100 or long_data > -70:
                        latLongConsole.delete(1.0, "end")
                        latLongConsole.insert(1.0, "The lat/long signs are incorrect.")
                        return
                    else:
                        latLongConsole.delete(1.0, "end")
                        latLongConsole.insert(1.0, "The lat/long signs are correct:")
                        latLongConsole.insert(2.0, "\n")
                        latLongConsole.insert(2.0, "Latitude Sign: Positive")
                        latLongConsole.insert(3.0, "\n")
                        latLongConsole.insert(3.0, "Longitude Sign: Negative")
                        return
            latLongConsole.delete(1.0, "end")
            latLongConsole.insert(1.0, "No lat/long data detected.")
        Logging.writeToLogs("End Function Call - checkLatLongSigns()")
    except FileNotFoundError:
        fileNotFoundError2()

def checkLatLongExists(event=None):
    latLongConsole.delete(1.0, "end")
    try:
        with open(download_filename, 'r') as openfile:
            for line in openfile:
                if line.startswith('MTX'):
                    latLongConsole.delete(1.0, "end")
                    latLongConsole.insert(1.0, "Sample Lat/Long Data:")
                    latLongConsole.insert(2.0, "\n")
                    latLongConsole.insert(2.0, "Lattitude: " + str(line[23:40]))
                    latLongConsole.insert(3.0, "\n")
                    latLongConsole.insert(3.0, "Longitude: " + str(line[40:57]))
                    return
            latLongConsole.insert(1.0, "No lat/long data detected.")
    except FileNotFoundError:
        fileNotFoundError2()

def printAllLatLongData(event=None):
    counter = 1.0
    total_latlong = 0
    line_number = 1
    try:
        with open(download_filename, 'r') as openfile:
            latLongConsole.delete(1.0, "end")
            for line in openfile:
                if line.startswith('MTX'):
                    lat_data = line[23:40].rstrip()
                    long_data = line[40:57].rstrip()
                    if pattern_lat_long.match(lat_data) and pattern_lat_long.match(long_data):
                        latLongConsole.insert(counter, str(line_number)+" "+line)
                        latLongConsole.insert(counter+1, "\n")
                        total_latlong+=1
                counter+=1
                line_number+=1
            if total_latlong == 0:
                latLongConsole.insert(1.0, "There was no lat/long data found.")
    except FileNotFoundError:
        fileNotFoundError2()

def getReadDirections(event=None):
    cc = {}
    counter = 3.0
    try:
        with open(download_filename, 'r') as openfile:
            for line in openfile:
                if line.startswith('RDG'):
                    commodity = line[11:15].strip()
                    direction = line[16]
                    c = commodity + " " + direction
                    if c not in cc:
                        cc[c]=1
                    else:
                        cc[c]+=1
            bocConsole.delete(1.0, "end")
            bocConsole.insert(1.0, "Read Directions\n")
            bocConsole.insert(2.0, "-------------------\n")
            for fart in cc:
                bocConsole.insert(counter, str(fart)+"\t. . . :\t"+str(cc[fart])+"\n")
                counter+=1.0
            bocConsole.insert(counter, "-------------------")
    except FileNotFoundError:
        fileNotFoundError()

def createELFfile(event=None):
    answer = messagebox.askokcancel("Confirmation", "All possible fields will be formatted into an ELF file.\nRFF records must exist and must match a customer record.")
    if answer == None or answer == False:
        return 
    try:
        with open(download_filename, 'r') as openfile:
            with open('generatedELF.csv', 'w') as builtfile:
                builtfile.write('Street Address, Endpoint ID, City, State, Zip, Latitude, Longitude, GeopointSource, Market\n')
                for line in openfile:
                    if line.startswith('CUS'):
                        address = line[54:94]
                        #print("address: " + address)
                        builtfile.write(address+',')
                    if line.startswith('RFF'):
                        ert = line[11:21]
                        #print("ert: " + ert)
                        builtfile.write(ert+'\n')

    except FileNotFoundError():
        fileNotFoundError3()

def compareReads():
    try:
        with open(download_filename, 'r') as openfile:
            for line in openfile:
                if line.startswith('RDG'):
                    formatted_read = line[33:43]
                    print("formatted: \t" + formatted_read)
                if line.startswith('RFF'):
                    raw_read = line[72:82]
                    print("raw read: \t"+ raw_read)
    except FileNotFoundError:
        fileNotFoundError3()

def getCustomerRecordLength():
    try:
        with open(download_filename, 'r') as openfile:
            counter = start_line = end_line = 0
            for line in openfile:
                counter+=1
                if line.startswith('CUS'):
                    start_line = counter
                if line.startswith('RFF'):
                    end_line = counter
                    length = (end_line-start_line)+1
                    return length
    except FileNotFoundError:
        fileNotFoundError()       

def clearBOCConsole():
    bocConsole.delete(1.0, "end")

def clearLatLongConsole():
    latLongConsole.delete(1.0, "end")

def clearELFConsole():
    ELFConsole.delete(1.0, "end")

def save():
    Logging.writeToLogs('Start Function Call - save()')
    export_filename = "DatFileToolExport " + str(datetime.today().strftime('%Y-%m-%d_%H-%M')) + ".txt"
    with open("exports\\"+export_filename, 'w') as openfile:
        if TAB_CONTROL.index(TAB_CONTROL.select()) == 0:
            text2save = str(bocConsole.get(1.0, "end"))
        else:
            text2save = str(latLongConsole.get(1.0, "end"))
        openfile.write(text2save)
    messagebox.showinfo("Export", "Data successfully exported to the 'exports' folder!")
 
def saveAs():
    Logging.writeToLogs('Start Function Call - saveAs()')
    files = [('Text Files', '*.txt'),
             ('All Files', '*.*'),
             ('CSV Files', '*.csv')]
    f = asksaveasfile(mode='w', defaultextension='.txt', filetypes=files)
    if f is None:
        return
    if TAB_CONTROL.index(TAB_CONTROL.select()) == 0:
        text2save = str(bocConsole.get(1.0, "end"))
    else:
        text2save = str(latLongConsole.get(1.0, "end"))
    if f.name.endswith('.csv'):
        parsed = parseCSV(text2save)
        f.write(parsed)
        f.close()
        return
    f.write(text2save)
    f.close()

def parseCSV(text):
    return re.sub(pattern_space_nonewline, ',', text.strip())

def populateMissingMeters(event=None):
    answer = messagebox.askokcancel("Confirmation", "A new download file will be created\n with populated meter records.")
    if answer == None or answer == False:
        return 
    try:
        with open(download_filename, 'r') as openfile:
            with open('download -- populated meters.dat', 'w') as builtfile:
                for line in openfile:
                    if line.startswith('MTR'):
                        meter_record = line[45:57]
                        if pattern_missing_meters.match(meter_record):
                            line = str(line[0:49]) + "11111" + str(line[54::]) #concatenate a new line with populated record
                    builtfile.write(line)
    except FileExistsError:
        messagebox.showinfo("Error", "A populated download file already exists in the directory")
    except FileNotFoundError:
        fileNotFoundError3()

def openFile():
    Logging.writeToLogs('Start Function Call - openFile()')
    filename = tk.filedialog.askopenfilename(title="Open File")
    if tab2enforcebutton.instate(['selected']):
        if not filename.lower().endswith(('.dat', '.DAT', '.hdl', '.HDL')):
            messagebox.showinfo("ERROR", "Filetype imports are enforced. Please select a compatible file.")
            return
    global download_filename
    download_filename = filename
    text.set(os.path.basename(download_filename))
    Logging.writeToLogs('Opened new file: ' + str(filename))
       
def resizeWindow():
    width = window.winfo_screenwidth()
    height = window.winfo_screenheight()
    window.geometry('%dx%d+0+0' %(width, height))

def resetWindow():
    height = window.winfo_screenheight()/3
    width = window.winfo_screenwidth()/3
    window.geometry('780x330+%d+%d' %(width, height)) #reset height must be height-20 to account for the menu being created at this point
    bocConsole.delete(1.0, "end")
    bocConsole.insert(1.0, "United Systems dat File Tool [Version 1.6.0]")
    bocConsole.insert(2.0, "\n")
    bocConsole.insert(2.0, "(c) 2020 United Systems and Software, Inc.")
    bocConsole.insert(3.0, "\n")
    latLongConsole.delete(1.0, "end")
    latLongConsole.insert(1.0, "United Systems dat File Tool [Version 1.6.0]")
    latLongConsole.insert(2.0, "\n")
    latLongConsole.insert(2.0, "(c) 2020 United Systems and Software, Inc.")
    latLongConsole.insert(3.0, "\n")

def changeTheme(theme):
    s = ttk.Style()
    s.theme_use(theme)

def fileNotFoundError():
    bocConsole.delete(1.0, "end")
    bocConsole.insert(1.0, "ERROR: FILE NOT FOUND")

def fileNotFoundError2():
    latLongConsole.delete(1.0, "end")
    latLongConsole.insert(1.0, "ERROR: FILE NOT FOUND")

def fileNotFoundError3():
    ELFConsole.delete(1.0, "end")
    ELFConsole.insert(1.0, "ERROR: FILE NOT FOUND")

def aboutDialog():
    dialog = """ Author: Chris Sesock \n Version: 1.6.0 \n Commit: 077788d6166f5d69c9b660454aa264dd62956fb6 \n Date: 2020-08-13:12:00:00 \n Python: 3.8.3 \n OS: Windows_NT x64 10.0.10363
             """
    messagebox.showinfo("About", dialog)

# Create Tab Control
TAB_CONTROL = ttk.Notebook(window)
# Basic Operations tab
tabBasicOperations = ttk.Frame(TAB_CONTROL)
TAB_CONTROL.add(tabBasicOperations, text='Validation Tools')
# Lat/Long tab
tabLatLong = ttk.Frame(TAB_CONTROL)
TAB_CONTROL.add(tabLatLong, text="Lat/Long Tools")
TAB_CONTROL.pack(expand=1, fill="both")
# File Operations tab
tabELFcreation = ttk.Frame(TAB_CONTROL)
TAB_CONTROL.add(tabELFcreation, text="Export Tools")
TAB_CONTROL.pack(expand=1, fill="both")
# ELF File Creation Tool tab
# tab4 = ttk.Frame(TAB_CONTROL)
# TAB_CONTROL.add(tab4, text="ELF Creation Tool")
# TAB_CONTROL.pack(expand=1, fill="both")
# Settings tab
tabDeveloper = ttk.Frame(TAB_CONTROL)
TAB_CONTROL.add(tabDeveloper, text="Settings")
TAB_CONTROL.pack(expand=1, fill="both")

###################
##BOC Tab Widgets##
###################

# btnNumkey1 = ttk.Button(tabBasicOperations, text="1.", width=1.5, command=lambda:searchRecords()).place(x=20, y=35)
# btnVerboseRecordScan = ttk.Button(tabBasicOperations, text="Record Search...", command=lambda:searchRecords(), width=BUTTON_WIDTH).place(x=50, y=35)

# btnNumkey2 = ttk.Button(tabBasicOperations, text="2.", width=1.5, command=lambda:scanAllRecordsVerbose()).place(x=20, y=76)
# btnsearchRecords = ttk.Button(tabBasicOperations, text="Record Counts", command=lambda:scanAllRecordsVerbose(), width=BUTTON_WIDTH).place(x=50, y=76)

# btnNumkey3 = ttk.Button(tabBasicOperations, text="3.", width=1.5, command=lambda:disallowedCharacters()).place(x=20, y=117)
# btnSingleRecordScan = ttk.Button(tabBasicOperations, text="Bad Meter Characters", command=lambda:disallowedCharacters(), width=BUTTON_WIDTH).place(x=50, y=117)

# btnNumkey4 = ttk.Button(tabBasicOperations, text="4.", width=1.5, command=lambda:missingMeters()).place(x=20, y=158)
# btnOfficeRegionZone = ttk.Button(tabBasicOperations, text="Blank Meter Numbers", command=lambda:missingMeters(), width=BUTTON_WIDTH).place(x=50, y=158)

# btnNumkey5 = ttk.Button(tabBasicOperations, text="5.", width=1.5, command=lambda:officeRegionZone()).place(x=20, y=199)
# MissingMeterButton = ttk.Button(tabBasicOperations, text="Office-Region-Zone", command=lambda:officeRegionZone(), width=BUTTON_WIDTH).place(x=50, y=199)

# btnNumkey6 = ttk.Button(tabBasicOperations, text="6.", width=1.5, command=lambda:printReadTypeVerbose()).place(x=20, y=240)
# PrintReadTypeButton = ttk.Button(tabBasicOperations, text="Read Type Codes", command=lambda:printReadTypeVerbose(), width=BUTTON_WIDTH).place(x=50, y=240)

btnNumkey1 = ttk.Button(tabBasicOperations, text="1.", width=1.5, command=lambda:searchRecords()).place(x=20, y=20)
btnVerboseRecordScan = ttk.Button(tabBasicOperations, text="Record Search...", command=lambda:searchRecords(), width=BUTTON_WIDTH).place(x=50, y=20)

btnNumkey2 = ttk.Button(tabBasicOperations, text="2.", width=1.5, command=lambda:scanAllRecordsVerbose()).place(x=20, y=58)
btnsearchRecords = ttk.Button(tabBasicOperations, text="Record Counts", command=lambda:scanAllRecordsVerbose(), width=BUTTON_WIDTH).place(x=50, y=58)

btnNumkey3 = ttk.Button(tabBasicOperations, text="3.", width=1.5, command=lambda:disallowedCharacters()).place(x=20, y=96)
btnSingleRecordScan = ttk.Button(tabBasicOperations, text="Bad Meter Characters", command=lambda:disallowedCharacters(), width=BUTTON_WIDTH).place(x=50, y=96)

btnNumkey4 = ttk.Button(tabBasicOperations, text="4.", width=1.5, command=lambda:missingMeters()).place(x=20, y=134)
btnOfficeRegionZone = ttk.Button(tabBasicOperations, text="Blank Meter Numbers", command=lambda:missingMeters(), width=BUTTON_WIDTH).place(x=50, y=134)

btnNumkey5 = ttk.Button(tabBasicOperations, text="5.", width=1.5, command=lambda:officeRegionZone()).place(x=20, y=172)
MissingMeterButton = ttk.Button(tabBasicOperations, text="Office-Region-Zone", command=lambda:officeRegionZone(), width=BUTTON_WIDTH).place(x=50, y=172)

btnNumkey6 = ttk.Button(tabBasicOperations, text="6.", width=1.5, command=lambda:printReadTypeVerbose()).place(x=20, y=210)
PrintReadTypeButton = ttk.Button(tabBasicOperations, text="Read Type Codes", command=lambda:printReadTypeVerbose(), width=BUTTON_WIDTH).place(x=50, y=210)

btnReadDirectionNumkey4 = ttk.Button(tabBasicOperations, text="7.", width=1.5, command=lambda:getReadDirections()).place(x=20, y=248)
btnReadDirection = ttk.Button(tabBasicOperations, text="Read Direction", width=BUTTON_WIDTH, command=lambda:getReadDirections()).place(x=50, y=248)

currentlabel = ttk.Label(tabBasicOperations, text="Current file: ")
currentlabel.place(x=220, y=20)

text = tk.StringVar()
if os.path.isfile('download.dat'):
    text.set('download.dat')
else:
    text.set('None')
label = ttk.Label(tabBasicOperations, textvariable=text, foreground='dark slate gray').place(x=287, y=20)

btnConsoleSave = ttk.Button(tabBasicOperations, text="save", width=4.25, command=lambda:save()).place(x=673, y=6)
btnConsoleClear = ttk.Button(tabBasicOperations, text="clear", width=4.25, command=lambda:clearBOCConsole()).place(x=717, y=6)

bocConsole = tk.Text(tabBasicOperations, height=CONSOLE_HEIGHT, width=CONSOLE_WIDTH, background='black', foreground='lawn green', 
                    insertborderwidth=7, undo=True, bd=3)
bocConsole.place(x=220, y=42)
bocConsole.configure(font=consoleFont)
bocConsole.insert(1.0, "United Systems dat File Tool [Version 1.6.0]")
bocConsole.insert(2.0, "\n")
bocConsole.insert(2.0, "(c) 2020 United Systems and Software, Inc.")
bocConsole.insert(3.0, "\n")

#################
##Lat/Long Tab###
#################

labelCurrentFileLatLong = ttk.Label(tabLatLong, text="Current file: ").place(x=220, y=20)
labelFile = ttk.Label(tabLatLong, textvariable=text, foreground='dark slate gray').place(x=287, y=20)

btnNumkeyLat3 = ttk.Button(tabLatLong, text="1.", width=1.5, command=lambda:checkMalformedLatLong()).place(x=20, y=35)
btnLatMalformed = ttk.Button(tabLatLong, text="Malformed Lat/Long", width=BUTTON_WIDTH, command=lambda:checkMalformedLatLong()).place(x=50, y=35)

btnNumkeyLat4 = ttk.Button(tabLatLong, text="2.", width=1.5, command=lambda:printAllLatLongData()).place(x=20, y=76)
btnLatAllMalformed = ttk.Button(tabLatLong, text="All Lat/Long", width=BUTTON_WIDTH, command=lambda:printAllLatLongData()).place(x=50, y=76)

labelRegion = ttk.Label(tabLatLong, text="Region:").place(x=22, y=120)
dropdownRegion = ttk.Combobox(tabLatLong, width=26, values = ["Central US", "Eastern US", "Western US"])
dropdownRegion.place(x=22, y=140)
dropdownRegion.state(['readonly'])
dropdownRegion.set("Central US (default)")

latLongConsole = tk.Text(tabLatLong, height=CONSOLE_HEIGHT, width=CONSOLE_WIDTH, background='black', foreground='lawn green',
                        insertborderwidth=7, undo=True, bd=3)
latLongConsole.place(x=220, y=42)
latLongConsole.configure(font=consoleFont)
latLongConsole.insert(1.0, "United Systems dat File Tool [Version 1.6.0]")
latLongConsole.insert(2.0, "\n")
latLongConsole.insert(2.0, "(c) 2020 United Systems and Software, Inc.")
latLongConsole.insert(3.0, "\n")

btnConsoleSave = ttk.Button(tabLatLong, text="save", width=4.25, command=lambda:save()).place(x=673, y=6)
btnLatConsoleClear = ttk.Button(tabLatLong, text="clear", width=4.25, command=lambda:clearLatLongConsole()).place(x=717, y=6)

########################
###ELF Tab Widgets######
########################

#tab widgets
btnPopulateMissingMetersNumKey1 = ttk.Button(tabELFcreation, text="1.", width=1.5, command=lambda:populateMissingMeters()).place(x=20, y=35)
btnPopulateMissingMeters = ttk.Button(tabELFcreation, text="Populate Missing Meters", width=BUTTON_WIDTH, command=lambda:populateMissingMeters()).place(x=50, y=35)

btnCheckForELFCompatibilityNumKey2 = ttk.Button(tabELFcreation, text="2.", width=1.5).place(x=20, y=76)
btnCheckForELFCompatibility = ttk.Button(tabELFcreation, text="Validate All Records", width=BUTTON_WIDTH).place(x=50, y=76)

#btnCompareRawFormatted = ttk.Button(tabELFcreation, text="Compare Reads", width=BUTTON_WIDTH, command=lambda:compareReads()).place(x=50, y=158)
btnCreateELFfile = ttk.Button(tabELFcreation, text="Create ELF File", width=27, command=lambda:createELFfile()).place(x=20, y=134)

labelAutoPopulate = ttk.Label(tabELFcreation, text="Fields to auto-populate").place(x=20, y=170)
checkboxState = ttk.Checkbutton(tabELFcreation, text="State").place(x=20, y=190)
inputState = ttk.Entry(tabELFcreation, width=9).place(x=135, y=190)
checkboxCountry = ttk.Checkbutton(tabELFcreation, text="Country").place(x=20, y=212)
inputCountry = ttk.Entry(tabELFcreation, width=9).place(x=135, y=212)
checkboxGeopointSource = ttk.Checkbutton(tabELFcreation, text="GeopointSource").place(x=20, y=234)
inputGeonpointSource = ttk.Entry(tabELFcreation, width=9).place(x=135, y=234)
checkboxMarket = ttk.Checkbutton(tabELFcreation, text="Market").place(x=20, y=256)
inputMarket = ttk.Entry(tabELFcreation, width=9).place(x=135, y=256)


#default console widgets
labelCurrentFileELF = ttk.Label(tabELFcreation, text="Current file: ").place(x=220, y=20)
labelELF = ttk.Label(tabELFcreation, textvariable=text, foreground='dark slate gray').place(x=287, y=20)

btnELFsave = ttk.Button(tabELFcreation, text="save", width=4.25, command=lambda:save()).place(x=673, y=6)
btnELFclear = ttk.Button(tabELFcreation, text="clear", width=4.25, command=lambda:clearELFConsole()).place(x=717, y=6)

ELFConsole = tk.Text(tabELFcreation, height=CONSOLE_HEIGHT, width=CONSOLE_WIDTH, background='black', foreground='lawn green', 
                    insertborderwidth=7, undo=True, bd=3)
ELFConsole.place(x=220, y=42)
ELFConsole.configure(font=consoleFont)
ELFConsole.insert(1.0, "United Systems dat File Tool [Version 1.6.0]")
ELFConsole.insert(2.0, "\n")
ELFConsole.insert(2.0, "(c) 2020 United Systems and Software, Inc.")
ELFConsole.insert(3.0, "\n")

########################
####### Tab 4 Widgets ##
########################

# labelAutoPopulate = ttk.Label(tab4, text="Fields to auto-populate:", font=labelFont).place(x=20, y=25)

# checkboxState = ttk.Checkbutton(tab4, text="State").place(x=20, y=50)
# inputState = ttk.Entry(tab4, width=16).place(x=90, y=50)
# checkboxCountry = ttk.Checkbutton(tab4, text="Country").place(x=20, y=70)
# inputCountry = ttk.Entry(tab4, width=16).place(x=90, y=70)
# checkboxZip = ttk.Checkbutton(tab4, text="Zip").place(x=20, y=90)
# inputZip = ttk.Entry(tab4, width=16).place(x=90, y=90)

# checkboxGeopointSource = ttk.Checkbutton(tab4, text="GeopointSource").place(x=20, y=130)
# inputGeonpointSource = ttk.Entry(tab4, width=9).place(x=135, y=130)
# checkboxMarket = ttk.Checkbutton(tab4, text="Market").place(x=20, y=150)
# inputMarket = ttk.Entry(tab4, width=9).place(x=135, y=150)


########################
##Settings Tab Widgets##
########################

labelFileSettings = ttk.Label(tabDeveloper, text="File Settings", font=labelFont).place(x=20, y=30)

tab2defaultextensionlabel = ttk.Label(tabDeveloper, text="• Default file extension:").place(x=20, y=53)
tab2defaultinput = ttk.Entry(tabDeveloper, width=4)
tab2defaultinput.insert(0, '.txt')
tab2defaultinput.place(x=155, y=53)

tab2defaultsavelabel = ttk.Label(tabDeveloper, text="• Default 'save' location:")
tab2defaultsavelabel.place(x=20, y=78)
tab2defaultsaveentry = ttk.Entry(tabDeveloper, width=10)
tab2defaultsaveentry.insert(0, '\\exports')
tab2defaultsaveentry.place(x=155, y=78)

tab2enforcebutton = ttk.Checkbutton(tabDeveloper, text="Enforce filetype imports")
tab2enforcebutton.place(x=20, y=100)

label=ttk.Label(tabDeveloper, image=photo)
label.image = photo
label.place(x=650, y=180)

# log settings
loglabel = ttk.Label(tabDeveloper, text="Log Settings", font=labelFont).place(x=300, y=30)

labelDelete = ttk.Label(tabDeveloper, text="• Log files allowed before deletion:").place(x=300, y=53)
logDeleteOldInput = ttk.Entry(tabDeveloper, width=4)
logDeleteOldInput.place(x=490, y=53)
logDeleteOldInput.insert(0, '10')

logverbose = ttk.Checkbutton(tabDeveloper, text="Log all function calls")
logverbose.place(x=300, y=78)
logverbose.state(['selected'])

########
##Menu##
########

menubar = tk.Menu(window)

filemenu = tk.Menu(menubar, tearoff=0)
filemenu.add_command(label="Open...", accelerator='Ctrl+O', command=lambda:openFile())
filemenu.add_command(label="Save", accelerator='Ctrl+S', command=lambda:save())
filemenu.add_command(label="Save As...", accelerator='Ctrl+Alt+S', command=lambda:saveAs())
filemenu.add_separator()
filemenu.add_command(label="Exit", accelerator='Alt+F4', command=lambda:window.destroy())
menubar.add_cascade(label="File", menu=filemenu)

editmenu = tk.Menu(menubar, tearoff=0)
editmenu.add_command(label="Clear Console", accelerator="Ctrl+C", command=lambda:clearBOCConsole())

submenu = Menu(editmenu)

submenu.add_command(label="clam", command=lambda:changeTheme('clam'))
submenu.add_command(label="winnative", command=lambda:changeTheme('winnative'))
submenu.add_command(label="alt", command=lambda:changeTheme('alt'))
submenu.add_command(label="xpnative", command=lambda:changeTheme('xpnative'))
submenu.add_command(label="default", command=lambda:changeTheme('default'))
submenu.add_command(label="classic", command=lambda:changeTheme('classic'))
submenu.add_command(label="vista", command=lambda:changeTheme('vista'))

editmenu.add_cascade(label="Theme", menu=submenu)
menubar.add_cascade(label="Edit", menu=editmenu)

windowmenu = tk.Menu(menubar, tearoff=0)
windowmenu.add_command(label="Full Screen", accelerator="F11", command=lambda:resizeWindow())
windowmenu.add_separator()
windowmenu.add_command(label="Reset Window", accelerator="F10", command=lambda:resetWindow())
menubar.add_cascade(label="Window", menu=windowmenu)

helpmenu = tk.Menu(menubar, tearoff=0)
helpmenu.add_command(label="About This Tool", accelerator='F1', command=lambda:aboutDialog())
helpmenu.add_command(label="Purge Log Files", command=lambda:Logging.deleteLog(int(logDeleteOldInput.get())))
menubar.add_cascade(label="Help", menu=helpmenu)

if __name__ == "__main__":
    Logging.createLogFile(int(logDeleteOldInput.get()))
    window.config(menu=menubar)
    window.mainloop()