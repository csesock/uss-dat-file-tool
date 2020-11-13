import tkinter as tk
from tkinter import *
from tkinter import ttk 

def adjustReadingsPopup(download_filename):
    root = tk.Tk()
    root.title("Adjust Readings Wizard")
    root.resizable(False, False)
    t = ttk.Style(root)
    t.theme_use('clam')
    try:
        photo = PhotoImage(file="assets\\IconSmall.png")
        root.iconphoto(False, photo)
    except:
        pass
    
    def getRadioButton():
        r = radio_var.get()
        print(radio_var.get())
        print(r)

    def adjustReadings():
        # which_button_is_selected = radio_var.get()
        # print(which_button_is_selected)
        correct = []

        with open('corrected.txt', 'r') as cor:
            for line in cor:
                correct.append(line.strip().rstrip())

        with open('upload.dat', 'r') as openfile:
            with open('upload--corrected.dat', 'w') as builtfile:
                counter = 0
                rdg = ""
                rff = ""
                for line in openfile:
                    if line.startswith('RDG'):
                        line = line.replace(line[33:43], correct[counter])
                        counter+=1
                    builtfile.write(line)
            
        with open('upload--corrected.dat', 'r') as openfile:
            rdg = ""
            rff = ""
            counter = 1
            for line in openfile:
                if line.startswith('RDG'):
                    rdg = line[33:43]
                if line.startswith('RFF'):
                    rff = line[72:82]
                    if rdg == rff:
                        print("MATCH: " + str(counter) + " " + rdg + " " + rff)
                    else:
                        print("DOES NOT MATCH: " + str(counter) + " " + rdg + " " + rff)
                counter+=1

    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    x = (sw - 380)/2
    y = (sh - 240)/2
    root.geometry('%dx%d+%d+%d' % (380, 240, x, y))

    Label(root, text="File:").place(x=50, y=20)
    Label(root, text=download_filename[-40:]).place(x=80, y=20)
    Label(root, text="This window will create a new download file by pulling \n the raw read and adjusting the numbers accordingly. \n Specify below how to adjust the readings.").place(x=50, y=50)

    radio_var = IntVar()    
    Radiobutton(root,text='Increment', value=5, variable=radio_var).place(x=100, y=110)
    Radiobutton(root, text="Decrement", value=6, variable=radio_var).place(x=185, y=110)

    Label(root, text="Digits to change:").place(x=105, y=140)
    numToDrop = ttk.Combobox(root, width=6, values = ["0", "1", "2", "3", "4"])
    numToDrop.place(x=200, y=140)
    numToDrop.state(['readonly'])
    numToDrop.set("1")

    ttk.Button(root, text="Execute", width=10, command=lambda:getRadioButton()).place(x=100, y=180)
    ttk.Button(root, text="Exit", command=root.destroy, width=10).place(x=190, y=180)

    mainloop()