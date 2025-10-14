from Bio.Nexus import Nexus
import os
import glob
import re

def get_number_from_file_name(s):
	# find numbers in string
	numbers = re.findall(r'\d+', s)
	if numbers:
		return int(numbers[0])
	return 0

file_list = []

for value in glob.glob('*.nex'):
	file_list.append(value)

# sort list of files according to the locus number
sorted_file_list = sorted(file_list, key=get_number_from_file_name)

nexi = [(fname, Nexus.Nexus(fname)) for fname in sorted_file_list]

combined = Nexus.combine(nexi)
combined.write_nexus_data(filename = open('COMBINED.nex', 'w'))
