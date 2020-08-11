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

def deleteLog(filename):
    pass
