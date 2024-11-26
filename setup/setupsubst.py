import sys,os,re,math,shutil

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
    
    