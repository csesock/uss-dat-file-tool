#Functions for the logging system
#
import os, sys
from datetime import datetime


developer = True
log_filename = os.getcwd() + "\\logs\\Logfile " + datetime.today().strftime('%Y-%m-%d_%H-%M') + ".txt"

def createLogFile():
    try:
        f = open(log_filename, 'w')
        if developer == True:
            f.write("DEVELOPER MODE ON \n")
        f.write(datetime.today().strftime('%Y-%m-%d_%H-%M') + " Program successfully started \n")
        f.write(datetime.today().strftime('%Y-%m-%d_%H-%M') + " Logfile successfully created")
        f.close()
    except FileExistsError:
        pass

def writeToLogs(message):
    try:
        f = open(log_filename, 'a')
        f.write('\n')
        f.write(datetime.today().strftime('%Y-%m-%d_%H-%M') + " " + message)
        f.close()
    except:
        pass

def viewLog():
    counter = 1.0
    try:
        with open(log_filename, 'r') as openfile:
            if TAB_CONTROL.index(TAB_CONTROL.select()) == 0: #boc console
                bocConsole.delete(1.0, 'end')
                console = bocConsole
            else:
                latLongConsole.delete(1.0, 'end')
                console = latLongConsole
            for line in openfile:
                console.insert(counter, line)
                counter+=1
    except:
        pass

def deleteLog(max_log_count):
    count=0
    d = os.getcwd()+'\\logs'
    for path in os.listdir(d):
        if os.path.isfile(os.path.join(d, path)):
            count+=1
    if count > max_log_count:
        num_to_delete = count - max_log_count
        files = os.listdir(d)
        for i in range(num_to_delete):
            os.remove(d+"\\"+files[i])

    
