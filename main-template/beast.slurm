#!/bin/bash

#SBATCH -p priority
#SBATCH -q pol02003sky
#SBATCH -A pol02003
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --array=1-__NJOBS__%36
#SBATCH --job-name=beast
#SBATCH -o beast-%a.out
#SBATCH -e beast-%a.err
#SBATCH --mem=150G

LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$HOME/lib"
export TIMEFORMAT="user-seconds %3U"
cd $HOME/__MAINDIR__/rep${SLURM_ARRAY_TASK_ID}/beast
time __BEAST_PATH__ starbeast.xml
