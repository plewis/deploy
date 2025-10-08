import sys, re, os, subprocess as sub
from math import log

# this file calculates BHV info after td program has been run

nreps = __NLOCI__

prior_variance = []
posterior_variance = []
prior_lengths = []
posterior_lengths = []

for rep in range(nreps):
	rep_plus_one = rep + 1

	fn = 'gene%d/output-prior/mean.txt' % rep_plus_one
	stuff = open(fn, 'r').read()
	m1 = re.search(r'# 95% radius =\s*(\d+(?:\.\d+)?)', stuff, re.M | re.S)
	assert m1 is not None
	radius = float(m1.group(1))
	m3 = re.search(r'# tree length =\s*(\d+(?:\.\d+)?)', stuff, re.M | re.S)
	assert m3 is not None
	prior_variance.append(radius)
	prior_length = float(m3.group(1))
	prior_lengths.append(prior_length)

for rep in range(nreps):
	rep_plus_one = rep + 1

	fn = 'gene%d/output-posterior/mean.txt' % rep_plus_one
	stuff = open(fn, 'r').read()
	m1 = re.search(r'# 95% radius =\s*(\d+(?:\.\d+)?)', stuff, re.M | re.S)
	radius = float(m1.group(1))
	m3 = re.search(r'# tree length =\s*(\d+(?:\.\d+)?)', stuff, re.M | re.S)
	assert m3 is not None
	posterior_variance.append(radius)
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
