import time
import os
import shutil
from os.path import isfile, join

import matplotlib.pyplot as plt
import matplotlib.patches as pats

valuesx = []
y_plain = []
y_lossless = []

def compress(uncompressed):
    """Compress a string to a list of output symbols."""
 
    # Build the dictionary.
    dict_size = 256
    dictionary = dict((chr(i), i) for i in range(dict_size))
    # in Python 3: dictionary = {chr(i): i for i in range(dict_size)}
 
    w = ""
    result = []
    for c in uncompressed:
        wc = w + c
        if wc in dictionary:
            w = wc
        else:
            result.append(dictionary[w])
            # Add wc to the dictionary.
            dictionary[wc] = dict_size
            dict_size += 1
            w = c
 
    # Output the code for w.
    if w:
        result.append(dictionary[w])
    return result
 
 
def decompress(compressed):
    """Decompress a list of output ks to a string."""
    from io import StringIO
 
    # Build the dictionary.
    dict_size = 256
    dictionary = dict((i, chr(i)) for i in range(dict_size))
    # in Python 3: dictionary = {i: chr(i) for i in range(dict_size)}
 
    # use StringIO, otherwise this becomes O(N^2)
    # due to string concatenation in a loop
    result = StringIO()
    w = chr(compressed.pop(0))
    result.write(w)
    for k in compressed:
        if k in dictionary:
            entry = dictionary[k]
        elif k == dict_size:
            entry = w + w[0]
        else:
            raise ValueError('Bad compressed k: %s' % k)
        result.write(entry)
 
        # Add w+entry[0] to the dictionary.
        dictionary[dict_size] = w + entry[0]
        dict_size += 1
 
        w = entry
    return result.getvalue()

def transfere_File(src, dist):
    shutil.copyfile(src, dist)
 
def getstring(dictionary):
    return ' '.join(str(e) for e in dictionary)

def getDictionary(text): 
    text_dict = text.split(" ")
    floats = list(map(float, text_dict))
    return list(map(int, floats))

def save_times(file_sizes, times, file_type, curr_dir):
    #save values for file size and times
    output_file = open(curr_dir+"/results/LWZ_" + file_type + ".txt", "w")

    for x,y in zip(file_sizes, times):
        output_file.write(str(x) + " " + str(y) + "\n")

    output_file.close()
    
    return

def test_Compression(input_file_paths, destination_path, curr_dir):
    numb_files = len(input_file_paths)
    file_sizes = []
    compression_times = []
    transmission_times = []
    decompression_times = []
    for i in range(0, numb_files):
        #Get Data from file
        path = "/files/text_files/" + input_file_paths[i]
        file_size = os.path.getsize(curr_dir + path)
        file_sizes.append(file_size)
        valuesx.append(file_size)
        total_time = 0;

        startTime = time.time() #time in milli seconds
        file = open(curr_dir + path, "r")
        uncompressed_data = file.read()
        file.close()

        #Compress Data
        compressed_data = compress(uncompressed_data)
        new_data = getstring(compressed_data)

        out_file = "/files/compressed_LWZ/text_file_" + str(i) + "_comp.txt"
        compressed_data_file = open(curr_dir + out_file,'w')
        compressed_data_file.write(new_data)
        compressed_data_file.close()
        endTime = time.time()   #time in micro seconds

        diff = (endTime - startTime)*1000
        compression_times.append(diff)
        total_time = total_time + diff

        #Transmitt File
        startTime = time.time() #time in milli seconds
        src = curr_dir + out_file
        dist = destination_path + "/file_" + str(i) + "_comp_copy.txt"
        transfere_File(src, dist)
        endTime = time.time()   #time in micro seconds

        diff = (endTime - startTime)*1000
        transmission_times.append(diff)
        total_time = total_time + diff

        #Decompress
        startTime = time.time() #time in milli seconds
        comp_data_file = open(dist, "r")
        comp_data = comp_data_file.read()
        diction = getDictionary(comp_data)
        comp_data_file.close()
        decomp_data = decompress(diction)

        new_file = curr_dir + "/files/decompressed_LWZ/text_file_" + str(i) + "_decomp.txt"
        end_file = open(new_file, "w")
        end_file.write(decomp_data)
        end_file.close()
        endTime = time.time()   #time in micro seconds

        diff = (endTime - startTime)*1000
        decompression_times.append(diff)
        total_time = total_time + diff
        total_time = total_time

        #Check if Lossless
        if (decomp_data == uncompressed_data):
            y_lossless.append(total_time)

            input_file_info = os.stat(curr_dir + path)
            output_file_info = os.stat(dist)
            print("Transmited: ", input_file_paths[i], " \t time: ", total_time)
            #print("I File ", i, " size: ", input_file_info.st_size, " bytes")
            #print("O File ", i, " size: ", output_file_info.st_size, " bytes")
        else:
            print("Fail: data lost")
            y_lossless.append(0)

    save_times(file_sizes, compression_times, "compression_times", curr_dir)
    save_times(file_sizes, transmission_times, "trans_times", curr_dir)
    save_times(file_sizes, decompression_times, "decompr_times", curr_dir)

def plain_transfer(file_list, desti_path, current_dir):
    num = 0;
    file_sizes = []
    for file_name in file_list:
        source = current_dir + "/files/text_files/" + file_name
        destination = desti_path + "/text_file_" + str(num) + "_ncopy.txt"

        startTime = time.time() #time in milli seconds
        transfere_File(source, destination)
        endTime = time.time()   #time in milli seconds
        diff = (endTime - startTime)*1000
        y_plain.append(diff)
        file_size = os.path.getsize(source)
        file_sizes.append(file_size)
        print("Transmited: ", file_name, " \t time: ", diff)
        num += 1
    save_times(file_sizes, y_plain, "ncopy", curr_dir)
    return

#File Compress
#os.chdir("..")
#input_file_paths = ["text_files/text_data_1.txt", "text_files/text_data_2.txt", "text_files/text_data_3.txt", "text_files/text_data_4.txt", "text_files/text_data_5.txt", "text_files/text_data_6.txt"]
#output_paths = ["text_files/text_comp_1.txt", "text_files/text_comp_2.txt", "text_files/text_comp_3.txt", "text_files/text_comp_4.txt", "text_files/text_comp_5.txt", "text_files/text_comp_6.txt"]

curr_dir = os.getcwd()
#print("Current Directory: ", curr_dir)

#Get list of files to work with
mypath = curr_dir + "/files/text_files/"
file_list = [f for f in os.listdir(mypath) if isfile(join(mypath, f))]
file_list = sorted(file_list)
#print(file_list)

destination_paths = curr_dir + "/files/destination_LWZ"

#print("===============LZW===============")
print("===============Plain Transfer===============")
plain_transfer(file_list, destination_paths, curr_dir)
print("===============Transfer With Compression: LWZ===============")
test_Compression(file_list, destination_paths, curr_dir)
#print("Done!!!")

"""==========PLOT Graphs=========="""
'''
#Normal Transfer
red = pats.Patch(color = "red", label = "Normal Transfer")
plt.plot(valuesx, y_plain, "r")
#Tranfer With Compression
green = pats.Patch(color = "green", label = "Tranfer With Compression")
plt.plot(valuesx, y_lossless, "g")

plt.legend(handles = [red, green])
plt.title("Graph for Normal Data transmission VS with lossless Compression")
plt.xlabel("File Size (bytes)")
plt.ylabel("Transimision Time (ms)")
plt.show()'''
