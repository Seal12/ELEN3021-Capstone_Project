# Shannon-Fano Data Compression
# http://en.wikipedia.org/wiki/Shannon%E2%80%93Fano_coding
# (Max compressible file size: 2**32 bytes)
# FB - 201012153
import sys
import os

import filecmp
import time
import shutil
from os.path import isfile, join

import matplotlib.pyplot as plt
import matplotlib.patches as pats

valuesx = []
y_plain = []
y_lossless = []

def shannon_fano_encoder(iA, iB): # iA to iB : index interval
    global tupleList
    size = iB - iA + 1
    if size > 1:
        # Divide the list into 2 groups.
        # Top group will get 0, bottom 1 as the new encoding bit.
        mid = int(size / 2 + iA)
        for i in range(iA, iB + 1):
            tup = tupleList[i]
            if i < mid: # top group
                tupleList[i] = (tup[0], tup[1], tup[2] + '0')
            else: # bottom group
                tupleList[i] = (tup[0], tup[1], tup[2] + '1')
        # do recursive calls for both groups
        shannon_fano_encoder(iA, mid - 1)
        shannon_fano_encoder(mid, iB)

def byteWriter(bitStr, outputFile):
    global bitStream
    bitStream += bitStr
    while len(bitStream) > 8: # write byte(s) if there are more then 8 bits
        byteStr = bitStream[:8]
        bitStream = bitStream[8:]
        outputFile.write(chr(int(byteStr, 2)))

def bitReader(n): # number of bits to read
    global byteArr
    global bitPosition
    bitStr = ''
    for i in range(n):
        bitPosInByte = 7 - (bitPosition % 8)
        bytePosition = int(bitPosition / 8)
        byteVal = byteArr[bytePosition]
        bitVal = int(byteVal / (2 ** bitPosInByte)) % 2
        bitStr += str(bitVal)
        bitPosition += 1 # prepare to read the next bit
    return bitStr

def decode(outputFile): # FILE DECODING
    global bitPosition
    bitPosition = 0
    n = int(bitReader(8), 2) + 1 # first read the number of encoding tuples
    # print 'Number of encoding tuples:', n
    dic = dict()
    for i in range(n):
        # read the byteValue
        byteValue = int(bitReader(8), 2)
        # read 3-bit(len(encodingBitStr)-1) value
        m = int(bitReader(3), 2) + 1
        # read encodingBitStr
        encodingBitStr = bitReader(m)
        dic[encodingBitStr] = byteValue # add to the dictionary
    # print 'The dictionary of encodingBitStr : byteValue pairs:'
    # print dic
    # print

    # read 32-bit file size (number of encoded bytes) value
    numBytes = long(bitReader(32), 2) + 1
    print 'ln78.Number of bytes to decode:', numBytes
    
    # read the encoded data, decode it, write into the output file
    fo = open(outputFile, 'wb')
    b = 0
    while(b < numBytes):
    #for b in range(numBytes):
        # read bits until a decoding match is found
        encodingBitStr = ''
        while True:
            encodingBitStr += bitReader(1)
            if encodingBitStr in dic:
                byteValue = dic[encodingBitStr]
                fo.write(chr(byteValue))
                break
        b +=1
    fo.close()

def encode(fileSize, outputFile):
    # calculate the total number of each byte value in the file
    global byteArr
    freqList = [0] * 256
    for b in byteArr:
        freqList[b] += 1

    # create a list of (frequency, byteValue, encodingBitStr) tuples
    global tupleList
    tupleList = []
    for b in range(256):
        if freqList[b] > 0:
            tupleList.append((freqList[b], b, ''))

    # sort the list according to the frequencies descending
    tupleList = sorted(tupleList, key=lambda tup: tup[0], reverse = True)

    shannon_fano_encoder(0, len(tupleList) - 1)
    # print 'The list of (frequency, byteValue, encodingBitStr) tuples:'
    # print tupleList
    # print

    # create a dictionary of byteValue : encodingBitStr pairs
    dic = dict([(tup[1], tup[2]) for tup in tupleList])
    del tupleList # unneeded anymore
    # print 'The dictionary of byteValue : encodingBitStr pairs:'
    # print dic

    # write a list of (byteValue,3-bit(len(encodingBitStr)-1),encodingBitStr)
    # tuples as the compressed file header
    global bitStream
    bitStream = ''
    fo = open(outputFile, 'wb')
    fo.write(chr(len(dic) - 1)) # first write the number of encoding tuples
    for (byteValue, encodingBitStr) in dic.iteritems():
        # convert the byteValue into 8-bit and send to be written into file
        bitStr = bin(byteValue)
        bitStr = bitStr[2:] # remove 0b
        bitStr = '0' * (8 - len(bitStr)) + bitStr # add 0's if needed for 8 bits
        byteWriter(bitStr, fo)
        # convert len(encodingBitStr) to 3-bit and send to be written into file
        bitStr = bin(len(encodingBitStr) - 1) # 0b0 to 0b111
        bitStr = bitStr[2:] # remove 0b
        bitStr = '0' * (3 - len(bitStr)) + bitStr # add 0's if needed for 3 bits
        byteWriter(bitStr, fo)
        # send encodingBitStr to be written into file
        byteWriter(encodingBitStr, fo)

    # write 32-bit (input file size)-1 value
    bitStr = bin(fileSize - 1)
    bitStr = bitStr[2:] # remove 0b
    bitStr = '0' * (32 - len(bitStr)) + bitStr # add 0's if needed for 32 bits
    byteWriter(bitStr, fo)

    # write the encoded data
    for b in byteArr:
        byteWriter(dic[b], fo)

    byteWriter('0' * 8, fo) # to write the last remaining bits (if any)
    fo.close()

def transfere_File(src, dist):
    shutil.copyfile(src, dist)

def are_same(OG_file, decomp_file):
    return filecmp.cmp(OG_file, decomp_file)

def save_times(file_sizes, times, file_type, current_directory):
    #save values for file size and times
    output_file = open(current_directory + "/results/shannon_" + file_type + ".txt", "w")

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
        path = "/files/text_files/" + input_file_paths[i]
        file_size = os.path.getsize(curr_dir + path)
        file_sizes.append(file_size)
        valuesx.append(file_size)
        total_time = 0;


        original_file = curr_dir + path
        compressed_file = curr_dir + "/files/compressed_shannon/text_file_" + str(i) + "_comp.txt"
        decompressed_file = curr_dir + "/files/decompressed_shannon/text_file_" + str(i) + "_decomp.txt"

        #Compress file
        startTime = time.time() #time in milli seconds
        # read the whole input file into a byte array
        fileSize = os.path.getsize(original_file)
        fi = open(original_file, 'rb')
        # byteArr = map(ord, fi.read(fileSize))
        global byteArr
        byteArr = bytearray(fi.read(fileSize))
        fi.close()
        fileSize = len(byteArr)
        encode(fileSize, compressed_file)
        endTime = time.time()   #time in micro seconds


        diff = (endTime - startTime)*1000
        compression_times.append(diff)
        total_time = total_time + diff

        #Transmitt File
        startTime = time.time() #time in milli seconds
        src = compressed_file
        dist = destination_path + "/file_" + str(i) + "_comp_copy.txt"
        transfere_File(src, dist)
        endTime = time.time()   #time in micro seconds

        diff = (endTime - startTime)*1000
        transmission_times.append(diff)
        total_time = total_time + diff

        #Decompress file
        startTime = time.time() #time in milli seconds
        decode(decompressed_file)
        endTime = time.time()   #time in micro seconds

        diff = (endTime - startTime)*1000
        decompression_times.append(diff)
        total_time = total_time + diff
        total_time = total_time

        #Check if Lossless
        if(are_same(original_file, decompressed_file) == True):
            y_lossless.append(total_time)

            input_file_info = os.stat(curr_dir + path)
            output_file_info = os.stat(dist)
            print "Transmited: %s \t time: %f" % (input_file_paths[i], total_time)
        else:
            print "Fail: data lost"
            y_lossless.append(0)

    save_times(file_sizes, compression_times, "compression_times", curr_dir)
    save_times(file_sizes, transmission_times, "trans_times", curr_dir)
    save_times(file_sizes, decompression_times, "decompr_times", curr_dir)

# Main
#
    '''if len(sys.argv) != 4:
        print 'Usage: ShannonFano.py [e|d] [path]InputFileName [path]OutputFileName'
        sys.exit()
    mode = sys.argv[1] # encoding/decoding
    inputFile = sys.argv[2]
    outputFile = sys.argv[3]
    print "%s %s into %s" %(mode, inputFile, outputFile)

    # read the whole input file into a byte array
    fileSize = os.path.getsize(inputFile)
    fi = open(inputFile, 'rb')
    # byteArr = map(ord, fi.read(fileSize))
    byteArr = bytearray(fi.read(fileSize))
    fi.close()
    fileSize = len(byteArr)
    print 'File size in bytes:', fileSize
    print'''

curr_dir = os.getcwd()
#print "Current Directory: %s" % curr_dir

#Get list of files to work with
mypath = curr_dir + "/files/text_files/"
file_list = [f for f in os.listdir(mypath) if isfile(join(mypath, f))]
file_list = sorted(file_list)
#print file_list

destination_path = curr_dir + "/files/destination_shannon"

tupleList = [] #used by encode
bitStream = '' #used by encode
bitPosition = 0 #used by decode
byteArr = [] #used by decode
#print "===============Plain Transfer===============" 
#plain_transfer(file_list, destination_paths, curr_dir)
print "===============Transfer With Compression: Shannon fano===============" 
test_Compression(file_list, destination_path, curr_dir)


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
