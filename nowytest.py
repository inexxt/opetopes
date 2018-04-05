from Opetope import Opetope, NegCounter
from Products import product

a = Opetope(name='a')
b = Opetope(name='b')
c = Opetope(name='c')
ab = Opetope(ins=[a], out=b, name="ab")
bc = Opetope(ins=[b], out=c, name="bc")
ac = Opetope(ins=[a], out=c, name="ac")
alpha = Opetope(ins=[ab, bc], out=ac, name="alpha")

d = Opetope(name='d')
e = Opetope(name='e')
f = Opetope(name='f')
de = Opetope(ins=[d], out=e, name="de")
ef = Opetope(ins=[e], out=f, name="ef")
df = Opetope(ins=[d], out=f, name="df")
gamma = Opetope(ins=[de, ef], out=df, name="gamma")

b, s = product(alpha, gamma)
p = b | s
c = NegCounter()
for x in p:
    c[x.level] += 1
print(c)

print("Len: ", len(p))