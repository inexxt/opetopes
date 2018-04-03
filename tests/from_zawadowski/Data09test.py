from Opetope import Opetope, NegCounter
from Products import product

# union segment
x = Opetope(name="x") 
y = Opetope(name="y") 
xy = Opetope(ins=[x], out=y, name="xy")

a1 = Opetope(ins=[], out=None, name='a1')
a2 = Opetope(ins=[], out=None, name='a2')
a3 = Opetope(ins=[], out=None, name='a3')
a4 = Opetope(ins=[], out=None, name='a4')
a5 = Opetope(ins=[a4], out=a1, name='a5')
a6 = Opetope(ins=[a2], out=a1, name='a6')
a7 = Opetope(ins=[a3], out=a2, name='a7')
a8 = Opetope(ins=[a4], out=a3, name='a8')
a9 = Opetope(ins=[a6, a7, a8], out=a5, name='a9')

b, s = product(xy, a9)
p = b | s
c = NegCounter()
for x in p:
    c[x.level] += 1
print([(k, v) for k, v in sorted(list(c.counts.items()))])
print(len(p))
