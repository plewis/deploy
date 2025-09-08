import sys, re, os, subprocess as sub

plot_theta_vs_lambda = __PLOT_THETA_VS_LAMBDA__
nspecies = __NUM_SPECIES__

data_from_file = False
if len(sys.argv) > 1:
    data_from_file = True
    
    
summary = []


print('Creating BHV info plot...')

with open('info.txt', 'r') as file:
     info_lines = lines = file.readlines()

nreps = __NREPS__
for rep in range(nreps):
  rep_plus_one = rep + 1
          
  if __AAM21005__:
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

      # extract BHV info
      rep_info = info_lines[rep].rstrip(',\n')
      assert rep_info is not None, 'could not extract bhv info from info.txt file'
      smc_info = float(rep_info)
      
  elif __JJC23002__:
      # extract deep coalescences
      fn = 'g-prior/rep%d/sim/deep_coalescences.txt' % rep_plus_one
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
                  
  elif __POL02003__:
            # extract deep coalescences
      fn = 'g-prior/rep%d/sim/deep_coalescences.txt' % rep_plus_one
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
  
     # Extract SMC RF means
     fn = 'smcrf%d.txt' % rep_plus_one
     assert (os.path.exists(fn))
     lines = open(fn, 'r').readlines()
     smcrfsum = 0.0
     smcrfnum = 0
     for line in lines[1:]:
         parts = line.strip().split()
         assert len(parts) == 2, 'expecting 2 parts but found %d in file "%s"' % (len(parts), fn)
         smcrfnum += 1
         smcrfsum += float(parts[1])
         smc_rf = smcrfsum/smcrfnum
            
     summary.append({'theta':theta,'lambda':lamBda,'numdeep':numdeep,'maxdeep':maxdeep,'sppTreeObsHt':stoheight, 'sppTreeExpHt':stxheight, 'smc_info':smc_info, 'smc_rf':smc_rf})

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


# Create smcInfomeans
smcInfomeans = []
numdeep = []
maxdeep = []
for s in summary:
    smcInfomeans.append('%g' % s['smc_info'])
    breakpt = s['smc_info']
    numdeep.append('%d' % s['numdeep'])
    maxdeep.append('%d' % s['maxdeep'])
    halfthetastr = ','.join(halfthetavector)
     
# Create smcmeans
smcRFmeans = []
for s in summary:
    smcRFmeans.append('%g' % s['smc_rf'])


smcinfostr = ','.join(smcInfomeans)
numdeepstr = ','.join(numdeep)
maxdeepstr = ','.join(maxdeep)
smcrfstr = ','.join(smcRFmeans)

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
    stuff = re.sub('__NUMDEEP__', numdeepstr, stuff, re.M | re.S)
    stuff = re.sub('__MAXDEEP__', maxdeepstr, stuff, re.M | re.S)
    stuff = re.sub('__SMCRFMEANS__', smcrfstr, stuff, re.M | re.S)

outf = open('plot-bhv-info.Rmd', 'w')
outf.write(stuff)
outf.close()
