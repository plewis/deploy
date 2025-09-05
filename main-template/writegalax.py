nreps = __NREPS__
for rep in range(nreps):
	rep_plus_one = rep + 1
	g = 'galax --treefile rep%d/smc/alt_species_trees.trees --rooted --outfile smcout%d' % (rep_plus_one, rep_plus_one)
	    
	with open("rungalax.sh", "a") as text_file:
		text_file.write(g + "\n")
