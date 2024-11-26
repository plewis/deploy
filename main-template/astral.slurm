#!/bin/bash

#SBATCH -p priority
#SBATCH -q pol02003sky
#SBATCH -A pol02003
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --array=1-__NJOBS__%36
#SBATCH --job-name=astral
#SBATCH -o astral-%a.out
#SBATCH -e astral-%a.err
#SBATCH --mem=10G

export TIMEFORMAT="user-seconds %3U"
cd $HOME/__MAINDIR__/rep${SLURM_ARRAY_TASK_ID}/astral
time __PAUP_PATH__ mlgenetrees.nex
time java -jar __ASTRAL_PATH__ -i genetrees.txt -a mapfile.txt 2> astral-output-rep${SLURM_ARRAY_TASK_ID}.txt

