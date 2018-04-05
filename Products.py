import itertools

from Opetope import Opetope, Face, flatten, NegCounter
from memoization import memoize

from typing import Set

all_results = set()

DEBUG = True

def build_possible_opetopes(op, building_blocks, P, Q):
    # build all possible opetopes which have the codomain == op
    # and are constructed only from elems
    
    # and proceed from here by DFS
    results = set()
#     print("Starting DFS, out {} blocks {} P {} Q {}".format(op, building_blocks, P, Q))
    
    DFS({op.out}, set(), building_blocks, results, op, P, Q)
    return results

# debug_faces = set()

@memoize
def DFS(current_ins: Set[Face], used: Set[Face], building_blocks: Set[Face], results, target_out: Face, P: Opetope, Q: Opetope):
    # extremely ugly, but necessary FIXME
    if target_out.level < 1:
        return

    if Face.verify_construction(p1=P, p2=Q, ins=used, out=target_out):
        new_face = Face(p1=P, p2=Q, ins=used, out=target_out)
        results.add(new_face)
        all_results.add(new_face)
        if DEBUG:
            print("Current face count: {} in {} {} current_ins {} used {} target_out {}".format(len(all_results), P, Q, current_ins, used, target_out))
        #     print(new_face.ins, new_face.out)
        #     debug_faces.add(new_face)
        return

    # ugly hack, but points do not have themselves as outs, so it is needed
    out = lambda x: x if not x.level else x.out
    
    # if not, we have to iterate through all possible to use opetopes and check each combination recursively
    for b in sorted(building_blocks, key=lambda x: str(x)):
        for i in sorted(current_ins, key=lambda x: str(x)):
            # if DEBUG:
            #     print("Now focusing on b: {} u: {}".format(b, i))
            if i == out(b):
#                 print("Used")
                new_ins = {*current_ins, *b.ins} - {i}
                new_used = {*used, b}
                new_blocks = building_blocks - {b}
                
                assert len(new_used) > len(used)
                assert len(new_blocks) < len(building_blocks)
                DFS(current_ins=new_ins, 
                    used=new_used, 
                    building_blocks=new_blocks, 
                    results=results, 
                    target_out=target_out, P=P, Q=Q)
    return

@memoize
# todo change Set[Face] to OpetopicNet, imposing appropriate restrictions
def product(P: Opetope, Q: Opetope) -> (Set[Face], Set[Face]):

    # if DEBUG:
    #     print("Now analyzing opetopes {} and {}".format(P, Q))
    subs1 = P.all_subopetopes()
    subs2 = Q.all_subopetopes()

    # the goal is to construct big_faces - the faces which map simultaneously to whole op1 and whole op2
    big_faces = set()

    # we also need small_faces - these are the ones that don't map to whole op1 and whole op2 simultaneously
    small_faces = set()

    points = lambda s: {p for p in s if not p.level}
    arrows = lambda s: {p for p in s if p.level == 1}
    small_faces |= {Face.from_point_and_point(s1, s2) for s1 in points(subs1) for s2 in points(subs2)}
    small_faces |= {Face.from_arrow_and_point(s1, s2) for s1 in arrows(subs1) for s2 in points(subs2)}
    small_faces |= {Face.from_point_and_arrow(s1, s2) for s1 in points(subs1) for s2 in arrows(subs2)}
    small_faces |= {Face.from_arrow_and_arrow(s1, s2) for s1 in arrows(subs1) for s2 in arrows(subs2)}
    
    # going from the lowest dimension first
    s1s2 = itertools.product(subs1, subs2)
    for (s1, s2) in sorted(s1s2, key=lambda x: str(x)): # FIXME remove sorted
        if (s1, s2) != (P, Q) and (s1.level, s2.level) not in [(0, 1), (0, 0), (1, 0)]:
            (big, small) = product(s1, s2)
            small_faces |= big | small # big faces from subopetope are small faces in here
    
    # minimal dimension of such a face is k = max(dim(P), dim(Q))
    k = max(P.level, Q.level)
    
    # induction on l - dimension of such face
    l = k

    # special case when we product two arrows and there is big face from the beginning - FIXME
    if P.level == 1 and Q.level == 1:
        big_faces |= {Face.from_arrow_and_arrow(P, Q)}

    # we proceed until there is no new face
    while True:
        # we have constructed all big faces of dimension < l
        # we now proceed to faces dimension l
        
        # the possible codomains of such a face are:
        possible_codomains = set()
        # 1) all (l-1)-dimensional big_faces
        possible_codomains |= {f for f in big_faces if f.level == l - 1}

        if l == k:
            possible_codomains |= {f for f in small_faces if f.p1 == P.out and f.p2 == Q.out}

        # 2) if dim(P) <= dim(Q), then it may be a face that maps to P and codomain(Q)
        if P.level < Q.level and l == k:
            possible_codomains |= {f for f in small_faces if f.p1 == P
                                                          and f.p2 == Q.out
                                                          and f.level == l - 1}
        # 3) if dim(Q) <= dim(P), then it may be a face that maps to Q and codomain(P)
        if Q.level < P.level and l == k:
            possible_codomains |= {f for f in small_faces if f.p1 == P.out
                                                          and f.p2 == Q
                                                          and f.level == l - 1}


        # now, for each possible codomain, we build the opetope that contains it
        new_opetopes = set()
        for f in sorted(possible_codomains, key=lambda x: x.to_string()): # FIXME remove sorted
            # I think it is enough to build just from the stuff that has the right dimension
            # eg, equal to dim(f)
            building_blocks = {s for s in small_faces | big_faces if s.level == f.level and f != s}
            new_opetopes |= build_possible_opetopes(op=f, building_blocks=building_blocks, P=P, Q=Q)
        

        if not new_opetopes and l > 1:  # checking for l > 1 for special case when we product two arrows
            # print("No more faces for {} {}".format(P, Q))
            return  (big_faces, small_faces)
        
        big_faces |= new_opetopes
        l += 1