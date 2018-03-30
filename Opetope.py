from collections import namedtuple, defaultdict, Counter
import string
import random
import functools
import pdb
from typing import List


def flatten(ss):
    return [x for s in ss for x in s]

NAME_LEN = 3

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

def memoize(f):
    memo = MEMO

    @functools.wraps(f)
    def helper(*args, **kwargs):
        if kwargs["shape"] not in memo:
            memo.add(kwargs["shape"])
            f(*args, **kwargs)
        return
    return helper


def print_debug(op):
    pass
    print("\t\t\t Debug:: \n")
    print("\t\t", op.to_string())
    print("\t\t\n Subopetopes:\n")
    for x in Opetope.all_subopetopes(op):
        print("\t\t", x.to_string())
    print("\n")


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
        ins_of_out = Counter(out.ins)
        for opetope in ins:
            ins_of_out -= Counter(opetope.ins)
            ins_of_out += Counter({opetope.out})
        ins_of_out -= Counter({out.out})
        return not ins_of_out
    
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


class Face(Opetope):
    def __init__(self, p1: Opetope, p2: Opetope, ins: 'List[Face]' = (), out = None, name=""):
        super().__init__(ins=ins, out=out, name=name)
        # TODO add verification that dimensions of projections and self are OK
        self.p1 = p1
        self.p2 = p2

    def to_string(self, remove_names=False):
        return "({}, {})\n".format(self.p1.to_string(remove_names), self.p2.to_string(remove_names))

    
    @staticmethod
    def from_point_and_point(p1: 'Face', p2: 'Face'):
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
                                        self.ins, 
                                        self.out, 
                                        self.name))
