from Products import product
from Opetope import Opetope, NegCounter 

a0 = Opetope(name="a0") 
a1 = Opetope(name="a1") 
a2 = Opetope(name="a2") 
a3 = Opetope(name="a3") 
a4 = Opetope(name="a4") 
a5 = Opetope(name="a5")
a6 = Opetope(out=a1, ins=[a5], name="a6")
a7 = Opetope(out=a1, ins=[a2], name="a7")
a8 = Opetope(out=a2, ins=[a5], name="a8")
a9 = Opetope(out=a2, ins=[a4], name="a9")
a10 = Opetope(out=a2, ins=[a3], name="a10")
a11 = Opetope(out=a3, ins=[a4], name="a11")
a12 = Opetope(out=a4, ins=[a5], name="a12")
a13 = Opetope(out=a6, ins=[a7, a10, a11, a12], name="a13")
a14 = Opetope(out=a6, ins=[a7, a10, a11, a12], name="a14")
a15 = Opetope(out=a6, ins=[a7, a10, a11, a12], name="a15")
a16 = Opetope(out=a6, ins=[a7, a9, a12], name="a16")
a17 = Opetope(out=a6, ins=[a7, a9, a12], name="a17")
a18 = Opetope(out=a6, ins=[a7, a8], name="a18")
a19 = Opetope(out=a8, ins=[a9, a12], name="a19")
a20 = Opetope(out=a9, ins=[a10, a11], name="a20")
a21 = Opetope(out=a13, ins=[a18, a19, a20], name="a21")
a22 = Opetope(out=a13, ins=[a15], name="a22")
a23 = Opetope(out=a13, ins=[a14], name="a23")
a24 = Opetope(out=a14, ins=[a15], name="a24")
a25 = Opetope(out=a15, ins=[a16, a20], name="a25")
a26 = Opetope(out=a16, ins=[a18, a19], name="a26")
a27 = Opetope(out=a16, ins=[a17], name="a27")
a28 = Opetope(out=a16, ins=[a17], name="a28")
a29 = Opetope(out=a17, ins=[a18, a19], name="a29")
a30 = Opetope(out=a21, ins=[a23, a24, a25, a28, a29], name="a30")
a31 = Opetope(out=a21, ins=[a22, a25, a26], name="a31")
a32 = Opetope(out=a22, ins=[a23, a24], name="a32")
a33 = Opetope(out=a26, ins=[a27, a29], name="a33")
a34 = Opetope(out=a27, ins=[a28], name="a34")
a35 = Opetope(out=a30, ins=[a31, a32, a33, a34], name="a35")


# union segment
x = Opetope(name="x") 
y = Opetope(name="y") 
xy = Opetope(out=y, ins=[x], name="xy")

b, s = product(xy, a35)
p = b | s
c = NegCounter()
for x in p:
    c[x.level] += 1

# should be 2041
print(sum(c.values()))
print(c)

