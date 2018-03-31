from collections import namedtuple, defaultdict
import string
import random
import functools
import pdb
from typing import List, Iterable


def flatten(ss):
    return [x for s in ss for x in s]

NAME_LEN = 6

def generate_id():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(NAME_LEN))

def masks(n):
    if n == 1:
        return [[True], [False]]
    else:
        ms = masks(n-1)
        return flatten([[[True] + m, [False] + m] for m in ms])

def unescape(x):
    return x.replace("'", "").replace('"', "")

MEMO = set()

def clear_cache():
    MEMO.clear()


from collections import Counter


class NegCounter(Counter):
    def __add__(self, other):
        return NegCounter({x: self.get(x, 0) + other.get(x, 0) for x in set(self.keys()) | set(other.keys())})
    def __sub__(self, other):
        return NegCounter({x: self.get(x, 0) - other.get(x, 0) for x in set(self.keys()) | set(other.keys())})
    def __or__(self, other):
        return NegCounter({x: self.get(x, 0) + other.get(x, 0) for x in set(self.keys()) | set(other.keys())})
    def __and__(self, other):
        return NegCounter({x: self.get(x, 0) + other.get(x, 0) for x in set(self.keys()) & set(other.keys())})
    def is_empty(self):
        return all(not v for v in self.values())
    def __iadd__(self, other):
        return NegCounter({x: self.get(x, 0) + other.get(x, 0) for x in set(self.keys()) & set(other.keys())})
    def __isub__(self, other):
        return NegCounter({x: self.get(x, 0) - other.get(x, 0) for x in set(self.keys()) & set(other.keys())})


def memoize(f):
    memo = MEMO

    @functools.wraps(f)
    def helper(*args, **kwargs):
        if kwargs["shape"] not in memo:
            memo.add(kwargs["shape"])
            f(*args, **kwargs)
        return
    return helper


# def print_debug(op):
#     pass
#     print("\t\t\t Debug:: \n")
#     print("\t\t", op.to_string())
#     print("\t\t\n Subopetopes:\n")
#     for x in Opetope.all_subopetopes(op):
#         print("\t\t", x.to_string())
#     print("\n")


class Opetope:

    def __init__(self, ins=(), out=None, name=""):
        """ins is list of opetopes one level lower,
        out is a single opetope one level lower
        """
        self.name = name
        self.id = name if name else generate_id()
        
        if out:
            assert isinstance(out, Opetope)

            # check that levels are ok
            assert all([i.level == out.level for i in ins])
            self.level = out.level + 1
            if self.level > 1:
                assert Opetope.match(ins, out)
            
            # check that lower level opetopes really "match"
            self.ins = tuple(ins)
            self.out = out

        else:
            self.level = 0
            self.ins = ()
            self.out = -1 # TODO change that - (-1) to not confuse replace_a_by_b, which uses the fact that None is not a valid opetope 
    
    @staticmethod
    def match(ins, out):
        # allow waiting makes it possible to eg
        # build opetope (ab: [a] -> b) from [(ab: [a] -> b), b]
        # technical detail neede in products


        ins_of_out = NegCounter(out.ins)
        for opetope in ins:
            ins_of_out = ins_of_out - NegCounter(opetope.ins)
            ins_of_out = ins_of_out + NegCounter({opetope.out})
        ins_of_out = ins_of_out - NegCounter({out.out})
        return ins_of_out.is_empty()
    
    def __str__(self):
        return self.to_string()
    
    def __repr__(self):
        return self.to_string()
    
    def is_unary(self):
        return len(self.ins) == 1

    def to_string(self, remove_names=False):
        
        if not self.level:
            return "*" if remove_names else self.name

        if remove_names:
            return unescape("{} -> {}".format([i.to_string(remove_names) for i in self.ins], self.out.to_string(remove_names)))
        else:
            return unescape("({}: {} -> {})".format(self.name, [i.to_string(remove_names) for i in self.ins], self.out.to_string(remove_names)))

    def all_subopetopes(self):
        if not self.level:
            return {self}
        
        return set(flatten([o.all_subopetopes() for o in self.ins])) | self.out.all_subopetopes() | {self}
    
    def all_subouts(self):
        if not self.level:
            return {}
        return {self.out} | set(flatten([o.all_subouts() for o in [*self.ins, self.out]]))

    def shape(self, remove_names=True):
        # "shape" of the opetope: not caring about the names, just the canonical names
        # I may use tree representation in the future
        # but for now, just as a "function"-type
        # returns a Representation(string representation, modifiers)
        return self.to_string(remove_names)

    @staticmethod
    def from_shape(shape):
        # return Opetope with shape specified
        pass
    
    def __eq__(self, other):
        # todo change that, it doesnt take into account that there 
        # might be different arrows between the same set of objects
        return str(self) == str(other)
    
    def __hash__(self):
        return hash(self.name)

    @staticmethod
    def is_valid_morphism(op1: 'Opetope', op2: 'Opetope'):

        # contract all things in op1
        def contract(op):
            if not op.level:
                return op
            out = contract(op.out)
            ins = [contract(i) for i in op.ins]
            ins = [i for i in ins if i.level == out.level]
            if all([i.name == op.name for i in ins]) and out.name == op.name:
                return contract(op.out)
            return Opetope(ins=ins, out=out, name=op.name)

        return contract(op1).to_string() == op2.to_string()

    def is_non_degenerated(self):
        # basically not having loops
        if not self.level:
            return True
        if self.level == 1:
            return self.ins[0] != self.out
        else:
            return all(i.is_non_degenerated() for i in [*self.ins, self.out])

class Face(Opetope):
    def __init__(self, p1: Opetope, p2: Opetope, ins: 'List[Face]' = (), out = None, name=""):
        super().__init__(ins=ins, out=out, name=name)

        # We have to check here if this is a valid projection
        # eg if all (recursivly) faces of self, projected on p1, together get us p1
        # and similarly p2

        self.p1 = p1
        self.p2 = p2

    def to_string(self, remove_names=False):
        return "({}, {})!{}\n".format(self.p1.to_string(remove_names), self.p2.to_string(remove_names), self.level)


    @staticmethod
    def verify_construction(p1: Opetope, p2: Opetope, ins: 'List[Face]' = (), out = None, name=""):
        try:
            face = Face(p1, p2, ins, out, name)
            def get_pxs(f: 'Face', px):
                if not f.level:
                    return Opetope(name=px(f).name)
                if not isinstance(f, Face):
                    return f

                out = get_pxs(f.out, px)
                ins = [get_pxs(i, px) for i in f.ins if i.level == out.level]
                ins = [i for i in ins if i.is_non_degenerated()]
                return Opetope(ins=ins, out=out, name=px(f).name)

            op1 = get_pxs(face, lambda x: x.p1)
            op2 = get_pxs(face, lambda x: x.p2)
            # print("face")

            assert Opetope.is_valid_morphism(op1, p1) and Opetope.is_valid_morphism(op2, p2)


        except:
            return False

        return True

    @staticmethod
    def from_point_and_point(p1: 'Opetope', p2: 'Opetope'):
        assert (p1.level, p2.level) == (0, 0)
        return Face(p1, p2)

    @staticmethod
    def from_arrow_and_point(p1: 'Face', p2: 'Face'):
        assert (p1.level, p2.level) == (1, 0)
        return Face(p1, p2, ins=[Face.from_point_and_point(p1.ins[0], p2)], 
                            out=Face.from_point_and_point(p1.out, p2))

    @staticmethod
    def from_point_and_arrow(p1: 'Face', p2: 'Face'):
        assert (p1.level, p2.level) == (0, 1)
        # we can't just use from_arrow_and_point, because the order p1, p2 is important
        return Face(p1, p2, ins=[Face.from_point_and_point(p1, p2.ins[0])], 
                            out=Face.from_point_and_point(p1, p2.out))

    @staticmethod
    def from_arrow_and_arrow(p1: 'Face', p2: 'Face'):
        assert (p1.level, p2.level) == (1, 1)
        return Face(p1, p2, ins=[Face.from_point_and_point(p1.ins[0], p2.ins[0])], 
                            out=Face.from_point_and_point(p1.out, p2.out))

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        return hash("{}{}{}{}{}".format(self.p1, 
                                        self.p2, 
                                        "".join(str(hash(i)) for i in self.ins),
                                        self.out,
                                        self.name))