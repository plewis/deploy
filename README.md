## TODO

This readme files needs to be updated!

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
        
The _sim_ directory is where the simulated dataset will be created, and the _smc_, _beast_, and _astral_ directory contain files needed to carry out SMC, BEAST, and ASTRAL analyses of the simulated data.

### setup

This directory contains python module files that set up each replicate once the _rep-template_ directory has been copied. There are two python module files that are
required, but others can be added as helper modules for these two.

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

### Setup for testing on a local machine

This assumes you have Python 3, BEAST2, ASTRAL III, and PAUP* installed on your local machine.

Use the command 

    python3 deploy.py
    
to create the directory _g_. Move _g_ to your home directory:

    cd
    mv deploy2/g .

Navigate into _g_ and then issue these commands

    cd g
    . svdq.sh
    . beast.sh
    . astral.sh
    
If you have specified `True` for `smc_use_svdq_estimates` in setupmain.py, you will need to run the following command before running SMC. This specifies the SVD-qage estimates of both theta and lambda in the SMC proj.conf file:

    python3 theta-lambda-svdqage.py
    
Now you can run SMC as follows:

    . smc.sh
    
To summarize the output, run these commands:

    paup rfsmc.nex
    paup rfbeast.nex
    python3 summarize.py
    cat summary.txt
    
### Setup for running on a cluster

#### Install Beast2

Download _BEAST.v2.7.7.Linux.x86.tgz_ from [https://www.beast2.org/download-linux-x86/](https://www.beast2.org/download-linux-x86/)

Copy to cluster and untar into $HOME

    tar zxvf BEAST.v2.7.7.Linux.x86.tgz
    
You will also need to install the packages starbeast3 v1.1.8, BEASTLabs v2.0.2, and ORC v1.1.2 using the packagemanager script (see [https://www.beast2.org/managing-packages/](https://www.beast2.org/managing-packages/)):

		cd $HOME/beast/bin
		./packagemanager -dir /home/pol02003/beast-packages -add starbeast3

Modify last line of _beast/bin/beast_ start script to specify location of beast packages
		"$JAVA" -Dbeast.user.package.dir=/home/pol02003/beast-packages -Dlauncher.wait.for.exit=true ...

#### Install ASTRAL III

Download _ASTRAL-5.7.1.tar.gz_ from [https://github.com/smirarab/ASTRAL/releases/tag/v5.7.1](https://github.com/smirarab/ASTRAL/releases/tag/v5.7.1)

Copy to cluster and untar into $HOME, then unzip the embedded zip file _Astral.5.7.1.zip_ and move the resulting _Astral_ directory to $HOME.

    tar zxvf ASTRAL-5.7.1.tar.gz
    cd ASTRAL-5.7.1
    unzip Astral.5.7.1.zip
    mv Astral $HOME

Use the command 

    python3 deploy.py
    
to create the directory _g_. Move _g_ to your home directory:

    cd
    mv deploy2/g .

Navigate into _g_ and then issue these commands

    cd g
    module load gcc/14.2.0 tcl/8.6.12 sqlite3/3.45.2 python/3.12.5  openjdk/22
    sbatch svdq.slurm
    sbatch beast.slurm
    sbatch astral.slurm
    
If you have specified `True` for `smc_use_svdq_estimates` in setupmain.py, you will need to run the following command before running SMC. This specifies the SVD-qage estimates of both theta and lambda in the SMC proj.conf file:

    python3 theta-lambda-svdqage.py
    
Now you can run SMC as follows:

    sbatch smc.slurm
    
To summarize the output, login to node using `srun` and run these commands:

    srun --partition priority --qos pol02003sky --account pol02003 --pty bash 

    paup rfsmc.nex
    paup rfbeast.nex
    python3 summarize.py
    cat summary.txt



