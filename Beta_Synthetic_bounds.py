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


def xxrange(start,stop,step):
	x = start
	while (x<=stop):
		yield x
		x += step


#['burgess_bound_ideal_small', 'altered_burgess_bound_small', 'neyman_bound_ideal', 'burgess_bound_small', 'Hoeffding_selection', 'burgess_bound', 'Maurer_selection', 'Audibert_selection']
methods = ['burgess_bound_ideal', 'altered_burgess_bound_small', 'neyman_bound_ideal', 'burgess_bound_small', 'Hoeffding_selection', 'burgess_bound', 'Maurer_selection', 'burgess_bound_ideal_small', 'Audibert_selection']
methods_list = {m:globals()[m] for m in methods}

allocation_method = super_castro
#['super_castro_small', 'super_castro']

sstep = 0.01
pvals = list(xxrange(sstep,0.9999999999,sstep))

#open csv file
with open("Beta_Synthetic_bounds.csv","w") as f:
	with open("Beta_Synthetic_bounds.json","w") as ff:

		#for each sample budget
		for mperN in [50,100]:
			print mperN

			#data holding for the errors
			data = [[[] for ii in range(len(pvals))] for i in range(len(methods_list.keys()))]
			
			iterator = range(1000)
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
				
				samples = super_castro_small(vals,m,d)
				if (0 in samples) or (1 in samples):
					continue
				mean = [sum(cc)*1.0/len(cc) for cc in vals]
				sample_mean = [sum(cc[0:samples[i]])*1.0/samples[i] for i,cc in enumerate(vals)]
				var = [sum([(c-mean[i])**2 for c in cc])*1.0/len(cc) for i,cc in enumerate(vals)]
				s_var = [sum([(c-sample_mean[i])**2 for c in cc[0:samples[i]]])*1.0/(samples[i]-1) for i,cc in enumerate(vals)]

				for iii,k in enumerate(methods):
					for ii,p in enumerate(pvals):
						if 'ideal' in k:
							data[iii][ii].append(methods_list[k](len(vals),[len(v) for v in vals],samples,var,d,p))
						else:
							data[iii][ii].append(methods_list[k](len(vals),[len(v) for v in vals],samples,s_var,d,p))

			#write csv entry, using rough quartile reporting
			f.write("{} sample budget per strata\n".format(mperN))
			f.write(",{}\n".format(",".join(methods)))
			for i,p in enumerate(pvals):
				f.write("{},".format(p))
				for ii,m in enumerate(methods):
					f.write("{},".format(min(1,sum(data[ii][i])*1.0/len(data[ii][i]))))
				f.write("\n")
			
			ff.write("{} sample budget per strata\n".format(mperN))
			for ii,m in enumerate(methods):
				ff.write("{}\n".format(m))
				for i,p in enumerate(pvals):
					ff.write("({},{})".format(min(1,sum(data[ii][i])*1.0/len(data[ii][i])),p))
				ff.write("\n");
print "Finished Experiment"



