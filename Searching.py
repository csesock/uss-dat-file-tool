
#Polymorphic search function for .dat file tool
records = []

def searchFront(download_filename, to_search, condition=None):
	with open(download_filename, 'r') as openfile:
		for line in openfile:
			if line.startswith(to_search):
                                records.append(line)
                return records 
				

def searchMiddle(download_filename, to_search, index1, index2):
    with open(download_filename, 'r') as openfile:
        for line in openfile:
            #first index must be n-1 [2:5] -> [1:5]
            value = line[index1::index2]
            if value == to_search:
                records.append(value)
        return records 
            
            
