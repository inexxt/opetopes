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
    a6 = Opetope(ins=[a5], out=a1, name='a6')
    a7 = Opetope(ins=[a2], out=a1, name='a7')
    a8 = Opetope(ins=[a2], out=a1, name='a8')
    a9 = Opetope(ins=[a3], out=a2, name='a9')
    a10 = Opetope(ins=[a5], out=a3, name='a10')
    a11 = Opetope(ins=[a4], out=a3, name='a11')
    a12 = Opetope(ins=[a4], out=a3, name='a12')
    a13 = Opetope(ins=[a5], out=a4, name='a13')
    a14 = Opetope(ins=[a8, a9, a12, a13], out=a6, name='a14')
    a15 = Opetope(ins=[a7, a9, a10], out=a6, name='a15')
    a16 = Opetope(ins=[a8], out=a7, name='a16')
    a17 = Opetope(ins=[a11, a13], out=a10, name='a17')
    a18 = Opetope(ins=[a12], out=a11, name='a18')
    a19 = Opetope(ins=[a15, a16, a17, a18], out=a14, name='a19')
    b, s = product(xy, a19)
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
