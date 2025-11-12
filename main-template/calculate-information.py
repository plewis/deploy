import sys, re, os, subprocess as sub

# this file calculates BHV info after td program has been run

nreps = __NREPS__

prior_variance = []
posterior_variance = []

for rep in range(nreps):
	rep_plus_one = rep + 1

	# Extract rank
	fn = 'g-prior/rep%d/smc/mean.R' % rep_plus_one
	stuff = open(fn, 'r').read()
	m1 = re.search(r'variance =\s*(\d+(?:\.\d+)?)', stuff, re.M | re.S)
	prior_var = m1.group(1)
	prior_variance.append(prior_var)
	
for rep in range(nreps):
	rep_plus_one = rep + 1

	# Extract rank
	fn = 'g-posterior/rep%d/smc/mean.R' % rep_plus_one
	stuff = open(fn, 'r').read()
	m1 = re.search(r'variance =\s*(\d+(?:\.\d+)?)', stuff, re.M | re.S)
	post_var = m1.group(1)
	posterior_variance.append(post_var)
	
info_list = []

for rep in range(nreps):
	prior_var = float(prior_variance[rep])
	post_var = float(posterior_variance[rep])
	info_list.append((prior_var - post_var) / prior_var)

with open('info.txt', 'w') as file:
	for i in info_list:
		file.write(str(i) + ',' + '\n')
