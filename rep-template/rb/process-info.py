import os

filename = "info.txt"
cutoff_value = 0.8
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
				print(line)
				with open (my_file, "a") as f:
					str_to_write = "rm locus" + str(count) + ".nex" + "\n"
					f.write(str_to_write)
			count = count + 1
except FileNotFoundError:
	print(f"Error: The file '{filename}' was not found.")
except Exception as e:
	print(f"An unexpected error occurred: {e}")
