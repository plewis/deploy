import subprocess as sub
import sys,os,re,math,shutil,random
import copydata, setupsubst, setupmain

# scriptdir = os.path.dirname(os.path.realpath(sys.argv[0]))

def calcDimRowCol(rep, nreps):
    # If nreps = 9, then the grid is 3x3, where dim = sqrt(nreps) = 3
    # 
    # Assuming 
    #   x_min  = 0.001, x_max = 0.201, x_max - x_min = 0.200
    #   y_min = 0.100,  y_max = 1.100, y_max - y_min = 1.000
    #
    # rep  | row  = (rep-1)/3  |  col  = (rep-1)%3  |       x =   min + row*(max-min)/(dim-1) |      y = min + col*(max-min)/(dim-1) |
    #   1  |   0  =       0/3  |   0   =       0%3  |   0.001 = 0.001 +  0 *  0.200  /   2    |    0.1 = 0.1 +  0 *   1.0   /    2   | 
    #   2  |   0  =       1/3  |   1   =       1%3  |   0.001 = 0.001 +  0 *  0.200  /   2    |    0.6 = 0.1 +  1 *   1.0   /    2   |
    #   3  |   0  =       2/3  |   2   =       2%3  |   0.001 = 0.001 +  0 *  0.200  /   2    |    1.1 = 0.1 +  2 *   1.0   /    2   |
    #   4  |   1  =       3/3  |   0   =       3%3  |   0.101 = 0.001 +  1 *  0.200  /   2    |    0.1 = 0.1 +  0 *   1.0   /    2   |
    #   5  |   1  =       4/3  |   1   =       4%3  |   0.101 = 0.001 +  1 *  0.200  /   2    |    0.6 = 0.1 +  1 *   1.0   /    2   |
    #   6  |   1  =       5/3  |   2   =       5%3  |   0.101 = 0.001 +  1 *  0.200  /   2    |    1.1 = 0.1 +  2 *   1.0   /    2   |
    #   7  |   2  =       6/3  |   0   =       6%3  |   0.201 = 0.001 +  2 *  0.200  /   2    |    0.1 = 0.1 +  0 *   1.0   /    2   |
    #   8  |   2  =       7/3  |   1   =       7%3  |   0.201 = 0.001 +  2 *  0.200  /   2    |    0.6 = 0.1 +  1 *   1.0   /    2   |
    #   9  |   2  =       8/3  |   2   =       8%3  |   0.201 = 0.001 +  2 *  0.200  /   2    |    1.1 = 0.1 +  2 *   1.0   /    2   |

    dim = math.sqrt(nreps)    
    row = (rep-1)//dim
    col = (rep-1)%dim
        
    return (dim,row,col)

def readNexusFile(fn):
    '''
    Reads nexus file whose name is specified by fn and returns ntax, nchar, taxa, and a
    sequences dictionary with taxon names as keys. The values ntax and nchar are integers,
    while taxa is a list of taxon names in the order they were found in the taxa block or
    data block. Any underscores in taxon names are converted to spaces before being saved
    in the taxa list or as a key in the sequences dictionary. Also all nexus comments
    (text in square brackets) will be ignored.
    '''
    stuff = open(fn, 'r').read()
    mask = None

    # determine if taxa block exists
    taxa_block = None
    m = re.search(r'(?:BEGIN|Begin|begin)\s+(?:TAXA|Taxa|taxa)\s*;(.+?)(?:END|End|end)\s*;', stuff, re.M | re.S)
    if m is not None:
        taxa_block = m.group(1).strip()

    # determine if characters block exists
    characters_block = None
    m = re.search(r'(?:BEGIN|Begin|begin)\s+(?:CHARACTERS|Characters|characters)\s*;(.+?)(?:END|End|end)\s*;', stuff, re.M | re.S)
    if m is not None:
        characters_block = m.group(1).strip()

    # determine if data block exists
    data_block = None
    m = re.search(r'(?:BEGIN|Begin|begin)\s+(?:DATA|Data|data)\s*;(.+?)(?:END|End|end)\s*;', stuff, re.M | re.S)
    if m is not None:
        data_block = m.group(1).strip()

    if data_block is not None:
        # get ntax and nchar
        m = re.search(r'(?:DIMENSIONS|dimensions|Dimensions)\s+(?:NTAX|ntax|Ntax|NTax)\s*=\s*(\d+)\s+(?:NCHAR|nchar|Nchar|NChar)\s*=\s*(\d+)\s*;', data_block, re.M | re.S)
        assert m, 'Could not decipher dimensions statement in data block'
        ntax = int(m.group(1))
        nchar = int(m.group(2))

        # get matrix
        m = re.search(r'(?:MATRIX|matrix|Matrix)\s+(.+?)\s*;', data_block, re.M | re.S)
        assert m, 'Could not decipher matrix statement in data block'
        lines = m.group(1).strip().split('\n')
        taxa = []
        sequences = {}
        for line in lines:
            m = re.match(r'\[([-*]+)\]', line.strip())
            if m is not None:
                mask = m.group(1)
            else:
                stripped_line = re.sub(r'\[.+?\]', '', line).strip()
                if len(stripped_line) > 0:
                    parts = line.split()
                    assert len(parts) == 2, 'Found more than 2 parts to this line:\n%s' % line
                    taxon_name = re.sub(r'_', ' ', parts[0]).strip()
                    taxa.append(taxon_name)
                    sequences[taxon_name] = parts[1]
    else:
        assert characters_block is not None and taxa_block is not None, 'Assuming nexus file contains either a data block or a taxa block and characters block'

        # get ntax from taxa block
        m = re.search(r'(?:DIMENSIONS|dimensions|Dimensions)\s+(?:NTAX|ntax|Ntax|NTax)\s*=\s*(\d+)\s*;', taxa_block, re.M | re.S)
        assert m, 'Could not decipher dimensions statement in taxa block'
        ntax = int(m.group(1))

        # get nchar from characters block
        m = re.search(r'(?:DIMENSIONS|dimensions|Dimensions)\s+(?:NCHAR|nchar|Nchar|NChar)\s*=\s*(\d+)\s*;', characters_block, re.M | re.S)
        assert m, 'Could not decipher dimensions statement in characters block'
        nchar = int(m.group(1))

        # get matrix from characters block
        m = re.search(r'(?:MATRIX|matrix|Matrix)\s+(.+?)\s*;', characters_block, re.M | re.S)
        assert m, 'Could not decipher matrix statement in characters block'
        lines = m.group(1).strip().split('\n')
        taxa = []
        sequences = {}
        for line in lines:
            m = re.match(r'\[([-*]+)\]', line.strip())
            if m is not None:
                mask = m.group(1)
            else:
                stripped_line = re.sub(r'\[.+?\]', '', line).strip()
                if len(stripped_line) > 0:
                    parts = stripped_line.split()
                    assert len(parts) == 2, 'Found more than 2 parts to this line:\n%s' % line
                    taxon_name = re.sub(r'_', ' ', parts[0]).strip()
                    taxa.append(taxon_name)
                    sequences[taxon_name] = parts[1]

    return (ntax, nchar, mask, taxa, sequences)

def writeFASTAFile(fn, ntax, nchar, taxa, sequences):
    if os.path.exists(fn):
        os.rename(fn, '%s.bak' % fn)
    longest = max([len(t) for t in taxa])
    taxonfmt = '  %%%ds' % longest
    f = open(fn, 'w')
    for t in taxa:
        taxon_name = re.sub(r'\s+', '_', t)
        f.write('> %s\n' % taxon_name)
        f.write('%s\n' % sequences[t])
    f.close()
    
def writeNexusFile(fn, ntax, nchar, mask, taxa, sequences):
    if os.path.exists(fn):
        os.rename(fn, '%s.bak' % fn)
    longest = max([len(t) for t in taxa])
    taxonfmt = '  %%%ds' % longest
    f = open(fn, 'w')
    f.write('#nexus\n\n')
    f.write('begin data;\n')
    f.write('  dimensions ntax=%d nchar=%d;\n' % (ntax, nchar))
    f.write('  format datatype=dna gap=-;\n')
    f.write('  matrix\n')
    if mask is not None:
        f.write(taxonfmt % ' ')
        f.write('[%s]\n' % mask)
    for t in taxa:
        taxon_name = re.sub(r'\s+', '_', t)
        f.write(taxonfmt % taxon_name)
        f.write(' %s\n' % sequences[t])
    f.write('  ;\n')
    f.write('end;\n')
    f.close()
    
def paupForAstral(astraldir, subset_info, nloci):
    # Build string s containing PAUP* commands to estimate gene trees
    # for each locus
    s = ''
    for subset in subset_info:
        locus = subset['locus']
        
        if setupmain.useFASTA:
            s += '  tonexus format=fasta fromfile=locus%d.fa tofile=locus%d.nex replace;\n' % (locus,locus)
        s += '  exe locus%d.nex;\n' % locus
        s += '  set crit=like forcepolyt=yes maxtrees=1000 increase=auto autoinc=1000;\n'
        s += '  lset nst=1 basefreq=equal rates=equal pinvar=0;\n'
#        s += '  hsearch start=nj;\n'
        s += 'hsearch start=nj swap=nni timelimit=600;\n'
        s += '  contree all / treefile=genetrees.txt format=newick %s;\n' % (locus == 1 and 'replace' or 'append',)
        s += '  cleardata;\n'
        s += '  cleartrees;\n'
        if locus < nloci:
            s += '\n'
    
    # Create mlgenetrees.nex file that will later be executed by PAUP*
    stuff = open(os.path.join(astraldir, 'mlgenetrees.nex'), 'r').read()
    stuff, n = re.subn(r'__MLGENETREES__', s, stuff, re.M | re.S)
    open(os.path.join(astraldir, 'mlgenetrees.nex'), 'w').write(stuff)
    
def segregateLocusData(simfn, outputdir, subset_info):
    ntax, nchar, mask, taxa, sequences = readNexusFile(simfn)

    # Create concatenated data file
    if setupmain.useFASTA:
        fn = os.path.join(outputdir, 'concat.fa')
        writeFASTAFile(fn, ntax, nchar, taxa, sequences)
    else:
        fn = os.path.join(outputdir, 'concat.nex')
        writeNexusFile(fn, ntax, nchar, mask, taxa, sequences)

    for subset in subset_info:
        # gather subset info
        locus = subset['locus']
        seq_begin = subset['first']-1
        seq_end   = subset['last']
        nsites    = seq_end - seq_begin

        # identify taxa that are not missing all data
        valid_taxa = []
        valid_seqs = {}
        for t in taxa:
            tseq = sequences[t][seq_begin:seq_end]
            tmp,n = re.subn(r'[?]','',tseq)
            if n < nsites:
                valid_taxa.append(t)
                valid_seqs[t] = tseq
        
        # write file containing data for just this subset
        if setupmain.useFASTA:
            fn = os.path.join(outputdir, 'locus%d.fa' % locus)
            writeFASTAFile(fn, len(valid_taxa), nsites, valid_taxa, valid_seqs)
        else:
            fn = os.path.join(outputdir, 'locus%d.nex' % locus)
            writeNexusFile(fn, len(valid_taxa), nsites, None, valid_taxa, valid_seqs)
            
def estimateGeneTrees(genetreesdir, subset_info):
    pass

def run(rep, nreps, maindir, repdir, rnseed):
    print('  setting up rep %d in directory "%s/%s"' % (rep, maindir, repdir))
    
    refinfof = open(os.path.join(maindir, repdir,'rep-info.txt'),'w')
    
    #############################################
    # Init random number generator for choosing #
    # number of sites and aspects of rate het.  #
    #############################################
    random.seed(rnseed)
    
    ###############################################
    # Get paths to all subdirs for this replicate #
    ###############################################
    
    inner_simdir       = os.path.join(repdir, 'sim')
    inner_beastdir     = os.path.join(repdir, 'beast')
    inner_smcdir       = os.path.join(repdir, 'smc')
    inner_svdqdir      = os.path.join(repdir, 'svdq')
    inner_astraldir    = os.path.join(repdir, 'astral')
    inner_viewerdir    = os.path.join(repdir, 'viewer')
    inner_genetreesdir = os.path.join(repdir, 'genetrees')
            
    outer_simdir       = os.path.join(maindir, inner_simdir)
    outer_beastdir     = os.path.join(maindir, inner_beastdir)
    outer_smcdir       = os.path.join(maindir, inner_smcdir)
    outer_svdqdir      = os.path.join(maindir, inner_svdqdir)
    outer_astraldir    = os.path.join(maindir, inner_astraldir)
    outer_viewerdir    = os.path.join(maindir, inner_viewerdir)
    outer_genetreesdir = os.path.join(maindir, inner_genetreesdir)
            
    ##################################
    # Determine row and col from rep #
    ##################################
    dim, row, col = calcDimRowCol(rep, nreps)
        
    #######################################################
    # Determine true theta mean and Yule speciation rate  #
    #######################################################
    if setupmain.theta_vs_lambda:
        # Grid has x = theta and y = speciation rate (i.e. lambda)
        if nreps == 1:
            theta_mean      = (setupmain.theta_min + setupmain.theta_max)/2.0
            speciation_rate = (setupmain.lambda_min + setupmain.lambda_max)/2.0
        else:
            theta_mean      =  setupmain.theta_min + row*(setupmain.theta_max  - setupmain.theta_min)/(dim-1)
            speciation_rate = setupmain.lambda_min + col*(setupmain.lambda_max - setupmain.lambda_min)/(dim-1)
    else:
        # Grid has x = half_theta and y = T, where T is species tree height
        # Need to convert half_theta to theta and T to specieation_rate (i.e. lambda)
        nspp = len(setupmain.species)
        suminv = sum([1.0/x for x in range(2,nspp+1)])
        
        if nreps == 1:
            half_theta_mean = (setupmain.half_theta_min + setupmain._half_theta_max)/2.0
            T = (setupmain.T_min + setupmain.T_max)/2.0
        else:
            half_theta_mean =  setupmain.half_theta_min + row*(setupmain.half_theta_max  - setupmain.half_theta_min)/(dim-1)
            T = setupmain.T_min + col*(setupmain.T_max - setupmain.T_min)/(dim-1)
            
        theta_mean = 2.0*half_theta_mean
        speciation_rate = suminv/T
    
    ##############################
    # Set up the "sim" directory #
    ##############################
    infile  = os.path.join(outer_simdir, '%s-proj.conf' % setupmain.user)
    outfile = infile
    
    # Create data partitioning and specify relative rates
    subset_info = []
    site_cursor = 1
    subsets = ''
    relrates = ''
    
    # Choose the number of loci for this simulation
    nloci = random.randint(setupmain.min_n_loci, setupmain.max_n_loci)
    if setupmain.user == 'aam21005' or setupmain.user == 'jjc23002':
         relrates += 'relative_rates = '
    for g in range(nloci):
        locus = g + 1

        # Choose the number of sites for this locus 
        nsites_this_locus = random.randint(setupmain.min_sites_per_locus, setupmain.max_sites_per_locus)
        first = site_cursor
        last  = site_cursor + nsites_this_locus - 1
        subsets += 'subset = locus%d[nucleotide]:%d-%d\n' % (locus,first,last)

        # Choose the relative rate for this locus 
        relrate_this_locus = random.gammavariate(setupmain.subset_relrate_shape, setupmain.subset_relrate_scale)
        if setupmain.user == 'pol02003':
            relrates += 'relrate = locus%d:%.5f\n' % (locus, relrate_this_locus)
        elif setupmain.user == 'aam21005' or setupmain.user == 'jjc23002':
            if g == 0:
                relrates += str(relrate_this_locus)
            else:
                relrates += ", " + str(relrate_this_locus)

        # Save information about this locus in subset_info vector
        subset_info.append({'locus':locus, 'relrate':relrate_this_locus, 'nsites':nsites_this_locus, 'first':first, 'last':last})

        # Save information about this locus to rep info file
        refinfof.write('\nlocus%d:\n' % locus)
        refinfof.write('  relrate = %g\n' % relrate_this_locus)
        refinfof.write('  nsites  = %d\n' % nsites_this_locus)
        refinfof.write('  first   = %d\n' % first)
        refinfof.write('  last    = %d\n' % last)
        refinfof.flush()
        
        site_cursor += nsites_this_locus
        
    if setupmain.user == 'aam21005' or setupmain.user == 'jjc23002':
         relrates += '\n'
        
    # Define number of species and number of individuals for each species
    nspecies = len(setupmain.species) 
    if setupmain.user == 'pol02003':
        species = 'simnspecies = %d\n' % nspecies
        for s in range(nspecies):
            nindivs = setupmain.indivs_for_species[s]
            species += 'simntaxaperspecies = %d\n' % nindivs
    elif setupmain.user == 'aam21005' or setupmain.user == 'jjc23002':
        species = 'nspecies = %d\n' % nspecies
        species += 'ntaxaperspecies = '
        species += ','.join(['%d' % x for x in setupmain.indivs_for_species])
        species += '\n'
        
    # Choose random edge rate variance
    u = random.random()
    edge_rate_variance = setupmain.min_edge_rate_variance + u*(setupmain.max_edge_rate_variance - setupmain.min_edge_rate_variance)
    
    # Choose random occupancy probability
    u = random.random()
    occupancy = setupmain.min_occupancy + u*(setupmain.max_occupancy - setupmain.min_occupancy)
    
    # Choose random ASRV shape
    u = random.random()
    asrv_shape = setupmain.min_asrv_shape + u*(setupmain.max_asrv_shape - setupmain.min_asrv_shape)
    
    # Choose random compositional heterogeneity Dirichlet parameter
    u = random.random()
    comphet = setupmain.min_comphet + u*(setupmain.max_comphet - setupmain.min_comphet)
    
    # choose random number for slow loci
    if setupmain.slowloci == True:
    	nloci_slow = random.randint(1, setupmain.max_n_loci)
    
    
    if setupmain.user == "aam21005" or setupmain.user == "jjc23002":
         setupsubst.substitutions({
             '__RNSEED__':        rnseed, 
             '__THETAMEAN__':     theta_mean, 
             '__LAMBDA__':        speciation_rate,
             '__SUBSETS__':       subsets,
             '__RELRATES__':      relrates,
             '__SPECIES__':       species,
             '__OCCUPANCY__':     occupancy,
             '__ASRV_SHAPE__':    asrv_shape,
             '__EDGE_RATE_VAR__': edge_rate_variance,
             '__COMP_HET__':      comphet,
             '__SAVEGENETREESSEPARATELY__': setupmain.sim_save_gene_trees_separately,
             '__NLOCISLOW__': nloci
             }, infile, outfile)
         os.rename(outfile, os.path.join(outer_simdir, 'proj.conf'))
    else:
         setupsubst.substitutions({
             '__RNSEED__':        rnseed, 
             '__THETAMEAN__':     theta_mean, 
             '__LAMBDA__':        speciation_rate,
             '__SUBSETS__':       subsets,
             '__RELRATES__':      relrates,
             '__SPECIES__':       species,
             '__OCCUPANCY__':     occupancy,
             '__ASRV_SHAPE__':    asrv_shape,
             '__EDGE_RATE_VAR__': edge_rate_variance,
             '__COMP_HET__':      comphet
             }, infile, outfile)
         os.rename(outfile, os.path.join(outer_simdir, 'proj.conf'))

    ##############################################################
    # Run simulation program to simulate data for this replicate #
    ##############################################################
    completed_process = sub.run([setupmain.simulator_path], cwd=outer_simdir, capture_output=True, text=True)
    if completed_process.returncode != 0:
        print('\nreturncode: ', completed_process.returncode)
        print('\nstderr: ', completed_process.stderr)
        print('\nstdout: ', completed_process.stdout)
        sys.exit('Aborted.')
    else:
        stdoutput = str(completed_process.stdout)
        open(os.path.join(outer_simdir, 'output%d.txt' % rep), 'w').write(stdoutput)
    
    ################################################
    # Break up sim.nex into individual nexus files #
    # that have all-missing taxa removed           #
    ################################################
    segregateLocusData(os.path.join(outer_simdir, 'sim.nex'), outer_astraldir, subset_info)

    ################################################
    # Copy the newicks.js file generated by        #
    # simulation program to the "viewer" directory #
    ################################################
    if setupmain.user == 'pol02003':
        shutil.copy(os.path.join(outer_simdir, 'newicks.js'), outer_viewerdir)
    
    ##############################
    # Set up the "svdq" directory #
    ##############################
    infile  = os.path.join(outer_svdqdir, 'svd-qage.nex')
    outfile = infile

    # Create PAUP partition string
    nspecies = len(setupmain.species) 
    paup_part = ''
    for s in range(nspecies):
        nindivs = setupmain.indivs_for_species[s]
        for i in range(nindivs):
            paup_part += '%s ' % setupmain.species[s]
    
    setupsubst.substitutions({
        '__PARTITION__':   paup_part.strip()
        }, infile, outfile)

    ##############################
    # Set up the "smc" directory #
    ##############################
    infile  = os.path.join(outer_smcdir, '%s-proj.conf' % setupmain.user)
    outfile = infile
    if setupmain.smc_use_svdq_estimates:
        # Put off specifying these until SVD-qage has been run
        smc_theta_mean = '__SVDQ_EST_THETA__'
        smc_lambda = '__SVDQ_EST_LAMBDA__'
    else:
        smc_theta_mean = theta_mean
        smc_lambda = speciation_rate
        
    if setupmain.user == "aam21005" or setupmain.user == "jjc23002":
        setupsubst.substitutions({
            '__RNSEED__':    rnseed, 
            '__SUBSETS__':   subsets,
            '__RELRATES__':  relrates,
            '__THETAMEAN__': smc_theta_mean, 
            '__LAMBDA__':    smc_lambda,
            '__SMCNPARTICLES__': setupmain.smc_nparticles,
            '__SMCTHIN__': setupmain.smc_thin,
            '__SMCNSPECIESPARTICLES__': setupmain.smc_nspeciesparticles,
            '__SMCNGROUPS__': setupmain.smc_ngroups,
            '__SMCSAVEEVERY__': setupmain.smc_saveevery,
            '__SMCNTHREADS__': setupmain.smc_nthreads,
            '__SMCSAVEGENETREES__': setupmain.smc_savegenetrees,
            '__SMCGENENEWICKS__': setupmain.smc_genenewicks,
            '__SMCNLOCI__': nloci,
            '__SMCSAVEMEMORY__': setupmain.smc_savememory,
            '__SMCNEWICKPATH__': setupmain.smc_newickpath
            }, infile, outfile)
    else:
    	setupsubst.substitutions({
    	    '__RNSEED__':    rnseed, 
    	    '__SUBSETS__':   subsets,
            '__RELRATES__':  relrates,
    	    '__THETAMEAN__': smc_theta_mean, 
    	    '__LAMBDA__':    smc_lambda,
    	    '__SMCNPARTICLES__': setupmain.smc_nparticles,
            '__SMCNKEPT__': setupmain.smc_nkept,
            '__SMCNSPECIESPARTICLES__': setupmain.smc_nspeciesparticles,
            '__SMCNSPECIESKEPT__': setupmain.smc_nspecieskept
            }, infile, outfile)
    os.rename(outfile, os.path.join(outer_smcdir, 'proj.conf'))

    ################################
    # Set up the "beast" directory #
    ################################
    #taxa,seqs = copydata.beast(os.path.join(outer_simdir, 'sim.nex'), setupmain.nloci, setupmain.sites_per_locus)
    taxa,seqs = copydata.beast(os.path.join(outer_simdir, 'sim.nex'), nloci, subset_info)

    taxonset = ''
    nspecies = len(setupmain.species)
    taxon_index = 0
    for i in range(nspecies):
        spp = setupmain.species[i]
        taxonset += '                    <taxon id="%s" spec="TaxonSet">\n' % spp
        for j in range(setupmain.indivs_for_species[i]):
            indiv_name = '%s' % taxa[taxon_index]
            m = re.match(r'.+?\^(.+)', indiv_name)
            assert m is not None, 'individual name ("%s") does not match pattern indiv^species' % indiv_name
            spp_check = m.group(1)
            assert spp_check == spp
            taxonset += '                    <taxon id="%s" spec="Taxon"/>\n' % indiv_name
            taxon_index += 1
        taxonset += '                    </taxon>\n'
    taxonset += '\n'
    
    loci = ''
    sbi = ''
    speciescoalescent = ''
    likelihood = ''
    treeprior = ''
    tree = ''
    parallel = ''
    loglocus = ''
    treetop = ''
    loggerlocus = ''
    clustertree = 2
    for g in range(nloci):
        locus = g + 1
        loci += '            <tree id="Tree.t:gene%d" spec="beast.base.evolution.tree.Tree" name="stateNode">\n' % locus
        loci += '                <taxonset id="TaxonSet.gene%d" spec="TaxonSet">\n' % locus
        loci += '                    <alignment idref="gene%d"/>\n' % locus
        loci += '                </taxonset>\n'
        loci += '            </tree>\n'
        sbi += '            <gene idref="Tree.t:gene%d"/>\n' % locus
        speciescoalescent += '                <distribution id="treePrior.t:gene%d" spec="starbeast3.evolution.speciation.GeneTreeForSpeciesTreeDistribution" populationModel="@speciesTreePopulationModel" speciesTree="@Tree.t:Species" speciesTreePrior="@SpeciesTreePopSize.Species" tree="@Tree.t:gene%d"/>\n' % (locus, locus)
        likelihood += '                <distribution id="treeLikelihood.gene%d" spec="TreeLikelihood" data="@gene%d" tree="@Tree.t:gene%d">\n' % (locus,locus,locus)
        likelihood += '                    <siteModel id="SiteModel.s:gene%d" spec="SiteModel">\n' % locus
        likelihood += '                        <parameter id="mutationRate.s:gene%d" spec="parameter.RealParameter" estimate="false" name="mutationRate">1.0</parameter>\n' % locus
        likelihood += '                        <parameter id="gammaShape.s:gene%d" spec="parameter.RealParameter" estimate="false" lower="0.0" name="shape">1.0</parameter>\n' % locus
        likelihood += '                        <parameter id="proportionInvariant.s:gene%d" spec="parameter.RealParameter" estimate="false" lower="0.0" name="proportionInvariant" upper="1.0">0.0</parameter>\n' % locus
        likelihood += '                        <substModel id="JC69.s:gene%d" spec="JukesCantor"/>\n' % locus
        likelihood += '                    </siteModel>\n'
        likelihood += '                    <branchRateModel id="GeneTreeClock.c:gene%d" spec="starbeast3.evolution.branchratemodel.StarBeast3Clock" geneTree="@treePrior.t:gene%d" sharedRateModel="@branchRatesModel.Species" tree="@Tree.t:gene%d">\n' % (locus,locus,locus)
        likelihood += '                        <parameter id="clockRate.c:gene%d" spec="parameter.RealParameter" estimate="false" lower="0.0" name="clock.rate">1.0</parameter>\n' % locus
        likelihood += '                    </branchRateModel>\n'
        likelihood += '                </distribution>\n'
        treeprior += '            <gene idref="treePrior.t:gene%d"/>\n' % locus
        tree += '                <down idref="Tree.t:gene%d"/>\n' % locus
        parallel += '            <distribution id="ParallelMCMCTreeOperatorLikelihood.gene%d" spec="starbeast3.operators.ParallelMCMCTreeOperatorTreeDistribution" geneprior="@treePrior.t:gene%d" tree="@Tree.t:gene%d" treelikelihood="@treeLikelihood.gene%d"/>\n' % (locus,locus,locus,locus)
        loglocus += '            <log idref="treeLikelihood.gene%d"/>\n' % locus
        loglocus += '            <log idref="treePrior.t:gene%d"/>\n' % locus
        loglocus += '            <log id="TreeStat.t:gene%d" spec="beast.base.evolution.tree.TreeStatLogger" tree="@Tree.t:gene%d"/>\n' % (locus,locus)
        loglocus += '            <log id="TreeDistanceNJ.t:gene%d" spec="beastlabs.evolution.tree.TreeDistanceLogger" tree="@Tree.t:gene%d">\n' % (locus,locus)
        loglocus += '                <ref id="ClusterTree.%d" spec="beast.base.evolution.tree.ClusterTree" clusterType="neighborjoining" taxa="@gene%d"/>\n' % (clustertree, locus)
        loglocus += '            </log>\n'
        loglocus += '            <log id="TreeDistanceUPGMA.t:gene%d" spec="beastlabs.evolution.tree.TreeDistanceLogger" tree="@Tree.t:gene%d">\n' % (locus,locus)
        loglocus += '                <ref id="ClusterTree.%d" spec="beast.base.evolution.tree.ClusterTree" clusterType="upgma" taxa="@gene%d"/>\n' % (clustertree + 1,locus)
        loglocus += '            </log>\n'
        treetop += '                    <tree idref="Tree.t:gene%d"/>\n' % locus
        loggerlocus += '        <logger id="treelog.t:gene%d" spec="Logger" fileName="$(tree).trees" logEvery="%d" mode="tree">\n' % (locus, setupmain.beast_logevery)
        loggerlocus += '            <log id="TreeWithMetaDataLogger.t:gene%d" spec="beast.base.evolution.TreeWithMetaDataLogger" tree="@Tree.t:gene%d"/>\n' % (locus,locus)
        loggerlocus += '        </logger>\n'
        clustertree += 2
    loci += '\n'

    if setupmain.smc_use_svdq_estimates:
        # Put off specifying these until SVD-qage has been run
        beast_theta_mean = '__SVDQ_EST_THETA__'
        beast_lambda1 = '__SVDQ_EST_LAMBDA1__'
        beast_lambda2 = '__SVDQ_EST_LAMBDA2__'
        beast_lambda3 = '__SVDQ_EST_LAMBDA3__'
    else:
        beast_theta_mean = setupmain.beast_thetamean
        beast_lambda1 = setupmain.beast_lambda
        beast_lambda2 = setupmain.beast_lambda
        beast_lambda3 = setupmain.beast_lambda

    infile = os.path.join(outer_beastdir, 'starbeast.xml')
    outfile = infile
    setupsubst.substitutions({
        '__SEQUENCES__': seqs,
        '__CHAINLENGTH__': setupmain.beast_chainlength,
        '__PREBURNIN__': setupmain.beast_preburnin,
        '__STOREEVERY1__': setupmain.beast_storeevery,
        '__STOREEVERY2__': setupmain.beast_storeevery,
        '__STOREEVERY3__': setupmain.beast_storeevery,
        '__TAXONSET__': taxonset,
        '__LOCI__': loci,
        '__SBI__': sbi,
        '__SPECIESCOALESCENT__': speciescoalescent,
        '__LIKELIHOOD__': likelihood,
        '__TREEPRIOR1__': treeprior,
        '__TREEPRIOR2__': treeprior,
        '__TREEPRIOR3__': treeprior,
        '__TREEPRIOR4__': treeprior,
        '__TREE__': tree,
        '__PARALLEL__': parallel,
        '__LOGLOCUS__': loglocus,
        '__TREETOP__': treetop,
        '__LOGGERLOCUS__': loggerlocus,
        '__LAMBDA1__': beast_lambda1,
        '__LAMBDA2__': beast_lambda2,
        '__LAMBDA3__': beast_lambda3,
        '__THETAMEAN__': beast_theta_mean
        }, infile, outfile)
    
    #################################
    # Set up the "astral" directory #
    #################################
    paupForAstral(outer_astraldir, subset_info, nloci)

    ####################################
    # Set up the "genetrees" directory #
    ####################################
    estimateGeneTrees(outer_genetreesdir, subset_info)

    #######################E##########
    # Append to the "astral.sh" file #
    ########################E#########
    astral_for_rep = 'cd %s\n%s mlgenetrees.nex\njava -jar %s -i genetrees.txt -a mapfile.txt 2> astral-output-rep%d.txt\ncd -\n\n# __ASTRAL__' % (inner_astraldir, setupmain.paup_path, setupmain.astral_path, rep)
    infile = os.path.join(maindir, 'astral.sh')
    outfile = infile
    setupsubst.substitutions({
        '# __ASTRAL__': astral_for_rep
        }, infile, outfile)
    
    #################################
    # Append to the "beast.sh" file #
    #################################
    beast_for_rep = 'cd %s\n%s starbeast.xml\ncd -\n\n# __BEAST__' % (inner_beastdir, setupmain.beast_path)
    infile = os.path.join(maindir, 'beast.sh')
    outfile = infile
    setupsubst.substitutions({
        '# __BEAST__': beast_for_rep,
        }, infile, outfile)
    
    ################################
    # Append to the "smc.sh" file #
    ################################
    smc_for_rep = 'cd %s\n%s\ncd -\n\n# __SMC__' % (inner_smcdir, setupmain.smc_path)
    infile = os.path.join(maindir, 'smc.sh')
    outfile = infile
    setupsubst.substitutions({
        '# __SMC__': smc_for_rep
        }, infile, outfile)
    
    ##################################
    # Append to the "rfsmc.nex" file #
    ##################################
    smcrf_for_rep = '''
    gettrees file = %s/true-species-tree.tre mode=3;
    gettrees file = %s/%s mode=7;
    deroot;
    treedist all / measure=rfSymDiff refTree=1 file=smcrf%d.txt;
    [__RFSMC__]''' % (inner_simdir,inner_smcdir,setupmain.smc_speciestreefile,rep)
    infile = os.path.join(maindir, 'rfsmc.nex')
    outfile = infile
    setupsubst.substitutions({
        r'\[__RFSMC__\]': smcrf_for_rep
        }, infile, outfile)
        
    ####################################
    # Append to the "rfbeast.nex" file #
    ####################################
    beastrf_for_rep = '''
    gettrees file = %s/true-species-tree.tre mode=3;
    gettrees file = %s/species.trees mode=7;
    deroot;
    treedist all / measure=rfSymDiff refTree=1 file=beastrf%d.txt;
    
    [__RFBEAST__]''' % (inner_simdir,inner_beastdir,rep)
    infile = os.path.join(maindir, 'rfbeast.nex')
    outfile = infile
    setupsubst.substitutions({
        r'\[__RFBEAST__\]': beastrf_for_rep
        }, infile, outfile)        
    
    ################################
    # Append to the "svdq.sh" file #
    ################################
    svdq_for_rep = 'cd %s\n%s svd-qage.nex\ncd -\n\n# __SVDQ__' % (inner_svdqdir, setupmain.paup_path)
    infile = os.path.join(maindir, 'svdq.sh')
    outfile = infile
    setupsubst.substitutions({
        '# __SVDQ__': svdq_for_rep
        }, infile, outfile)

    refinfof.close()
