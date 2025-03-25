#!/bin/bash

#SBATCH -p priority
#SBATCH -q pol02003sky
#SBATCH -A pol02003
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=5
#SBATCH --array=1-__NJOBS__%10
#SBATCH --job-name=smc
#SBATCH -o smc-%a.out
#SBATCH -e smc-%a.err
#SBATCH --mem=150G

LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$HOME/lib"
export TIMEFORMAT="user-seconds %3U"
cd $HOME/__MAINDIR__/rep${SLURM_ARRAY_TASK_ID}/smc
time __SMC_PATH__
