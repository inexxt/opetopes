from Opetope import Opetope, NegCounter
from Products import product

# union segment
x = Opetope(name="x") 
y = Opetope(name="y") 
xy = Opetope(ins=[x], out=y, name="xy")

a1 = Opetope(ins=[], out=None, name='a1')
a2 = Opetope(ins=[], out=None, name='a2')
a3 = Opetope(ins=[a2], out=a1, name='a3')
a4 = Opetope(ins=[a2], out=a1, name='a4')
a5 = Opetope(ins=[a4], out=a3, name='a5')
a6 = Opetope(ins=[a4], out=a3, name='a6')
a7 = Opetope(ins=[a6], out=a5, name='a7')

b, s = product(xy, a7)
p = b | s
c = NegCounter()
for x in p:
    c[x.level] += 1
print([(k, v) for k, v in sorted(list(c.counts.items()))])
print(len(p))