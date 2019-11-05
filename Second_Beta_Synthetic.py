#Experiment: Synthetic Data
#--------------------------
#
# computes the average error for mean estimation in the case
# of randomly generated strata numbers of beta distributed data
# for sample budgets between 10 and 150, outputs data to csv file


#do imports
from random import shuffle,random,randint,betavariate
from copy import deepcopy as copy
from methods import *
import sys
try:
	from tqdm import tqdm
	tqdm_enabled=True
except ImportError:
	tqdm_enabled=False

d=1.0 #data width is one for beta distribution

print "Computing Beta data Experiment"
print " for sample budget per strata of [10,50,100,150] ---"


Hoeffding_union_method =	Adapto_sampling(Hoeffding_selection)
Audibert_union_method =		Adapto_sampling(Audibert_selection)
Maurer_union_method =		Adapto_sampling(Maurer_selection)
Burgess_union_method =		Adapto_sampling(Burgess_selection)
Random_union_method =		Adapto_sampling(Random_selection)




methods_list = [
("Ney",super_castro)
]

methods_keys = [a[0] for a in methods_list]
methods_list = {a:b for a,b in methods_list}

#open csv file
with open("Second_Beta_Synthetic.csv","w") as f:
	with open("Second_Beta_Synthetic_bounds.json","w") as ff:

		#for each sample budget
		for mperN in [50]:
			print mperN

			#data holding for the errors
			sampling_errors = [list() for i in range(len(methods_list.keys()))] #[[],[],[],[],[],[],[]]
			
			iterator = range(10000)
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
			for p in [(ii+1)*1.0/40 for ii in range(39)]:
				pp = [s[int(len(s)*p)] for s in sampling_errors]
				f.write("{} percentile,".format(p))
				f.write((",".join(["{}" for ppp in pp])).format(*pp))
				f.write("\n")
			
			ff.write("{} sample budget per strata\n".format(mperN))
			ff.write(",{}\n".format(",".join(methods_keys)))
			for i,s in enumerate(sampling_errors):
				ff.write(methods_keys[i])
				ff.write("\n")
				for p in [(ii+1)*1.0/40 for ii in range(39)]:
					pp = s[int(len(s)*p)]
					ff.write("({},{})".format(pp,1.0-p))
				ff.write("\n")

print "Finished Experiment"



