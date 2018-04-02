from Opetope import Opetope, NegCounter
from Products import product

a = Opetope(name='a')
b = Opetope(name='b')
ab = Opetope(ins=[a], out=b, name="ab")

c = Opetope(name='c')
d = Opetope(name='d')
e = Opetope(name='e')
cd = Opetope(ins=[c], out=d, name="cd")
de = Opetope(ins=[d], out=e, name="de")
ce = Opetope(ins=[c], out=e, name="ce")
alpha = Opetope(ins=[cd, de], out=ce, name="alpha")

# for _ in range(100):
b, s = product(ab, alpha)
p = b | s
c = NegCounter()
for x in p:
    c[x.level] += 1
print(c)
print("Len: ", len(p))

# should be ?
