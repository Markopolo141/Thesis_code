#  Methods.py
#  ---------
#
# The Implementation of all the sampling methods used for the synthetic data experiments
# and some utility functions

from random import shuffle,choice,randint
from math import floor,factorial,log,sqrt

'''given an array of numbers a, scale thoes numbers to closest integers such as to sum to integer v'''
def scale_array(a,v):
	if sum(a) != 0:
		vsuma = v*1.0/sum(a)
		a = [vsuma*aa for aa in a]
		overflow = [aa-floor(aa) for aa in a]
		a = [int(floor(aa)) for aa in a]
		while sum(a)<v:
			i = overflow.index(max(overflow))
			overflow[i]-=1
			a[i]+=1
		return a
	else:
		a = [int(v*1.0/len(a)) for aa in a]
		i=-1
		while sum(a)<=v:
			i += 1
			a[i] += 1
		a[i] -= 1
		return a


def super_castro_small(vals,m,d):
	lengths = [len(v) for v in vals]
	sumN = sum([len(v) for v in vals])
	meanvals = [sum(vals[i])*1.0/len(vals[i]) for i in range(len(vals))]
	varvals = [sum([(vals[i][o]-meanvals[i])**2 for o in range(len(vals[i]))])*1.0/len(vals[i]) for i in range(len(vals))]
	samples = [1 for i in range(len(vals))]
	new_samples = scale_array([sqrt(varvals[i])*lengths[i] for i in range(len(vals))],m-sum(samples))
	for i in range(len(samples)):
		samples[i] += new_samples[i]
	return samples

def super_castro(vals,m,d):
	lengths = [len(v) for v in vals]
	sumN = sum([len(v) for v in vals])
	meanvals = [sum(vals[i])*1.0/len(vals[i]) for i in range(len(vals))]
	varvals = [sum([(vals[i][o]-meanvals[i])**2 for o in range(len(vals[i]))])*1.0/len(vals[i]) + 0.00000001 for i in range(len(vals))]
	samples = [1 for i in range(len(varvals))]
	allocated = sum(samples)

	while allocated < m:
		new_samples = scale_array([sqrt(varvals[i])*lengths[i] for i in range(len(vals))],m-allocated)
		for i in range(len(samples)):
			if samples[i]+new_samples[i] >= len(vals[i]):
				varvals[i]=0
				additional = len(vals[i])-samples[i]
			else:
				additional = new_samples[i]
			samples[i] += additional
			allocated += additional
	return samples



#OmegaBig = lambda n,N: sum([1.0/(k**2) for k in range(n,N)])
#PsiBig = lambda n,N: N*sum([1.0/(k**2*(k+1)) for k in range(n,N)])
OmegaBig = lambda n,N: (n+1)*(1-n*1.0/N)*1.0/(n**2)
PsiBig = lambda n,N: (N+1.0-n)/(n**2)
OmegaSmall = lambda n,N: 1.0/n
PsiSmall = lambda n,N: 1.0/n
def burgess_bound(N,ni,Ni,var,d,r):
	sumN = sum(Ni)
	onN = [0 for i in range(2)]
	max1 = [0 for i in range(2)]
	var1 = [0 for i in range(2)]
	d1 = [0 for i in range(2)]
	log6r = log(6/r)
	log3r = log(3/r)
	log2r = log(2/r)
	log6Nr = log(6*N/r)
	d2 = d*d;
	for i in range(N):
		tau = Ni[i]*1.0/sumN
		OB = OmegaBig(ni[i],Ni[i])
		OS = OmegaSmall(ni[i],Ni[i])
		PB = PsiBig(ni[i],Ni[i])
		PS = PsiSmall(ni[i],Ni[i])
		onN[0] += PB*min(OB,OS)*tau**2
		onN[1] += PS*min(OB,OS)*tau**2
		max1[0] = max(max1[0],PB*min(PB,PS)*tau**2)
		max1[1] = max(max1[1],PS*min(PB,PS)*tau**2)
		var1[0] += PB*((ni[i]-1)*var[i]*1.0/ni[i])*tau**2
		var1[1] += PS*((ni[i]-1)*var[i]*1.0/ni[i])*tau**2
		d1[0] += OB*tau**2
		d1[1] += OS*tau**2
	A = [0,0]
	A[0] = (d2*4.0/(17))*log6r*d1[0] + log6r*(sqrt(2*var1[0] + log6Nr*d2*onN[0] + log3r*d2*max1[0]) + sqrt(log3r*d2*max1[0]))**2
	A[1] = (d2*4.0/(17))*log6r*d1[1] + log6r*(sqrt(2*var1[1] + log6Nr*d2*onN[1] + log3r*d2*max1[1]) + sqrt(log3r*d2*max1[1]))**2
	return sqrt(min(A))



def burgess_bound_small(N,ni,Ni,var,d,r):
	sumN = sum(Ni)
	onN = 0
	max1 = 0
	var1 = 0
	d1 = 0
	log6r = log(6/r)
	log3r = log(3/r)
	log2r = log(2/r)
	logN = log(N)
	log2 = log(2)
	d2 = d*d;
	for i in range(N):
		tau = Ni[i]*1.0/sumN
		OS = OmegaSmall(ni[i],Ni[i])
		PS = PsiSmall(ni[i],Ni[i])
		onN += PS*OS*tau**2
		max1 = max(max1,PS*PS*tau**2)
		var1 += PS*((ni[i]-1)*var[i]*1.0/ni[i])*tau**2
		d1 += OS*tau**2
	A = [0]
	A[0] = (d2*4.0/(17))*log6r*d1 + log6r*(sqrt(2*var1 + (log6r+logN)*d2*onN/log2 + log3r*d2*max1) + sqrt(log3r*d2*max1))**2
	return sqrt(min(A))



def burgess_bound_ideal_small(N,Ni,ni,var,d,p):
	oversumN = 1.0/sum(Ni)
	v = 0
	d2 = d*d
	o17 = 1.0/17
	for i in range(N):
		a = (OmegaBig(ni[i],Ni[i])*d2*o17 + PsiBig(ni[i],Ni[i])*var[i]*0.5)*(Ni[i]*oversumN)**2
		b = (OmegaSmall(ni[i],Ni[i])*d2*o17 + PsiSmall(ni[i],Ni[i])*var[i]*0.5)*(Ni[i]*oversumN)**2
		v += min(a,b)
	return sqrt(4*log(2.0/p)*v)


def neyman_bound_ideal(N,Ni,ni,var,d,p):
	oversumN = 1.0/sum(Ni)
	v = 0
	for i in range(N):
		a = (var[i]*1.0/ni[i])*(Ni[i]*oversumN)**2
		v += a
	return sqrt(v*1.0/p)




def burgess_bound_ideal_small(N,Ni,ni,var,d,p):
	oversumN = 1.0/sum(Ni)
	v = 0
	d2 = d*d
	o17 = 1.0/17
	for i in range(N):
		b = (OmegaSmall(ni[i],Ni[i])*d2*o17 + PsiSmall(ni[i],Ni[i])*var[i]*0.5)*(Ni[i]*oversumN)**2
		#d = (OmegaSmall(ni[i],Ni[i])*d2*1.0/2)*(Ni[i]*1.0/sumN)**2
		v += b
	return sqrt(4*log(2.0/p)*v)




def Hoeffding_selection(N,Ni,n,v,d,t):
	t /= N
	SNi = sum(Ni)
	vector = [sqrt(log(1.0/t)/(2*n[i])) for i in range(len(m))]
	vector = [Ni[i]*v*1.0/SNi for i,v in enumerate(vector)]
	return sum(vector)

def Audibert_selection(N,Ni,n,v,d,t):
	t /= N
	SNi = sum(Ni)
	vector = [sqrt(v[i]*log(3.0/t)/(2*n[i])) + 3*log(3.0/t)/(2*n[i]) for i in range(len(m))]
	vector = [Ni[i]*v*1.0/SNi for i,v in enumerate(vector)]
	return sum(vector)

def Maurer_selection(N,Ni,n,v,d,t):
	t /= N
	SNi = sum(Ni)
	vector = [sqrt(2*v[i]*log(2.0/t)/(n[i])) + 7*log(2.0/t)/(3*(n[i]-1)) for i in range(len(m))]
	vector = [Ni[i]*v*1.0/SNi for i,v in enumerate(vector)]
	return sum(vector)


def altered_burgess_bound_small(N,ni,Ni,var,d,r):
	sumN = sum(Ni)
	onN = 0
	max1 = 0
	var1 = 0
	d1 = 0
	log6Nr = log(N*6.0/r)/2
	log3r = log(3.0/r)/2
	d2 = d*d;
	for i in range(N):
		tau = Ni[i]*1.0/sumN
		OS = OmegaSmall(ni[i],Ni[i])
		PS = PsiSmall(ni[i],Ni[i])
		onN += PS*OS*tau**2
		max1 = max(max1,PS*PS*tau**2)
		var1 += PS*((ni[i]-1)*var[i]*1.0/ni[i])*tau**2
	return sqrt(3.0/r)*(sqrt(var1 + log6Nr*d2*onN + log3r*d2*max1) + sqrt(log3r*d2*max1))




