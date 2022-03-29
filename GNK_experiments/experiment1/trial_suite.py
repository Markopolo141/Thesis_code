from minimax_solver6 import calculate_value, calc_LMP
from numpy import array
from tqdm import tqdm
import pdb
import json
from scoop import futures
from copy import deepcopy as copy


def xxrange(start,end,step=1):
	A = []
	i = 0
	while start+i*step < end:
		A.append([i,start+i*step])
		i += 1
	return A


ppc = {}
# bus_i type Pd Qd Gs Bs area Vm Va baseKV zone Vmax Vmin
ppc["bus"] = array([
    [1,-1, 0],
    [2,-1, 0],
    [3,-1, 0],
    [4,-1, 0],
    [5,-1, 0]
])
# bus, Pg, Qg, Qmax, Qmin, Vg, mBase, status, Pmax, Pmin, Pc1, Pc2,
# Qc1min, Qc1max, Qc2min, Qc2max, ramp_agc, ramp_10, ramp_30, ramp_q, apf
ppc["gen"] = array([
    [1, -1,-1,-1,-1,-1,-1,-1, 200, 0],
    [2, -1,-1,-1,-1,-1,-1,-1, 0, -100],
    [3, -1,-1,-1,-1,-1,-1,-1, 0, -100],
    [4, -1,-1,-1,-1,-1,-1,-1, 0, -100],
    [5, -1,-1,-1,-1,-1,-1,-1, 0, -100]
])
# fbus, tbus, r, x, b, rateA, rateB, rateC, ratio, angle, status, angmin, angmax
ppc["branch"] = array([
    [1, 2, -1,-1,  1, 70],
    [1, 3, -1,-1,  1, 140],
    [1, 4, -1,-1,  1, 70],
    [3, 5, -1,-1,  1, 70]
])
##---  OPF Data  ---##
## generator cost data
# 1 startup shutdown n x1 y1 ... xn yn
# 2 startup shutdown n c(n-1) ... c0
ppc["gencost"] = array([
    [2, 0, 0, 2, 0.2, 0],
    [2, 0, 0, 2, 1.9, 0],
    [2, 0, 0, 2, 1.8, 0],
    [2, 0, 0, 2, 1.7, 0],
    [2, 0, 0, 2, 1.6, 0]
],dtype=float)

xticks = []
data = [[[],[],[],[],[],[],[],[]] for a in range(len(ppc['bus']))]

ppc['gen'] = ppc['gen'].astype(float)



def simulate(ppc):
	print(ppc['gen'][0][8],ppc['excluded'])
	if ppc['excluded']==-1:
		lmp = calc_LMP(ppc, debug=True)
		value = calculate_value(ppc, debug=True, tqdm_show=False, bignum=999999) 
		return value, lmp
	else:
		lmp = calc_LMP(ppc, debug=True)
		return None, lmp

if __name__ == "__main__":
	ppcs = []
	for a,i in xxrange(0.1,380,1.7):
		for j in range(-1,len(ppc['bus'])):
			ppc['gen'][0][8] = i
			ppc['excluded'] = j
			ppcs.append(copy(ppc))
			if (j>=0):
				ppcs[-1]['gen'][j][8] = 0
				ppcs[-1]['gen'][j][9] = 0
		xticks.append(i)
	#raw_data = list(futures.map(simulate, ppcs))
	raw_data = map(simulate, ppcs)
	for i,r in enumerate(raw_data):
		results, results2 = r
		if ppcs[i]['excluded']==-1:
			for ii in range(len(data)):
				data[ii][0].append(results[0][ii])
				data[ii][1].append(results[1][ii])
				data[ii][2].append(results[2][0]['p{}'.format(ii)])
				data[ii][3].append(results[2][1]['p{}'.format(ii)])
				data[ii][4].append(results2[0][ii])
				data[ii][5].append(results2[1][ii])
				data[ii][6].append(0)
				data[ii][7].append(0)
				for iii in range(len(data)):
					data[ii][6][-1] += float(results2[2][iii])
					if iii!=ii:
						data[ii][7][-1] += float(results2[2][iii])
		else:
			for iii in range(len(data)):
				data[ppcs[i]['excluded']][6][-1] -= float(results2[2][iii])
				data[ppcs[i]['excluded']][7][-1] -= float(results2[2][iii])
	#pdb.set_trace()
	with open('data.json',"w") as f:
		f.write(json.dumps({"data":data,"xticks":xticks}))




