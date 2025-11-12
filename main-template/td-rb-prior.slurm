#!/bin/bash

#SBATCH -p priority
#SBATCH -q pol02003sky
#SBATCH -A pol02003
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=5
#SBATCH --array=1-__SMCNLOCI__%10
#SBATCH --job-name=tdrbprior
#SBATCH -o tdrbprior-%a.out
#SBATCH -e tdrbprior-%a.err
#SBATCH --mem=150G

LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$HOME/lib"
export TIMEFORMAT="user-seconds %3U"
cd $HOME/__MAINDIR__/rep1/rb/gene${SLURM_ARRAY_TASK_ID}/output-prior
__TD_PATH__ --treefile gene${SLURM_ARRAY_TASK_ID}.trees --frechetmean --prefix mean  --frechet-k 1000000 --frechet-n 10 --frechet-e 0.001  --rooted true
