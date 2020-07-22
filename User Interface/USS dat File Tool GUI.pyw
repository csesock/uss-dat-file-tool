import tkinter as tk
from tkinter import *
from tkinter import messagebox, simpledialog, ttk
from tkinter.filedialog import asksaveasfile
from tkinter.font import Font

from collections import deque
from datetime import datetime
import sys, os, re, time

developer = True

record_pattern = re.compile('[a-z][0-9]*\s*')   
empty_pattern = re.compile('[^\S\n\t]{11}')     #missing meters
empty2_pattern = re.compile('[^\S\r\n]{8}')
lat_long_pattern = re.compile('-?[0-9]{2}\.\d{1,13}$')

download_filename = 'download.dat'

window = tk.Tk()
s = ttk.Style()
s.theme_use('clam')

DEFAULT_FONT_SIZE = 10
CONSOLE_WIDTH = 76
CONSOLE_HEIGHT = 15
BUTTON_WIDTH = 22

consoleFont = Font(family="Consolas", size=DEFAULT_FONT_SIZE)

window.title("USS dat File Tool v1.3.0")
window.resizable(False, False)

height = window.winfo_screenheight()/3
width = window.winfo_screenwidth()/3
window.geometry('780x350+%d+%d' %(width, height))

defaut_file_extension = '.txt'

try:
    dirp = os.path.dirname(__file__)
    photo = PhotoImage(file="assets\\IconSmall.png")
    window.iconphoto(False, photo)
except:
    pass

window.bind('1', lambda event: singleRecordScan())
window.bind('2', lambda event: scanAllRecordsVerbose())
window.bind('3', lambda event: printSingleRecord())
window.bind('4', lambda event: fixOfficeRegionZoneFields())
window.bind('5', lambda event: missingMeters())
window.bind('6', lambda event: printReadType())
window.bind('7', lambda event: checkMalformedLatLong())

window.bind('<Control-o>', lambda event: openFile())
window.bind('<Control-s>', lambda event: save())
window.bind('<Control-Alt-s>', lambda event: saveAs())
window.bind('<Control-c>', lambda event: bocConsole.delete(1.0, "end"))
window.bind('<F1>', lambda event: aboutDialog())
window.bind('<F10>', lambda event: resetWindow())
window.bind('<Alt-r>', lambda event: increaseFontSize())
window.bind('<Alt-t>', lambda event: decreaseFontSize())

def singleRecordScan(event=None):
    answer = simpledialog.askstring("Enter Record", "Enter the record type to search:", parent=window)
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
    except FileNotFoundError:
        fileNotFoundError()

def printSingleRecord(event=None):
    record_type = simpledialog.askstring("Enter Record", "Enter the record type to search:", parent=window)
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
    except FileNotFoundError:
        fileNotFoundError()
        
def fixOfficeRegionZoneFields(event=None):
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
    except FileNotFoundError:
        fileNotFoundError()
        
def scanAllRecordsVerbose(event=None):
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
    except FileNotFoundError:
        fileNotFoundError()

def missingMeters(event=None):
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
    except FileNotFoundError:
        fileNotFoundError()

def printReadType(event=None):
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
    except FileNotFoundError:
        fileNotFoundError()

def printReadTypeVerbose(event=None):
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
    except FileNotFoundError:
        fileNotFoundError()

def checkMalformedLatLong(event=None):
    line_number = 1
    try:
        with open(download_filename, 'r') as openfile:
            for line in openfile:
                if line.startswith('MTX'):
                    lat_data = line[23:40].rstrip()
                    long_data = line[40:57].rstrip()
                    if not lat_long_pattern.match(lat_data) and not lat_long_pattern.match(long_data):
##                        if empty2_pattern.match(lat_data) and empty2_pattern.match(long_data):
##                            #lat long data is blank
##                            latLongConsole.delete(1.0, "end")
##                            latLongConsole.insert(1.0, "Lat/long entry blank at line: " + str(line_number))
                        latLongConsole.delete(1.0, "end")
                        latLongConsole.insert(1.0, "Malformed lat/long data at line: " + str(line_number))
                        latLongConsole.insert(2.0, "\n")
                        latLongConsole.insert(2.0, "Line: " + line)
                        return
                line_number+=1
            latLongConsole.delete(1.0, "end")
            latLongConsole.insert(1.0, "No malformation within lat/long data detected.")
    except FileNotFoundError:
        fileNotFoundError2()

def checkLatLongSigns(event=None):
    try:
        with open(download_filename, 'r') as openfile:
            for line in openfile:
                if line.startswith('MTX'):
                    lat_data = float(line[23:40].rstrip())
                    long_data = float(line[40:57].rstrip())
                    if lat_data < 0 or long_data > 0:
                        latLongConsole.delete(1.0, "end")
                        latLongConsole.insert(1.0, "The lat/long signs are incorrect.")
                        return
                    else:
                        latLongConsole.delete(1.0, "end")
                        latLongConsole.insert(1.0, "The lat/long signs are correct:")
                        latLongConsole.insert(2.0, "\n")
                        latLongConsole.insert(2.0, "Longitude Sign: Positive")
                        latLongConsole.insert(3.0, "\n")
                        latLongConsole.insert(3.0, "Latitude Sign: Negative")
                        return
            latLongConsole.delete(1.0, "end")
            latLongConsole.insert(1.0, "No lat/long data detected.")
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
    export_filename = "DatFileToolExport " + str(datetime.today().strftime('%Y-%m-%d_%H-%M')) + ".txt"
    with open(export_filename, 'w') as openfile:
        text = bocConsole.get('1.0', 'end')
        openfile.write(text)
    messagebox.showinfo("Export", "Data successfully exported!")
 
def saveAs(default_file_extension):
    files = [('Text Files', '*.txt'),
             ('All Files', '*.*'),
             ('Python Files', '*.py'),
             ('CSV Files', '*.csv')]
    f = asksaveasfile(mode='w', defaultextension=default_file_extension, filetypes=files)
    if f is None:
        return
    text2save = str(bocConsole.get(1.0, "end"))
    f.write(text2save)
    f.close()

def openFile():
    filename = tk.filedialog.askopenfilename(title="Import File")
    if tab2enforcebutton.instate(['selected']):
        if not filename.lower().endswith(('.dat', '.DAT', '.hdl', '.HDL')):
            messagebox.showinfo("ERROR", "An error occured. Please select another file.")
            return
    global download_filename
    download_filename = filename
    text.set(os.path.basename(download_filename))
    text2.set(os.path.basename(download_filename))
       
def resizeWindow():
    width = window.winfo_screenwidth()
    height = window.winfo_screenheight()
    window.geometry('%dx%d+0+0' %(width, height))

def resetWindow():
    height = window.winfo_screenheight()/3
    width = window.winfo_screenwidth()/3
    window.geometry('780x350+%d+%d' %(width, height))
    bocConsole.delete(1.0, "end")
    bocConsole.insert(1.0, "United Systems dat File Tool")
    bocConsole.insert(2.0, "\n")
    bocConsole.insert(2.0, "(c) 2020 United Systems and Software, Inc.")
    bocConsole.insert(3.0, "\n")

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
    dialog = """ Author: Chris Sesock \n Version: 1.3.0 \n Commit: aebb993a87843e0ffc8b5fc2f32813638cc9be90 \n Date: 2020-07-16:2:00:00 \n Python: 3.8.3 \n OS: Windows_NT x64 10.0.10363
             """
    messagebox.showinfo("About", dialog)

def enableDev():
    global developer
    developer=True

# Create Tab Control
TAB_CONTROL = ttk.Notebook(window)
# Tab 1
TAB1 = ttk.Frame(TAB_CONTROL)
TAB_CONTROL.add(TAB1, text='Basic Operations')
# Tab 3
tab3 = ttk.Frame(TAB_CONTROL)
TAB_CONTROL.add(tab3, text="Lat/Long Operations")
TAB_CONTROL.pack(expand=1, fill="both")
# Tab 2
if developer == True:
    tab2 = ttk.Frame(TAB_CONTROL)
    TAB_CONTROL.add(tab2, text="Settings")
    TAB_CONTROL.pack(expand=1, fill="both")

#################
##Tab 1 Widgets##
#################

Numkey1 = ttk.Button(TAB1, text="1.", width=1.5, command=lambda:singleRecordScan())
Numkey1.place(x=20, y=35)
SingleRecordScanButton = ttk.Button(TAB1, text="Record Count Search", command=lambda:singleRecordScan(), width=BUTTON_WIDTH)
SingleRecordScanButton.place(x=50, y=35)

Numkey2 = ttk.Button(TAB1, text="2.", width=1.5, command=lambda:scanAllRecordsVerbose())
Numkey2.place(x=20, y=76)
VerboseRecordScanButton = ttk.Button(TAB1, text="Record Type Count", command=lambda:scanAllRecordsVerbose(), width=BUTTON_WIDTH)
VerboseRecordScanButton.place(x=50, y=76)

Numkey3 = ttk.Button(TAB1, text="3.", width=1.5, command=lambda:printSingleRecord())
Numkey3.place(x=20, y=117)
PrintSingleRecordButton = ttk.Button(TAB1, text="Record Type Search", command=lambda:printSingleRecord(), width=BUTTON_WIDTH)
PrintSingleRecordButton.place(x=50, y=117)

Numkey4 = ttk.Button(TAB1, text="4.", width=1.5, command=lambda:fixOfficeRegionZoneFields())
Numkey4.place(x=20, y=158)
OfficeRegionZoneFieldButton = ttk.Button(TAB1, text="Office-Region-Zone", command=lambda:fixOfficeRegionZoneFields(), width=BUTTON_WIDTH)
OfficeRegionZoneFieldButton.place(x=50, y=158)

Numkey5 = ttk.Button(TAB1, text="5.", width=1.5, command=lambda:missingMeters())
Numkey5.place(x=20, y=199)
MissingMeterButton = ttk.Button(TAB1, text="Blank Meter Numbers", command=lambda:missingMeters(), width=BUTTON_WIDTH)
MissingMeterButton.place(x=50, y=199)

Numkey6 = ttk.Button(TAB1, text="6.", width=1.5, command=lambda:printReadTypeVerbose())
Numkey6.place(x=20, y=240)
PrintReadTypeButton = ttk.Button(TAB1, text="Read Type Code Count", command=lambda:printReadTypeVerbose(), width=BUTTON_WIDTH)
PrintReadTypeButton.place(x=50, y=240)

currentlabel = ttk.Label(TAB1, text="Current file: ")
currentlabel.place(x=220, y=20)

text = tk.StringVar()
if os.path.isfile('download.dat'):
    text.set('download.dat')
else:
    text.set('None')
label = ttk.Label(TAB1, textvariable=text)
label.place(x=290, y=20)

consoleclearbutton = ttk.Button(TAB1, text="clear", width=4.25, command=lambda:clearBOCConsole())
consoleclearbutton.place(x=715, y=6)

bocConsole = tk.Text(TAB1, height=CONSOLE_HEIGHT, width=CONSOLE_WIDTH, background='black', foreground='lawn green')

bocConsole.place(x=220, y=40)
bocConsole.configure(font=consoleFont)
bocConsole.insert(1.0, "United Systems dat File Tool")
bocConsole.insert(2.0, "\n")
bocConsole.insert(2.0, "(c) 2020 United Systems and Software, Inc.")
bocConsole.insert(3.0, "\n")

#################
##Tab 2 Widgets##
#################

if developer == True:
    tab2headerlabel = ttk.Label(tab2, text="""The default settings below should be changed at your own risk. \nMay cause unexpected errors.""")
    tab2headerlabel.place(x=20, y=20)

    tab2defaultextensionlabel = ttk.Label(tab2, text="Default file extension:")
    tab2defaultextensionlabel.place(x=20, y=70)
    tab2defaultinput = ttk.Entry(tab2, width=5)
    tab2defaultinput.insert(0, '.txt')
    tab2defaultinput.place(x=150, y=70)

    tab2defaultsavelabel = ttk.Label(tab2, text="Default 'Save' location:")
    tab2defaultsavelabel.place(x=20, y=100)
    tab2defaultsaveentry = ttk.Entry(tab2, width=5)
    tab2defaultsaveentry.insert(0, '**')
    tab2defaultsaveentry.place(x=150, y=100)
    tab2explainlabel = ttk.Label(tab2, text="(** for same directory)")
    tab2explainlabel.place(x=190, y=100)

    tab2resizablebutton = ttk.Checkbutton(tab2, text="Make window resizable (not recommended)")
    tab2resizablebutton.place(x=20, y=140)

    tab2enforcebutton = ttk.Checkbutton(tab2, text="Enforce filetype imports (recommended)")
    tab2enforcebutton.place(x=20, y=160)
    tab2enforcebutton.state(['selected'])

    tab2referencebutton = ttk.Checkbutton(tab2, text="Enforce referential integrity (recommended)")
    tab2referencebutton.place(x=20, y=180)
    tab2referencebutton.state(['selected'])

    tab2geobutton = ttk.Checkbutton(tab2, text="Assume geographic area for lat/long data (recommended)")
    tab2geobutton.place(x=20, y=200)
    tab2geobutton.state(['selected'])

    label=ttk.Label(tab2, image=photo)
    label.image = photo
    label.place(x=650, y=180)

#################
##Tab 3 Widgets##
#################

currentlabel2 = ttk.Label(tab3, text="Current file: ")
currentlabel2.place(x=220, y=20)

text2 = tk.StringVar()
if os.path.isfile('download.dat'):
    text2.set('download.dat')
else:
    text2.set('None')

label2 = ttk.Label(tab3, textvariable=text2)
label2.place(x=290, y=20)

NumkeyLatLong1 = ttk.Button(tab3, text="1.", width=1.5, command=lambda:checkLatLongExists())
NumkeyLatLong1.place(x=20, y=35)
tab3existsbutton = ttk.Button(tab3, text="Find First Lat/Long", width=BUTTON_WIDTH, command=lambda:checkLatLongExists())
tab3existsbutton.place(x=50, y=35)

NumkeyLatLong2 = ttk.Button(tab3, text="2.", width=1.5, command=lambda:checkLatLongSigns())
NumkeyLatLong2.place(x=20, y=76)
tab3checksignbutton = ttk.Button(tab3, text="Lat/Long Signs", width=BUTTON_WIDTH, command=lambda:checkLatLongSigns())
tab3checksignbutton.place(x=50, y=76)

NumkeyLatLong3 = ttk.Button(tab3, text="3.", width=1.5, command=lambda:checkMalformedLatLong())
NumkeyLatLong3.place(x=20, y=117)
tab3malformedbutton = ttk.Button(tab3, text="Check for Malformation", width=BUTTON_WIDTH, command=lambda:checkMalformedLatLong())
tab3malformedbutton.place(x=50, y=117)

NumkeyLatLong4 = ttk.Button(tab3, text="4.", width=1.5, command=lambda:printAllLatLongData())
NumkeyLatLong4.place(x=20, y=158)
tab3allmalformedbutton = ttk.Button(tab3, text="All Lat/Long", width=BUTTON_WIDTH, command=lambda:printAllLatLongData())
tab3allmalformedbutton.place(x=50, y=158)

latLongConsole = tk.Text(tab3, height=CONSOLE_HEIGHT, width=CONSOLE_WIDTH, background='black', foreground='lawn green')

latLongConsole.place(x=220, y=40)
latLongConsole.configure(font=consoleFont)
latLongConsole.insert(1.0, "United Systems dat File Tool")
latLongConsole.insert(2.0, "\n")
latLongConsole.insert(2.0, "(c) 2020 United Systems and Software, Inc.")
latLongConsole.insert(3.0, "\n")

consoleclearbutton2 = ttk.Button(tab3, text="clear", width=4.25, command=lambda:clearLatLongConsole())
consoleclearbutton2.place(x=715, y=6)

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
helpmenu.add_command(label="Enable Developer Mode", command=lambda:enableDev())
menubar.add_cascade(label="Help", menu=helpmenu)



if __name__ == "__main__":
    window.config(menu=menubar)
    window.mainloop()
