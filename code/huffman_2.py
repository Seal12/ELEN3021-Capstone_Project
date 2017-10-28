import os
import marshal
import cPickle
import array

import filecmp
import time
import shutil
from os.path import isfile, join

import matplotlib.pyplot as plt
import matplotlib.patches as pats

class HuffmanNode(object):
    recurPrint = False
    def __init__(self, ch=None, fq=None, lnode=None, rnode=None, parent=None):
        self.L = lnode
        self.R = rnode
        self.p = parent
        self.c = ch
        self.fq = fq
        
    def __repr__(self):
        if HuffmanNode.recurPrint:
            lnode = self.L if self.L else '#'  
            rnode = self.R if self.R else '#'        
            return ''.join( ('(%s:%d)'%(self.c, self.fq), str(lnode), str(rnode) ) )
        else:
            return '(%s:%d)'%(self.c, self.fq)
    
    def __cmp__(self, other):
        if not isinstance(other, HuffmanNode):
            return super(HuffmanNode, self).__cmp__(other)
        return cmp(self.fq, other.fq)

def _pop_first_two_nodes(nodes):
    if len(nodes)>1:
        first=nodes.pop(0)
        second=nodes.pop(0)
        return first, second
    else:
        #print "[popFirstTwoNodes] nodes's length <= 1"
        return nodes[0], None
        
def _build_tree(nodes):    
    nodes.sort()
    while(True):
        first, second = _pop_first_two_nodes(nodes)
        if not second:
            return first
        parent = HuffmanNode(lnode=first, rnode=second, fq=first.fq+second.fq)
        first.p = parent
        second.p = parent
        nodes.insert(0, parent)
        nodes.sort()

def _gen_huffman_code(node, dict_codes, buffer_stack=[]):
    if not node.L and not node.R:
        dict_codes[node.c] = ''.join(buffer_stack)
        return
    buffer_stack.append('0')
    _gen_huffman_code(node.L, dict_codes, buffer_stack)
    buffer_stack.pop()
    
    buffer_stack.append('1')
    _gen_huffman_code(node.R, dict_codes, buffer_stack)
    buffer_stack.pop()

def _cal_freq(long_str):
    from collections import defaultdict
    d = defaultdict(int)
    for c in long_str:
        d[c] += 1
    return d

MAX_BITS = 8

class Encoder(object):
    def __init__(self, filename_or_long_str=None):
        if filename_or_long_str:
            if os.path.exists(filename_or_long_str):
                self.encode(filename_or_long_str)
            else:
                print '[Encoder] take \'%s\' as a string to be encoded.(ln85)'\
                      % filename_or_long_str
                self.long_str = filename_or_long_str

    def __get_long_str(self):
        return self._long_str
    def __set_long_str(self, s):
        self._long_str = s
        if s:
            self.root = self._get_tree_root()
            self.code_map = self._get_code_map()
            self.array_codes, self.code_length = self._encode()
    long_str = property(__get_long_str, __set_long_str)
    
    def _get_tree_root(self):
        d = _cal_freq(self.long_str)
        return _build_tree(
            [HuffmanNode(ch=ch, fq=int(fq)) for ch, fq in d.iteritems()]
            )

    def _get_code_map(self):
        a_dict={}
        _gen_huffman_code(self.root, a_dict)
        return a_dict
        
    def _encode(self):
        array_codes = array.array('B')
        code_length = 0
        buff, length = 0, 0
        for ch in self.long_str:
            code = self.code_map[ch]        
            for bit in list(code):
                if bit=='1':
                    buff = (buff << 1) | 0x01
                else: # bit == '0'
                    buff = (buff << 1)
                length += 1
                if length == MAX_BITS:
                    array_codes.extend([buff])
                    buff, length = 0, 0

            code_length += len(code)
            
        if length != 0:
            array_codes.extend([buff << (MAX_BITS-length)])
            
        return array_codes, code_length

    def encode(self, filename):
        fp = open(filename, 'rb')
        self.long_str = fp.read()
        fp.close()

    def write(self, filename):
        if self._long_str:
            fcompressed = open(filename, 'wb')
            marshal.dump(
                (cPickle.dumps(self.root), self.code_length, self.array_codes),
                fcompressed)
            fcompressed.close()
        else:
            print "You haven't set 'long_str' attribute."

class Decoder(object):
    def __init__(self, filename_or_raw_str=None):
        if filename_or_raw_str:
            if os.path.exists(filename_or_raw_str):
                filename = filename_or_raw_str
                self.read(filename)            
            else:
                print '[Decoder] take \'%s\' as raw string' % filename_or_raw_str
                raw_string = filename_or_raw_str
                unpickled_root, length, array_codes = marshal.loads(raw_string)
                self.root = cPickle.loads(unpickled_root)
                self.code_length = length        
                self.array_codes = array.array('B', array_codes)

    def _decode(self):
        string_buf = []
        total_length = 0    
        node = self.root
        for code in self.array_codes:
            buf_length = 0
            while (buf_length < MAX_BITS and total_length != self.code_length):
                buf_length += 1
                total_length += 1            
                if code >> (MAX_BITS - buf_length) & 1:
                    node = node.R
                    if node.c:
                        string_buf.append(node.c)
                        node = self.root
                else:
                    node = node.L
                    if node.c:
                        string_buf.append(node.c)
                        node = self.root

        return ''.join(string_buf)        

    def read(self, filename):
        fp = open(filename, 'rb')
        unpickled_root, length, array_codes = marshal.load(fp)        
        self.root = cPickle.loads(unpickled_root)
        self.code_length = length        
        self.array_codes = array.array('B', array_codes)
        fp.close()

    def decode_as(self, filename):
        decoded = self._decode()
        fout = open(filename, 'wb')
        fout.write(decoded)
        fout.close()

'''My functions'''

valuesx = []
y_plain = []
y_lossless = []

def transfere_File(src, dist):
    shutil.copyfile(src, dist)

def are_same(OG_file, decomp_file):
    return filecmp.cmp(OG_file, decomp_file)

def save_times(file_sizes, times, file_type, current_directory):
    #save values for file size and times
    output_file = open(current_directory + "/results/HUFF_" + file_type + ".txt", "w")

    for x,y in zip(file_sizes, times):
        output_file.write(str(x) + " " + str(y) + "\n")

    output_file.close()
    
    return

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
        print "Transmited: %s \t time: %f" % (file_name, diff)
        num += 1
    save_times(file_sizes, y_plain, "ncopy", current_dir)
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
        compressed_file = curr_dir + "/files/compressed_Huff/text_file_" + str(i) + "_comp.txt"
        decompressed_file = curr_dir + "/files/decompressed_Huff/text_file_" + str(i) + "_decomp.txt"

        #Compress file
        startTime = time.time() #time in milli seconds
        enc = Encoder(original_file) #runs huffman encoding
        enc.write(compressed_file) #saves compressed file
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
        dec = Decoder(compressed_file)
        dec.decode_as(decompressed_file)
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

curr_dir = os.getcwd()
#print "Current Directory: %s" % curr_dir

#Get list of files to work with
mypath = curr_dir + "/files/text_files/"
file_list = [f for f in os.listdir(mypath) if isfile(join(mypath, f))]
file_list = sorted(file_list)
#print file_list

destination_paths = curr_dir + "/files/destination_Huff"

#print "===============Plain Transfer===============" 
#plain_transfer(file_list, destination_paths, curr_dir)
print "===============Transfer With Compression: Huffman===============" 
test_Compression(file_list, destination_paths, curr_dir)


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

'''
original_file = 'test_file.txt'
compressed_file = 'test_file_comp.txt'
decompressed_file = 'test_file_decomp.txt'

# first way to use Encoder/Decoder
enc = Encoder(original_file)    
enc.write(compressed_file)
dec = Decoder(compressed_file)
dec.decode_as(decompressed_file)
print("Done!")'''

