from Opetope import Opetope
from Products import Product

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
p = Product(ab, alpha)
print(p.is_contractible())
# should be 101
print("Len: ", len(p.faces))
