for v in {0..9}
do

	nslow_loci=0
	nfast_loci=0
	
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

	# calculate the relative rates
	# for now, assume first 50 are slow, second 50 are faster
	

	# copy and edit the proj.conf file
	cp ../../smc/proj.conf .
	sed -i 's#../sim/sim.nex#../COMBINED.nex#g' proj.conf

	# calculate the number of slow and fast loci
	for filename in *; do
		if [[ "$filename" == *".nex" ]]; then # check that file ends with .nex
			number="${filename//[^0-9]/}"
		if [[ -n "$number" ]]; then # Check if any numbers were found
			if (( $number < 51 )); then # assumes first 50 loci are slow
				((nslow_loci++))
			else
				((nfast_loci++))
			fi
		fi
	fi
	done

	# calculate relative rates
	numerator=$(echo "scale=4; (0.01 * $nslow_loci) + $nfast_loci" | bc)
	denominator=$(echo "scale=4; $nslow_loci + $nfast_loci" | bc)
	total_rate=$(echo "scale=4; $numerator / $denominator" | bc)
	faster_rate=$(echo "scale=4; 1 / $total_rate" | bc)
	slow_rate=$(echo "scale=4; $faster_rate * 0.01" | bc)

	rates="relative_rates = "
	for ((i=1; i<=$nslow_loci; i++))
	do
		rates+="${slow_rate} , "
	done

	nfast_loci_minus_one=$(echo "scale =4; $nfast_loci - 1" | bc)

	for ((l=1; l<=$nslow_loci; l++))
	do
		if (( l < $nfast_loci )); then
			rates+="${faster_rate} , "
		else
			rates+="$faster_rate"
		fi
	done

	# TODO: replace relative rates in conf file
	
	# TODO: remove extra subsets
	# TODO: create a prior and posterior folder
	cd ..
done

# TODO: create smc.slurm and td.slurm and td-true.slurm files
