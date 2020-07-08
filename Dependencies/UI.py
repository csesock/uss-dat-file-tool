import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog
import sys
import os

# intializing the window
window = tk.Tk()
window.title("USS dat File Tool v0.9")

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
        textBox.delete(1.0, "end")
        textBox.insert(1.0, "ERROR: FILE NOT FOUND")
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
        textBox.delete(1.0, "end")
        textBox.insert(1.0, "ERROR: FILE NOT FOUND.")

def printAllRecords():
    try:
        with open('download.dat', 'r') as openfile:
            counter = 1
            for line in openfile:
                textBox.insert(float(counter), line)
                counter+=1
    except FileNotFoundError:
        textBox.delete(1.0, "end")
        textBox.insert(1.0, "ERROR: FILE NOT FOUND.")
        
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
                    textBox.insert(1.0, "Office: \t" + str(office))
                    textBox.insert(2.0, "\n")
                    textBox.insert(2.0, "Region: \t" + str(region))
                    textBox.insert(3.0, "\n")
                    textBox.insert(3.0, "Zone: \t" + str(zone))
                    break
    except FileNotFoundError:
        textBox.delete(1.0, "end")
        textBox.insert(1.0, "ERROR: FILE NOT FOUND.")
        
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
        textBox.delete(1.0, "end")
        textBox.insert(1.0, "ERROR: FILE NOT FOUND.")

def exportMissingMeters():
    counter=0
    current_line=1
    total_line = getFileLineCount(working_file_name)
    try:
        with open('download.dat', 'r') as openfile:
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
                    if counter == 0:
                        builtfile.close()
                        os.remove(missing_meter_filename)
                        print()
                        print("No records found.")
                        print()
                        main()
            except FileExistsError:
                textBox.insert("end", "file already exists")
    except FileNotFoundError:
        textBox.delete(1.0, "end")
        textBox.insert(1.0, "ERROR: FILE NOT FOUND.")
    textBox.delete(1.0, "end")
    textBox.insert(1.0, "The operation was successful.")
    textBox.insert(2.0, "\n")


################################################

#Create Tab Control
TAB_CONTROL = ttk.Notebook(window)

#Tab1
TAB1 = ttk.Frame(TAB_CONTROL)
TAB_CONTROL.add(TAB1, text=' Operations ')

#Tab2
TAB2 = ttk.Frame(TAB_CONTROL)
TAB_CONTROL.add(TAB2, text=' Visualizations ')
TAB_CONTROL.pack(expand=1, fill="both")

#Tab3
TAB3 = ttk.Frame(TAB_CONTROL)
TAB_CONTROL.add(TAB3, text=" Import/Export ")
TAB_CONTROL.pack(expand=1, fill="both")

#Tab1 Widgets
b1 = tk.Button(TAB1, text="1. Single Record Scan", command=lambda:singleRecordScan())
b1.place(x=20, y=20)
b2 = tk.Button(TAB1, text="2. Verbose Record Scan", command=lambda:scanAllRecordsVerbose())
b2.place(x=20, y=60)
b3 = tk.Button(TAB1, text="3. Print Single Record", command=lambda:printSingleRecord())
b3.place(x=20, y=100)
b4 = tk.Button(TAB1, text="4. Print Office-Region-Zone", command=lambda:fixOfficeRegionZoneFields())
b4.place(x=20, y=140)
b5 = tk.Button(TAB1, text="5. Export Missing Meters")
b5.place(x=20, y=180)
b6 = tk.Button(TAB1, text="6. Export Meter Type")
b6.place(x=20, y=220)
b7 = tk.Button(TAB1, text="7. Check Malformed Lat/Long")
b7.place(x=20, y=260)

l = tk.Label(TAB1, text="Console:").place(x=205, y=10)
textBox = tk.Text(TAB1, height=16, width=55, background='black', foreground='lawn green')
textBox.place(x=210, y=30)

#Tab2 Widgets
tab2label = tk.Label(TAB2, text="Data Visualization")
tab2label.place(x=20, y=20)
tab2label2 = tk.Label(TAB2, text="Select Data to Display:")
tab2label2.place(x=20, y=50)

tab2check1 = tk.Checkbutton(TAB2, text="Customer")
tab2check1.place(x=30, y=80)
tab2check2 = tk.Checkbutton(TAB2, text="Route")
tab2check2.place(x=30, y=100)
tab2check3 = tk.Checkbutton(TAB2, text="Meter")
tab2check3.place(x=30, y=120)
tab2check4 = tk.Checkbutton(TAB2, text="Radio Reads")
tab2check4.place(x=30, y=140)

canvas = tk.Canvas(TAB2, width=200, height=200)
canvas.place(x= 250, y=30)
canvas.create_line(0, 0, 200, 100)
canvas.create_line(0, 100, 200, 0)

#Tab3 Widgets
tab3label = tk.Label(TAB3, text="Import/Export data:")
tab3label.place(x=20, y=20)
tab3importbutton = tk.Button(TAB3, text="Import Data...")
tab3importbutton.place(x=20, y=50)
tab3exportbutton = tk.Button(TAB3, text="Export Data...")
tab3exportbutton.place(x=110, y=50)

# menu
menubar = tk.Menu(window)

filemenu = tk.Menu(menubar, tearoff=0)
filemenu.add_command(label="Open")
filemenu.add_command(label="Save")
filemenu.add_separator()
filemenu.add_command(label="Exit", underline=0, command=lambda:window.destroy())
menubar.add_cascade(label="File", menu=filemenu)

# create more pulldown menus
editmenu = tk.Menu(menubar, tearoff=0)
editmenu.add_command(label="Cut")
editmenu.add_command(label="Copy")
editmenu.add_command(label="Paste")
menubar.add_cascade(label="Edit", menu=editmenu)

helpmenu = tk.Menu(menubar, tearoff=0)
helpmenu.add_command(label="About")
menubar.add_cascade(label="Help", menu=helpmenu)

# display the menu
window.config(menu=menubar)
#Calling Main()
window.mainloop()





