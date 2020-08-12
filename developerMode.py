import os, sys, time
from os import system

system("title "+"Developer Mode Change Script 0.1")
developer = None

print("(c) 2020 United Systems and Software, Inc.")
answer = str(input("Change developer mode settings? (Y or N): ")).upper()
if answer == 'Y':
    try:
        with open('USSdatFileTool.pyw', 'r') as openfile:
            for line in openfile:
                if line.startswith('developer=True'):
                    developer = False
                    print("Developer mode is currently enabled.")
                    print("Disabling...")
                    time.sleep(2)
                elif line.startswith('developer=False'):
                    developer = True
                    print("Developer mode is currently disabled.")
                    print("Enabling...")
                    time.sleep(2)
                else:
                    pass
        os.system("pause")
    except:
        print("An Error Occured: Please see exception.")
elif answer == 'N':
    print("Quitting...")
    time.sleep(2)
    sys.exit(0)
else:
    print("Unknown input. Quitting...")
    time.sleep(2)
    sys.exit(0)