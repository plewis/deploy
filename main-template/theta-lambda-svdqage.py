import re,os

def substitutions(replacements, infile_path, outfile_path):
    # replacements is a map whose keys are string placeholders
    # that should exist in the target file and values are the 
    # quantities to substitute for those placeholders. Values
    # will be converted to strings using the str() function.
    assert os.path.exists(infile_path), 'Could not find file "%s"' % infile_path
    s = open(infile_path, 'r').read()
    for k in replacements.keys():
        v = str(replacements[k])
        #print('replacing "%s" with "%s" in file "%s"' % (k, v, infile_path))
        s,n = re.subn(k, v, s, re.M | re.S)
        assert n == 1, 'failed to replace "%s" with "%s" in file "%s" (n = %d)' % (k, v, infile_path, n)
    outf = open(outfile_path, 'w')
    outf.write(s)
    outf.close()

print('%12s %12s %12s %12s %12s' % ('rep', 'true theta', 'est. theta', 'true lambda', 'est. lambda'))

nreps = __NREPS__
for rep in range(nreps):
    rep_plus_one = rep + 1
    
    # Extract true theta and lambda from sim/proj.conf
    fn = 'rep%d/sim/proj.conf' % rep_plus_one
    stuff = open(fn, 'r').read()
    if __AAM21005__ or if JC_NET_ID:
        m = re.search(r'.+?theta\s+=\s+(?P<truetheta>[.0-9]+).+?lambda\s+=\s+(?P<truelambda>[.0-9]+)', stuff, re.M | re.S)
    elif __POL02003__:
        m = re.search(r'.+?fixedthetamean\s+=\s+(?P<truetheta>[.0-9]+).+?lambda\s+=\s+(?P<truelambda>[.0-9]+)', stuff, re.M | re.S)
    assert m is not None, 'could not extract true theta and lambda from file "%s"' % fn
    truetheta = float(m.group('truetheta'))
    truelambda = float(m.group('truelambda'))

    # Extract theta and sumbrlens from SVD-qage output
    fn = 'rep%d/svdq/svdout.txt' % rep_plus_one
    stuff = open(fn, 'r').read()
    m = re.search(r'.+?Taxon partition used to assign species membership = .species. \(\d+ lineages mapped to (?P<nspecies>\d+) species\).+?Estimated theta = (?P<theta>[.0-9]+).+?Sum\s+(?P<sumbrlens>[.0-9]+)', stuff, re.M | re.S)
    assert m is not None, 'could not extract nspecies, theta, and sumbrlens from file "%s"' % fn
    esttheta = float(m.group('theta'))
    sumbrlens = float(m.group('sumbrlens'))
    nspecies = int(m.group('nspecies'))
    
    # Estimate lambda from sumbrlens
    
    # Example: n = 5 species
    # 
    #  A   B   C   D   E
    #  |   |   |   |   |    E[t5] = 1/(5*lambda)
    #  +---+   |   |   |
    #    |     |   |   |    E[t4] = 1/(4*lambda)
    #    |     +---+   |
    #    |       |     |    E[t3] = 1/(3*lambda)
    #    |       +-----+
    #    |          |       E[t2] = 1/(2*lambda)
    #    +----------+
    # 
    # sumbrlens =   2*t2   +   3*t3   +   4*t4   +   5*t5
    #
    #                2           3          4         5
    #           = -------- + -------- + -------- + --------
    #             2*lambda   3*lambda   4*lambda   5*lambda
    #
    #           = 4/lambda
    #
    estlambda = (nspecies-1)/sumbrlens
    
    print('%12d %12.5f %12.5f %12.5f %12.5f' % (rep_plus_one, truetheta, esttheta, truelambda, estlambda))
    
    # The setuprep.py file has inserted the strings "__SVDQ_EST_THETA__" 
    # and "__SVDQ_EST_LAMBDA__" into both the smc/proj.conf file and 
    # the beast/starbeast.xml file, so we will now replace those strings
    # with the estimated values

    # Substitute estimated theta and lambda values into proj.conf file in the smc directory of this replicate
    fn = 'rep%d/smc/proj.conf' % rep_plus_one
    substitutions({
        '__SVDQ_EST_THETA__': esttheta,
        '__SVDQ_EST_LAMBDA__': estlambda
    }, fn, fn)

    # Substitute estimated theta and lambda values into starbeast.xml file in the beast directory of this replicate 
    fn = 'rep%d/beast/starbeast.xml' % rep_plus_one
    substitutions({
        '__SVDQ_EST_THETA__': esttheta / 4.0,
        '__SVDQ_EST_LAMBDA1__': estlambda,
        '__SVDQ_EST_LAMBDA2__': estlambda,
        '__SVDQ_EST_LAMBDA3__': estlambda
    }, fn, fn)
