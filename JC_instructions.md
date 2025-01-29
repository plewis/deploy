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


## Here are the instructions for setting up a run. These instructions assume you have compiled the SMC program, PAUP*, and galax on the cluster.

Open the script 'setupmain.py' under the 'setup' folder. Change 'user = ' to your username under the section starting with 'Specify NetID of user.' You can comment out the user names you are not using with a #.

Specify local = False on line 11 (section starting with 'Specify local = True if....'). This tells the program you are going to run the simulations on the remote cluster.

On line 21, specify theta_vs_lambda = False (section starting with 'Specify whether grid should be...'). This tells the program we will choose parameters based on theta / 2 and species tree height.

Under the Paths section (line 24), find the section corresponding to your user name. We are not using your local computer to do anything right now, so you can skip to the section that says "else:" (this corresponds to paths on the remote cluster). 'simulator_path' and 'smc_path' should both correspond to the path of the SMC program on the cluster. Don't worry about 'beast_path' and 'astral_path' for now. 'paup_path' should correspond to the path of the PAUP* program on the cluster.

Under the Simulation settings section (line 69), you can specify the parameters for the simulations. 
The important parameters to set right now are:
	ngridpoints =
	nloci =
	species =
	indivs_for_species = 

For now, you can set 'ngridpoints = 10' and 'nloci = 10'. ngridpoints sets the square of the number of simulations to conduct (i.e. 'ngridpoints = 10' will result in 100 simulations). 'nloci' sets the number of loci to use in each simulation. You can keep 'species' and 'indivs_for_species' as they are right now ('species            = ['A', 'B', 'C', 'D', 'E']' and 'indivs_for_species = [ 2,   2,   2,   2,   2]'). 'species' sets the number of species in the species trees, and 'indivs_for_species' sets the number of taxa in the gene trees per species.

Because you should have already specified theta_vs_lambda = False, any changes you make between lines 120 and 142 (starting with 'if theta_vs_lambda') will be ignored. You can change the parameter values starting after the 'else:' on line 143:
	half_theta_min =
	half_theta_max =
	T_min =
	T_max =
Decreasing half_theta_max and T_max will make the problems harder. For now, you can keep the values as they are or change them.

There are 2 kinds of experiments we can specify under the section 'SMC settings'. You can modify the parameters under the section that includes your username (starting on line 187):

1) Give the SMC program the true gene trees and have it estimate the species tree. To do this, set 'smc_genenewicks = True'. Set 'smc_nparticles = 1' and 'smc_thin = 1.0' and 'smc_saveevery = 1'. You can set 'smc_nspeciesparticles'. (For now, use 'smc_nspeciesparticles = 1000'? Increasing this number will take longer but may be more accurate.)

2) Give the SMC program the raw data and have it estimate the gene trees and the species tree. To do this, set 'smc_genenewicks = False'. You can set 'smc_nparticles'. (For now, use 'smc_nparticles = 10000'? Increasing this number will take longer but may be more accurate.) You can set 'smc_nspeciesparticles'. (For now, use 'smc_nspeciesparticles = 1000'? Increasing this number will take longer but may be more accurate.) You can also set 'smc_thin'. (For now, use 'smc_thin = 0.1'? Increasing this number will take longer but will give you more samples.) You can also set 'smc_saveevery'. (For now, use 'smc_saveevery = 100'? Decreasing this number will give you more samples.)

For both experiments, you can also set 'smc_nthreads = 36;. This will allow the cluster to use all processors that are available to you.

You can ignore the section 'BEAST settings'.

You can also ignore the section 'Calculated from settings provided above.' This will set up the directories to run your experiments.


## Here are the instructions for running the simulations. These instructions assume setupmain.py is set up.

Run the deploy script using the command
	python3 deploy.py

Note you must be in the same directory as deploy.py. If you are in the 'setup' directory, you may have to use
	cd ..
to return to the deploy directory.

You should now have a directory named 'g'. If you have an existing 'g' directory, you will have to remove it (rm -rf g) or rename it (mv g new-name). Be sure you don't actually want the directory before removing it, since this action is permanent.

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


You can now transfer the file 'plot-galax.Rmd' to your local laptop and run it in RStudio to  visualize the results.


