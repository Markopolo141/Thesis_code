from copy import deepcopy as copy
from math import sqrt

def get(A,index):
	if index<0:
		return 0
	if index>=len(A):
		return 0
	return A[index]

def conv(A,B):
	lenA = len(A)
	lenB = len(B)
	R = []
	for offset in range(1,max(lenA,lenB)+min(lenA,lenB)):
		z = 0
		for j in range(offset):
			z += get(A,j)*get(B,lenB+j-offset)
		R.append(z)
	return R

datas = []

A = [0]+[1 for i in range(41)]+[0]
datas.append(A)
B = copy(A)
for i in range(4):
	B = conv(A,B)
	datas.append(B)

#print datas

datas = [[((i*1.0/(len(d)-1)-0.5)*sqrt(ii+1),dd*1.0/max(d)) for i,dd in enumerate(d)] for ii,d in enumerate(datas)]

for d in datas:
	s = ""
	for dd in d:
		s += str(dd)
	print s
	print ""

