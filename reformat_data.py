

def protected_list_lookup(l,i,v):
	try:
		return l[i]
	except:
		return v

with open("Beta_Synthetic.csv","r") as f:
	lines = f.readlines()
lines = [l.strip() for l in lines]

data = {}

#import pdb
#pdb.set_trace()

li = 0
while (li<len(lines)):
	mperN = int(lines[li].split(' ')[0])
	data[mperN] = {}
	li += 1
	headers = lines[li].split(",")[1:]
	li += 1
	for p in [0.09,0.25,0.5,0.75,0.91]:
		dat = [float(aa) for aa in lines[li].split(',')[1:]]
		for ii,d in enumerate(dat):
			look = protected_list_lookup(headers,ii,'method{}'.format(ii))
			if (data[mperN].get(look) is None):
				data[mperN][look] = []
			data[mperN][look].append(d)
		li += 1

print data

for k in data.keys():
	print k
	for kk in data[k].keys():
		print "% -- {}".format(kk)
		print "\\addplot [boxplot prepared={{lower whisker={},lower quartile={},median={},upper quartile={},upper whisker={} }}] coordinates {{}};".format(*(data[k][kk]))

print "Finished Experiment"



