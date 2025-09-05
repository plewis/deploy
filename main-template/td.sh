for i in rep*/smc; do
	echo "$i"
	cd "$i"
	td --treefile species_trees.trees --frechet mean
	cd ../..
done
