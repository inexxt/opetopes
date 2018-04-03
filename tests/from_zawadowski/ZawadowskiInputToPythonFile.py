import sys
# coding: utf-8

# In[71]:

FILE = sys.argv[1]
FILE = FILE.split("FS")[0]

# In[72]:

imports = """from Opetope import Opetope, NegCounter
from Products import product

# union segment
x = Opetope(name="x") 
y = Opetope(name="y") 
xy = Opetope(ins=[x], out=y, name="xy")

"""


# In[73]:

calculations = """

b, s = product(xy, {})
p = b | s
c = NegCounter()
for x in p:
    c[x.level] += 1
print([(k, v) for k, v in sorted(list(c.counts.items()))])
print(len(p))
"""


# In[74]:

result = []
with open(FILE + "FS.txt", "r") as f:
    for l in sorted(f.readlines(), key=lambda x: int(x.split()[0])):
        l = l.replace("\n", "")
        l = l.split(" ")
        name = "a{}".format(l[0])
        out = "a{}".format(l[1]) if l[1] != "0" else None
        ins = "[" + ", ".join(["a{}".format(t) for t in l[2:]]) + "]"
        
        result.append("{} = Opetope(ins={}, out={}, name='{}')".format(name, ins, out, name))


# In[75]:

result = "\n".join(result[1:])


# In[76]:

result = imports + result + calculations.format(name)


# In[77]:

with open(FILE + "test.py", "w") as f:
    f.write(result)


# In[ ]:



