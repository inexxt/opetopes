from Opetope import Opetope, NegCounter
from Products import product

a = Opetope(name='a')
b = Opetope(name='b')
ab = Opetope(ins=[a], out=b, name="ab")

c = Opetope(name='c')
d = Opetope(name='d')
cd = Opetope(ins=[c], out=d, name="cd1")

b, s = product(ab, cd)
p = b | s
c = NegCounter()
for x in p:
    c[x.level] += 1
print(c)

# should be 11
print("Len: ", len(p))