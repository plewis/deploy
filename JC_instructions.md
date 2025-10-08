## instructions for running information content experiments

## Here is some information about the scripts.

## Deploy script

The _deploy.py_ script generates a directory structure comprising n replicate subdirectories, each containing a simulated data set and directories for various analyses of that dataset.

To deploy, simply type

    python3 deploy.py
    
This will only work if you have set up the directories _main-template_, _rep-template_, and _setup_ first.

### main-template

Place here any files that need to be at the outer level of the directory created. For example, a slurm script specifying an array job for carrying out a particular kind of analysis should be placed here.

### rep-template

This directory will be copied n times to create n simulate replicates. For example,

    rep-template
        astral
        beast
        smc
        sim

Don't worry about the astral and beast directories for now.

### setup

This directory contains python module files that set up each replicate once the _rep-template_ directory has been copied.

#### setupmain.py

This python module file must have a `run` function that takes 2 arguments that is used to set up
the files copied from _main-template_. The arguments are:

* `maindir` is the parent directory of all the replicate subdirectories (e.g. "g")
* `nreps` is the number of replicates (e.g. 49)

#### setuprep.py

This python module must have a `run` function that takes the following 5 arguments:

* `rep` is the replicate index (i.e. a value in the range 1, 2, ..., nreps)
* `nreps` is the number of replicates (e.g. 49)
* `maindir` is the parent directory of all the replicate subdirectories (e.g. "g")
* `repdir` is the subdirectory of `maindir` corresponding to `rep` (e.g. "rep1")
* `rnseed` is the pseudorandom number seed to use for this replicate

It is up to you to use the arguments provided to set up one replicate in this function.


## Here are the instructions for setting up a run. These instructions assume you have compiled the `SMC` program, `PAUP*`, and `galax` on the cluster.

Request an interactive node with:
`srun --ntasks=1 --nodes=1 --partition=general --pty bash`

Open the script `setupmain.py` under the `setup` folder. Change `user =`  to your username under the section starting with `Specify NetID of user`. You can comment out the user names you are not using with a #.

Specify
* `local = False` 
on line 11 (section starting with `Specify local = True if....`. This tells the program you are going to run the simulations on the remote cluster.

On line 21, specify 
* `theta_vs_lambda = False`
(section starting with `Specify whether grid should be...`). This tells the program we will choose parameters based on theta / 2 and species tree height.

Under the Paths section (line 24), find the section corresponding to your user name. We are not using your local computer to do anything right now, so you can skip to the section that says "else:" (this corresponds to paths on the remote cluster).
* `simulator_path`
* `smc_path`
should both correspond to the path of the SMC program on the cluster.

* `paup_path`
should correspond to the path of the PAUP* program on the  cluster,

Don't worry about these settings for now:
* `beast_path`
* `astral_path`

Under the Simulation settings section (line 69), you can specify the parameters for the simulations. 
The important parameters to set right now are:
* `ngridpoints`
* `nloci`
* `species`
* `indivs_for_species`

For now, you can set
* `ngridpoints = 10`
* `nloci = 10`
`ngridpoints` sets the square of the number of simulations to conduct (i.e. `ngridpoints = 10` will result in 100 simulations). `nloci` sets the number of loci to use in each simulation.\

You can keep the following settings as they are right now:
* `species`
* `indivs_for_species`

`species            = ['A', 'B', 'C', 'D', 'E']` and `indivs_for_species = [ 2,   2,   2,   2,   2]`). `species` sets the number of species in the species trees, and `indivs_for_species` sets the number of taxa in the gene trees per species.

Because you should have already specified `theta_vs_lambda = False`, any changes you make between lines 120 and 142 (starting with `if theta_vs_lambda`) will be ignored. You can change the parameter values starting after the 'else:' on line 143:
* `half_theta_min`
* `half_theta_max`
* `T_min`
* `T_max`

Decreasing `half_theta_max` and `T_max` will make the problems harder. For now, you can keep the values as they are or change them.

There are 2 kinds of experiments we can specify under the section `SMC settings`. You can modify the parameters under the section that includes your username (starting on line 187):

For both experiments, you can set
* `smc_nthreads = 36`

This will allow the cluster to use all processors that are available to you.

1. Give the SMC program the true gene trees and have it estimate the species tree. To do this, set
* `smc_genenewicks = True`
* `smc_nparticles = 1`
* `smc_thin = 1.0`
* `smc_nspeciesparticles = 1000`
* `smc_saveevery = 1.0`

(For now, use 'smc_nspeciesparticles = 1000'? Increasing this number will take longer but may be more accurate.)

2. Give the SMC program the raw data and have it estimate the gene trees and the species tree. To do this, set
* `smc_genenewicks = False`
* `smc_nparticles = 10000`
* `smc_nspeciesparticles = 1000`
* `smc_thin = 0.1`
* `smc_saveevery = 100`

(For now, use 'smc_nparticles = 10000'? Increasing this number will take longer but may be more accurate.)\
(For now, use 'smc_nspeciesparticles = 1000'? Increasing this number will take longer but may be more accurate.)\
(For now, use 'smc_thin = 0.1'? Increasing this number will take longer but will give you more samples.)\
(For now, use 'smc_saveevery = 100'? Decreasing this number will give you more samples.)\n


You can ignore the section `BEAST settings`.

You can also ignore the section `Calculated from settings provided above`. This will set up the directories to run your experiments.

## Here are the instructions for running the simulations. These instructions assume `setupmain.py` is set up.

Run the deploy script using the command

	python3 deploy.py

Note you must be in the same directory as `deploy.py`. If you are in the 'setup' directory, you may have to use
	
	cd ..
	
to return to the deploy directory.

You should now have a directory named `g`. If you have an existing `g` directory, you will have to remove it (`rm -rf g`) or rename it (`mv g new-name`). Be sure you don't actually want the directory before removing it, since this action is permanent.

It may be a good idea to save the `setupmain.py` file so we can recreate the analyses if we need to:

	cp setup/setupmain.py g/.

Move the 'g' directory to your home using the command:
	
	mv g ~

Now cd into the 'g' directory:
	
	cd ~/g

Now run some scripts to replace place-holder values in the template files:
	
	. svdq.sh
	python3 theta-lambda-svdqage.py
	
Now run the SMC program:
	
	sbatch smc.slurm

You can check the status of your jobs using:
	
	sacct -A pol02003

When the jobs have finished, summarize the results by running the scripts
	
	paup rfsmc.nex
	python3 summarize.py

This will calculate Robinson-Foulds (RF) distances between the trees the SMC program sampled and the true tree and summarize the results. If you get a message "The limit of 1 tree (= 'Maxtrees') has been reached.  Do you want to increase Maxtrees?", you can type 'y'. If you then get the message 'Enter new value for 'Maxtrees' (101):'', type any value over 101, then type '2' to automatically increase the number of trees. You can ignore any errors about ASTRAL or BEAST trees not found since you did not run those programs.
  

Now you can run galax on the results:
	
	python3 writegalax.py
	. rungalax.sh
	python3 summarize-galax.py


You can now transfer the file `plot-galax.Rmd` to your local laptop using the instructions at [this link](https://kb.uconn.edu/space/SH/26033783688/File+Transfer) You can then run the file in RStudio to  visualize the results.


# slow genes
To use a slower rate for a random proportion of loci:

Follow all the above instructions, except in setupmain.py, set `slowloci = True`.

After running all the above scripts, run:
	python3 summarize-galax-slowloci.py

 And move the file `plot-galax-slow.Rmd` to your computer.

# BHV information content
To use the new BHV geodesic distance metric:

Run one set of analyses under the prior and rename the directory g-prior. (to run analyses under the prior, modify the line in `setup/setupmain.py` that says sample_from_prior = false to sample_from_prior = true.

Run second set of analyses under the posterior and rename the directory g-posterior.

For each directory, run sbatch td.slurm. This will run the treedistance program and create a file called mean.txt in each 'smc' replicate directory.

Create a new directory (`g-bhv`) and move both `g-prior` and `g-posterior` into this directory. Move 'calculate-information-hpd.py' into this directory from `g-prior` (mv g-prior/calculate-information-hpd.py .)

Before running the smc analyses, you will have to modify the following files with their correct path:
in `g-posterior`:
	`smc.slurm`
 	`td.slurm`
  	`td-true.slurm`

in `g-prior`:
	`smc.slurm`
 	`td.slurm`
Run sbatch smc.slurm for both g-prior and g-posterior directories. Once these analyses have finished, run sbatch td.slurm in each directory. In `g-posterior`, run `python3 create-bhv-files.py` and then also run `sbatch td-true.slurm`.


Run information calculation in the `g-bhv` directory: python3 calculate-information-hpd.py

Move info.txt into `g-posterior`. Calculate BHV distances between true tree and sampled trees.

Run `python3 summarize-bhv-info.py`. Transfer the output file `plot-bhv-info.Rmd` to your local laptop.


# RevBayes information content (use RevBayes to analyze individual loci, then calculate information content and use it to decide which loci to include in the species tree analysis)
You can set up the deploy script as normal, but we will only work with directory `rep`<br>

Change 'rep-template/sim/.conf' - add correct number of slow loci and comment out the existing number.<br>
After setting up the g directory, run '. create-rb-folders.sh'<br>
run `sbatch rb-prior.slurm`<br>
run `sbatch rb-post.slurm`<br>

run `sbatch td-rb-prior.slurm`<br>
run `sbatch td-rb-post.slurm`<br>

cd into `rep1/rb` directory and run `python3 calc-info-radius-rb.py`<br>

This will create a file called `info.txt` that lists information content in each locus. The first half are the slow rate loci.<br>

Open the file `process-info.py` and replace `cutoff_value` with the value you want.<br>
Then run `python3 process-info.py`.<br>
This will create a file that begins with `remove`.<br>
This file will later be run to delete all loci with information below the cutoff value.<br>

Then do the following by hand:<br>
`cd ..`<br>
Make a new directory and name it appropriately (ex. `mkdir smc-0.8-cutoff`)<br>
Copy all the loci from the `astral` directory into your new directory (ex. `cp astral/*.nex smc-0.8-cutoff`)<br>
`cd` into your new directory.<br>
Remove the `concat.nex` and `mlgenetrees.nex` file (`rm concat.nex` `rm mlgenetrees.nex`)<br>
Copy the `remove` script you created into your new directory (ex. `cp ../rb/remove0.8.sh .`)<br>
Then run the `remove` script (ex. `. remove0.8.sh`)<br>
Copy the `crunch.py` file from the `rb` directory into the current directory. (`cp ../rb/crunch.py .`)<br>

Now you are ready to run the SMC analyses. You will need to run under the prior and posterior.<br>

You will need to copy and modify the `proj.conf` file:<br>
`cp ../smc/proj.conf .`<br>
Open `proj.conf` and change `datafile  = ../sim/sim.nex` to `datafile = ../COMBINED.nex`<br>

The last thing is to change the `relative_rates` line of the `proj.conf` to reflect the deleted loci:<br>
Copy the corresponding file from the `rb` directory: `cp ../rb/calc-adjusted-rel-rates.py .`<br>
Modify this file to have the correct number of slow and fast loci. You can look in the `removexx.sh` file to figure this out. Remember the first half of the original loci are the slow rates ones (if there were 10 loci originally, the first 5 were slow). For example, if the `removexx.sh` file says this, and there were 10 loci originally:<br>

`rm locus1.nex<br>
rm locus2.nex<br>
rm locus3.nex<br>
rm locus4.nex`<br>

This means 4 of the 5 slow loci were removed, and 0 of the 5 faster loci were removed.<br>
The first two lines of the `calc-adjusted-rel-rates.py` file should say:<br>

`nslow = 1<br>
nfast = 5`<br>

Copy the output and replace the line `relative_rates = ` in the `proj.conf` file with the new output.<br>

The total number of new loci equals `nslow + nfast`.<br>
Remove any extra subsets from the `proj.conf` file.<br>
For example, if the top of the `proj.conf` file looked like this previously:<br>

`subset = locus1[nucleotide]:1-1000`<br>
`subset = locus2[nucleotide]:1001-2000`<br>
`subset = locus3[nucleotide]:2001-3000`<br>
`subset = locus4[nucleotide]:3001-4000`<br>
`subset = locus5[nucleotide]:4001-5000`<br>
`subset = locus6[nucleotide]:5001-6000`<br>
`subset = locus7[nucleotide]:6001-7000`<br>
`subset = locus8[nucleotide]:7001-8000`<br>
`subset = locus9[nucleotide]:8001-9000`<br>
`subset = locus10[nucleotide]:9001-10000`<br>

You will need to delete loci 7-10 so the correct number of subsets remain:<br>
`subset = locus1[nucleotide]:1-1000`<br>
`subset = locus2[nucleotide]:1001-2000`<br>
`subset = locus3[nucleotide]:2001-3000`<br>
`subset = locus4[nucleotide]:3001-4000`<br>
`subset = locus5[nucleotide]:4001-5000`<br>
`subset = locus6[nucleotide]:5001-6000`<br>

Now make one directory called `posterior` and one called `prior`.<br>
Copy the `proj.conf` file into both (`cp proj.conf posterior` `cp proj.conf prior`.<br>

cd into the `posterior` directory.<br>
Copy the `smc.slurm` file from the `g` directory: `cp ../../../smc.slurm .`<br>
Edit this file to reflect the current directory by removing the line `cd $HOME/g/rep${SLURM_ARRAY_TASK_ID}/smc` since you will run this in the current directory.<br>
Also remove the line `#SBATCH --array=1xxx` since there is only one job to run now. Then start the analysis (`sbatch smc.slurm`).<br>

Once this analysis is done, run the treedistance program on the results:<br>
`cp ../../../td.slurm .`<br>
`cp ../../../td-true.slurm .`<br>

Make a new tree file that the treedistance program can read:<br>
`cp species_trees.trees bhv_trees.tre`<br>

Now get the true species tree file:<br>
`cat ../../sim/true-species-tree.tre`<br>
Copy the output line `tree test = [&R]..... );`<br>
Open the `bhv_trees.tre` file and insert it as the first line after the `begin trees;` line.<br>

Now edit the `td.slurm` and `td-true.slurm` files:<br>
delete the lines `#SBATCH --array=1xxx` and `cd $HOME/g/rep${SLURM_ARRAY_TASK_ID}/smc`<br>

Then run these analyses:<br>
`sbatch td.slurm`<br>
`sbatch td-true.slurm`<br>

When these analyses are done, get the average distance to the true tree:<br>
`cp ../../rb/get-bhv-mean.Rmd .`<br>
`Rscript get-bhv-mean.Rmd`<br>

Record this number. This is the species tree accuracy.<br>

cd into the `prior` directory (`cd ../prior`).<br>
Modify the line in the `proj.conf` file that says `sample_from_prior = False` to `sample_from_prior = True`.<br>
Copy the `smc.slurm` file from `posterior` into the current `prior` directory (`cp ../posterior/smc.slurm .`)<br>
Run the `smc.slurm` file (`sbatch smc.slurm`)<br>

Also copy the `td.slurm` file from the `posterior` directory (`cp ../posterior/td.slurm .`) Then run this analyses:<br>
`sbatch td.slurm`<br>

Once these analysis are done, `cd ..` (back into the `smc-xx-cutoff` directory) <br>

Now you will run the treedistance program again on these results to get information content and accuracy for the species trees sampled:<br>

`cp ../../td.slurm .`<br>
cp ../../td-true.slurm .`<br>

Now calculate information content:<br>
`cp ../../calculate-information-slow.py .`<br>
Run this file:<br>
`python3 calculate-information-slow.py`<br>

This will write the information data to a file called `info.txt`. <br>
`cat info.txt` to see this number and record it.<br>

Ideally, you will do this for different cutoff values and end up with a table like this:

    | cutoff value      | accuracy   | information  |
    | 0.1   			| xx 		 | xx   		|
    | 0.2  				| xx  		 | xx   		|
	| 0.3  				| xx  		 | xx   		|
	| 0.4  				| xx  		 | xx   		|
	| 0.5  				| xx  		 | xx   		|
	| 0.6  				| xx  		 | xx   		|
	| 0.7  				| xx  		 | xx   		|
	| 0.8  				| xx  		 | xx   		|
	| 0.9  				| xx  		 | xx   		|
	| 1.0  				| xx  		 | xx   		|
