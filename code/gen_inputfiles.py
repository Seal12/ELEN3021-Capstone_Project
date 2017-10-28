from random_words import LoremIpsum
import random

li = LoremIpsum()
files = []

def get_file_list(n): 
#returns list of n file names
	list = []
	for i in range(n):
		list.append("files/text_files/text_file_" + str(i) + ".txt")

	return list

def get_paragraph():
	num_sentences = random.randint(3, 9)
	return li.get_sentences(num_sentences)

def gen_text(n, file_name): 
#generates text and writes it to file. 
#n will determin the file size order.
	file = open(file_name, "w")
	for i in range(n):	
		print("\t Section " + str(i))
		for i in range(10000):
			file.write(get_paragraph())
			file.write("\n\n")

	file.close()
	return

def generate_files(n):
#generates n files
	file_list = get_file_list(n)
	for i in range(n):
		print("Creating file " + str(i))
		gen_text(i+1, file_list[i])

	print("\nDone!!!")

num_files = int(input("Enter the number of text file you want:"))
generate_files(num_files)

