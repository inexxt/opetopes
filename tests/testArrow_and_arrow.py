from Opetope import Opetope, NegCounter
from Products import product, Product

a = Opetope(name='a')
b = Opetope(name='b')
ab = Opetope(ins=[a], out=b, name="ab")

c = Opetope(name='c')
d = Opetope(name='d')
cd = Opetope(ins=[c], out=d, name="cd1")

p = Product(ab, cd)

print(p.is_contractible())
# should be 11
print("Len: ", len(p.faces))