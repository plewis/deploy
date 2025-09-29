for i in rep*/smc; do
	echo "$i"
	cd "$i"
	td --treefile species_trees.trees --frechetmean --prefix mean  --frechet-k 1000000 --frechet-n 10 --frechet-e 0.00001
	cd ../..
done
