import sys, re, os, subprocess as sub

nspecies = __NUM_SPECIES__

data_from_file = False
if len(sys.argv) > 1:
    data_from_file = True
    
def calcContourBreaksStr(cbmin, cbmax):    
    diff = cbmax - cbmin
    incr = diff/9.0
    breaks = []
    curr = lower
    while curr < upper:
        breaks.append('%.3f' % curr)
        curr += incr
    return breaks
    
def calcRF(rep_plus_one, source, newick):
    simdir = os.path.join('./rep%d' % rep_plus_one, 'sim')
    
    # Create paup command file containing newick
    open('tmp.nex', 'w').write('''
#nexus

[source = %s]
    
begin trees;
    tree test = %s;    
end;

begin paup;
    gettrees file=%s/true-species-tree.tre mode=7;
    deroot;
    treedist all / measure=rfSymDiff refTree=2 file=tmp.txt replace;
    quit;
end;
''' % (source, newick, simdir))
        
    # Execute paup command file
    completed_process = sub.run(['__PAUPPATH__', 'tmp.nex'], capture_output=True, text=True)
    
    # Extract RF from PAUP* output
    assert completed_process.returncode == 0, 'could not compute RF distance for %s tree in rep %d' % (source, rep_plus_one)
    stuff = open('tmp.txt', 'r').read()
    m = re.search(r'tree\s+distance to tree 2\s+\d+\s+(\d+)', stuff, re.M | re.S)
    assert m is not None, 'could not extract RF distance from file "tmp.txt"'
    return int(m.group(1))
    
summary = []

if data_from_file:
    fn = sys.argv[1]
    print('Opening file "%s"...' % fn)
    
    # Open the input file
    lines = open(sys.argv[1], 'r').readlines()
    
    # Read headers and ensure that format is what was expected
    headers = lines[0].strip().split('\t')
    nheaders = len(headers)
    assert nheaders == 9, 'Expecting 9 columns but instead found %d in headers\nheaders: %s\n' % (nheaders,headers)
    assert headers[0] == 'rep' 
    assert headers[1] == 'theta' 
    assert headers[2] == 'lambda' 
    assert headers[3] == 'numdeep' 
    assert headers[4] == 'maxdeep' 
    assert headers[5] == 'svdq-rf' 
    assert headers[6] == 'astral-rf' 
    assert headers[7] == 'smc-rf' 
    assert headers[8] == 'beast-rf' 
    
    nlines = len(lines)
    print('nlines = %d' % nlines)
    
    for i,line in enumerate(lines[1:]):
        parts = line.strip().split('\t')
        nparts = len(parts)
        assert nparts == 9, 'Expecting 9 columns but instead found %d in line %d\nline: %s\n' % (nparts, i, line.strip())
        rep       =   int(parts[0])
        theta     = float(parts[1])
        lamBda    = float(parts[2])
        numdeep   =   int(parts[3])
        maxdeep   =   int(parts[4])
        svdq_rf   = float(parts[5])
        astral_rf = float(parts[6])
        smc_rf    = float(parts[7])
        beast_rf  = float(parts[8])
        summary.append({'theta':theta,'lambda':lamBda,'numdeep':numdeep,'maxdeep':maxdeep,'svdq_rf':svdq_rf,'astral_rf':astral_rf,'smc_rf':smc_rf,'beast_rf':beast_rf})
else:
    print('Summarizing output...')

    # Open the output file
    outf = open('summary.txt', 'w')
    outf.write('rep\ttheta\tlambda\tnumdeep\tmaxdeep\tsppTreeObsHt\tsppTreeExpHt\tsvdq-rf\tastral-rf\tsmc-rf\tbeast-rf\n')

    nreps = __NREPS__
    for rep in range(nreps):
        rep_plus_one = rep + 1
        
        print('Replicate %d of %d...' % (rep_plus_one,nreps))
        
        if __AAM21005__:
            # extract deep coalescences
            fn = 'rep%d/sim/deep_coalescences.txt' % rep_plus_one
            maxdeep = 0
            stuff = open(fn, 'r').read()
        m = re.search(r'num deep coalescences = (?P<numdeep>\d+)\s+Maximum number of deep coalescences = (?P<maxdeep>\d+)', stuff, re.M | re.S)
            assert m is not None, 'could not extract deep coalescences from file "%s"' % fn
            numdeep = int(m.group('numdeep'))
        maxdeep = int(m.group('maxdeep'))
            
            # extract lambda and theta mean
            fn = 'rep%d/sim/proj.conf' % rep_plus_one
            stuff = open(fn, 'r').read()
        m = re.search('theta\s+=\s+(?P<theta>[-.e0-9]+)\s+lambda\s+=\s+(?P<lambda>[.e0-9]+)', stuff, re.M | re.S)
            assert m is not None, 'could not extract theta and lambda from file "%s"' % fn
            theta = float(m.group('theta'))
            lamBda = float(m.group('lambda'))
            
            # Is species tree expected height (stxheight) and observed height (stoheight) saved?
            stxheight = -1.0
            stoheight = -1.0
        elif __POL02003__:
            fn = 'rep%d/sim/output%d.txt' % (rep_plus_one,rep_plus_one)
            stuff = open(fn, 'r').read()
            
            # Extract stxheight (species tree expected height)
            m = re.search(r'Expected species tree height = (?P<stxheight>[.0-9]+)', stuff, re.M | re.S)
            assert m is not None, 'could not extract expected species tree height from file "%s"' % fn
            stxheight = float(m.group('stxheight'))
            
            # Extract numdeep, maxdeep, and stoheight
            m = re.search(r'Number of deep coalescences = (?P<numdeep>\d+)\s+Maximum number of deep coalescences = (?P<maxdeep>\d+)\s+True species tree height = (?P<stoheight>[.0-9]+)', stuff, re.M | re.S)
            assert m is not None, 'could not extract deep coalescences from file "%s"' % fn
            numdeep = int(m.group('numdeep'))
            maxdeep = int(m.group('maxdeep'))
            stoheight = float(m.group('stoheight'))
            
            # Extract theta and lambda
            m = re.search(r'theta  = (?P<theta>[.e0-9]+)\s+lambda = (?P<lambda>[.e0-9]+)', stuff, re.M | re.S)    
            assert m is not None, 'could not extract theta and lambda from file "%s"' % fn
            theta = float(m.group('theta'))
            lamBda = float(m.group('lambda'))
        
        # Save true species tree
        fn = 'rep%d/sim/true-species-tree.tre' % rep_plus_one
        stuff = open(fn, 'r').read()
    m = re.search('tree \S+ = \[&R\] (.+?);', stuff, re.M | re.S)
        assert m is not None, 'could not locate newick in file "%s"' % fn
        true_tree = m.group(1)
        true_tree = re.sub(':[.0-9]+', '', true_tree)
        print('  TRUE tree: %s' % true_tree)
        
        # Compute RF distance between ASTRAL species tree and true species tree
        fn = 'rep%d/astral/astral-output-rep%d.txt' % (rep_plus_one,rep_plus_one)
        if os.path.exists(fn):
            stuff = open(fn, 'r').read()
            m = re.search(r'Optimal tree inferred in [-.e0-9]+ secs.\s*(\S+)\sFinal quartet score', stuff, re.M | re.S)    
            assert m is not None
            astral_tree = m.group(1)
            astral_rf = calcRF(rep_plus_one, 'ASTRAL', astral_tree)
            print('  ASTRAL tree: %s (RF = %d)' % (astral_tree,astral_rf))
        else:
            astral_rf = -1
            print('  ASTRAL tree not found')
    
        # Compute RF distance between SVD-Qage species tree and true species tree
        fn = 'rep%d/svdq/svd.tre' % rep_plus_one
        if os.path.exists(fn):
            stuff = open(fn, 'r').read()
            m = re.search(r'tree qAge = \[&R\] (\S+);', stuff, re.M | re.S)    
            assert m is not None
            svdq_tree = m.group(1)
            svdq_tree = re.sub(':[.0-9]+', '', svdq_tree)
            svdq_rf = calcRF(rep_plus_one, 'SVDQ', svdq_tree)
            print('  SVDQ tree: %s (RF = %d)' % (svdq_tree,svdq_rf))
        else:
            svdq_rf = -1
            print('  SVDQ tree not found')
        
        # Compute mean RF distance between sampled SMC species trees and the true species tree
        fn = 'smcrf%d.txt' % rep_plus_one
        if os.path.exists(fn):
            lines = open(fn, 'r').readlines()
            smcrfsum = 0.0
            smcrfnum = 0
            for line in lines[1:]:
                parts = line.strip().split()
                assert len(parts) == 2, 'expecting 2 parts but found %d in file "%s"' % (len(parts), fn)
                smcrfnum += 1
                smcrfsum += float(parts[1])
            smc_rf = smcrfsum/smcrfnum
        else:
            smc_rf = -1
            print('  SMC trees not found')
        
        # Compute mean RF distance between sampled BEAST species trees and the true species tree
        fn = 'beastrf%d.txt' % rep_plus_one
        if os.path.exists(fn):
            lines = open(fn, 'r').readlines()
            beastrfsum = 0.0
            beastrfnum = 0
            for line in lines[1:]:
                parts = line.strip().split()
                assert len(parts) == 2, 'expecting 2 parts but found %d in file "%s"' % (len(parts), fn)
                beastrfnum += 1
                beastrfsum += float(parts[1])
            beast_rf = beastrfsum/beastrfnum
        else:
            beast_rf = -1
            print('  BEAST trees not found')
        
        summary.append({'theta':theta,'lambda':lamBda,'numdeep':numdeep,'maxdeep':maxdeep,'stoheight':stoheight, 'stxheight':stxheight, 'svdq_rf':svdq_rf,'astral_rf':astral_rf,'smc_rf':smc_rf,'beast_rf':beast_rf})
        output_string  = '%d\t' % rep_plus_one
        output_string += '%.5f\t' % theta
        output_string += '%.5f\t' % lamBda
        output_string += '%d\t' % numdeep
        output_string += '%d\t' % maxdeep
        output_string += '%.5f\t' % stoheight
        output_string += '%.5f\t' % stxheight
        output_string += '%.5f\t' % svdq_rf
        output_string += '%.5f\t' % astral_rf
        output_string += '%.5f\t' % smc_rf
        output_string += '%.5f\n' % beast_rf
        outf.write(output_string)

# Create lambdavector, thetavector, smcmeans, and beastmeans
nsummary = len(summary)
print('len(summary) = %d' % nsummary)
lambdavector = []
thetavector = []
smcRFmeans = []
beastRFmeans = []
smcMinusBeastRF = []
contour_breaks_max = None
contour_breaks_min = None
for s in summary:
    lambdavector.append('%g' % s['lambda'])
    thetavector.append('%g' % s['theta'])
    smcRFmeans.append('%g' % s['smc_rf'])
    beastRFmeans.append('%g' % s['beast_rf'])
    diff = s['smc_rf'] - s['beast_rf']
    if contour_breaks_max is None or diff > contour_breaks_max:
        contour_breaks_max = diff
    if contour_breaks_min is None or diff < contour_breaks_min:
        contour_breaks_min = diff
    smcMinusBeastRF.append('%g' % diff)

lambdastr = ','.join(lambdavector)
thetastr = ','.join(thetavector)
smcrfstr = ','.join(smcRFmeans)
beastrfstr = ','.join(beastRFmeans)
smcminusbeaststr = ','.join(smcMinusBeastRF)

contour_breaks_str = calcContourBreaksStr(contour_breaks_min, contour_breaks_max)

# Open plot-template.Rmd
stuff = open('plot-template.Rmd', 'r').read()
stuff = re.sub('__NSPECIES__', '%d' % nspecies, stuff, re.M | re.S)
stuff = re.sub('__LAMBDAVECTOR__', lambdastr, stuff, re.M | re.S)
stuff = re.sub('__THETAVECTOR__', thetastr, stuff, re.M | re.S)
stuff = re.sub('__SMCRFMEANS__', smcrfstr, stuff, re.M | re.S)
stuff = re.sub('__BEASTRFMEANS__', beastrfstr, stuff, re.M | re.S)
stuff = re.sub('__SMC_MINUS_BEAST_RF__', smcminusbeaststr, stuff, re.M | re.S)
stuff = re.sub('__CONTOUR_BREAKS__', contour_breaks_str, stuff, re.M | re.S)
        
outf = open('plot.Rmd', 'w')
outf.write(stuff)
outf.close()