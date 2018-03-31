from Opetope import Opetope, NegCounter
from Products import product

a = Opetope(name='a')
b = Opetope(name='b')
ab = Opetope(ins=[a], out=b, name="ab")

c = Opetope(name='c')
d = Opetope(name='d')
cd1 = Opetope(ins=[c], out=d, name="cd1")
cd2 = Opetope(ins=[c], out=d, name="cd2")
alpha = Opetope(ins=[cd1], out=cd2, name="alpha")

b, s = product(ab, alpha)
p = b | s
c = NegCounter()
for x in p:
    c[x.level] += 1
print(c)

# should be 25
print("Len: ", len(p))