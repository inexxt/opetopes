import sys
# coding: utf-8


imports = """from Opetope import Opetope, NegCounter
from Products import product
def run(): 
    # union segment
    x = Opetope(name="x") 
    y = Opetope(name="y") 
    xy = Opetope(ins=[x], out=y, name="xy")

"""


calculations = """
    b, s = product(xy, {})
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
"""

if __name__=="__main__":

    FILE = sys.argv[1]
    try:
        FILE = FILE.split("FS")[0]

        result = []
        with open(FILE + "FS.txt", "r") as f:
            for l in sorted(f.readlines(), key=lambda x: int(x.split()[0])):
                l = l.replace("\n", "")
                l = l.split(" ")
                name = "a{}".format(l[0])
                out = "a{}".format(l[1]) if l[1] != "0" else None
                ins = "[" + ", ".join(["a{}".format(t) for t in l[2:]]) + "]"

                result.append("    {} = Opetope(ins={}, out={}, name='{}')".format(name, ins, out, name))


        result = "\n".join(result[1:])
        result = imports + result + calculations.format(name)
    except:
        result = "print('Exception')\nprint()"

    with open(FILE + "test.py", "w") as f:
        f.write(result)