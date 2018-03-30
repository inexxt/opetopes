
# coding: utf-8

# In[1]:
#
# get_ipython().magic('load_ext autoreload')
# get_ipython().magic('autoreload 2')


# In[2]:

# Double induction
# - over dimension of the opetope
# - over dimension of the faces 


# In[3]:


import itertools

from Opetope import Opetope, Face, flatten, clear_cache, MEMO


# In[4]:

a = Opetope(name='a')
b = Opetope(name='b')
ab = Opetope(ins=[a], out=b, name="ab")

c = Opetope(name='c')
d = Opetope(name='d')
cd1 = Opetope(ins=[c], out=d, name="cd1")
cd2 = Opetope(ins=[c], out=d, name="cd2")
gamma = Opetope(ins=[cd1], out=cd2, name="gamma")


# In[35]:

from collections import Counter


# In[36]:

from typing import Set
from pdb import set_trace
from typing import List

def build_possible_opetopes(op, building_blocks, P, Q):
    # build all possible opetopes which have the codomain == op
    # and are constructed only from elems
    
    # and proceed from here by DFS
    results = set()
#     print("Starting DFS, out {} blocks {} P {} Q {}".format(op, building_blocks, P, Q))
    
    DFS({op.out}, set(), building_blocks, results, op, P, Q)
    return results
    
def DFS(current_ins: Set[Face], used: Set[Face], building_blocks: Set[Face], results, target_out: Face, P: Opetope, Q: Opetope):
#     set_trace()
    
    if Face.verify_construction(p1=P, p2=Q, ins=used, out=target_out):
        new_face = Face(p1=P, p2=Q, ins=used, out=target_out)
        results.add(new_face)
        print("Found face!!!")
        print(new_face)
        return

    # ugly hack, but points do not have themselves as outs, so it is needed
    out = lambda x: x if not x.level else x.out
    
    # if not, we have to iterate through all possible to use opetopes and check each combination recursively
    for b in building_blocks:
        for i in current_ins:
#             print("Now focusing on b: {} u: {}".format(b, i))
            if i.p1 == out(b.p1) and i.p2 == out(b.p2):
#                 print("Used")
                new_ins = {*current_ins, *b.ins} - {i}
                new_used = {*used, b}
                new_blocks = {x for x in building_blocks if x != b}
                
                assert len(new_used) > len(used)
                assert len(new_blocks) < len(building_blocks)
                DFS(current_ins=new_ins, 
                    used=new_used, 
                    building_blocks=new_blocks, 
                    results=results, 
                    target_out=target_out, P=P, Q=Q)
    return
    
# todo change Set[Face] to OpetopicNet, imposing appropriate restrictions
def product(P: Opetope, Q: Opetope, small_faces: Set[Face]) -> Set[Face]:
    
    print("Now analyzing opetopes {} and {}".format(P, Q))
    subs1 = P.all_subopetopes()
    subs2 = Q.all_subopetopes()

    # product is a set of Faces
    # small_faces, because these are the ones that don't map to whole op1 and whole op2 simultaneously
    
    points = lambda s: {p for p in s if not p.level}
    arrows = lambda s: {p for p in s if p.level == 1}
    small_faces |= {Face.from_point_and_point(s1, s2) for s1 in points(subs1) for s2 in points(subs2)}
    small_faces |= {Face.from_arrow_and_point(s1, s2) for s1 in arrows(subs1) for s2 in points(subs2)}
    small_faces |= {Face.from_point_and_arrow(s1, s2) for s1 in points(subs1) for s2 in arrows(subs2)}
    small_faces |= {Face.from_arrow_and_arrow(s1, s2) for s1 in arrows(subs1) for s2 in arrows(subs2)}
    
    # going from the lowest dimension first, since
    s1s2 = sorted(itertools.product(subs1, subs2), key=lambda x: (x[0].level, x[1].level))
    for (s1, s2) in s1s2:
        if (s1, s2) != (P, Q) and (s1.level, s2.level) >= (1, 1):
            small_faces |= product(s1, s2, small_faces)
    
    # now we only have to construct big_faces the faces which map simultaneously to whole op1 and whole op2
    # minimal dimension of such a face is k = max(dim(P), dim(Q))
    big_faces = set()
    k = max(P.level, Q.level)
    
    # induction on l - dimension of such face
    l = k

    # we proceed until there is no new face
    while True:
        # we have constructed all big faces of dimension < l
        # we now proceed to faces dimension l
        
        # the possible codomains of such a face are:
        possible_codomains = set()
        # 1) all (l-1)-dimensional big_faces
        possible_codomains |= {f for f in big_faces if f.level == l-1}
        
        if l == k:
            possible_codomains |= {f for f in small_faces if f.p1 == P and f.p2 == Q}
        
        # 2) if dim(P) <= dim(Q), then it may be a face that maps to P and codomain(Q)
        if P.level < Q.level and l == k:
            possible_codomains |= {f for f in small_faces if f.p1 == P
                                                          and f.p2 == Q.out}
        # 3) if dim(Q) <= dim(P), then it may be a face that maps to Q and codomain(P)
        if Q.level < P.level and l == k:
            possible_codomains |= {f for f in small_faces if f.p1 == P.out
                                                          and f.p2 == Q}
        
        # now, for each possible codomain, we build the opetope that contains it
        new_opetopes = set()
        for f in possible_codomains:
            # I think it is enough to build just from the stuff that has the right dimension
            # eg, equal to dim(f)
            building_blocks = {s for s in small_faces if s.level == f.level and f != s}
            new_opetopes |= build_possible_opetopes(op=f, building_blocks=building_blocks, P=P, Q=Q)
        

        if not new_opetopes:
            print("No more faces for {} {}".format(P, Q))
            return small_faces | big_faces
        
        big_faces |= new_opetopes
        l += 1


p = product(ab, gamma, set())

c = Counter()
for x in p:
    c[x.level] += 1
print(c)

print("Len: ", len(p))
# print(p)



