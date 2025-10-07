#!/bin/bash

#SBATCH -p priority
#SBATCH -q pol02003sky
#SBATCH -A pol02003
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=5
#SBATCH --array=1-__SMCNLOCI__%10
#SBATCH --job-name=rbpost
#SBATCH -o rbpost-%a.out
#SBATCH -e rbpost-%a.err
#SBATCH --mem=150G

LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$HOME/lib"
cd $HOME/__MAINDIR__/rep1/rb/gene${SLURM_ARRAY_TASK_ID}
rb jc-post.Rev
