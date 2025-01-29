import sys, re, os, subprocess as sub

plot_theta_vs_lambda = __PLOT_THETA_VS_LAMBDA__
nspecies = __NUM_SPECIES__

data_from_file = False
if len(sys.argv) > 1:
    data_from_file = True
    
def calcContourBreaksStr(cbmin, cbmax):    
    diff = cbmax - cbmin
    incr = diff/9.0
    breaks = []
    curr = cbmin
    while curr < cbmax:
        breaks.append('%.3f' % curr)
        curr += incr
    return ','.join(breaks)
    
    
summary = []

if data_from_file:
    fn = sys.argv[1]
    print('Opening file "%s"...' % fn)
    
    # Open the input file
    lines = open(sys.argv[1], 'r').readlines()
    
   # # Read headers and ensure that format is what was expected
   # headers = lines[0].strip().split('\t')
   # nheaders = len(headers)
   # assert nheaders == 11, 'Expecting 11 columns but instead found %d in headers\nheaders: %s\n' % (nheaders,headers)
   # assert headers[0] == 'rep' 
   # assert headers[1] == 'theta' 
   # assert headers[2] == 'lambda' 
   # assert headers[3] == 'numdeep' 
   # assert headers[4] == 'maxdeep' 
   # assert headers[5] == 'sppTreeObsHt' 
   # assert headers[6] == 'sppTreeExpHt' 
   # assert headers[7] == 'svdq-rf' 
   # assert headers[8] == 'astral-rf' 
   # assert headers[9] == 'smc-rf' 
   # assert headers[10] == 'beast-rf' 
    
    nlines = len(lines)
    print('nlines = %d' % nlines)
    
    for i,line in enumerate(lines[1:]):
        parts = line.strip().split('\t')
        nparts = len(parts)
        assert nparts == 11, 'Expecting 11 columns but instead found %d in line %d\nline: %s\n' % (nparts, i, line.strip())
        rep       =   int(parts[0])
        theta     = float(parts[1])
        lamBda    = float(parts[2])
        numdeep   =   int(parts[3])
        maxdeep   =   int(parts[4])
        sppTreeObsHt = float(parts[5])
        sppTreeExpHt = float(parts[6])
        svdq_rf      = float(parts[7])
        astral_rf    = float(parts[8])
        smc_rf       = float(parts[9])
        beast_rf     = float(parts[10])
        summary.append({'theta':theta,'lambda':lamBda,'numdeep':numdeep,'maxdeep':maxdeep,'sppTreeObsHt':sppTreeObsHt,'sppTreeExpHt':sppTreeExpHt,'svdq_rf':svdq_rf,'astral_rf':astral_rf,'smc_rf':smc_rf,'beast_rf':beast_rf})
else:
    print('Creating galax plot...')

    nreps = __NREPS__
    for rep in range(nreps):
        rep_plus_one = rep + 1
                
        if __AAM21005__ or if JC_NET_ID:
            # extract deep coalescences
            fn = 'rep%d/sim/deep_coalescences.txt' % rep_plus_one
            maxdeep = 0
            stuff = open(fn, 'r').read()
            # Extract numdeep, maxdeep, and stoheight
            m = re.search(r'num deep coalescences = (?P<numdeep>\d+)\s+Maximum number of deep coalescences = (?P<maxdeep>\d+)\s+True species tree height = (?P<stoheight>[.0-9]+)', stuff, re.M | re.S)
            assert m is not None, 'could not extract deep coalescences from file "%s"' % fn
            numdeep = int(m.group('numdeep'))
            maxdeep = int(m.group('maxdeep'))
            stoheight = float(m.group('stoheight'))
            
             # Extract stxheight (species tree expected height)
            m = re.search(r'Expected species tree height = (?P<stxheight>[.0-9]+)', stuff, re.M | re.S)
            assert m is not None, 'could not extract expected species tree height from file "%s"' % fn
            stxheight = float(m.group('stxheight'))
            
            # extract lambda and theta mean
            fn = 'rep%d/sim/proj.conf' % rep_plus_one
            stuff = open(fn, 'r').read()
            m = re.search(r'theta\s+=\s+(?P<theta>[-.e0-9]+)\s+lambda\s+=\s+(?P<lambda>[.e0-9]+)', stuff, re.M | re.S)
            assert m is not None, 'could not extract theta and lambda from file "%s"' % fn
            theta = float(m.group('theta'))
            lamBda = float(m.group('lambda'))
            
           # Extract information from new galax output
            fn = 'smcout%d.txt' % rep_plus_one
            stuff_two = open(fn, 'r').read()
            
            m = re.search(r'([0-9]*\.[0-9]*) percent information given sample size', stuff_two, re.M | re.S)
            assert m is not None, 'could not extract information content from file "%s"' % fn
            smc_info = float(m.group(1))
            
           # Extract information from old galax output
            fn = 'smcout%d.txt' % rep_plus_one
            stuff_three = open(fn, 'r').read()
            
            m = re.search(r'average *[0-9]*[ \t]+[0-9.]*[ \t]+[0-9.]*[ \t]+[0-9.]*[ \t]+[0-9.]*[ \t]+([0-9.]*)', stuff_three, re.M | re.S)
            assert m is not None, 'could not extract information content from file "%s"' % fn
            smc_old_info = float(m.group(1))
            
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
            
        summary.append({'theta':theta,'lambda':lamBda,'numdeep':numdeep,'maxdeep':maxdeep,'sppTreeObsHt':stoheight, 'sppTreeExpHt':stxheight, 'smc_info':smc_info, 'smc_old_info':smc_old_info})
        output_string  = '%d\t' % rep_plus_one
        output_string += '%.5f\t' % theta
        output_string += '%.5f\t' % lamBda
        output_string += '%d\t' % numdeep
        output_string += '%d\t' % maxdeep
        output_string += '%.5f\t' % stoheight
        output_string += '%.5f\t' % stxheight
        output_string += '%.5f\t' % smc_info  
        output_string += '%.5f\t' % smc_old_info      

nsummary = len(summary)
print('len(summary) = %d' % nsummary)

if plot_theta_vs_lambda:
    # Create thetavector and lambdavector
    lambdavector = []
    thetavector = []
    for s in summary:
        lambdavector.append('%g' % s['lambda'])
        thetavector.append('%g' % s['theta'])
    lambdastr = ','.join(lambdavector)
    thetastr = ','.join(thetavector)
else:
    # Create halfthetavector and Tvector
    Tvector = []
    halfthetavector = []
    for s in summary:
        halftheta = s['theta']/2.0
        T = s['sppTreeExpHt']
        Tvector.append('%g' % T)
        halfthetavector.append('%g' % halftheta)
    Tstr = ','.join(Tvector)
    halfthetastr = ','.join(halfthetavector)

# Create smcInfomeans
smcInfomeans = []
numdeep = []
maxdeep = []
contour_breaks_max = None
contour_breaks_min = None
for s in summary:
    smcInfomeans.append('%g' % s['smc_info'])
    diff = s['smc_info']
    if contour_breaks_max is None or diff > contour_breaks_max:
        contour_breaks_max = diff
    if contour_breaks_min is None or diff < contour_breaks_min:
        contour_breaks_min = diff
    numdeep.append('%d' % s['numdeep'])
    maxdeep.append('%d' % s['maxdeep'])
    
# Create smcOldInfomeans
smcOldInfomeans = []
for s in summary:
    smcOldInfomeans.append('%g' % s['smc_old_info'])
    diff = s['smc_old_info']

smcinfostr = ','.join(smcInfomeans)
smcoldinfostr = ','.join(smcOldInfomeans)
numdeepstr = ','.join(numdeep)
maxdeepstr = ','.join(maxdeep)

contour_breaks_str = calcContourBreaksStr(contour_breaks_min, contour_breaks_max)

if plot_theta_vs_lambda:
    assert False # does not work yet
    ## Open plot-theta-lambda-template.Rmd
    #stuff = open('plot-theta-lambda-template.Rmd', 'r').read()
    #stuff = re.sub('__NSPECIES__', '%d' % nspecies, stuff, re.M | re.S)
    #stuff = re.sub('__LAMBDAVECTOR__', lambdastr, stuff, re.M | re.S)
    #stuff = re.sub('__THETAVECTOR__', thetastr, stuff, re.M | re.S)
    #stuff = re.sub('__CONTOUR_BREAKS__', contour_breaks_str, stuff, re.M | re.S)
    #stuff = re.sub('__NUMDEEP__', numdeepstr, stuff, re.M | re.S)
    #stuff = re.sub('__MAXDEEP__', maxdeepstr, stuff, re.M | re.S)
    #stuff = re.sub('__SMC_INFO__', smcinfostr, stuff, re.M | re.S)
else:
    # Open plot-halftheta-T-template.Rmd
    stuff = open('plot-halftheta-T-galax-template.Rmd', 'r').read()
    stuff = re.sub('__NSPECIES__', '%d' % nspecies, stuff, re.M | re.S)
    stuff = re.sub('__TVECTOR__', Tstr, stuff, re.M | re.S)
    stuff = re.sub('__HALFTHETAVECTOR__', halfthetastr, stuff, re.M | re.S)
    stuff = re.sub('__SMC_INFO__', smcinfostr, stuff, re.M | re.S)
    stuff = re.sub('__SMC_OLD_INFO__', smcoldinfostr, stuff, re.M | re.S)
    stuff = re.sub('__CONTOUR_BREAKS__', contour_breaks_str, stuff, re.M | re.S)
    stuff = re.sub('__NUMDEEP__', numdeepstr, stuff, re.M | re.S)
    stuff = re.sub('__MAXDEEP__', maxdeepstr, stuff, re.M | re.S)

outf = open('plot-galax.Rmd', 'w')
outf.write(stuff)
outf.close()
