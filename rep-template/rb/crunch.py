from Bio.Nexus import Nexus
import os
import glob

file_list = []

for value in glob.glob('*.nex'):
	file_list.append(value)

nexi = [(fname, Nexus.Nexus(fname)) for fname in file_list]

combined = Nexus.combine(nexi)
combined.write_nexus_data(filename = open('COMBINED.nex', 'w'))
