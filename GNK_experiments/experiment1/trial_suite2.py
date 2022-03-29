from minimax_solver6 import calculate_value, calc_LMP
from numpy import array
from tqdm import tqdm
import pdb
import json
from scoop import futures
from copy import deepcopy as copy
from collections import defaultdict

def xxrange(start,end,step=1):
	A = []
	i = 0
	while start+i*step < end:
		A.append([i,start+i*step])
		i += 1
	return A


ppc = {}
# bus_i type Pd Qd Gs Bs area Vm Va baseKV zone Vmax Vmin
ppc["bus"] = [
    [1,-1, 0],
    [2,-1, 0],
    [3,-1, 0],
    [4,-1, 0],
    [5,-1, 0]
]
# bus, Pg, Qg, Qmax, Qmin, Vg, mBase, status, Pmax, Pmin, Pc1, Pc2,
# Qc1min, Qc1max, Qc2min, Qc2max, ramp_agc, ramp_10, ramp_30, ramp_q, apf
ppc["gen"] = [
    [1, -1,-1,-1,-1,-1,-1,-1, 200, 0],
    [2, -1,-1,-1,-1,-1,-1,-1, 0, -100],
    [3, -1,-1,-1,-1,-1,-1,-1, 0, -100],
    [4, -1,-1,-1,-1,-1,-1,-1, 0, -100],
    [5, -1,-1,-1,-1,-1,-1,-1, 0, -100]
]
# fbus, tbus, r, x, b, rateA, rateB, rateC, ratio, angle, status, angmin, angmax
ppc["branch"] = [
    [1, 2, -1,-1,  1, 70],
    [1, 3, -1,-1,  1, 140],
    [1, 4, -1,-1,  1, 70],
    [3, 5, -1,-1,  1, 70]
]
##---  OPF Data  ---##
## generator cost data
# 1 startup shutdown n x1 y1 ... xn yn
# 2 startup shutdown n c(n-1) ... c0
ppc["gencost"] = [
    [2, 0, 0, 2, 0.2, 0],
    [2, 0, 0, 2, 1.9, 0],
    [2, 0, 0, 2, 1.8, 0],
    [2, 0, 0, 2, 1.7, 0],
    [2, 0, 0, 2, 1.6, 0]
]

#ppc['gen'] = ppc['gen'].astype(float)



def simulate(ppc):
	print(ppc['gen_capacity'],ppc['included'])
	lmp = calc_LMP(ppc, debug=False)
	costs = [-float(f) for f in lmp[-2]]
	val = -float(lmp[-1])
	return [costs,val]

if __name__ == "__main__":
	xticks = []
	ppcs = []
	N = len(ppc['bus'])
	for a,i in xxrange(0.1,380,1.7):
		for j in range(0,2**N):
			j_array = [(j>>ii)&1 for ii in range(N)]
			ppcs.append(copy(ppc))
			ppcs[-1]['gen'][0][8] = i
			ppcs[-1]['included'] = j_array
			ppcs[-1]['gen_capacity'] = i
			for ii,jj in enumerate(j_array):
				if jj==0:
					ppcs[-1]['gen'][ii][8] = 0
					ppcs[-1]['gen'][ii][9] = 0
		xticks.append(i)
	raw_data = list(futures.map(simulate, ppcs))
	#raw_data = map(simulate, ppcs)
	data = defaultdict(list)
	for i,r in enumerate(raw_data):
		data[ppcs[i]['gen_capacity']].append([ppcs[i]['included'],r])
	with open('data_shapley.json',"w") as f:
		f.write(json.dumps({"data":data,"xticks":xticks}))




