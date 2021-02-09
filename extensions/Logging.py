# Logging system for USS .dat File Tool
import os, sys
from datetime import datetime

log_filename = os.getcwd() + "\\logs\\Logfile " + datetime.today().strftime('%Y-%m-%d_%H-%M') + ".txt"

def createLogFile(max_log_count):
    file_path = os.getcwd()+"\\logs"
    try:
        count = getFileCount(file_path)
        if count >= max_log_count:
            deleteLog(max_log_count)
        with open(log_filename, 'w') as openfile:
            openfile.write(datetime.today().strftime('%Y-%m-%d_%H-%M') + " Program successfully started \n")
            openfile.write(datetime.today().strftime('%Y-%m-%d_%H-%M') + " Logfile successfully created")
    except:
        pass

def writeToLogs(message):
    try:
        with open(log_filename, 'a') as openfile:
            openfile.write('\n')
            openfile.write(datetime.today().strftime('%Y-%m-%d_%H-%M') + " " + message)
    except:
        pass

def deleteLog(max_log_count):
    try:
        file_path = os.getcwd()+'\\logs'
        count = getFileCount(file_path)
        if count > max_log_count:
            num_to_delete = count - max_log_count
            files = os.listdir(file_path)
            for i in range(num_to_delete):
                os.remove(file_path+"\\"+files[i])
    except:
        pass

def getFileCount(file_path):
    count=0
    try:
        for path in os.listdir(file_path):
            if os.path.isfile(os.path.join(file_path, path)):
                count+=1
        return count 
    except:
        pass