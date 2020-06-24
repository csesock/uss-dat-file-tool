import re, os, time

lat_long_pattern = re.compile('-?[0-9]{2}\.\d{1,13}$')
WAIT_TIME = 0.2

def checkMalformedLatLong():
    malformed_data = False
    counter=1 #first line in file
    try:
        with open('download.dat', 'r') as openfile:
            for line in openfile:
                if line.startswith('MTX'):
                    lat_data = line[23:40].rstrip()
                    long_data = line[40:57].rstrip()
                    if not lat_long_pattern.match(lat_data):
                        malformed_data = True 
                        print("Malformed lat data at line:", counter, "Value:", lat_data)
                    elif not lat_long_pattern.match(long_data):
                        malformed_data = True
                        print("Malformed long data at line:", counter, "Value:", long_data)
                counter+=1
        if malformed_data == True:
            print("The above data is malformed in some way.")
            os.system("PAUSE")
        else:
            if checkLatLongSigns(float(lat_data), float(long_data)) == False:
                print("The data is not malformed.")
                os.system("PAUSE")
            else:
                print("The data has malformed sign values.")
                os.system("PAUSE")
        print()
        os.system('PAUSE')
    except FileNotFoundError:
        print("ERROR: FILE NOT FOUND")

# an additional level of checking to make sure that lat/long data is correct
# lat data will always be +, long will always be - in our region
def checkLatLongSigns(lat_data, long_data):
    if lat_data < 0 or long_data > 0:
        return True
    else:
        return False

if __name__ == '__main__':
    checkMalformedLatLong()