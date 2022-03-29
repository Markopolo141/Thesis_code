from tqdm import tqdm
import pdb
import json
from statistics import mean
from tqdm import tqdm
from collections import defaultdict

with open('data_shapley.json',"r") as f:
	data = json.load(f)

data = data['data']
players = len(data[list(data.keys())[0]][0][0])
shapley_values = defaultdict(list)
shapley_costs = {}
for k in data.keys():
	data_k = data[k]
	k = float(k)
	data_by_index = {}
	for dd in data_k:
		data_by_index[tuple(dd[0])] = dd[1][1]
		if 0 not in dd[0]:
			shapley_costs[k] = dd[1][0]
	for p in range(players):
		indices = [dd[0] for dd in data_k if dd[0][p]==0] #all the indices which the player is absent
		indices_by_number = defaultdict(list)
		for dd in indices:
			mod_dd = dd.copy()
			mod_dd[p] = 1
			indices_by_number[sum(dd)].append(data_by_index[tuple(mod_dd)] - data_by_index[tuple(dd)])
		for kk in indices_by_number.keys():
			indices_by_number[kk] = mean(indices_by_number[kk])
		shapley_values[p].append((k,mean(indices_by_number.values())))

with open("data_shap.txt","w") as f:
	sorted_keys = sorted(shapley_values.keys())
	for p in sorted_keys:
		f.write("".join([str(ss) for ss in shapley_values[p]]))
		f.write("\n\n")

with open("data_shap_transfers.txt","w") as f:
	sorted_keys = sorted(shapley_values.keys())
	for p in sorted_keys:
		f.write("".join([str((ss[0],ss[1]-shapley_costs[ss[0]][p])) for ss in shapley_values[p]]))
		f.write("\n\n")

