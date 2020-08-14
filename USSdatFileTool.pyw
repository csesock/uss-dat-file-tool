import tkinter as tk
from tkinter import *
from tkinter import messagebox, simpledialog, ttk
from tkinter.filedialog import asksaveasfile
from tkinter.font import Font

from collections import deque
from datetime import datetime
import sys, os, re, time
try:
    import Logging
except:
    print("Logging system files not found -- to enable logging please place Logging.py in the same directory")
    pass

#enables advanced options in UI
developer=True

#regular expressions for parsing
record_pattern = re.compile('[a-z][0-9]*\s*')   
empty_pattern = re.compile('[^\S\n\t]{11}')     #missing meters
empty2_pattern = re.compile('[^\S\r\n]{8}')
lat_long_pattern = re.compile('-?[0-9]{2}\.\d{1,13}$')

#file configurations
download_filename = 'download.dat'
defaut_file_extension = '.txt'

window = tk.Tk()
s = ttk.Style()
s.theme_use('clam')

#default UI visual configuration
DEFAULT_FONT_SIZE = 10
CONSOLE_WIDTH = 76
CONSOLE_HEIGHT = 15
BUTTON_WIDTH = 22
consoleFont = Font(family="Consolas", size=DEFAULT_FONT_SIZE)
window.title("United System .dat File Tool")
window.resizable(False, False)
height = window.winfo_screenheight()/3
width = window.winfo_screenwidth()/3
window.geometry('780x350+%d+%d' %(width, height))

try:
    dirp = os.path.dirname(__file__)
    photo = PhotoImage(file="assets\\IconSmall.png")
    window.iconphoto(False, photo)
except:
    pass

window.bind('1', lambda event: singleRecordScan())
window.bind('2', lambda event: scanAllRecordsVerbose())
window.bind('3', lambda event: printSingleRecord())
window.bind('4', lambda event: officeRegionZone())
window.bind('5', lambda event: missingMeters())
window.bind('6', lambda event: printReadType())
window.bind('7', lambda event: checkMalformedLatLong())

window.bind('<Control-o>', lambda event: openFile())
window.bind('<Control-s>', lambda event: save())
window.bind('<Control-Alt-s>', lambda event: saveAs())
window.bind('<Control-c>', lambda event: bocConsole.delete(1.0, "end"))
window.bind('<F1>', lambda event: aboutDialog())
#window.bind('<F2>', lambda event: Logging.deleteLog(int(logDeleteOldInput.get())))
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

def singleRecordScan(event=None):
    Logging.writeToLogs('Start Function Call - singleRecordScan()')
    answer = simpledialog.askstring("Enter Record", "Enter the record type to search: \n(blank to display entire file)", parent=window)
    if answer is None or answer == "":
        return
    answer = answer.upper()
    counter = 0
    try:
        with open(download_filename, 'r') as openfile:
            for line in openfile:
                if line.startswith(answer):
                    counter+=1
            bocConsole.delete(1.0, "end")
            bocConsole.insert("end", f"{counter:,d} " + answer + " records found")
            bocConsole.insert("end", "\n")
        Logging.writeToLogs('End Function Call - singleRecordScan()')
    except FileNotFoundError:
        fileNotFoundError()

def printSingleRecord(event=None):
    Logging.writeToLogs('Start Function Call - printSingleRecord()')
    record_type = simpledialog.askstring("Record Search", "Enter the record type to search: \n\n(blank to display entire file)", parent=window)
    if record_type is None:
        return
    record_type = record_type.upper()
    counter = 1.0
    try:
        with open(download_filename, 'r') as openfile:
            bocConsole.delete(1.0, "end")
            for line in openfile:
                if line.startswith(record_type):
                    bocConsole.insert(counter, line + "\n")
                    counter+=1
        Logging.writeToLogs('End Function Call - printSingleRecord()')
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
                            if empty_pattern.match(meter_record):
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
                    if not lat_long_pattern.match(lat_data) and not lat_long_pattern.match(long_data):
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
    try:
        with open(download_filename, 'r') as openfile:
            latLongConsole.delete(1.0, "end")
            for line in openfile:
                if line.startswith('MTX'):
                    lat_data = line[23:40].rstrip()
                    long_data = line[40:57].rstrip()
                    if lat_long_pattern.match(lat_data) and lat_long_pattern.match(long_data):
                        latLongConsole.insert(counter, line)
                        latLongConsole.insert(counter+1, "\n")
                        total_latlong+=1
                counter+=1
            if total_latlong == 0:
                latLongConsole.insert(1.0, "There was no lat/long data found.")
    except FileNotFoundError:
        fileNotFoundError2()

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
             ('Python Files', '*.py'),
             ('CSV Files', '*.csv')]
    f = asksaveasfile(mode='w', defaultextension='.txt', filetypes=files)
    if f is None:
        return
    if TAB_CONTROL.index(TAB_CONTROL.select()) == 0:
        text2save = str(bocConsole.get(1.0, "end"))
    else:
        text2save = str(latLongConsole.get(1.0, "end"))
    f.write(text2save)
    f.close()

def openFile():
    Logging.writeToLogs('Start Function Call - openFile()')
    filename = tk.filedialog.askopenfilename(title="Import File")
    if tab2enforcebutton.instate(['selected']):
        if not filename.lower().endswith(('.dat', '.DAT', '.hdl', '.HDL')):
            messagebox.showinfo("ERROR", "Filetype imports are enforced. Please select a compatible file.")
            return
    global download_filename
    download_filename = filename
    text.set(os.path.basename(download_filename))
    labelFileVar.set(os.path.basename(download_filename))
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
    bocConsole.insert(1.0, "United Systems dat File Tool [Version 1.5.1]")
    bocConsole.insert(2.0, "\n")
    bocConsole.insert(2.0, "(c) 2020 United Systems and Software, Inc.")
    bocConsole.insert(3.0, "\n")
    latLongConsole.delete(1.0, "end")
    latLongConsole.insert(1.0, "United Systems dat File Tool [Version 1.5.1]")
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

def aboutDialog():
    dialog = """ Author: Chris Sesock \n Version: 1.5.1 \n Commit: 077788d6166f5d69c9b660454aa264dd62956fb6 \n Date: 2020-08-13:12:00:00 \n Python: 3.8.3 \n OS: Windows_NT x64 10.0.10363
             """
    messagebox.showinfo("About", dialog)

# Create Tab Control
TAB_CONTROL = ttk.Notebook(window)
# Basic Operations tab
tabBasicOperations = ttk.Frame(TAB_CONTROL)
TAB_CONTROL.add(tabBasicOperations, text='Basic Operations')
# Lat/Long tab
tabLatLong = ttk.Frame(TAB_CONTROL)
TAB_CONTROL.add(tabLatLong, text="Lat/Long Operations")
TAB_CONTROL.pack(expand=1, fill="both")
# (Optional) Developer Settings tab
if developer == True:
    tabDeveloper = ttk.Frame(TAB_CONTROL)
    TAB_CONTROL.add(tabDeveloper, text="Settings")
    TAB_CONTROL.pack(expand=1, fill="both")

###################
##BOC Tab Widgets##
###################

btnNumkey1 = ttk.Button(tabBasicOperations, text="1.", width=1.5, command=lambda:scanAllRecordsVerbose()).place(x=20, y=35)
btnVerboseRecordScan = ttk.Button(tabBasicOperations, text="All Record Counts", command=lambda:scanAllRecordsVerbose(), width=BUTTON_WIDTH).place(x=50, y=35)

btnNumkey2 = ttk.Button(tabBasicOperations, text="2.", width=1.5, command=lambda:printSingleRecord()).place(x=20, y=76)
btnPrintSingleRecord = ttk.Button(tabBasicOperations, text="Record Type Search", command=lambda:printSingleRecord(), width=BUTTON_WIDTH).place(x=50, y=76)

btnNumkey3 = ttk.Button(tabBasicOperations, text="3.", width=1.5, command=lambda:disallowedCharacters()).place(x=20, y=117)
btnSingleRecordScan = ttk.Button(tabBasicOperations, text="Bad Meter Characters", command=lambda:disallowedCharacters(), width=BUTTON_WIDTH).place(x=50, y=117)

btnNumkey4 = ttk.Button(tabBasicOperations, text="4.", width=1.5, command=lambda:missingMeters()).place(x=20, y=158)
btnOfficeRegionZone = ttk.Button(tabBasicOperations, text="Blank Meter Numbers", command=lambda:missingMeters(), width=BUTTON_WIDTH).place(x=50, y=158)

btnNumkey5 = ttk.Button(tabBasicOperations, text="5.", width=1.5, command=lambda:officeRegionZone()).place(x=20, y=199)
MissingMeterButton = ttk.Button(tabBasicOperations, text="Office-Region-Zone", command=lambda:officeRegionZone(), width=BUTTON_WIDTH).place(x=50, y=199)

btnNumkey6 = ttk.Button(tabBasicOperations, text="6.", width=1.5, command=lambda:printReadTypeVerbose()).place(x=20, y=240)
PrintReadTypeButton = ttk.Button(tabBasicOperations, text="Read Type Codes", command=lambda:printReadTypeVerbose(), width=BUTTON_WIDTH).place(x=50, y=240)

currentlabel = ttk.Label(tabBasicOperations, text="Current file: ")
currentlabel.place(x=220, y=20)

text = tk.StringVar()
if os.path.isfile('download.dat'):
    text.set('download.dat')
else:
    text.set('None')
label = ttk.Label(tabBasicOperations, textvariable=text).place(x=290, y=20)

# textStatus = tk.StringVar()
# textStatus.set('0 records found')
# labelStatus = ttk.Label(tabBasicOperations, textvariable=textStatus).place(x=660, y=273)
# labelRecords = ttk.Label(tabBasicOperations, text=" records found").place(x=670, y=275)

btnConsoleClear = ttk.Button(tabBasicOperations, text="clear", width=4.25, command=lambda:clearBOCConsole()).place(x=670, y=6)
btnConsoleReset = ttk.Button(tabBasicOperations, text="reset", width = 4.24, command=lambda:resetWindow()).place(x=715,y=6)

bocConsole = tk.Text(tabBasicOperations, height=CONSOLE_HEIGHT, width=CONSOLE_WIDTH, background='black', foreground='lawn green')

bocConsole.place(x=220, y=42)
bocConsole.configure(font=consoleFont)
bocConsole.insert(1.0, "United Systems dat File Tool [Version 1.5.1]")
bocConsole.insert(2.0, "\n")
bocConsole.insert(2.0, "(c) 2020 United Systems and Software, Inc.")
bocConsole.insert(3.0, "\n")

#################
##Lat/Long Tab###
#################

labelCurrentFileLatLong = ttk.Label(tabLatLong, text="Current file: ").place(x=220, y=20)

labelFileVar = tk.StringVar()
if os.path.isfile('download.dat'):
    labelFileVar.set('download.dat')
else:
    labelFileVar.set('None')
labelFile = ttk.Label(tabLatLong, textvariable=labelFileVar)
labelFile.place(x=290, y=20)

btnNumkeyLat1 = ttk.Button(tabLatLong, text="1.", width=1.5, command=lambda:checkLatLongExists()).place(x=20, y=35)
btnLatExists = ttk.Button(tabLatLong, text="Find First Lat/Long", width=BUTTON_WIDTH, command=lambda:checkLatLongExists()).place(x=50, y=35)

btnNumkeyLat2 = ttk.Button(tabLatLong, text="2.", width=1.5, command=lambda:checkLatLongSigns()).place(x=20, y=76)
btnLatSigns = ttk.Button(tabLatLong, text="Lat/Long Ranges", width=BUTTON_WIDTH, command=lambda:checkLatLongSigns()).place(x=50, y=76)

btnNumkeyLat3 = ttk.Button(tabLatLong, text="3.", width=1.5, command=lambda:checkMalformedLatLong()).place(x=20, y=117)
btnLatMalformed = ttk.Button(tabLatLong, text="Check for Malformation", width=BUTTON_WIDTH, command=lambda:checkMalformedLatLong()).place(x=50, y=117)

btnNumkeyLat4 = ttk.Button(tabLatLong, text="4.", width=1.5, command=lambda:printAllLatLongData()).place(x=20, y=158)
btnLatAllMalformed = ttk.Button(tabLatLong, text="All Lat/Long", width=BUTTON_WIDTH, command=lambda:printAllLatLongData()).place(x=50, y=158)

labelRegion = ttk.Label(tabLatLong, text="Region:").place(x=22, y=200)
dropdownRegion = ttk.Combobox(tabLatLong, width=26, values = ["Eastern US", "Western US", "New Zealand"])
dropdownRegion.place(x=22, y=220)
dropdownRegion.state(['readonly'])
dropdownRegion.set('Eastern US')

latLongConsole = tk.Text(tabLatLong, height=CONSOLE_HEIGHT, width=CONSOLE_WIDTH, background='black', foreground='lawn green')
latLongConsole.place(x=220, y=42)
latLongConsole.configure(font=consoleFont)
latLongConsole.insert(1.0, "United Systems dat File Tool [Version 1.5.1]")
latLongConsole.insert(2.0, "\n")
latLongConsole.insert(2.0, "(c) 2020 United Systems and Software, Inc.")
latLongConsole.insert(3.0, "\n")

btnLatConsoleClear = ttk.Button(tabLatLong, text="clear", width=4.25, command=lambda:clearLatLongConsole()).place(x=670, y=6)
btnLatConsoleReset = ttk.Button(tabLatLong, text="reset", width=4.25, command=lambda:resetWindow()).place(x=715, y=6)

########################
##Settings Tab Widgets##
########################

if developer == True:
    #labelDevWarning = ttk.Label(tabDeveloper, text="""The settings below are for testing purposes and should be changed at your own risk.""").place(x=20, y=20)

    labelFileSettings = ttk.Label(tabDeveloper, text="File Settings").place(x=20, y=55)

    tab2defaultextensionlabel = ttk.Label(tabDeveloper, text="Default file extension:").place(x=20, y=78)
    tab2defaultinput = ttk.Entry(tabDeveloper, width=4)
    tab2defaultinput.insert(0, '.txt')
    tab2defaultinput.place(x=150, y=78)

    tab2defaultsavelabel = ttk.Label(tabDeveloper, text="Default 'Save' location:")
    tab2defaultsavelabel.place(x=20, y=103)
    tab2defaultsaveentry = ttk.Entry(tabDeveloper, width=4)
    tab2defaultsaveentry.insert(0, '***')
    tab2defaultsaveentry.place(x=150, y=103)

    tab2enforcebutton = ttk.Checkbutton(tabDeveloper, text="Enforce filetype imports")
    tab2enforcebutton.place(x=20, y=125)

    label=ttk.Label(tabDeveloper, image=photo)
    label.image = photo
    label.place(x=650, y=180)

    # log settings
    loglabel = ttk.Label(tabDeveloper, text="Log Settings").place(x=20, y=180)

    labelDelete = ttk.Label(tabDeveloper, text="Log files allowed before deletion:").place(x=20, y=205)
    logDeleteOldInput = ttk.Entry(tabDeveloper, width=3)
    logDeleteOldInput.place(x=200, y=205)
    logDeleteOldInput.insert(0, '10')

    logverbose = ttk.Checkbutton(tabDeveloper, text="Log all function calls")
    logverbose.place(x=20, y=227)
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
    Logging.createLogFile()
    window.config(menu=menubar)
    window.mainloop()
