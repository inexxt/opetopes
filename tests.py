from Opetope import Opetope

# test1 - OK
a = Opetope(name='a')
b = Opetope(name='b')
c = Opetope(name='c')
d = Opetope(name='d')

ab = Opetope(ins=[a], out=b, name='ab')
bc = Opetope(ins=[b], out=c, name='bc')
cd = Opetope(ins=[c], out=d, name='cd')
ad = Opetope(ins=[a], out=d, name='ad')
ac = Opetope(ins=[a], out=c, name='ac')

alpha = Opetope(ins=[ab, bc], out=ac, name='alpha')
beta = Opetope(ins=[ac, cd], out=ad, name='beta')
gamma = Opetope(ins=[ab, bc, cd], out=ad, name='gamma')

whole1 = Opetope(ins=[alpha, beta], out=gamma, name='whole1')
print(whole1)

assert alpha.shape() == beta.shape()
assert alpha.shape() != gamma.shape()