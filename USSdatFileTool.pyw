import tkinter as tk 
from tkinter import *
from tkinter import messagebox, simpledialog, ttk
import tkinter.scrolledtext as tkscrolled
from tkinter.filedialog import asksaveasfile
from tkinter.font import Font

from collections import deque #to efficiently store data stream
from datetime import datetime #for writing timestamped files
import sys, os, re, time, csv, shutil #default library utilities

extension_path = os.getcwd().replace('\\', '/')+'/extensions'
sys.path.append(extension_path)

#internal tool extensions
#found in /extensions/...
try:
    import extensions.Logging as Logging #logging system
    import extensions.AdjustReadings as AdjustReadings #manually adjust readings
except:
    print("import failure")
    pass

#regular expressions for pattern matching
pattern_missing_meters = re.compile(r'[^\S\n\t]{11}')
pattern_lat_long = re.compile(r'-?[0-9]{2}\.\d{1,13}$')
pattern_lat_long2 = re.compile(r'(-?[0-9]{2})(\.)([0-9]{1,13})') #improved lat/long regular expression with grouping
pattern_space_nonewline = re.compile(r'\t|[ ]{2,}')

#file configurations
download_filename = 'download.dat'
ELF_filename = "Generated ELF File " + datetime.today().strftime('%Y-%m-%d_%H-%M') + '.csv' #endpoint location file naming scheme
defaut_file_extension = '.txt'
window = tk.Tk()
s = ttk.Style()
s.theme_use('clam') #default UI style 

#default UI sizes
DEFAULT_FONT_SIZE = 10
CONSOLE_WIDTH = 76
#CONSOLE_WIDTH = 126
CONSOLE_HEIGHT = 15
BUTTON_WIDTH = 22

#default tkk configuration
consoleFont = Font(family="Consolas", size=DEFAULT_FONT_SIZE)
labelFont = Font(size=10, weight='bold')
window.title("United Systems .dat File Tool")
window.resizable(False, False)
height = window.winfo_screenheight()/3
width = window.winfo_screenwidth()/3
window.geometry('790x350+%d+%d' %(width, height))

#build window icons
try:
    dirp = os.path.dirname(__file__)
    photo = PhotoImage(file="assets\\IconSmall.png")
    photo2 = PhotoImage(file="assets\\SmartCity.png")
    window.iconphoto(False, photo)
except:
    pass

#menu bindings
window.bind('<Control-o>', lambda event: openFile())
window.bind('<Control-s>', lambda event: save())
window.bind('<Control-Alt-s>', lambda event: saveAs())
window.bind('<Control-x>', lambda event: clearConsole(TAB_CONTROL.index(TAB_CONTROL.select())+1))
window.bind('<F1>', lambda event: aboutDialog())
window.bind('<F10>', lambda event: resetWindow())
window.bind('<F11>', lambda event: fullscreenWindow())

###################
##File Functions###
###################

#search through the current file, find any characters that FCS does not allow
#list of disallowed characters can be found in HDL guide provided by Itron
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
                bocConsole.insert(1.0, 'No disallowed characters found in ['+os.path.basename(download_filename)+']')
                bocConsole.insert('end', '\n')
                bocConsole.insert('end', "Disallowed characters include: * < > \\ / \"")
        Logging.writeToLogs('End Function Call - disallowedCharacters()')
    except FileNotFoundError:
        fileNotFoundError(1)

#dynamic record searching by parsing with regex
#default is to parse entire file if no input 
def searchRecords(event=None):
    Logging.writeToLogs('Start Function Call - searchRecords()')
    records = []
    record_type = simpledialog.askstring("Record Search", '    Enter the record types to search \n\n (Separate record types by comma) \n               (ex. cus, mtr, rff)  \n\n You can also enter ERT to print all ERTs', parent=window)
    if record_type is None:
        return
    record_type = record_type.upper()
    if 'ERT' in record_type:
        ERTsummary()
        return
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
        fileNotFoundError(1)
        
#find office region zone instance in file
#region, zone, office in that order
def officeRegionZone(event=None):
    Logging.writeToLogs('Start Function Call - officeRegionZone()')
    try:
        with open(download_filename, 'r') as openfile:
            for line in openfile:
                if line.startswith('RHD'):
                    region = line[71:73]
                    if region == "  ":
                        region = "BLANK"
                    zone = line[73:75]
                    if zone == "  ":
                        zone = "BLANK"
                    office = line[75:77]
                    if office == "  ":
                        office = "BLANK"
                    bocConsole.delete(1.0, "end")
                    bocConsole.insert(1.0, "Region-Zone-Office Fields")
                    bocConsole.insert(2.0, "\n")
                    bocConsole.insert(2.0, "------------------------")
                    bocConsole.insert(3.0, "\n")
                    bocConsole.insert(3.0, "Region . . . . : \t" + str(region))
                    bocConsole.insert(4.0, "\n")
                    bocConsole.insert(4.0, "Zone . . . . . : \t" + str(zone))
                    bocConsole.insert(5.0, "\n")
                    bocConsole.insert(5.0, "Office . . . . : \t" + str(office))
                    bocConsole.insert(6.0, "\n")
                    bocConsole.insert(6.0, "------------------------")
                    return
                if line.startswith('ERH'): #accounts for Extended Route Header record
                    region = line[83:85]
                    if region == "  ":
                        region = "BLANK"
                    zone = line[85:87]
                    if zone == "  ":
                        zone = "BLANK"
                    office = line[87:89]
                    if office == "  ":
                        office = "BLANK"
                    bocConsole.delete(1.0, "end")
                    bocConsole.insert(1.0, "Region-Zone-Office Fields")
                    bocConsole.insert(2.0, "\n")
                    bocConsole.insert(2.0, "------------------------")
                    bocConsole.insert(3.0, "\n")
                    bocConsole.insert(3.0, "Region . . . . : \t" + str(region))
                    bocConsole.insert(4.0, "\n")
                    bocConsole.insert(4.0, "Zone . . . . . : \t" + str(zone))
                    bocConsole.insert(5.0, "\n")
                    bocConsole.insert(5.0, "Office . . . . : \t" + str(office))
                    bocConsole.insert(6.0, "\n")
                    bocConsole.insert(6.0, "------------------------")
                    return
        Logging.writeToLogs('End Function Call - officeRegionZone()')
    except FileNotFoundError:
        fileNotFoundError(1)
        
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
        fileNotFoundError(1)

#search for missing meter numbers in MTR record
def missingMeters(event=None):
    Logging.writeToLogs('Start Function Call - missingMeters()')
    meters = []
    counter, line_number = 0, 1
    try:
        with open(download_filename, 'r') as openfile:
            previous_line = ''
            bocConsole.delete(1.0, "end")
            for line in openfile:
                        if line.startswith('MTR'):
                            meter_record = line[45:57] #46-57
                            meters.append(meter_record)
                            if pattern_missing_meters.match(meter_record):
                                bocConsole.insert("end", str(line_number) + " " + previous_line)    #inserts customer name
                                bocConsole.insert("end", str(line_number) + " " + line+"\n")        #inserts meter number
                                counter+=1
                        previous_line=line
                        line_number +=1
            #exportMeters(meters) #helper function call -- turned off by default
            if counter == 0:
                bocConsole.delete(1.0, "end")
                bocConsole.insert(1.0, "No missing meters found in ["+os.path.basename(download_filename)+"]")
                return
            elif counter > 0:
                answer = messagebox.askokcancel("Confirmation", "There were "+str(counter)+" blank meters found.\nCreate new download file with temp data?")
                if answer == None or answer == False:
                    return 
                populateMissingMeters(False)
        Logging.writeToLogs('End Function Call - missingMeters()')
    except FileNotFoundError:
        fileNotFoundError(1)

#helper function for writing stored meter numbers to a text file in root directory
def exportMeters(meters):
    Logging.writeToLogs('Start Function Call - exportMeters()')
    with open('builtfile.txt', 'w') as builtfile:
        for meter in meters:
            builtfile.write(meter+'\n')
    Logging.writeToLogs('End Function Call - exportMeters()')

#find and print read type codes to console
def printReadTypeVerbose(event=None):
    Logging.writeToLogs("Start Function Call - printReadTypeVerbose()")
    all_reads = {}
    p1 = p2 = p3 = ''
    counter = 1.0
    try:
        with open(download_filename, 'r') as openfile:
            for line in openfile:
                if line.startswith('MTR'):
                    commodity = line[101:102]
                if line.startswith('RDG'):
                    read_type_code = line[76:78]
                    x = str(commodity) + " " + str(read_type_code)
                    if x not in all_reads:
                        all_reads[x] = 1
                    else:
                        all_reads[x]+=1
                p3 = p2
                p2 = p1
                p1 = line 
            bocConsole.delete(counter, "end")
            bocConsole.insert(counter, "Commodity | Read Type Codes")
            counter+=1
            bocConsole.insert(counter, "\n")
            bocConsole.insert(counter, "-----------------------------")
            counter+=1
            bocConsole.insert(counter, "\n")
            for record in all_reads:
                bocConsole.insert(counter, str(record) + " . . . :\t" + f"{all_reads[record]:,d} ")
                counter+=1
                bocConsole.insert(counter, "\n")
            bocConsole.insert(counter, "-----------------------------")
        Logging.writeToLogs("End Function Call - printReadTypeVerbose()")
    except FileNotFoundError:
        fileNotFoundError(1)

#find and print current read direction for routes
def getReadDirections(event=None):
    Logging.writeToLogs('Start Function Call - getReadDirections()')
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
            bocConsole.insert(2.0, "-----------------------\n")
            for fart in cc:
                bocConsole.insert(counter, str(fart)+"\t. . . :\t"+str(cc[fart])+"\n")
                counter+=1.0
            bocConsole.insert(counter, "-----------------------")
        Logging.writeToLogs('End Function Call - getReadDirections()')
    except FileNotFoundError:
        fileNotFoundError(1)

def getHighLowValues(event=None):
    Logging.writeToLogs('Start Function Call - getHighLowValues()')
    highs, lows, counter = {}, {}, 3.0
    try:
        with open(download_filename, 'r') as openfile:
            for line in openfile:
                if line.startswith('RDG'):
                    high_val = line[41:51]
                    low_val = line[51:61]
                    #build data structure of highs
                    if high_val not in highs:
                        highs[high_val] = 1
                    else:
                        highs[high_val]+=1
                    #build data structures of lows
                    if low_val not in lows:
                        lows[low_val] = 1
                    else:
                        lows[low_val]+=1
            bocConsole.delete(1.0, "end")
            bocConsole.insert(2.0, "High Values\n")
            for x in highs:
                bocConsole.insert(str(counter), str(x)+"\t. . . :\t"+str(highs[x])+"\n")
                counter+=1
            print(highs, lows)
        Logging.writeToLogs('End Function Call - getHighLowValues()')
    except FileNotFoundError:
        fileNotFoundError(1)
                    
##########################
# Lat/Long tab functions #
##########################

#find malformed lat/long using regex
def checkMalformedLatLong(event=None):
    Logging.writeToLogs("Start Function Call - checkMalformedLatLong()")
    line_number = 1
    malformed = []
    try:
        with open(download_filename, 'r') as openfile:
            for line in openfile:
                if line.startswith('MTX'):
                    lat_data = line[23:40].rstrip()
                    long_data = line[40:57].rstrip()
                    if not pattern_lat_long2.match(lat_data) or not pattern_lat_long2.match(long_data):
                        latLongConsole.delete(1.0, "end")
                        latLongConsole.insert(1.0, "Malformed lat/long data at line: " + str(line_number))
                        latLongConsole.insert(2.0, "\n")
                        latLongConsole.insert(2.0, "Line: " + line)
                        malformed.append(line)
                line_number+=1
            latLongConsole.delete(1.0, "end")
            counter = 1.0
            for i in malformed:
                latLongConsole.insert(counter, i+'\n')
                counter+=1.0
            if counter == 1.0:
                latLongConsole.insert(1.0, "No malformation within lat/long data detected.")
        Logging.writeToLogs("End Function Call - checkMalformedLatLong()")
    except FileNotFoundError:
        fileNotFoundError(3)

#finds and prints all lat/long records to console 
def printAllLatLongData(event=None):
    counter, total_latlong, line_number = 1.0, 0, 1
    try:
        with open(download_filename, 'r') as openfile:
            latLongConsole.delete(1.0, "end")
            latLongConsole.insert(counter, "All Lat/Long Records"+"\n")
            counter+=1
            latLongConsole.insert(counter, "Line"+"\t"+"Latitude"+"\t\t"+"Longitude"+"\n")
            counter+=1
            latLongConsole.insert(counter, "---------------------------------------"+"\n")
            counter+=1
            for line in openfile:
                if line.startswith('MTX'):
                    lat_data = line[23:40].rstrip()
                    long_data = line[40:57].rstrip()
                    latLongConsole.insert(counter, str(line_number)+"\t"+lat_data+"\t\t"+long_data+'\n')
                    total_latlong+=1
                counter+=1
                line_number+=1
            if total_latlong == 0:
                latLongConsole.delete(1.0, "end")
                latLongConsole.insert(1.0, "There was no lat/long data found.")
    except FileNotFoundError:
        fileNotFoundError(3)

def checkRegion(event=None):
    counter, total_latlong = 4.0, 0
    try:
        with open(download_filename, 'r') as openfile:
            latLongConsole.delete(1.0, "end")
            latLongConsole.insert(1.0, "Lat/Long Regions"+"\n")
            latLongConsole.insert(2.0, "Latitude"+"\t\t"+"Longitude"+"\t\t"+"Is Valid"+"\n")
            latLongConsole.insert(3.0, "----------------------------------------"+"\n")
            isValid = 'Beans'
            for line in openfile:
                if line.startswith('MTX'):
                    lat_data = line[23:40].rstrip()
                    long_data = line[40:57].rstrip()
                    isValid = validRegion(lat_data, long_data)
                    latLongConsole.insert(counter, lat_data+"\t\t"+long_data+"\t\t"+isValid+"\n")
                    total_latlong+=1
                counter+=1
            if total_latlong == 0:
                latLongConsole.delete(1.0, "end")
                latLongConsole.insert(1.0, "There was no lat/long data found.")
    except FileNotFoundError:
        fileNotFoundError(3)

#simply returns a boolean value corresponding to the validity of the lat/long region
def validRegion(lat, long):
    region = 'Valid'
    long = float(long)
    lat = float(lat)
    if long < -96.8 or long > -75.8:
        region = 'Invalid'
    elif lat > 49 or lat < 29:
        region = 'Invalid'
    return region 

#############################
# ELF Creator tab functions #
#############################

#creates endpoint location file in /exports
def createELFfile(event=None):
    answer = messagebox.askokcancel("Confirmation", "All possible fields will be formatted into an ELF file.\nRFF records must exist and must match a customer record.")
    if answer == None or answer == False:
        return 
    try:
        with open(download_filename, 'r') as openfile:
            with open("exports\\"+ELF_filename, 'w') as builtfile:
                builtfile.write('Endpoint ID, Street Address, City, State, Country, Zip, Latitude, Longitude, GeopointSource, Market\n')
                address = ""
                ert = ""
                for line in openfile:
                    if line.startswith('CUS'):
                        address = line[54:94]
                    if line.startswith('RFF'):
                        ert = line[11:21]
                        elfline = ert + ',' + address + ',' + inputCity.get() + ',' + inputState.get() + ',' + inputCountry.get() + ',' + inputZip.get() + ',' + '0,0' + ',' + inputGeopointSource.get() + ',' + inputMarket.get() + ',' + '\n'
                        builtfile.write(elfline)
        messagebox.showinfo("Success", "ELF file successfully created in the \\exports folder.")
    except FileNotFoundError:
        fileNotFoundError(4)

def ERTsummary(event=None):
    lengths = {}
    try:
        with open(download_filename, 'r') as openfile:
            counter = 3.0
            for line in openfile:
                if line.startswith('RFF'):
                    ert = line[11:21].strip() #max possible length of ERT
                    length = len(ert)
                    if length not in lengths:
                        lengths[length]=1
                    else:
                        lengths[length]+=1
            bocConsole.delete(1.0, "end")
            bocConsole.insert(1.0, "ERT Summary\n")
            bocConsole.insert(2.0, "-----------------\n")
            for l in lengths:
                bocConsole.insert(counter, str(l)+". . . :\t"+str(lengths[l])+"\n")
                counter+=1.0
            bocConsole.insert(counter, "-----------------\n")
            printERTs(counter+1)
    except FileNotFoundError:
        fileNotFoundError(1)

#finds all instances of ERT serial numbers and prints them to the console
def printERTs(counter, event=None):
    try:
        with open(download_filename, 'r') as openfile:
            for line in openfile:
                if line.startswith('RFF'):
                    ert = line[11:21]
                    bocConsole.insert(counter, ert)
                    bocConsole.insert('end', '\n')
                    counter+=1.0
    except:
        fileNotFoundError(1)

def getNumCustomers():
    num = 0
    try:
        with open(download_filename, 'r') as openfile:
            for line in openfile:
                if line.startswith('CUS'):
                    num+=1
                else:
                    continue
        return num 
    except FileNotFoundError:
        FileNotFoundError(2)

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
        fileNotFoundError(1)       


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
             ('Rich Text Files', '*.rtf'),
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

def populateMissingMeters(warn, event=None):
    if warn == True:
        answer = messagebox.askokcancel("Confirmation", "A new download file will be created\n with populated meter records.")
        if answer == None or answer == False:
            return 
    try:
        with open(download_filename, 'r') as openfile:
            with open('exports\\download--populated meters.dat', 'w') as builtfile:
                for line in openfile:
                    if line.startswith('MTR'):
                        meter_record = line[45:57]
                        if pattern_missing_meters.match(meter_record):
                            line = str(line[0:49]) + "11111" + str(line[54::]) #concatenate a new line with populated record
                    builtfile.write(line)
            messagebox.showinfo("Success", "Download file successfully created in the \\exports folder.")
    except FileExistsError:
        messagebox.showinfo("Error", "A populated download file already exists in the directory")
    except FileNotFoundError:
        fileNotFoundError(2)

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
       
def backupDownloadFilef():
    if download_filename != 'download.dat':
            shutil.copy(download_filename, os.getcwd())
            return
    filename = tk.filedialog.askopenfilename(title="Choose File to Backup")
    shutil.copy(filename, os.getcwd())

def fullscreenWindow():
    width = window.winfo_screenwidth()
    height = window.winfo_screenheight()
    window.geometry('%dx%d+0+0' %(width, height))

def resetWindow():
    height = window.winfo_screenheight()/3
    width = window.winfo_screenwidth()/3
    window.geometry('780x330+%d+%d' %(width, height)) #reset height must be height-20 to account for the menu being created at this point

def changeTheme(theme):
    s = ttk.Style()
    s.theme_use(theme)

def clearConsole(tab):
    if tab==1:
        bocConsole.delete(1.0, "end")
    elif tab==3:
        latLongConsole.delete(1.0, "end")
    elif tab==4:
        ELFConsole.delete(1.0, "end")
    else:
        return 

def resetELF(event=None):
    inputCity.delete(0, "end")
    inputState.delete(0, "end")
    inputCountry.delete(0, "end")
    inputZip.delete(0, "end")
    inputGeopointSource.delete(0, "end")
    inputMarket.delete(0, "end")

def fileNotFoundError(tab):
    if tab==1:
        bocConsole.delete(1.0, "end")
        bocConsole.insert(1.0, "ERROR: FILE NOT FOUND")
    elif tab==3:
        latLongConsole.delete(1.0, "end")
        latLongConsole.insert(1.0, "ERROR: FILE NOT FOUND")
    elif tab==4:
        ELFConsole.delete(1.0, "end")
        ELFConsole.insert(1.0, "ERROR: FILE NOT FOUND")
    else:
        return

def adjustReadingsPopup(download_filename):
    AdjustReadings.adjustReadingsPopup(download_filename)

def aboutDialog():
    dialog = """ Author: Chris Sesock \n Version: 1.8.1 \n Commit: 02cf7a47a05c00db8883f650998e72d60527168d \n Date: 2021-06-02:09:21:00 \n Python: 3.8.5 \n OS: Windows_NT x64 10.0.18363.1379
             """
    messagebox.showinfo("About", dialog)

def on_closing():
    #if messagebox.askokcancel("Quit", "Do you want to quit?"):
    Logging.writeToLogs("Program successfully closed")
    window.destroy()

# Create Tab Control
TAB_CONTROL = ttk.Notebook(window)
# Basic Operations tab
tabBasicOperations = ttk.Frame(TAB_CONTROL)
TAB_CONTROL.add(tabBasicOperations, text='Basic Tools')
# Lat/long tab
tabLatLong = ttk.Frame(TAB_CONTROL)
TAB_CONTROL.add(tabLatLong, text="Lat/Long Tools")
TAB_CONTROL.pack(expand=1, fill="both")
# File Operations tab
tabELFcreation = ttk.Frame(TAB_CONTROL)
TAB_CONTROL.add(tabELFcreation, text="ELF Creator")
TAB_CONTROL.pack(expand=1, fill="both")
# Settings tab
tabDeveloper = ttk.Frame(TAB_CONTROL)
TAB_CONTROL.add(tabDeveloper, text="Settings")
TAB_CONTROL.pack(expand=1, fill="both")

###################
# BOC Tab Widgets #
###################

btnNumkey1 = ttk.Button(tabBasicOperations, text="1.", width=1.5, command=lambda:searchRecords()).place(x=20, y=20)
btnVerboseRecordScan = ttk.Button(tabBasicOperations, text="Record Search...", command=lambda:searchRecords(), width=BUTTON_WIDTH).place(x=50, y=20)

btnNumkey2 = ttk.Button(tabBasicOperations, text="2.", width=1.5, command=lambda:scanAllRecordsVerbose()).place(x=20, y=58)
btnsearchRecords = ttk.Button(tabBasicOperations, text="Record Counts", command=lambda:scanAllRecordsVerbose(), width=BUTTON_WIDTH).place(x=50, y=58)

btnNumkey3 = ttk.Button(tabBasicOperations, text="3.", width=1.5, command=lambda:disallowedCharacters()).place(x=20, y=96)
btnSingleRecordScan = ttk.Button(tabBasicOperations, text="Bad Meter Characters", command=lambda:disallowedCharacters(), width=BUTTON_WIDTH).place(x=50, y=96)

btnNumkey4 = ttk.Button(tabBasicOperations, text="4.", width=1.5, command=lambda:missingMeters()).place(x=20, y=134)
btnOfficeRegionZone = ttk.Button(tabBasicOperations, text="Blank Meter Numbers", command=lambda:missingMeters(), width=BUTTON_WIDTH).place(x=50, y=134)

btnNumkey5 = ttk.Button(tabBasicOperations, text="5.", width=1.5, command=lambda:officeRegionZone()).place(x=20, y=172)
MissingMeterButton = ttk.Button(tabBasicOperations, text="Region-Zone-Office", command=lambda:officeRegionZone(), width=BUTTON_WIDTH).place(x=50, y=172)

btnNumkey6 = ttk.Button(tabBasicOperations, text="6.", width=1.5, command=lambda:printReadTypeVerbose()).place(x=20, y=210)
PrintReadTypeButton = ttk.Button(tabBasicOperations, text="Read Type Codes", command=lambda:printReadTypeVerbose(), width=BUTTON_WIDTH).place(x=50, y=210)

btnReadDirectionNumkey4 = ttk.Button(tabBasicOperations, text="7.", width=1.5, command=lambda:getReadDirections()).place(x=20, y=248)
btnReadDirection = ttk.Button(tabBasicOperations, text="Read Direction", width=BUTTON_WIDTH, command=lambda:getReadDirections()).place(x=50, y=248)

text = tk.StringVar()
if os.path.isfile('download.dat'):
    text.set('download.dat')
else:
    text.set('None')

labelCurrentTab1 = ttk.Label(tabBasicOperations, text="Current file: ").place(x=220, y=20)
labelFileTab1 = ttk.Label(tabBasicOperations, textvariable=text, foreground='#3baf29').place(x=287, y=20)

btnConsoleSave = ttk.Button(tabBasicOperations, text="save", width=4.25, command=lambda:save()).place(x=673, y=6)
btnConsoleClear = ttk.Button(tabBasicOperations, text="clear", width=4.25, command=lambda:clearConsole(1)).place(x=717, y=6)

bocConsole = tkscrolled.ScrolledText(tabBasicOperations, height=CONSOLE_HEIGHT, width=CONSOLE_WIDTH, background='black', foreground='white', 
                    insertborderwidth=7, undo=True, bd=3)
bocConsole.place(x=220, y=42)
bocConsole.configure(font=consoleFont)
bocConsole.insert(1.0, "United Systems dat File Tool [Version 1.8.1]")
bocConsole.insert(2.0, "\n")
bocConsole.insert(2.0, "(c) 2021 United Systems and Software, Inc.")
bocConsole.insert(3.0, "\n")

text2 = tk.StringVar()
text2.set('Ln : 0 Col : 0')
labelFooter = ttk.Label(tabBasicOperations, textvariable=text2).place(x=220, y=278)

text3 = tk.StringVar()
text3.set('Ln : 0 Col : 0')

text4 = tk.StringVar()
text4.set('Ln : 0 Col : 0')

def check_pos(event):
    if TAB_CONTROL.index(TAB_CONTROL.select()) == 0:
        footer1 = "Ln : " + bocConsole.index(tk.INSERT).split('.')[0]
        footer2 = " Col : " + bocConsole.index(tk.INSERT).split('.')[1]
        text2.set(footer1+footer2)
    elif TAB_CONTROL.index(TAB_CONTROL.select()) == 1:
        text3.set("Ln : " + latLongConsole.index(tk.INSERT).split('.')[0] + " Col : " + latLongConsole.index(tk.INSERT).split('.')[1])
    else:
        text4.set("Ln : " + ELFConsole.index(tk.INSERT).split('.')[0] + " Col : " + ELFConsole.index(tk.INSERT).split('.')[1])
    
bocConsole.bindtags(('Text', 'post-class-bindings', '.', 'all'))
bocConsole.bind_class("post-class-bindings", "<KeyPress>", check_pos)
bocConsole.bind_class("post-class-bindings", "<Button-1>", check_pos)

#######################
# Lat/Long Tab Widgets#
#######################

labelCurrentTab3 = ttk.Label(tabLatLong, text="Current file: ").place(x=220, y=20)
labelFileTab3 = ttk.Label(tabLatLong, textvariable=text, foreground='#3baf29').place(x=287, y=20)

btnNumkeyLat3 = ttk.Button(tabLatLong, text="1.", width=1.5, command=lambda:checkMalformedLatLong()).place(x=20, y=35)
btnLatMalformed = ttk.Button(tabLatLong, text="Malformed Lat/Long", width=BUTTON_WIDTH, command=lambda:checkMalformedLatLong()).place(x=50, y=35)

btnNumkeyLat4 = ttk.Button(tabLatLong, text="2.", width=1.5, command=lambda:printAllLatLongData()).place(x=20, y=76)
btnLatAllMalformed = ttk.Button(tabLatLong, text="All Lat/Long", width=BUTTON_WIDTH, command=lambda:printAllLatLongData()).place(x=50, y=76)

btnNumKeyLat5 = ttk.Button(tabLatLong, text="3.", width=1.5, command=lambda:checkRegion()).place(x=20, y=160)
btnCheckRegion = ttk.Button(tabLatLong, text="Check Region", width=BUTTON_WIDTH, command=lambda:checkRegion()).place(x=50, y=160)

labelRegion = ttk.Label(tabLatLong, text="Region:").place(x=22, y=200)
dropdownRegion = ttk.Combobox(tabLatLong, width=26, values = ["Central US", "Eastern US", "Western US"])
dropdownRegion.place(x=22, y=200)
dropdownRegion.state(['readonly'])
dropdownRegion.set("Central US (default)")

latLongConsole = tkscrolled.ScrolledText(tabLatLong, height=CONSOLE_HEIGHT, width=CONSOLE_WIDTH, background='black', foreground='white',
                        insertborderwidth=7, undo=True, bd=3)
latLongConsole.place(x=220, y=42)
latLongConsole.configure(font=consoleFont)
latLongConsole.insert(1.0, "United Systems dat File Tool [Version 1.8.1]")
latLongConsole.insert(2.0, "\n")
latLongConsole.insert(2.0, "(c) 2021 United Systems and Software, Inc.")
latLongConsole.insert(3.0, "\n")

latLongConsole.bindtags(('Text', 'post-class-bindings', '.', 'all'))
latLongConsole.bind_class("post-class-bindings", "<KeyPress>", check_pos)
latLongConsole.bind_class("post-class-bindings", "<Button-1>", check_pos)

labelFooter3 = ttk.Label(tabLatLong, textvariable=text3).place(x=220, y=278)

btnConsoleSave = ttk.Button(tabLatLong, text="save", width=4.25, command=lambda:save()).place(x=673, y=6)
btnLatConsoleClear = ttk.Button(tabLatLong, text="clear", width=4.25, command=lambda:clearConsole(3)).place(x=717, y=6)

########################
##  ELF Tab Widgets ####
########################

btnCreateELFfile = ttk.Button(tabELFcreation, text="Create ELF", width=11, command=lambda:createELFfile()).place(x=21, y=180)
btnReset = ttk.Button(tabELFcreation, text="Clear", width=11, command=lambda:resetELF()).place(x=110, y=180)

labelAutoPopulate = ttk.Label(tabELFcreation, text="Fields to auto-populate", font=labelFont).place(x=20, y=15)

labelCity = ttk.Label(tabELFcreation, text="City").place(x=20, y=40)
inputCity = ttk.Entry(tabELFcreation, width=12)
inputCity.place(x=115, y=40)
inputCity.insert(0, "Benton")

labelState = ttk.Label(tabELFcreation, text="State").place(x=20, y=62)
inputState = ttk.Entry(tabELFcreation, width=12)
inputState.place(x=115, y=62)
inputState.insert(0, "KY")

labelCountry = ttk.Label(tabELFcreation, text="Country").place(x=20, y=84)
inputCountry = ttk.Entry(tabELFcreation, width=12)
inputCountry.place(x=115, y=84)
inputCountry.insert(0, "USA")

labelZip = ttk.Label(tabELFcreation, text="Zip Code").place(x=20, y=106)
inputZip = ttk.Entry(tabELFcreation, width=12)
inputZip.place(x=115,y=106)
inputZip.insert(0, "42025")

labelGeoPointSource = ttk.Label(tabELFcreation, text="GeopointSource").place(x=20, y=128)
inputGeopointSource = ttk.Entry(tabELFcreation, width=12)
inputGeopointSource.place(x=115, y=128)
inputGeopointSource.insert(0, "CIS")

labelMarket = ttk.Label(tabELFcreation, text="Market").place(x=20, y=150)
inputMarket = ttk.Entry(tabELFcreation, width=12)
inputMarket.place(x=115, y=150)
inputMarket.insert(0, "W")

#default console widgets
labelCurrenTab4 = ttk.Label(tabELFcreation, text="Current file: ").place(x=220, y=20)
labelFileTab4 = ttk.Label(tabELFcreation, textvariable=text, foreground='#3baf29').place(x=287, y=20)
labelFooter4 = ttk.Label(tabELFcreation, textvariable=text4, foreground='black').place(x=220, y=278)

btnELFsave = ttk.Button(tabELFcreation, text="save", width=4.25, command=lambda:save()).place(x=673, y=6)
btnELFclear = ttk.Button(tabELFcreation, text="clear", width=4.25, command=lambda:clearConsole(4)).place(x=717, y=6)

ELFConsole = tkscrolled.ScrolledText(tabELFcreation, height=CONSOLE_HEIGHT, width=CONSOLE_WIDTH, background='black', foreground='white', 
                    insertborderwidth=7, undo=True, bd=3)
ELFConsole.place(x=220, y=42)
ELFConsole.configure(font=consoleFont)
ELFConsole.insert(1.0, "United Systems dat File Tool [Version 1.8.1]")
ELFConsole.insert(2.0, "\n")
ELFConsole.insert(2.0, "(c) 2021 United Systems and Software, Inc.")
ELFConsole.insert(3.0, "\n")

ELFConsole.bindtags(('Text', 'post-class-bindings', '.', 'all'))
ELFConsole.bind_class("post-class-bindings", "<KeyPress>", check_pos)
ELFConsole.bind_class("post-class-bindings", "<Button-1>", check_pos)

########################
# Settings Tab Widgets #
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

checkAutoExportExcel = ttk.Checkbutton(tabDeveloper, text="Automatically export customer report")
checkAutoExportExcel.place(x=20, y=122)

# image
label=ttk.Label(tabDeveloper, image=photo2)
label.image = photo2
label.place(x=310, y=60)

# log settings
loglabel = ttk.Label(tabDeveloper, text="Log Settings", font=labelFont).place(x=300, y=30)

labelDelete = ttk.Label(tabDeveloper, text="• Log files allowed before deletion:").place(x=300, y=53)
logDeleteOldInput = ttk.Entry(tabDeveloper, width=4)
logDeleteOldInput.place(x=490, y=53)
logDeleteOldInput.insert(0, '10')

logverbose = ttk.Checkbutton(tabDeveloper, text="Log all function calls")
logverbose.place(x=300, y=75)
logverbose.state(['selected'])

logwarning = ttk.Checkbutton(tabDeveloper, text="Warning before purging logs")
logwarning.place(x=300, y=97)

########
# Menu #
########

menubar = tk.Menu(window)

filemenu = tk.Menu(menubar, tearoff=0)
filemenu.add_command(label="Open...", accelerator='Ctrl+O', command=lambda:openFile())
filemenu.add_command(label="Save", accelerator='Ctrl+S', command=lambda:save())
filemenu.add_command(label="Save As...", accelerator='Ctrl+Alt+S', command=lambda:saveAs())
filemenu.add_separator()
filemenu.add_command(label="Exit", command=lambda:window.destroy())
menubar.add_cascade(label="File", menu=filemenu)

editmenu = tk.Menu(menubar, tearoff=0)
editmenu.add_command(label="Copy", accelerator="Ctrl+C")
editmenu.add_command(label="Paste", accelerator="Ctrl+V")
editmenu.add_separator()
editmenu.add_command(label="Clear Console", accelerator="Ctrl+X", command=lambda:clearConsole(TAB_CONTROL.index(TAB_CONTROL.select())+1))

#editmenu.add_cascade(label="Theme", menu=submenu)
menubar.add_cascade(label="Edit", menu=editmenu)

windowmenu = tk.Menu(menubar, tearoff=0)

window_submenu = Menu(windowmenu)
window_submenu.add_command(label="780x350")
window_submenu.add_command(label="1540x700")
windowmenu.add_cascade(label="Window Size", menu=window_submenu)

windowmenu.add_separator()
windowmenu.add_command(label="Full Screen", accelerator="F11", command=lambda:fullscreenWindow())
windowmenu.add_command(label="Reset Window", accelerator="F10", command=lambda:resetWindow())

submenu = Menu(windowmenu)

submenu.add_command(label="clam", command=lambda:changeTheme('clam'))
submenu.add_command(label="winnative", command=lambda:changeTheme('winnative'))
submenu.add_command(label="alt", command=lambda:changeTheme('alt'))
submenu.add_command(label="xpnative", command=lambda:changeTheme('xpnative'))
submenu.add_command(label="default", command=lambda:changeTheme('default'))
submenu.add_command(label="classic", command=lambda:changeTheme('classic'))
submenu.add_command(label="vista", command=lambda:changeTheme('vista'))

windowmenu.add_cascade(label="Theme", menu=submenu)
menubar.add_cascade(label="Window", menu=windowmenu)

helpmenu = tk.Menu(menubar, tearoff=0)
helpmenu.add_command(label="About", accelerator='F1', command=lambda:aboutDialog())
helpmenu.add_command(label="Purge Log Files", accelerator='F2', command=lambda:Logging.deleteLog(int(logDeleteOldInput.get())))
helpmenu.add_command(label="Check for Updates...")
menubar.add_cascade(label="Help", menu=helpmenu)

if __name__ == "__main__":
    Logging.createLogFile(int(logDeleteOldInput.get()))
    window.config(menu=menubar)
    window.protocol('WM_DELETE_WINDOW', on_closing)
    window.mainloop()