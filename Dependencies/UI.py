import tkinter as tk
from tkinter import ttk

# intializing the window
window = tk.Tk()
window.title("USS dat File Tool v0.9")

# configuring size of the window 
window.geometry('700x350')

def printSingleRecord():
    counter = 0
    record_type = 'RHD'
    try:
        with open('download.dat', 'r') as openfile:
            for line in openfile:
                if record_type in line or record_type.lower() in line:
                    counter+=1
                    textBox.delete(1.0, "end")
                    textBox.insert(1.0, line + "\n")
    except FileNotFoundError:
        print("fnf")

def printAllRecords():
    try:
        with open('download.dat', 'r') as openfile:
            counter = 1
            for line in openfile:
                #print("{0}) {1}".format(counter, line))
                textBox.insert(float(counter), line)
                counter+=1
    except FileNotFoundError:
        print("fnf")

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
                    print("-------------------------")
                    print("Office: \t", str(office))
                    print("Region: \t", str(region))
                    print("Zone: \t\t", str(zone))
                    print("-------------------------")
                    textBox.insert(counter, "Office: \t", str(office) + "\n")
                    textBox.insert(counter, "Region: \t", str(region) + "\n")
                    textBox.insert(counter, "Zone: \t", str(zone) + "\n")
                    break
    except FileNotFoundError:
        print("fnf")

#Create Tab Control
TAB_CONTROL = ttk.Notebook(window)

#Tab1
TAB1 = ttk.Frame(TAB_CONTROL)
TAB_CONTROL.add(TAB1, text='File Operations')

#Tab2
TAB2 = ttk.Frame(TAB_CONTROL)
TAB_CONTROL.add(TAB2, text='Visualizations')
TAB_CONTROL.pack(expand=1, fill="both")

#Tab Name Labels
b1 = tk.Button(TAB1, text="1. Single Record Scan")
b1.place(x=20, y=20)
b2 = tk.Button(TAB1, text="2. Verbose Record Scan")
b2.place(x=20, y=60)
b3 = tk.Button(TAB1, text="3. Print Single Record", command=lambda:printAllRecords())
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
textBox = tk.Text(TAB1, height=16, width=55, background='black', foreground='green')
textBox.place(x=210, y=30)

ttk.Label(TAB2, text="This is Tab 2").grid(column=0, row=0, padx=10, pady=10)

#Calling Main()
window.mainloop()





