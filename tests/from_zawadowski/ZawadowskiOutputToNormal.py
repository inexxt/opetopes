
# coding: utf-8
import sys

# In[37]:

# FILE = "./Data09WalkProdFaces.txt"
FILE = sys.argv[1]
# print(FILE)

# In[38]:

from itertools import takewhile
from collections import defaultdict
from toposort import toposort_flatten


# In[39]:

def removewhile(pred, iterator):
    condition = True
    result = []
    for i in iterator:
        if not pred(i):
            condition = False
        if not condition:
            result.append(i)
    return result

x = [0,0,1,0,1]
assert removewhile(lambda x: x == 0, x) == [1, 0, 1]


# In[40]:

lines = []
with open(FILE, "r") as f:
    for l in f.readlines():
        lines.append(l)
lines = lines[4:-6]


# In[41]:

faces_desc = [[]]

for l in lines:
    if l == "\n":
        faces_desc.append([])
    else:
        faces_desc[-1].append(l.replace("\n", "").strip())

faces_desc.pop()


# In[42]:

final_list = []

def clean(f_descp):
    f_desc = [(x.strip(), y.strip()) for l in f_descp for x, y in [l.split("|")]]
    original_number = f_desc[0][0].split(" ")[0] 
    f_desc[0] = (f_desc[0][0].split(" ")[-1], f_desc[0][1])
    return (original_number, f_desc)

finals = {}
newnames = {}

for f_descp in faces_desc:
    orig, f_desc = clean(f_descp)
    
    faces = [[] for _ in range(len(list(x for x in f_desc[0][1].split(" ") if x)) + 1)]
    for f, s in f_desc:
        faces[0].append(f)
        for e, k in enumerate([x for x in s.split(" ") if x]):
            if k:
                faces[e+1].append(k)
            
    def transform(faces):
        return [list(removewhile(lambda x: x == 0, map(lambda x: int(x), [x for x in ff[:-1] if x != "--"])))
                for ff in faces if "".join(ff) not in ["", "--"]]
    faces = transform(faces)
    
    def goc(name):
        if not name:
            return None
        name = tuple(name)
        if name in newnames:
            return newnames[name]
        else:
            newnames[name] = len(newnames)
            return newnames[name]
    
    name = goc(faces[0])
    insf = goc(faces[1] if len(faces) > 1 else None)
    outf = [goc(f) for f in faces[2:]]
#     print(orig, faces[0], name, insf, outf, faces)
    finals[name] = (insf, outf)

dims = defaultdict(int)

for elem in toposort_flatten({k: set(v) for k, vv in finals.items() for _, v in [vv]}):
    dims[elem] = dims[finals[elem][0]] + 1

dims = {k: v - 1 for k, v in dims.items()}
del dims[None]


# In[43]:

# {k: (v, dims[k]) for k, v in finals.items()}


# In[44]:

from collections import Counter
print([(k, v) for k, v in list(sorted(Counter(dims.values()).items()))])
print(len(dims))


# In[ ]:



