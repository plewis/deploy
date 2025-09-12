import sys, re, os, subprocess as sub
from math import log

# this file calculates BHV info after td program has been run

nreps = __NREPS__

prior_variance = []
posterior_variance = []
prior_lengths = []
posterior_lengths = []

for rep in range(nreps):
	rep_plus_one = rep + 1

	# Extract rank
	fn = 'g-prior/rep%d/smc/mean.txt' % rep_plus_one
	stuff = open(fn, 'r').read()
	m1 = re.search(r'# 95% HPD lower =\s*(\d+(?:\.\d+)?)', stuff, re.M | re.S)
	assert m1 is not None
	hpd_lower = float(m1.group(1))
	m2 = re.search(r'# 95% HPD upper =\s*(\d+(?:\.\d+)?)', stuff, re.M | re.S)
	assert m2 is not None
	m3 = re.search(r'# tree length =\s*(\d+(?:\.\d+)?)', stuff, re.M | re.S)
	assert m3 is not None
	hpd_upper = float(m2.group(1))
	prior_variance.append(hpd_upper - hpd_lower)
	prior_length = float(m3.group(1))
	prior_lengths.append(prior_length)

for rep in range(nreps):
	rep_plus_one = rep + 1

	# Extract rank
	fn = 'g-posterior/rep%d/smc/mean.txt' % rep_plus_one
	stuff = open(fn, 'r').read()
	m1 = re.search(r'# 95% HPD lower =\s*(\d+(?:\.\d+)?)', stuff, re.M | re.S)
	hpd_lower = float(m1.group(1))
	m2 = re.search(r'# 95% HPD upper =\s*(\d+(?:\.\d+)?)', stuff, re.M | re.S)
	m3 = re.search(r'# tree length =\s*(\d+(?:\.\d+)?)', stuff, re.M | re.S)
	assert m3 is not None
	hpd_upper = float(m2.group(1))
	posterior_variance.append(hpd_upper - hpd_lower)
	posterior_length = float(m3.group(1))
	posterior_lengths.append(posterior_length)

info_list = []

for rep in range(nreps):
	prior_var = float(prior_variance[rep])
	post_var = float(posterior_variance[rep])
	prior_length = float(prior_lengths[rep])
	posterior_length = float(posterior_lengths[rep])
	scaling_factor = posterior_length / prior_length
	prior_var = prior_var * scaling_factor
	info_list.append(((prior_var - post_var) / prior_var))

	# LCR = log(prior_var) - log(post_var)
	# info_list.append(LCR)

with open('info.txt', 'w') as file:
	for i in info_list:
		file.write(str(i) + ',' + '\n')
