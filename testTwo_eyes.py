from Opetope import Opetope, NegCounter
from Products import product, DEBUG, Product

a = Opetope(name='a')
b = Opetope(name='b')
ab1 = Opetope(ins=[a], out=b, name="ab1")
ab2 = Opetope(ins=[a], out=b, name="ab2")
alpha = Opetope(ins=[ab1], out=ab2, name="alpha")

c = Opetope(name='c')
d = Opetope(name='d')
cd1 = Opetope(ins=[c], out=d, name="cd1")
cd2 = Opetope(ins=[c], out=d, name="cd2")
gamma = Opetope(ins=[cd1], out=cd2, name="gamma")

p = Product(alpha, gamma)
print(p)
# should be 101
print("Len: ", len(p.faces))