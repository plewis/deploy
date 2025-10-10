for v in {0..9}
do
	mkdir smc-cutoff-0.$v
	cd smc-cutoff-0.$v
	for l in {1..__NLOCI__}
	do
		cp ../gene$l/locus$l.nex .
	done
	cp ../remove0.$v.sh .
	. remove0.$v.sh
	python3 ../crunch.py
	cd ..
done
