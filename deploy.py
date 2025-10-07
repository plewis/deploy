# See README.md for details

import re,shutil,sys,os,random

sys.path.append('setup')
import setupsubst, setuprep, setupmain

if __name__ == '__main__':
    assert setupmain.nreps < 999999, 'nreps must be less than 999999'
    random.seed(setupmain.master_seed)
    rnseeds = []
    for rep in range(setupmain.nreps):
        # Choose random integer between 1 and 999999
        rint = random.randint(1,999999)
        
        # Create a string with rep+1 followed by rint
        # This ensures that no two random number seeds
        # will be the same
        s = '%d%d' % (rep+1,rint)    
        
        # Convert s to an integer
        sint = int(s)
        
        # Add sint to the vector of random number seeds
        rnseeds.append(sint)
    
    if os.path.exists(setupmain.maindir):
        sys.exit('Directory "%s" exists. Please move or rename it and try again.' % setupmain.maindir)
        
    print('Creating simulation directory "%s"...' % setupmain.maindir)

    # Copy everything in main-template directory to setupmain.maindir
    shutil.copytree('main-template', setupmain.maindir)
    
    setupmain.run(setupmain.maindir, setupmain.nreps)

    for rep in range(1,setupmain.nreps+1):
        print('Creating replicate %d...' % rep)
        
        repdir = os.path.join('rep%d' % rep)
        
        # Copy everything in rep-template directory to
        # a newly-created replicate directory
        shutil.copytree('rep-template', os.path.join(setupmain.maindir, repdir))
        
        # Set up repdir
        setuprep.run(rep, setupmain.nreps, setupmain.maindir, repdir, rnseeds[rep-1])

print('Done.')
