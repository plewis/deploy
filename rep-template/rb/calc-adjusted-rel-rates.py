nslow = 
nfast = 

total_rate = ((0.01 * nslow) + (1 * nfast)) / (nslow + nfast)
slow_rate = (1 / total_rate) * 0.01
faster_rate = (1 / total_rate) * 1

# assert rates average to 1
#assert (slow_rate * nslow + nfast * faster_rate == nslow + nfast)

rates = "relative_rates = "
for i in range(nslow):
	rates = rates + str(slow_rate) + " , "

for i in range(nfast):
	if i < nfast - 1:
		rates = rates + str(faster_rate) + " , "
	else:
		rates = rates + str(faster_rate)

print(rates)
