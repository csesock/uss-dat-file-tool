#requested by John Krumenacker
#creates a formatted "report" that contains different customer and meter information
def CustomerReport():
    confirmation = messagebox.askokcancel("Confirmation", "To build this report, CUS, MTR, and RFF records must exist for all customers or else data will be ommitted.")
    if confirmation == None or confirmation == False:
        return 
    try:
        with open(download_filename, 'r') as openfile:
            customer = meter = ert = ""
            counter = 8.0
            num = getNumCustomers()

            advConsole.delete(1.0, "end")

            advConsole.insert(1.0, "\t\t|Customer Report\n")
            advConsole.insert(2.0, '\t\t|'+str(os.path.basename(download_filename))+"\n")
            advConsole.insert(3.0, '\t\t|'+datetime.today().strftime('%Y/%m/%d_%H:%M\n'))
            advConsole.insert(4.0, "\t\t|Customers Found: "+str(num)+"\n")
            advConsole.insert(5.0, "_________________________________________________________\n")
            advConsole.insert(6.0, "Account#    \tAddress        \tMeter          \tERT#\n")
            advConsole.insert(7.0, "_________________________________________________________\n")
            
            for line in openfile:
                # (1) account number : CUS [15:34] -> [14:34]
                # (2) meter number   : MTR [46:57] -> [45:57]
                # (3) ERT number     : RFF [12:21] -> [11:21]
                if line.startswith('CUS'):
                    customer = line[14:34].strip().ljust(12)
                    address = line[54:67].strip().ljust(15)
                if line.startswith('MTR'):
                    meter = line[45:57].strip().ljust(15)
                if line.startswith('RFF'):
                    ert = line[11:21].strip().ljust(15)
                    advConsole.insert(counter, customer+'\t'+address+'\t'+meter+'\t'+ert+'\n')
                    counter+=1
    except FileNotFoundError:
        fileNotFoundError(2)