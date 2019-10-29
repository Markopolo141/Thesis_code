#Experiment: Synthetic Data
#--------------------------
#
# computes the average error for mean estimation in the case
# of randomly generated strata numbers of beta distributed data
# for sample budgets between 10 and 150, outputs data to csv file


#do imports
from random import shuffle,random,randint,betavariate
from copy import deepcopy as copy
from methods2 import *
import sys
try:
	from tqdm import tqdm
	tqdm_enabled=True
except ImportError:
	tqdm_enabled=False

d=1.0 #data width is one for beta distribution


methods = ['burgess_bound_ideal_small', 'altered_burgess_bound_small', 'neyman_bound_ideal', 'burgess_bound_small', 'Hoeffding_selection', 'burgess_bound', 'Maurer_selection', 'Audibert_selection']
methods_list = {m:globals()[m] for m in methods}

['super_castro_small', 'super_castro']

#open csv file
with open("Beta_Synthetic_bounds.csv","w") as f:

	#for each sample budget
	for mperN in [50,100]:
		print mperN

		#data holding for the errors
		sampling_errors = [list() for i in range(len(methods_list.keys()))]
		
		iterator = range(5000)
		if tqdm_enabled:
			iterator = tqdm(iterator)
		for trial in iterator: #iterate a large number of times

			# generate strata dimensions
			N = randint(5,21)							#number of strata
			Ni = [randint(10,201) for i in range(N)]	#strata sizes
			m = mperN * N								#sample budget
			while (sum(Ni)<m):							#regenerate while sample budget is too large
				N = randint(5,21)
				Ni = [randint(10,201) for i in range(N)]
				m = mperN * N

			#generate population data values for the strata
			vals = []
			for i in range(N):
				alpha = random()*4
				beta = random()*4
				vals.append([betavariate(alpha,beta) for ii in range(Ni[i])])

			#calculate actual population mean
			collected_vals = sum(vals,[])
			mean = sum(collected_vals)*1.0/len(collected_vals)

			for ii,k in enumerate(methods_keys):
				cvals = copy(vals)
				sampling_errors[ii].append(abs(mean-methods_list[k](cvals,m,d)))


		#sorting the sampling errors for quartile reporting
		sampling_errors = [sorted(s) for s in sampling_errors]

		#write csv entry, using rough quartile reporting
		f.write("{} sample budget per strata\n".format(mperN))
		f.write(",{}\n".format(",".join(methods_keys)))
		for p in [0.09,0.25,0.5,0.75,0.91]:
			pp = [s[int(len(s)*p)] for s in sampling_errors]
			f.write("{} percentile,".format(p))
			f.write((",".join(["{}" for ppp in pp])).format(*pp))
			f.write("\n")

print "Finished Experiment"



