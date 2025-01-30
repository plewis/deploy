import subprocess as sub
import sys,os,re,math,shutil
import setupsubst

# Specify NetID of user (this is for specifying home directories and choosing among template files)
#user = 'pol02003'
user = 'jjc23002'
#user = 'aam21005'

# Specify local = True if testing on your local laptop; if running on cluster set local = False
local = True

# This directory will be created and will contain the master slurm scripts as well
# as a subdirectory for every simulation replicate
maindir = 'g'

# Specify the master pseudorandom number seed
master_seed = 97531

# Specify whether grid should be theta vs lambda or theta/2 vs T (=species tree height)
theta_vs_lambda = False

#########
# Paths #
#########

if user == 'pol02003':
    if local:
        simulator_path = 'smc6'
        smc_path       = 'smc6'
        beast_path     = '/Applications/BEAST\ 2.7.7/bin/beast'
        astral_path    = '/Users/plewis/Documents/software/astral/astral.5.7.8.jar'
        paup_path      = 'paup'
    else:
        simulator_path = '/home/pol02003/bin/smc6'
        smc_path       = '/home/pol02003/bin/smc6'
        beast_path     = '/home/pol02003/beast/bin/beast'
        astral_path    = '/home/pol02003/Astral/astral.5.7.1.jar'
        paup_path      = '/home/pol02003/bin/paup'
elif user == 'aam21005':
    if local:
        simulator_path = 'smc'
        smc_path       = 'smc'
        beast_path     = '/Applications/BEAST\ 2.7.6/bin/beast'
        astral_path    = '/Users/analisamilkey/Documents/software/Astral/astral.5.7.1.jar'
        paup_path      = 'paup4a168_osx'
    else:
        simulator_path = 'single-smc'
        smc_path       = 'single-smc'
        beast_path     = '/home/aam21005/beast/bin/beast'
        astral_path    = '/home/aam21005/ASTRAL-5.7.1/Astral/astral.5.7.1.jar'
        paup_path      = 'paup4a168_centos64'
elif user == 'jjc23002':
# do not use local
    if local: 
        simulator_path = 'smc'
        smc_path       = 'smc'
        beast_path     = 'path_to_beast'
        astral_path    = 'path_to_astral'
        paup_path      = 'path_to_paup'
    else:
        simulator_path = '/home/jjc23002/bin/smc'
        smc_path       = '/home/jjc23002/bin/smc'
        beast_path     = '/home/jjc23002/beast/bin/beast'
        astral_path    = '/home/jjc23002/ASTRAL-5.7.1/Astral/astral.5.7.1.jar'
        paup_path      = '/home/jjc23002/bin/paup'

#######################
# Simulation settings #
#######################

# Whether to use FASTA or NEXUS format for individual locus-specific data files
useFASTA = True

# No. points along the x and y axes
ngridpoints = 2

# If ngridpoints > 1, this option is ignored and nreps is
# instead set to ngridpoints^2
nreps = 1

nloci           = 10
min_sites_per_locus = 500
max_sites_per_locus = 500

# Variance of lognormal distribution governing variation
# among rates on each edge of a gene tree. The mean rate
# is 1.0 because these are relative rates.
min_edge_rate_variance = 0.0
max_edge_rate_variance = 0.0

# Shape of Gamma distribution determining relative rates among loci
# Mean must equal 1, so scale=1/shape and variance = shape*scale^2 = 1/shape
subset_relrate_shape = 10000.0

# Shape of Gamma distribution determining relative rates among sites
# within loci. Mean must equal 1, so scale = 1/shape and variance = shape*scale^2 = 1/shape
min_asrv_shape = 10000.0
max_asrv_shape = 10000.0

# Occupancy is the probability that a particular taxon will
# be included for a particular gene. 1.0 means there will be
# data for all taxa in all genes. 0.9 means that, on average,
# 10% of taxa will have all missing data for any given locus
min_occupancy = 1.0
max_occupancy = 1.0

# Compositional heterogeneity is determined by a Dirichlet(a,a,a,a)
# distribution for any given locus. For example, setting 
# comphet = 1000 will ensure that piA, piC, piG, piT are all
# very nearly 0.25 for a locus, while comphet = 1 results in
# a completely unpredictable set of equilibrium base frequencies
# for a locus.
min_comphet = 10000
max_comphet = 10000

species            = ['A', 'B', 'C', 'D', 'E']
indivs_for_species = [ 2,   2,   2,   2,   2]

if theta_vs_lambda:
    # Average distance between two leaves in a gene tree
    # Average height to first coalescence
    # within a species in which n genes 
    # were sampled is theta/[n*(n-1)]:
    #  theta       n=2       n=3       n=4
    #   0.01   0.00500   0.00167   0.00083
    #   0.05   0.02500   0.00833   0.00417
    #   0.10   0.05000   0.01667   0.00833
    
    theta_min = 0.05
    theta_max = 0.05
    
    # Average height to first speciation event for n species
    # is 1/[n*lambda]:
    #  lambda         n=5    n=10       n=15
    #       1      0.2000   0.10000  0.06667
    #      10      0.0200   0.01000  0.00667
    #     100      0.0020   0.00100  0.00067
    #    1000      0.0002   0.00010  0.00007
    
    lambda_min = 10
    lambda_max = 10
else:
    # Average distance between two leaves in a gene tree
    # Average height to first coalescence
    # within a species in which n genes 
    # were sampled is (theta/2)/[n*(n-1)/2]:
    #  half_theta    n=2       n=3       n=4
    #        0.01   0.01   0.00333   0.00167
    #        0.05   0.05   0.01667   0.00833
    #        0.10   0.10   0.03333   0.01667
    #        0.15   0.15   0.05000   0.02500
    
    half_theta_min = 0.01
    half_theta_max = 0.15
    
    # Average height to first speciation event:
    # n =  5: suminv = 1.28333333 = 1/2 + 1/3 + 1/4 + 1/5
    # n = 10: suminv = 1.92896825 = 1/2 + 1/3 + 1/4 + 1/5 + 1/6 + 1/7 + 1/8 + 1/9 + 1/10
    # n = 15: suminv = 2.31822899 = 1/2 + 1/3 + 1/4 + 1/5 + 1/6 + 1/7 + 1/8 + 1/9 + 1/10 + 1/11 + 1/12 + 1/13 + 1/14 + 1/15 
    # T = suminv/lambda, so lambda = suminv/T
    # Height to first speciation event is 1/[n*lambda] = T/[n*suminv] 
    #    T        n=5                           n=10                            n=15
    #  1.0    0.15584 = 1.0/(5*1.28333333)   0.05184 = 1.0/(10*1.92896825)   0.02876 = 1.0/(15*2.31822899)
    #  0.8    0.12468 = 0.8/(5*1.28333333)   0.04147 = 0.8/(10*1.92896825)   0.02301 = 0.8/(15*2.31822899)
    #  0.6    0.09351 = 0.6/(5*1.28333333)   0.03110 = 0.6/(10*1.92896825)   0.01725 = 0.6/(15*2.31822899)
    #  0.4    0.06234 = 0.4/(5*1.28333333)   0.02074 = 0.4/(10*1.92896825)   0.01150 = 0.4/(15*2.31822899)
    #  0.2    0.03117 = 0.2/(5*1.28333333)   0.01037 = 0.2/(10*1.92896825)   0.00575 = 0.2/(15*2.31822899)
    
    T_min = 0.1
    T_max = 1.0
    
if user == 'aam21005' or user == 'jjc23002':
    sim_save_gene_trees_separately = True

################
# SMC settings #
################

# Determines values of theta and lambda provided to BEAST and SMC
# If True, use SVD-qage estimates of theta and lambda
# If False, use true theta and lambda
smc_use_svdq_estimates = True 

smc_nparticles        = 1
smc_nspeciesparticles = 1000
if user == 'aam21005' or user == 'jjc23002':
    smc_thin			  = 1.0
    smc_saveevery		  = 1
    smc_nthreads		  = 7
    smc_savegenetrees	  = False
    smc_savememory		  = False
    smc_speciestreefile   = 'species_trees.trees'
    smc_genenewicks		  = True
    smc_newickpath		  = "../sim"
elif user == 'pol02003':
    smc_nkept             = 50
    smc_nspeciesparticles = 200
    smc_nspecieskept      = 50
    smc_speciestreefile   = '2nd-final-species-trees.tre'
else:
    assert False, 'user must be either pol02003 or aam21005 or jjc23002'

##################
# BEAST settings #
##################

beast_chainlength     =  10000 # 10000000
beast_preburnin       =  1000  # 1000000
beast_storeevery      =  10    # 10000
beast_logevery        =  10    # 10000
beast_lambda		  =  10
beast_thetamean		  =  4.0

###########################################
# Calculated from settings provided above #
###########################################

if ngridpoints > 1:
    nreps = ngridpoints*ngridpoints
    
subset_relrate_scale = 1.0/subset_relrate_shape

def run(maindir, nreps):
    print('  setting up main directory')
    
    ##############################
    # Set up ASTRAL slurm script #
    ##############################
    astral_slurm_path = os.path.join(maindir, 'astral.slurm')
    setupsubst.substitutions({
        '__ASTRAL_PATH__': astral_path,
        '__PAUP_PATH__': paup_path,
        '__NJOBS__': nreps,
        '__MAINDIR__': maindir
        }, astral_slurm_path, astral_slurm_path)
                
    ###########################
    # Set up SMC slurm script #
    ###########################
    smc_slurm_path = os.path.join(maindir, 'smc.slurm')
    setupsubst.substitutions({
        '__SMC_PATH__': smc_path,
        '__NJOBS__': nreps,
        '__MAINDIR__': maindir
        }, smc_slurm_path, smc_slurm_path)

    #############################
    # Set up BEAST slurm script #
    #############################
    beast_slurm_path = os.path.join(maindir, 'beast.slurm')
    setupsubst.substitutions({
        '__BEAST_PATH__': beast_path,
        '__NJOBS__': nreps,
        '__MAINDIR__': maindir
        }, beast_slurm_path, beast_slurm_path)
        
    ############################
    # Set up SVDQ slurm script #
    ############################
    svdq_slurm_path = os.path.join(maindir, 'svdq.slurm')
    setupsubst.substitutions({
        '__PAUP_PATH__': paup_path,
        '__NJOBS__': nreps,
        '__MAINDIR__': maindir
        }, svdq_slurm_path, svdq_slurm_path)
        
    ##############################
    # Set up summarize.py script #
    ##############################
    nspp_str = '%d' % (len(species),)
    summarize_path = os.path.join(maindir, 'summarize.py')
    setupsubst.substitutions({
        '__PLOT_THETA_VS_LAMBDA__': theta_vs_lambda and 'True' or 'False',
        '__NUM_SPECIES__': nspp_str,
        '__PAUPPATH__': paup_path,
        '__NREPS__': nreps,
        '__AAM21005__': user == 'aam21005',
        '__JJC23002__': user == 'jjc3002',
        '__POL02003__': user == 'pol02003'
        }, summarize_path, summarize_path)
        
    ##############################
    # Set up summarize-galax.py script #
    ##############################
    nspp_str = '%d' % (len(species),)
    summarize_path = os.path.join(maindir, 'summarize-galax.py')
    setupsubst.substitutions({
        '__PLOT_THETA_VS_LAMBDA__': theta_vs_lambda and 'True' or 'False',
        '__NUM_SPECIES__': nspp_str,
        '__NREPS__': nreps,
        '__AAM21005__': user == 'aam21005',
        '__JJC23002__': user == 'jjc3002',
        '__POL02003__': user == 'pol02003'
        }, summarize_path, summarize_path)
        
    #########################################
    # Set up theta-lambda-svdqage.py script #
    #########################################
    theta_lambda_svdqage_path = os.path.join(maindir, 'theta-lambda-svdqage.py')
    setupsubst.substitutions({
        '__NREPS__': nreps,
        '__AAM21005__': user == 'aam21005',
        '__JJC23002__': user == 'jjc3002',
        '__POL02003__': user == 'pol02003'
        }, theta_lambda_svdqage_path, theta_lambda_svdqage_path)
        
    ###########################
    # Set up rfsmc.nex script #
    ###########################
    rfsmc_path = os.path.join(maindir, 'rfsmc.nex')
    smc_samplesize = 0
    if user == "pol02003":
        smc_samplesize = smc_nkept * smc_nspecieskept
    elif user == "aam21005" or user == "jjc23002":
        smc_samplessize = smc_nparticles * smc_thin * smc_nspeciesparticles / smc_saveevery
    setupsubst.substitutions({
        '__MAXTREES__': smc_samplesize + 1
        }, rfsmc_path, rfsmc_path)

    #############################
    # Set up rfbeast.nex script #
    #############################
    rfbeast_path = os.path.join(maindir, 'rfbeast.nex')
    beast_samplesize = int(beast_chainlength/beast_storeevery)
    setupsubst.substitutions({
        '__MAXTREES__': beast_samplesize + 1
        }, rfbeast_path, rfbeast_path)
        
    #########################################
    # Set up writegalax.py script #
    #########################################
    write_galax_path = os.path.join(maindir, 'writegalax.py')
    setupsubst.substitutions({
        '__NREPS__': nreps,
        }, write_galax_path, write_galax_path)
