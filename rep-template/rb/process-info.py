import os

cutoff_values = (0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9)


filename = "info.txt"
for value in cutoff_values:
	cutoff_value = value
	my_file = "remove" + str(cutoff_value) + ".sh"
	count = 1

	if os.path.exists(my_file):
		os.remove(my_file)
		print(f"Existing file '{my_file}' removed successfully.")

	try:
		with open(filename, 'r') as file_object:
			for line in file_object:
            	# Process each line here
            	# The 'line' variable will contain the current line as a string,
            	# including the trailing newline character (\n) if present.
				line = line.strip()
				line = line.replace(",", "")
				if float(line) < float(cutoff_value):
					with open (my_file, "a") as f:
						str_to_write = "rm locus" + str(count) + ".nex" + "\n"
						f.write(str_to_write)
				count = count + 1
	except FileNotFoundError:
		print(f"Error: The file '{filename}' was not found.")
	except Exception as e:
		print(f"An unexpected error occurred: {e}")

	#if nothing was written to the file, create a blank file
	try:
		with open(my_file, 'x') as f:
			f.write("")
	except FileExistsError:
    		print(f"File '{my_file}' already exists. No action taken.")
