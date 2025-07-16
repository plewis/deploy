import sys, re, os, subprocess as sub

nreps = __NREPS__
print("min:")

for rep in range(nreps):
	rep_plus_one = rep + 1

	# Extract rank
	fn = 'rep%d/smc/hpd.txt' % rep_plus_one
	stuff = open(fn, 'r').read()
	m1 = re.search(r'([.0-9]+)', stuff, re.M | re.S)
	min = m1.group(0)
	print(min, " ,")

print("max:")
for rep in range(nreps):
        rep_plus_one = rep + 1

       	# Extract rank
        fn = 'rep%d/smc/hpd.txt' % rep_plus_one
        stuff = open(fn, 'r').read()
        m2 = re.search(r'\t([.0-9]+)', stuff, re.M | re.S)
        max = m2.group(0)
       	#rank = float(m.group('rank'))
        print(max, " ,")