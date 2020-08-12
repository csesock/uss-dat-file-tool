import os

developer = None

try:
    with open('USSdatFileTool.pyw', 'r') as openfile:
        for line in openfile:
            if line.startswith('developer=True'):
                developer = False
            elif line.startswith('developer=False'):
                developer = True
            else:

            os.system("pause")
except:
    print("something broke")