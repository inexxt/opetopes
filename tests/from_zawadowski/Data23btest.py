from Opetope import Opetope, NegCounter
from Products import product
def run(): 
    # union segment
    x = Opetope(name="x") 
    y = Opetope(name="y") 
    xy = Opetope(ins=[x], out=y, name="xy")

    a1 = Opetope(ins=[], out=None, name='a1')
    a2 = Opetope(ins=[], out=None, name='a2')
    a3 = Opetope(ins=[], out=None, name='a3')
    a4 = Opetope(ins=[], out=None, name='a4')
    a5 = Opetope(ins=[], out=None, name='a5')
    a6 = Opetope(ins=[], out=None, name='a6')
    a7 = Opetope(ins=[], out=None, name='a7')
    a8 = Opetope(ins=[], out=None, name='a8')
    a9 = Opetope(ins=[], out=None, name='a9')
    a10 = Opetope(ins=[], out=None, name='a10')
    a11 = Opetope(ins=[], out=None, name='a11')
    a12 = Opetope(ins=[a11], out=a1, name='a12')
    a13 = Opetope(ins=[a11], out=a10, name='a13')
    a14 = Opetope(ins=[a3], out=a2, name='a14')
    a15 = Opetope(ins=[a4], out=a3, name='a15')
    a16 = Opetope(ins=[a5], out=a4, name='a16')
    a17 = Opetope(ins=[a6], out=a5, name='a17')
    a18 = Opetope(ins=[a7], out=a6, name='a18')
    a19 = Opetope(ins=[a8], out=a7, name='a19')
    a20 = Opetope(ins=[a9], out=a8, name='a20')
    a21 = Opetope(ins=[a10], out=a9, name='a21')
    a22 = Opetope(ins=[a2], out=a1, name='a22')
    a23 = Opetope(ins=[a13, a14, a15, a16, a17, a18, a19, a20, a21, a22], out=a12, name='a23')
    b, s = product(xy, a23)
    p = b | s
    c = NegCounter()
    for x in p:
        c[x.level] += 1
    print([(k, v) for k, v in sorted(list(c.counts.items()))])
    print(len(p))

if __name__=="__main__":
    try:
        run()
    except:
        print("Exception")
        print()
