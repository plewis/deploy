#!/bin/bash

#SBATCH -p priority
#SBATCH -q pol02003sky
#SBATCH -A pol02003
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=5
#SBATCH --array=1-__NJOBS__%10
#SBATCH --job-name=td
#SBATCH -o td-%a.out
#SBATCH -e td-%a.err
#SBATCH --mem=150G

LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$HOME/lib"
export TIMEFORMAT="user-seconds %3U"
cd $HOME/__MAINDIR__/rep${SLURM_ARRAY_TASK_ID}/smc
__TD_PATH__ --treefile species_trees.trees --frechetmean --prefix mean  --frechet-k 1000000 --frechet-n 10 --frechet-e 0.00001
