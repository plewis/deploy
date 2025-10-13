import os
import re

for i in range(10):
	file_path = 'smc-cutoff-0.%d/posterior/bhv_trees.tre' % i
	try:
		if os.path.exists(file_path):
			os.remove(file_path)
			print(f"The file '{file_path}' has been deleted.")

		print(f"File '{file_path}' created successfully.")
	except FileNotFoundError:
			print(f"Error: Folder for '{file_path}' does not exist.")

	with open(file_path, "a") as file:
		file.write("#nexus\n")
		file.write("begin trees;\n")

		true_file_path = "../sim/true-species-tree.tre"
		true_file = open(true_file_path)
		true_file_lines = true_file.readlines()

		for line in true_file_lines:
			flag = re.search('^  tree', line)
			if flag:
				file.write(line)


		posterior_file_path = 'smc-cutoff-0.%d/posterior/species_trees.trees' % i
		posterior_file = open(posterior_file_path)
		posterior_file_lines = posterior_file.readlines()

		for line in posterior_file_lines:
			flag = re.search('^  tree', line)
			if flag:
				file.write(line)

		file.write("end;")
