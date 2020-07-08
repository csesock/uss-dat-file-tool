import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
#from ttkthemes import themed_tk as tk
import sys
import os
import re
#import win32clipboard as clipboard

# regular expression patterns
record_pattern = re.compile('[a-z][0-9]*\s*')
empty_pattern = re.compile('[^\S\n\t]+')
empty2_pattern = re.compile('[^\S\r\n]{2,}')
lat_long_pattern = re.compile('-?[0-9]{2}\.\d{1,13}$')

# intializing the window
window = tk.Tk()
s = ttk.Style()
s.theme_use('clam')
window.title("USS dat File Tool v0.9")
window.resizable(False, False)

# configuring size of the window 
window.geometry('700x350')

def singleRecordScan():
    answer = simpledialog.askstring("Enter Record", "Enter the record type to search:",
                                parent=window)
    counter = 0
    try:
        with open('download.dat', 'r') as openfile:
            for line in openfile:
                if line.startswith(answer):
                    counter+=1
    except FileNotFoundError:
        textBox.insert("end", "ERROR: FILE NOT FOUND.")

    textBox.delete(1.0, "end")
    textBox.insert(1.0, f"{counter:,d} " + answer + " records found")


def printSingleRecord():
    counter = 1.0
    record_type = simpledialog.askstring("Enter Record", "Enter the record type to search:",
                                parent=window)
    try:
        with open('download.dat', 'r') as openfile:
            textBox.delete(1.0, "end")
            for line in openfile:
                if line.startswith(record_type):
                    textBox.insert(counter, line + "\n")
                    counter+=1
    except FileNotFoundError:
        textBox.insert("end", "ERROR: FILE NOT FOUND.")


def printAllRecords():
    try:
        with open('download.dat', 'r') as openfile:
            counter = 1
            for line in openfile:
                textBox.insert(float(counter), line)
                counter+=1
    except FileNotFoundError:
        textBox.insert("end", "ERROR: FILE NOT FOUND.")

        
def fixOfficeRegionZoneFields():
    counter = 1.0
    try:
        with open('download.dat', 'r') as openfile:
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
        textBox.insert("end", "ERROR: FILE NOT FOUND.")

        
def scanAllRecordsVerbose():
    all_records = {}
    counter = 3.0
    try:
        with open('download.dat', 'r') as openfile:
            for line in openfile:
                x = line[0:3]
                if x not in all_records:
                    all_records[x] = 1
                else:
                    all_records[x]+=1
            textBox.delete(1.0, "end")
            textBox.insert(1.0, "File scan successful.")
            textBox.insert(2.0, "\n")
            textBox.insert(2.0, "----------------------")
            textBox.insert(3.0, "\n")
            for record in all_records:
                textBox.insert(counter, str(record) + ". . . :\t" + f"{all_records[record]:,d}")
                counter+=1
                textBox.insert(counter, "\n")
    except FileNotFoundError:
        textBox.insert("end", "ERROR: FILE NOT FOUND.")


def exportMissingMeters():
    counter=0
    current_line=1
    try:
        with open('download.dat', 'r') as openfile:
            try:
                with open('missingMeters.txt', 'x') as builtfile:
                    previous_line = ''
                    for line in openfile:
                        if line.startswith('MTR'):
                            meter_record = line[45:57]
                            if empty_pattern.match(meter_record):
                                builtfile.write(previous_line)
                                counter+=1
                        previous_line=line
                        current_line+=1
                    if counter == 0:
                        builtfile.close()
                        os.remove('missingMeters.txt')
                        textBox.insert("end", "No missing meters found.")
            except FileExistsError:
                textBox.insert("end", "file already exists")
                return
    except FileNotFoundError:
        textBox.insert("end", "ERROR: FILE NOT FOUND.")
        return
    textBox.delete(1.0, "end")
    textBox.insert(1.0, "The operation was successful.")
    textBox.insert(2.0, "\n")


def checkMalformedLatLong():
    malformed_data = False
    counter=1
    try:
        with open('download.dat', 'r') as openfile:
            for line in openfile:
                if line.startswith('MTX'):
                    lat_data = line[23:40].rstrip()
                    long_data = line[40:57].rstrip()
                    if not lat_long_pattern.match(lat_data):
                        malformed_data = True 
                        print("Malformed lat data at line:", counter, "Value:", lat_data)
                    elif not lat_long_pattern.match(long_data):
                        malformed_data = True
                        print("Malformed long data at line:", counter, "Value:", long_data)
                counter+=1
            if malformed_data == True:
                print("The above data is malformed in some way.")
            else:
                if checkLatLongSigns(float(lat_data), float(long_data)) == False:
                    print("The data is not malformed.")
                else:
                    print("The data has malformed sign values.")
    except FileNotFoundError:
        textBox.insert("end", "ERROR: FILE NOT FOUND.")

# an additional level of checking to make sure that lat/long data is correct
# lat data will always be +, long will always be - in our region
def checkLatLongSigns(lat_data, long_data):
    if lat_data < 0 or long_data > 0:
        return True
    else:
        return False



def drawCanvas():
    canvas.create_rectangle(20, 140, 120, 180, fill="red")
    canvas.create_text(70, 130, text="Projects--20%")
    canvas.create_rectangle(140, 160, 240, 180, fill="blue")
    canvas.create_text(190, 150, text="Quizzes--10%")
    canvas.create_rectangle(260, 120, 360, 180, fill="green")
    canvas.create_text(310, 110, text="Midterm--30%")
    canvas.create_line(0, 180, 500, 180)

################################################

#Create Tab Control
TAB_CONTROL = ttk.Notebook(window)

#Tab1
TAB1 = ttk.Frame(TAB_CONTROL)
TAB_CONTROL.add(TAB1, text=' Basic Operations Center ')

#Tab2
TAB2 = ttk.Frame(TAB_CONTROL)
TAB_CONTROL.add(TAB2, text=' Visualizations ')
TAB_CONTROL.pack(expand=1, fill="both")

#Tab3
TAB3 = ttk.Frame(TAB_CONTROL)
TAB_CONTROL.add(TAB3, text=" Import/Export ")
TAB_CONTROL.pack(expand=1, fill="both")

#Tab1 Widgets
b1 = ttk.Button(TAB1, text="1. Single Record Scan", command=lambda:singleRecordScan())
b1.place(x=20, y=20)
b2 = ttk.Button(TAB1, text="2. Verbose Record Scan", command=lambda:scanAllRecordsVerbose())
b2.place(x=20, y=60)
b3 = ttk.Button(TAB1, text="3. Print Single Record", command=lambda:printSingleRecord())
b3.place(x=20, y=100)
b4 = ttk.Button(TAB1, text="4. Print Office-Region-Zone", command=lambda:fixOfficeRegionZoneFields())
b4.place(x=20, y=140)
b5 = ttk.Button(TAB1, text="5. Export Missing Meters", command=lambda:exportMissingMeters())
b5.place(x=20, y=180)
b6 = ttk.Button(TAB1, text="6. Export Meter Type")
b6.place(x=20, y=220)
b7 = ttk.Button(TAB1, text="7. Check Malformed Lat/Long", command=lambda:checkMalformedLatLong())
b7.place(x=20, y=260)

consolelabel = ttk.Label(TAB1, text="Console:")
consolelabel.place(x=205, y=10)
textBox = tk.Text(TAB1, height=16, width=55, background='black', foreground='lawn green')
textBox.place(x=210, y=30)

#Tab2 Widgets
tab2label = ttk.Label(TAB2, text="Data Visualization")
tab2label.place(x=20, y=20)
tab2label2 = ttk.Label(TAB2, text="Select Data to Display:")
tab2label2.place(x=20, y=50)

tab2check1 = ttk.Checkbutton(TAB2, text="Customer")
tab2check1.place(x=30, y=80)
tab2check2 = ttk.Checkbutton(TAB2, text="Route")
tab2check2.place(x=30, y=100)
tab2check3 = ttk.Checkbutton(TAB2, text="Meter")
tab2check3.place(x=30, y=120)
tab2check4 = ttk.Checkbutton(TAB2, text="Radio Reads")
tab2check4.place(x=30, y=140)
tab2check4 = ttk.Checkbutton(TAB2, text="Placeholder")
tab2check4.place(x=30, y=160)
tab2check4 = ttk.Checkbutton(TAB2, text="Placeholder2")
tab2check4.place(x=30, y=180)
tab2check4 = ttk.Checkbutton(TAB2, text="Placeholder3")
tab2check4.place(x=30, y=200)

redrawbutton = ttk.Button(TAB2, text="Render", command=lambda:drawCanvas())
redrawbutton.place(x=30, y=230)

canvas = tk.Canvas(TAB2, width=440, height=250)
canvas.place(x= 210, y=30)

#Tab3 Widgets
tab3label = ttk.Label(TAB3, text="Import/Export data:")
tab3label.place(x=20, y=40)

tab3importinput = tk.Text(TAB3, width=40, height=1)
tab3importinput.place(x=20, y=65)
tab3importinput.insert(1.0, "C:\\Users\\Alex\\Desktop\\download.dat")
tab3importbutton = ttk.Button(TAB3, text="Import...")
tab3importbutton.place(x=350, y=60)

tab3exportinput= tk.Text(TAB3, width=40, height=1)
tab3exportinput.place(x=20, y=110)
tab3exportinput.insert(1.0, "C:\\Users\\Alex\\Desktop")
tab3exportbutton = ttk.Button(TAB3, text="Export... ")
tab3exportbutton.place(x=350, y=105)

tab3enforcebutton = ttk.Checkbutton(TAB3, text="Enfore referential integrity")
tab3enforcebutton.place(x=20, y=150)

# menu
menubar = tk.Menu(window)

filemenu = tk.Menu(menubar, tearoff=0)
filemenu.add_command(label="Open")
filemenu.add_command(label="Save")
filemenu.add_separator()
filemenu.add_command(label="Exit", underline=0, command=lambda:window.destroy())
menubar.add_cascade(label="File", menu=filemenu, underline=0)

# create more pulldown menus
editmenu = tk.Menu(menubar, tearoff=0)
editmenu.add_command(label="Cut")
editmenu.add_command(label="Copy", command=lambda:copy())
editmenu.add_command(label="Paste")
menubar.add_cascade(label="Edit", menu=editmenu, underline=0)

helpmenu = tk.Menu(menubar, tearoff=0)
helpmenu.add_command(label="About")
menubar.add_cascade(label="Help", menu=helpmenu, underline=0)

# display the menu
window.config(menu=menubar)


#Calling Main()
window.mainloop()





