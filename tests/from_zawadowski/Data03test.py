from Opetope import Opetope, NegCounter
from Products import product

# union segment
x = Opetope(name="x") 
y = Opetope(name="y") 
xy = Opetope(ins=[x], out=y, name="xy")

a1 = Opetope(ins=[], out=None, name='a1')
a2 = Opetope(ins=[], out=None, name='a2')
a3 = Opetope(ins=[a2], out=a1, name='a3')

b, s = product(xy, a3)
p = b | s
c = NegCounter()
for x in p:
    c[x.level] += 1
print([(k, v) for k, v in sorted(list(c.counts.items()))])
print(len(p))
