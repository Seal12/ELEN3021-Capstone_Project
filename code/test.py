from os import listdir
from os.path import isfile, join

mypath = "/home/seal/Desktop/ELEN3021/code/files/text_files/"
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
print(onlyfiles)