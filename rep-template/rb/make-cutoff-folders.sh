for v in {0..9}
do
	mkdir smc-cutoff-0.$v
	cd smc-cutoff-0.$v
	for l in {1..__NLOCI__}
	do
		cp ../gene$l/locus$l.nex .
	done
	# copy and run the remove loci script
	cp ../remove0.$v.sh .
	. remove0.$v.sh

	# crunch the remaining loci
	python3 ../crunch.py

	# copy and edit the proj.conf file
	cp ../../smc/proj.conf .
	sed -i 's#../sim/sim.nex#COMBINED.nex#g' proj.conf
	cd ..
done
