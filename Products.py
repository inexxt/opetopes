import itertools

from collections import defaultdict, Counter

try:
    from fastcache import lru_cache
except:
    from functools import lru_cache

from Opetope import Opetope, Face, flatten, NegCounter, first

from typing import Set, List, Tuple, FrozenSet, Dict, Tuple

import pickle
import os
import time


DEBUG = True


if DEBUG:
    print("Debug legend:")
    print("m-face is a face that projects both on m_P and m_Q")

    print("#1 - num of m-faces")
    print("#2 - num of m-faces that have m-face in domain")
    print("#3 - num of m-faces that have m-face in codomain\n"
          "     don't have m-face in domain, and have something that projects on m_P and *\n"
          "     and second something that projects on * and m_Q\n"
          "     where * != m_P (/m_Q)")

    print("Counter(a:b) says that there are b faces of dimension a")
    print("\n")
    
all_results = set()
all_missed = []
all_not_missed = []



order = set()

def is_in_order(b, target_out):
    return all(any((bi, ti) in order for ti in target_out.ins) for bi in b.ins)

def build_possible_opetopes(op, building_blocks, P, Q):
    # build all possible opetopes which have the codomain == op
    # and are constructed only from elems
    
    # and proceed from here by DFS
    results = DFS(frozenset([op.out]), frozenset(), frozenset(building_blocks), op, P, Q)
    return results


def print_debug_info(all_results: Set[Face], P: Face, Q: Face):
    if DEBUG:
        print("Current face count: {}".format(len(all_results)))
        # print(new_face.ins, new_face.out)
        # debug_faces.add(new_face)
        big_face = lambda ll: list(filter(lambda t: t.p1 == P and t.p2 == Q, ll))
        big_face_p = lambda ll: list(filter(lambda t: t.p1 == P and (not t.p2 == Q), ll))
        big_face_q = lambda ll: list(filter(lambda t: (not t.p1 == P) and t.p2 == Q, ll))
        
        main_faces = big_face(all_results)

        faces1 = main_faces
        faces2 = [t for t in main_faces if big_face(t.ins)]
        faces3 = [t for t in main_faces if not big_face(t.ins)
                                           and big_face_p(t.ins) 
                                           and big_face_q(t.ins)]
        dims = lambda x: Counter(map(lambda t: t.level, x))
        print("#1 faces - {}".format(dims(faces1)))
        print("#2 faces - {}".format(dims(faces2)))
        print("#3 faces - {}".format(dims(faces3)))

    return


@lru_cache(maxsize=None)
def DFS(current_ins: FrozenSet[Face], used: FrozenSet[Face], building_blocks: FrozenSet[Face], target_out: Face, P: Opetope, Q: Opetope):

    if target_out.level < 1:
        return set()

    if Face.verify_construction(p1=P, p2=Q, ins=used, out=target_out):
        new_face = Face(p1=P, p2=Q, ins=used, out=target_out)
        all_results.add(new_face)

        print_debug_info(all_results, P, Q)

        return {new_face}

    # ugly hack, but points do not have themselves as outs, so it is needed
    out = lambda x: x if not x.level else x.out
    
    # if not, we have to iterate through all possible to use opetopes and check each combination recursively
    results = set()
    for b in building_blocks - used:
        for i in current_ins:
            # if DEBUG:
            #     print("Now focusing on b: {} u: {}".format(b, i))
            if i == out(b) and i.p1 in P.all_subopetopes() and i.p2 in Q.all_subopetopes():
                if not is_in_order(b, target_out):
                    continue
                new_ins = frozenset({*current_ins, *b.ins} - {i})
                new_used = frozenset([*used, b])
                
                # assert len(new_used) > len(used)
                # assert len(new_blocks) < len(building_blocks)
                results |= DFS(current_ins=new_ins,
                            used=new_used,
                            building_blocks=building_blocks,
                            target_out=target_out, P=P, Q=Q)

    return results

@lru_cache(maxsize=None)
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
    for (s1, s2) in s1s2: # FIXME remove sorted
        if (s1, s2) != (P, Q) and (s1.level, s2.level) not in [(0, 1), (0, 0), (1, 0)]:
            big, small = product(s1, s2)
            small_faces |= big | small # big faces from subopetope are small faces in here
    
    add_to_splus_order(order, small_faces) # ugly but necessary non-pure function

    # minimal dimension of such a face is k = max(dim(P), dim(Q))
    k = max(P.level, Q.level)
    
    # induction on l - dimension of such face
    l = k

    # special case when we product two arrows and there is big face from the beginning - FIXME
    if P.level == 1 and Q.level == 1:
        big_faces |= {Face.from_arrow_and_arrow(P, Q)}
    
    # we proceed until there is no new face
    while True:
        add_to_splus_order(order, big_faces) # ugly but necessary non-pure function
    
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
        for f in possible_codomains:
            # I think it is enough to build just from the stuff that has the right dimension
            # eg, equal to dim(f)
            building_blocks = {s for s in small_faces | big_faces if s.level == f.level and f != s}
            new_opetopes |= build_possible_opetopes(op=f, building_blocks=building_blocks, P=P, Q=Q)
        

        if not new_opetopes and l > 1:  # checking for l > 1 for special case when we product two arrows
            # print("No more faces for {} {}".format(P, Q))
            return  (big_faces, small_faces)
        
        big_faces |= new_opetopes

        l += 1


def transitive_reflexive_closure(relation: Set, new_elems: Set):
    closed_rel = set()
    closed_rel |= relation

    while True:
        added_elems = {(x, z) for (x, y) in new_elems for (w, z) in closed_rel if y == w}
        added_elems |= {(x, z) for (x, y) in closed_rel for (w, z) in new_elems if y == w}
            
        if not added_elems - closed_rel:
            break
        closed_rel |= added_elems
        new_elems |= added_elems

    closed_rel |= {(x, x) for (x, _) in closed_rel}
    closed_rel |= {(x, x) for (_, x) in closed_rel}

    return closed_rel


def calculate_splus_order(opetope: Face) -> Set[Tuple[Face, Face]]:
    """"partial order on subopetopes of equal dimension
    x <= y, x.level == y.level =: p if there is a sequence of opetopes o_1, ... o_n of levels p + 1, such that
     - o_(k+1).out in o_k.ins
     - y in o_n.ins
     - x == o_1.out
    + transitive-reflexive closure of said relation"""
    order = set()
    
    for sub_ope in opetope.all_subopetopes():
        if sub_ope.level:
            order |= {(sub_ope.out, i) for i in sub_ope.ins}
        order |= {(sub_ope, sub_ope)}
    
    return order

def add_to_splus_order(order, faces):
    new_elems = set()
    for f in faces:
        if not (f, f) in order:
            new_elems |= calculate_splus_order(f)

    if new_elems:
        # big computational overhead
        order |= new_elems
        order |= transitive_reflexive_closure(order, new_elems)

class Product:
    def __init__(self, p1: Opetope, p2: Opetope):
        self.p1 = p1
        self.p2 = p2

        b, s = product(p1, p2)
        self.faces = b | s
        print("Evals ", len(all_missed))

    def __repr__(self):
        c = NegCounter()
        for x in self.faces:
            c[x.level] += 1
        return [(k, c[k]) for k in sorted(c.counts)].__repr__()

    def __str__(self):
        return self.__repr__()

    def is_contractible(self):
        # horn filling

        all_faces = set(flatten(f.all_subopetopes() for f in self.faces))
        points = {k for k in all_faces if not k.level}
        # start with any point
        p = first(iter(points))
        used = {p}
        all_faces.remove(p)
        flag = True # flag indicating whenever something changed in the last loop
        # add face when all faces in its codomain are already added
        while flag:
            flag = False
            for f in all_faces - points:
                # if all but one faces are already added
                if sum(bool(k in used) for k in f.ins) + bool(f.out in used) == len(f.ins):
                    # add the remaining face and its last face
                    used.add(f)
                    used.add(f.out)
                    used.update(set(f.ins))
                    flag = True
            all_faces -= used
        return not all_faces

    def save(self, path=""):
        if not path:
            path = os.path.join(".", "pickles", f"product-{len(self.p1._all_subopetopes)}-{len(self.p2._all_subopetopes)}-{time.time()}.pickle")
        with open(path, "wb") as f:
            pickle.dump(self, f)