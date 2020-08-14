# Logging system for USS .dat File Tool

import os, sys
from datetime import datetime

log_filename = os.getcwd() + "\\logs\\Logfile " + datetime.today().strftime('%Y-%m-%d_%H-%M') + ".txt"

def createLogFile():
    try:
        f = open(log_filename, 'w')
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