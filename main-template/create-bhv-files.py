import os
import re

nreps = __NREPS__

for i in range(1, nreps+1):
	file_path = "rep" + str(i) + "/smc/bhv_trees.tre"
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

		new_sim_file_path = ""
		if i + 1 > nreps:
			new_sim_file_path = "rep1/sim/true-species-tree.tre"

		else:
			new_sim_file_path = "rep" + str(i+1) + "/sim/true-species-tree.tre" # this only works if all sims use same params

		new_sim_file = open(new_sim_file_path)
		new_sim_file_lines = new_sim_file.readlines()

		for line in new_sim_file_lines:
			flag = re.search('^  tree', line)
			if flag:
				file.write(line)


		true_file_path = "rep" + str(i) + "/sim/true-species-tree.tre"
		true_file = open(true_file_path)
		true_file_lines = true_file.readlines()

		for line in true_file_lines:
			flag = re.search('^  tree', line)
			if flag:
				file.write(line)


		posterior_file_path = "rep" + str(i) + "/smc/species_trees.trees"
		posterior_file = open(posterior_file_path)
		posterior_file_lines = posterior_file.readlines()

		for line in posterior_file_lines:
			flag = re.search('^  tree', line)
			if flag:
				file.write(line)

		file.write("end;")