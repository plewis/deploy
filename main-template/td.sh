for i in rep*/smc; do
	echo "$i"
	cd "$i"
	td --treefile bhv_trees.tre
	cd ../..
done