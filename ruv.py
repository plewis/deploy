import sys, re, os, subprocess as sub

nreps = 25
for rep in range(nreps):
	rep_plus_one = rep + 1
#	print('Replicate %d of %d...' % (rep_plus_one,nreps))

	# Extract rank
	fn = 'rep%d/smc/rank.txt' % rep_plus_one
	stuff = open(fn, 'r').read()
	m = re.search(r'rank: (?P<rank>[.0-9]+)', stuff, re.M | re.S)
	rank = float(m.group('rank'))
	print(rank, ",")
