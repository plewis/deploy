for i in {1..__NREPS__}
do
#	echo $i
	cd rep$i/rb
	for l in {1..__NLOCI__}
	do
#		echo gene$l
		mkdir gene$l
		pwd
		mv locus$l.nex gene$l
	done
	cd ../..
done
