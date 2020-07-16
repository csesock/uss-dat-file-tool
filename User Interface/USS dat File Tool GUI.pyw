import tkinter as tk
from tkinter import *
from tkinter import messagebox, simpledialog, ttk
from tkinter.filedialog import asksaveasfile

from collections import deque
from datetime import datetime
import sys, os, re, time

from tkinter.font import Font

record_pattern = re.compile('[a-z][0-9]*\s*')
empty_pattern = re.compile('[^\S\n\t]+')
empty2_pattern = re.compile('[^\S\r\n]{2,}')
lat_long_pattern = re.compile('-?[0-9]{2}\.\d{1,13}$')

download_filename = 'download.dat'

window = tk.Tk()
s = ttk.Style()
s.theme_use('clam')
DEFAULT_FONT_SIZE = 9
WIDTH = 77
HEIGHT = 16.5
textBoxFont = Font(family="Consolas", size=DEFAULT_FONT_SIZE)

window.title("USS dat File Tool v1.0.4")
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
window.bind('4', lambda event: fixOfficeRegionZoneFields())
window.bind('5', lambda event: missingMeters())
window.bind('6', lambda event: printMeterType())
window.bind('7', lambda event: checkMalformedLatLong())

window.bind('<Control-o>', lambda event: openFile())
window.bind('<Control-s>', lambda event: save())
window.bind('<Control-Alt-s>', lambda event: saveAs())
window.bind('<Control-c>', lambda event: textBox.delete(1.0, "end"))
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
    except FileNotFoundError:
        fileNotFoundError()
    textBox.delete(1.0, "end")
    textBox.insert("end", f"{counter:,d} " + answer + " records found")
    textBox.insert("end", "\n")

def printSingleRecord(event=None):
    record_type = simpledialog.askstring("Enter Record", "Enter the record type to search:", parent=window)
    if record_type is None:
        return
    record_type = record_type.upper()
    counter = 1.0
    try:
        with open(download_filename, 'r') as openfile:
            textBox.delete(1.0, "end")
            for line in openfile:
                if line.startswith(record_type):
                    textBox.insert(counter, line + "\n")
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
                    textBox.delete(1.0, "end")
                    textBox.insert(1.0, "Office . . . . : \t" + str(office))
                    textBox.insert(2.0, "\n")
                    textBox.insert(2.0, "Region . . . . : \t" + str(region))
                    textBox.insert(3.0, "\n")
                    textBox.insert(3.0, "Zone . . . . . : \t" + str(zone))
                    break
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
            textBox.delete(counter, "end")
            textBox.insert(counter, "File scan successful")
            counter+=1
            textBox.insert(counter, "\n")
            textBox.insert(counter, "--------------------------")
            counter+=1
            textBox.insert(counter, "\n")
            for record in all_records:
                textBox.insert(counter, str(record) + ". . . :\t" + f"{all_records[record]:,d} " + "\t\t |")
                counter+=1
                textBox.insert(counter, "\n")
            textBox.insert(counter, "--------------------------")
    except FileNotFoundError:
        fileNotFoundError()

def missingMeters(event=None):
    counter = 0
    try:
        with open(download_filename, 'r') as openfile:
            previous_line = ''
            textBox.delete(1.0, "end")
            for line in openfile:
                        if line.startswith('MTR'):
                            meter_record = line[45:57]
                            if empty_pattern.match(meter_record):
                                textBox.insert("end", previous_line)
                                textBox.insert("end", "\n")
                                counter+=1
                        previous_line=line
            if counter == 0:
                textBox.delete(1.0, "end")
                textBox.insert(1.0, "No missing meters found in ["+os.path.basename(download_filename)+"]")
                return
    except FileNotFoundError:
        fileNotFoundError()

def printMeterType(event=None):
    user_meter_code = simpledialog.askstring("Enter Record", "Enter the record type to search:", parent=window)
    if user_meter_code is None:
        return
    user_meter_code = user_meter_code.upper()
    counter = 0
    current_record = deque(maxlen=getCustomerRecordLength()+1)
    try:
        with open(download_filename, 'r') as openfile:
            textBox.delete(1.0, "end")
            for line in openfile:
                if line.startswith('RDG'):
                    meter_code = line[76:78]
                    if int(meter_code) == int(user_meter_code):
                        for record in current_record:
                            if record.startswith('CUS'):
                                textBox.insert("end", "{0} {1}".format(counter, record))
                                counter+=1
                current_record.append(line)
            if counter == 0:
                textBox.insert("end", "No meters of that type found.")
            elif counter != 0:
                textBox.insert("end", counter)
    except FileNotFoundError:
        fileNotFoundError()

def checkMalformedLatLong(event=None):
    malformed_data = False
    counter=1
    try:
        with open(download_filename, 'r') as openfile:
            for line in openfile:
                if line.startswith('MTX'):
                    lat_data = line[23:40].rstrip()
                    long_data = line[40:57].rstrip()
                    if not lat_long_pattern.match(lat_data) and not lat_long_pattern.match(long_data):
                        malformed_data = True
                        textBox.delete(1.0, "end")
                        textBox.insert(1.0, "Malformed lat/long data at line: " + str(counter))
                        return
                counter+=1
            textBox.delete(1.0, "end")
            textBox.insert(1.0, "No malformation within lat/long data detected.")
    except FileNotFoundError:
        fileNotFoundError()

def checkLatLongSigns(event=None):
    try:
        with open(download_filename, 'r') as openfile:
            for line in openfile:
                if line.startswith('MTX'):
                    lat_data = float(line[23:40].rstrip())
                    long_data = float(line[40:57].rstrip())
                    if lat_data < 0 or long_data > 0:
                        textBox2.delete(1.0, "end")
                        textBox2.insert(1.0, "The lat/long signs are malformed.")
                        return
                    else:
                        textBox2.delete(1.0, "end")
                        textBox2.insert(1.0, "The lat/long signs are correct.")
                        return
    except FileNotFoundError:
        fileNotFoundError()

def checkLatLongExists(event=None):
    try:
        with open(download_filename, 'r') as openfile:
            for line in openfile:
                if line.startswith('MTX'):
                    textBox2.delete(1.0, "end")
                    textBox2.insert(1.0, line[23:40])
                    textBox.insert(2.0, line[40:57])
                    return
    except FileNotFoundError:
        fileNotFoundError()


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

def clearText():
    textBox.delete(1.0, "end")

def save():
    export_filename = "DatFileToolExport " + str(datetime.today().strftime('%Y-%m-%d_%H-%M')) + ".txt"
    with open(export_filename, 'w') as openfile:
        text = textBox.get('1.0', 'end')
        openfile.write(text)
    messagebox.showinfo("Export", "Data successfully exported!")
 
def saveAs():
    files = [('All Files', '*.*'),
             ('Python Files', '*.py'),
             ('Text Files', '*.txt')]
    f = asksaveasfile(mode='w', defaultextension='.txt', filetypes=files)
    if f is None:
        return
    text2save = str(textBox.get(1.0, "end"))
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
    window.geometry('800x370+%d+%d' %(width, height))

def increaseFontSize():
    global DEFAULT_FONT_SIZE
    DEFAULT_FONT_SIZE+=1
    textBoxFont.configure(size=DEFAULT_FONT_SIZE)

def decreaseFontSize():
    global DEFAULT_FONT_SIZE
    DEFAULT_FONT_SIZE-=1
    textBoxFont.configure(size=DEFAULT_FONT_SIZE)

def fileNotFoundError():
    textBox.delete(1.0, "end")
    textBox.insert(1.0, "ERROR: File Not Found")


def aboutDialog():
    dialog = """ Author: Chris Sesock \n Version: 1.0.5 \n Commit: aebb993a87843e0ffc8b5fc2f32813638cc9be90 \n Date: 2020-07-16:2:00:00 \n Python: 3.9.1 \n OS: Windows_NT x64 10.0.10363
            """
    messagebox.showinfo("About", dialog)

# Create Tab Control
TAB_CONTROL = ttk.Notebook(window)

# Tab 1
TAB1 = ttk.Frame(TAB_CONTROL)
TAB_CONTROL.add(TAB1, text='Basic Operations Center')

# Tab 1 Widgets
Numkey1 = ttk.Button(TAB1, text="1.", width=1.5)
Numkey1.place(x=20, y=40)
SingleRecordScanButton = ttk.Button(TAB1, text="Single Record Scan", command=lambda:singleRecordScan(), width=22)
SingleRecordScanButton.place(x=50, y=40)
Numkey2 = ttk.Button(TAB1, text="2.", width=1.5)
Numkey2.place(x=20, y=80)
VerboseRecordScanButton = ttk.Button(TAB1, text="Full Record Scan", command=lambda:scanAllRecordsVerbose(), width=22)
VerboseRecordScanButton.place(x=50, y=80)
Numkey3 = ttk.Button(TAB1, text="3.", width=1.5)
Numkey3.place(x=20, y=120)
PrintSingleRecordButton = ttk.Button(TAB1, text="Display Record Type", command=lambda:printSingleRecord(), width=22)
PrintSingleRecordButton.place(x=50, y=120)
Numkey4 = ttk.Button(TAB1, text="4.", width=1.5)
Numkey4.place(x=20, y=160)
OfficeRegionZoneFieldButton = ttk.Button(TAB1, text="Office-Region-Zone", command=lambda:fixOfficeRegionZoneFields(), width=22)
OfficeRegionZoneFieldButton.place(x=50, y=160)
Numkey5 = ttk.Button(TAB1, text="5.", width=1.5)
Numkey5.place(x=20, y=200)
MissingMeterButton = ttk.Button(TAB1, text="Missing Meters", command=lambda:missingMeters(), width=22)
MissingMeterButton.place(x=50, y=200)
Numkey6 = ttk.Button(TAB1, text="6.", width=1.5)
Numkey6.place(x=20, y=240)
PrintReadTypeButton = ttk.Button(TAB1, text="Display Read Type", command=lambda:printMeterType(), width=22)
PrintReadTypeButton.place(x=50, y=240)
##Numkey7 = ttk.Button(TAB1, text="7.", width=1.5)
##Numkey7.place(x=20, y=260)
##MalformedLatLongButton = ttk.Button(TAB1, text="Malformed Lat/Long", command=lambda:checkMalformedLatLong(), width=20)
##MalformedLatLongButton.place(x=50, y=260)

currentlabel = ttk.Label(TAB1, text="Current file: ")
currentlabel.place(x=220, y=20)

text = tk.StringVar()
if os.path.isfile('download.dat'):
    text.set('download.dat')
else:
    text.set('No File')
#text.set(download_filename)
label = ttk.Label(TAB1, textvariable=text)
label.place(x=290, y=20)

consoleclearbutton = ttk.Button(TAB1, text="clear", width=4.25, command=lambda:clearText())
consoleclearbutton.place(x=720, y=6)

## Figure out font scaling here
#textBox = tk.Text(TAB1, height=16, width=63, background='black', foreground='lawn green')
textBox = tk.Text(TAB1, height=HEIGHT, width=WIDTH, background='black', foreground='lawn green')

textBox.place(x=220, y=40)
textBox.configure(font=textBoxFont)
textBox.insert(1.0, "United Systems dat File Tool")
textBox.insert(2.0, "\n")
textBox.insert(2.0, "(c) 2020 United Systems and Software, Inc.")
textBox.insert(3.0, "\n")

# Tab 3
tab3 = ttk.Frame(TAB_CONTROL)
TAB_CONTROL.add(tab3, text="Lat/Long Operations")
TAB_CONTROL.pack(expand=1, fill="both")

# Tab 2
tab2 = ttk.Frame(TAB_CONTROL)
TAB_CONTROL.add(tab2, text="Import/Export")
TAB_CONTROL.pack(expand=1, fill="both")

#Tab 2 Widgets
tab2label = ttk.Label(tab2, text="Import data from download file:")
tab2label.place(x=20, y=40)
tab2label2 = ttk.Label(tab2, text="Export current console data:")
tab2label2.place(x=20, y=115)

tab2importinput = tk.Text(tab2, width=60, height=1)
tab2importinput.place(x=20, y=65)
tab2importinput.insert(1.0, os.getcwd())
tab2importbutton = ttk.Button(tab2, text="Import...", command=lambda:openFile())
tab2importbutton.place(x=515, y=60)

tab2exportinput= tk.Text(tab2, width=60, height=1)
tab2exportinput.place(x=20, y=140)
tab2exportinput.insert(1.0, os.getcwd())

##photo = PhotoImage(file=r"assets/document.png")
##photoimage = photo.subsample(3, 3)

tab2exportbutton = ttk.Button(tab2, text="Export... ", command=lambda:save())
tab2exportbutton.place(x=515, y=135)

tab2enforcebutton = ttk.Checkbutton(tab2, text="Enforce file integrity (recommended)")
tab2enforcebutton.place(x=20, y=270)
tab2enforcebutton.state(['selected'])






# Tab 3 Widgets
currentlabel2 = ttk.Label(tab3, text="Current file: ")
currentlabel2.place(x=220, y=20)

text2 = tk.StringVar()
if os.path.isfile('download.dat'):
    text2.set('download.dat')
else:
    text2.set('No File')
#text.set(download_filename)
label2 = ttk.Label(tab3, textvariable=text2)
label2.place(x=290, y=20)

Numkey31 = ttk.Button(tab3, text="1.", width=1.5)
Numkey31.place(x=20, y=50)
tab3existsbutton = ttk.Button(tab3, text="Check Lat/Long Exist", width=22)
tab3existsbutton.place(x=50, y=50)

Numkey32 = ttk.Button(tab3, text="2.", width=1.5)
Numkey32.place(x=20, y=90)
tab3checksignbutton = ttk.Button(tab3, text="Check Lat/Long Signs", width=22, command=lambda:checkLatLongSigns())
tab3checksignbutton.place(x=50, y=90)

Numkey33 = ttk.Button(tab3, text="3.", width=1.5)
Numkey33.place(x=20, y=130)
tab3malformedbutton = ttk.Button(tab3, text="Check for Malformation", width=22)
tab3malformedbutton.place(x=50, y=130)

textBox2 = tk.Text(tab3, height=HEIGHT, width=WIDTH, background='black', foreground='lawn green')

textBox2.place(x=220, y=40)
textBox2.configure(font=textBoxFont)
textBox2.insert(1.0, "United Systems dat File Tool")
textBox2.insert(2.0, "\n")
textBox2.insert(2.0, "(c) 2020 United Systems and Software, Inc.")
textBox2.insert(3.0, "\n")

consoleclearbutton2 = ttk.Button(tab3, text="clear", width=4.25, command=lambda:clearText())
consoleclearbutton2.place(x=720, y=6)

# Menu
menubar = tk.Menu(window)

filemenu = tk.Menu(menubar, tearoff=0)
filemenu.add_command(label="Open...", accelerator='Ctrl+O', command=lambda:openFile())
filemenu.add_command(label="Save", accelerator='Ctrl+S', command=lambda:save())
filemenu.add_command(label="Save As...", accelerator='Ctrl+Alt+S', command=lambda:saveAs())
filemenu.add_separator()
filemenu.add_command(label="Exit", accelerator='Alt+F4', command=lambda:window.destroy())
menubar.add_cascade(label="File", menu=filemenu)

editmenu = tk.Menu(menubar, tearoff=0)
editmenu.add_command(label="Clear Console", accelerator="Ctrl+C", command=lambda:clearText())
menubar.add_cascade(label="Edit", menu=editmenu)

##formatmenu = tk.Menu(menubar, tearoff=0)
##formatmenu.add_command(label="Increase Font Size", accelerator="Alt+R", command=lambda:increaseFontSize())
##formatmenu.add_command(label="Decrease Font Size", accelerator="Alt+T", command=lambda:decreaseFontSize())
##formatmenu.add_separator()
##menubar.add_cascade(label="Format", menu=formatmenu)

windowmenu = tk.Menu(menubar, tearoff=0)
windowmenu.add_command(label="Full Screen", accelerator="F11", command=lambda:resizeWindow())
windowmenu.add_separator()
windowmenu.add_command(label="Reset Window", accelerator="F10", command=lambda:resetWindow())
menubar.add_cascade(label="Window", menu=windowmenu)

helpmenu = tk.Menu(menubar, tearoff=0)
helpmenu.add_command(label="About This Tool", accelerator='F1', command=lambda:aboutDialog())
menubar.add_cascade(label="Help", menu=helpmenu)

if __name__ == "__main__":
    window.config(menu=menubar)
    window.mainloop()
