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

	# replace relative rates in conf file
	sed -i "/^relative_rates/c\\$rates" proj.conf

	# remove all subset lines and rewrite them
	ntotal_loci=$(echo "scale=4; $nslow_loci + $nfast_loci" | bc)
	sed -i "/^subset/d" proj.conf

	begin_subset=1
	end_subset=1000 # for now, assuming all loci are 1000 bp's
	for (( v = 1; v <=$ntotal_loci; v++ ))
	do
		string="subset = locus$v[nucleotide]:$begin_subset-$end_subset"
		(( begin_subset+=1000 ))
		(( end_subset+=1000 ))
		echo $string >> proj.conf
	done

	# create a prior and posterior folder
	mkdir posterior
	cp proj.conf posterior/.

	mkdir prior
	cp proj.conf prior/.
	old_string="sample_from_prior = False" # modify proj.conf to sample from the prior
	new_string="sample_from_prior = True"
	sed -i "s/$old_string/$new_string/g" prior/proj.conf
	cd ..
	
	cd ..
done

# make new smc.slurm files
echo "#!/bin/bash" >> smc-post.slurm
echo "#SBATCH -p priority" >> smc-post.slurm
echo "#SBATCH -q pol02003sky" >> smc-post.slurm
echo "#SBATCH -A pol02003" >> smc-post.slurm
echo "#SBATCH --nodes=1" >> smc-post.slurm
echo "#SBATCH --ntasks=1" >> smc-post.slurm
echo "#SBATCH --cpus-per-task=5" >> smc-post.slurm
echo "#SBATCH --array=0-9%10" >> smc-post.slurm
echo "#SBATCH --job-name=smc" >> smc-post.slurm
echo "#SBATCH -o smc-%a.out" >> smc-post.slurm
echo "#SBATCH -e smc-%a.err" >> smc-post.slurm
echo "#SBATCH --mem=50G" >> smc-post.slurm
echo " " >> smc-post.slurm
echo 'LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$HOME/lib"' >> smc-post.slurm
echo "export TIMEFORMAT=\"user-seconds %3U\"" >> smc-post.slurm
echo 'cd $HOME/g/rep1/rb/smc-cutoff-0.${SLURM_ARRAY_TASK_ID}/posterior' >> smc-post.slurm
echo "time mixing-smc" >> smc-post.slurm

echo "#!/bin/bash" >> smc-prior.slurm
echo "#SBATCH -p priority" >> smc-prior.slurm
echo "#SBATCH -q pol02003sky" >> smc-prior.slurm
echo "#SBATCH -A pol02003" >> smc-prior.slurm
echo "#SBATCH --nodes=1" >> smc-prior.slurm
echo "#SBATCH --ntasks=1" >> smc-prior.slurm
echo "#SBATCH --cpus-per-task=5" >> smc-prior.slurm
echo "#SBATCH --array=0-9%10" >> smc-prior.slurm
echo "#SBATCH --job-name=smc" >> smc-prior.slurm
echo "#SBATCH -o smc-%a.out" >> smc-prior.slurm
echo "#SBATCH -e smc-%a.err" >> smc-prior.slurm
echo "#SBATCH --mem=50G" >> smc-prior.slurm
echo " " >> smc-prior.slurm
echo 'LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$HOME/lib"' >> smc-prior.slurm
echo "export TIMEFORMAT=\"user-seconds %3U\"" >> smc-prior.slurm
echo 'cd $HOME/g/rep1/rb/smc-cutoff-0.${SLURM_ARRAY_TASK_ID}/prior' >> smc-prior.slurm
echo "time mixing-smc" >> smc-prior.slurm

cp ../../smc.slurm .
# delete unnecessary lines
sed -i "/^#SBATCH --array/d" smc.slurm
sed -i "/^cd/d" smc.slurm
sed -i "/^time/d" smc.slurm
echo

# TODO: create smc.slurm and td.slurm and td-true.slurm files
