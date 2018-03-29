from collections import namedtuple, defaultdict
import string
import random
import functools
import pdb


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


def print_debug(parent):
    pass
    # print("\t\t\t Parent debug: \n")
    # print("\t\t", parent.to_string().rep)
    # print("\n")
    # for x in Opetope.all_subopetopes(parent):
    #     print("\t\t", x.to_string().rep)
    # print("\n")


Representation = namedtuple("Representation", ["rep", "mods"])
Old = namedtuple("Old", ["ins", "out", "in_parents", "out_parents", "inside_names", "level"])


class Opetope:


    def __init__(self, ins=(), out=None, name=""):
        """ins is list of opetopes one level lower,
        out is a single opetope one level lower
        """
        self.name = name
        self.id = name if name else generate_id()

        # this keeps track of what was degenerated into this opetope
        # eg, when ab: a -> b becomes a point, its name is ab, but
        # its inside_things are {"a", "b", "ab"}. 
        self.inside_names = ()
        self.in_parents = ()
        self.out_parents = ()
        self.olds_stack = []

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
            for op in self.ins:
                op.in_parents = (self, *op.in_parents)
            self.out.out_parents = (self, *self.out.out_parents)

        else:
            self.level = 0
            self.ins = ()
            self.out = -1 # TODO change that - (-1) to not confuse replace_a_by_b, which uses the fact that None is not a valid opetope 
    
    @staticmethod
    def match(ins, out):
        ins_of_out = set(out.ins)
        for opetope in ins:
            assert all([i in ins_of_out for i in opetope.ins])
            ins_of_out -= set(opetope.ins)
            ins_of_out.add(opetope.out)
        return list(ins_of_out)[0] == out.out
    
    def __str__(self):
        return self.to_string().rep
    
    def __repr__(self):
        return self.to_string().rep
    
    def is_gluable(self):
        return len(self.ins) == 1

    def to_string(self, remove_names=False):

        if not self.level:
            return Representation("*", self.inside_names) if remove_names else Representation(self.name, self.inside_names)

        ins_strs = []
        modifiers = []
        for i in self.ins:
            i_str, m = i.to_string(remove_names)
            modifiers.append(m)
            ins_strs.append(i_str)

        out_str, m = self.out.to_string(remove_names)
        modifiers.append(m)
        
        modifiers.append(self.inside_names)
        # print("Inside names: {}".format(self.inside_names))

        modifiers = tuple({m for m in modifiers if m})
        return Representation(unescape("({}: {} -> {})".format(self.name, ins_strs, out_str)), modifiers)
    

    @staticmethod
    def all_subopetopes(opetope):
        if not opetope.level:
            return {opetope}
        
        ins = flatten([Opetope.all_subopetopes(o) for o in opetope.ins])
        return set(ins) | Opetope.all_subopetopes(opetope.out) | {opetope}
    
    @staticmethod
    def all_subouts(opetope):
        if not opetope.level:
            return {}
        return {opetope.out} | set(flatten([Opetope.all_subouts(o) for o in [*opetope.ins, opetope.out]]))
    
    @staticmethod
    def generate_morphisms(op1, op2):
        degs = Opetope.degenerations(op1)
        subs = Opetope.all_subopetopes(op2)
        
        morphisms = set()
        # TODO
        
        return {s.shape() for s in subs if s.shape() in degs}


    @staticmethod
    def replace_a_by_b(a=None, b=None, 
                       only_in_parents=None, 
                       except_in_parents=None, 
                       only_out_parents=None,
                       except_out_parents=None):
        only_in_parents = only_in_parents or set()
        except_in_parents = except_in_parents or set()
        a_in_parents = a.in_parents if a and a.level else {}
        in_parents = only_in_parents or set(a_in_parents) - except_in_parents

        only_out_parents = only_out_parents or set()
        except_out_parents = except_out_parents or set()
        a_out_parents = a.out_parents if a and a.level else {}
        out_parents = only_out_parents or set(a_out_parents) - except_out_parents

        for p in in_parents:
            # FIXME so ugly with these set/tuple conversions
            p.ins = set(p.ins)
            if a in p.ins or not a:
                p.ins.discard(a)
                if b:
                    p.ins.add(b)
            p.ins = tuple(p.ins)
        
        for p in out_parents: 
            if a == p.out:
                if b:
                    p.out = b
                else:
                    # pdb.set_trace()
                    # print("aaa")
                    # x = 1
                    raise Exception("Removing opetope from output")

    
    def glue(self, parent_debug=None):
        print("gluing ", self.name)
        print_debug(parent_debug)
        assert len(self.ins) == 1
        
        # backup everything
        self.olds_stack.append(Old(out=self.out, ins=self.ins, level=self.level, in_parents=self.in_parents, out_parents=self.out_parents, inside_names=self.inside_names))
        olds = self.olds_stack[-1]

        # opetopes which used input, now use this self
        Opetope.replace_a_by_b(a=self.ins[0], b=self, except_in_parents={self})

        # opetopes which used output, now use this self
        Opetope.replace_a_by_b(a=self.out, b=self, except_out_parents={self})

        # opetopes which had this self in inputs, now have this self removed from inputs
        # opetopes which had this self as output - won't happen, because we only glue opetopes which are not anyone output
        Opetope.replace_a_by_b(a=self, b=None, only_in_parents=set(self.in_parents))

        # and finally
        # this self's parents are sum of ins parents, out parents and this self's parents
        self.in_parents = tuple((set(olds.in_parents) | set(olds.ins[0].in_parents) | set(olds.in_parents)) - {self})
        self.out_parents = tuple((set(olds.out_parents) | set(olds.ins[0].out_parents) | set(olds.out_parents)) - {self})
        # this self's level goes -1
        self.level -= 1
        # this self's inputs are replaced by self.out inputs
        self.ins = self.out.ins
        # this self's out is replaced by self.out output
        self.out = self.out.out
        

        # generate new inside_names
        self.inside_names = (self.name, olds.ins[0].name, olds.out.name, 
                             *self.inside_names, 
                             *olds.ins[0].inside_names,
                             *olds.out.inside_names) # is it even possible to have more inside_names?

        print("glued ", self.name)
        print_debug(parent_debug)

    def unglue(self, parent_debug=None):
        print("ungluing ", self.name)
        print_debug(parent_debug)

        # revert input removing - we don't care about replacing too much, we'll fix it later
        olds = self.olds_stack.pop()
        self.ins = olds.ins
        self.out = olds.out
        self.level = olds.level
        self.in_parents = olds.in_parents
        self.out_parents = olds.out_parents
        self.inside_names  = olds.inside_names


        Opetope.replace_a_by_b(a=self, b=self.ins[0], only_out_parents=set(self.ins[0].out_parents), only_in_parents=set(self.ins[0].in_parents))
        
        Opetope.replace_a_by_b(a=self, b=self.out, only_out_parents=set(self.out.out_parents), only_in_parents=set(self.out.in_parents))

        Opetope.replace_a_by_b(None, b=self, only_in_parents=set(self.in_parents), only_out_parents=set(self.out_parents))
        print("unglued ", self.name)
        print_debug(parent_debug)


    @staticmethod
    def degenerations(opetope, remove_names=False):
        all_degenerations = {opetope.to_string()}
        Opetope.degenerations_helper(opetope, all_degenerations, opetope, shape=opetope.to_string(), remove_names=remove_names)
        return all_degenerations



    @staticmethod
    @memoize
    def degenerations_helper(opetope, all_degenerations, parent, shape="", remove_names=False):
        # todo add memoization
        print("Now looking at;\n\n")
        print_debug(parent)
        all_degenerations.add(parent.to_string())
        if not opetope.level:
            return
        else:
            # FIXME all_subopetopes should memoize things
            gluable = {x for x in Opetope.all_subopetopes(parent) if x.is_gluable()} - set(Opetope.all_subouts(parent))
            
            for x in sorted(list(gluable), key=lambda x: (len(x.name), x.name)):
                print("Is gluable? ", x.is_gluable())
                x.glue(parent_debug=parent)
                # FIXME i probably want shape to be the shape of the current opetope, to stop recursion as early as possible
                # but for now, it'll do
                Opetope.degenerations_helper(opetope, all_degenerations, parent, shape=parent.to_string(), remove_names=remove_names)
                x.unglue(parent_debug=parent)
                # x,is_gluable = lambda: False
        return

    def shape(self, remove_names=True):
        # "shape" of the opetope: not caring about the names, just the canonical names
        # I may use tree representation in the future
        # but for now, just as a "function"-type
        # returns a Representation(string representation, modifiers)
        rep, mods = self.to_string(remove_names)
        return (rep, mods)

    
    @staticmethod
    def from_shape(shape):
        # return Opetope with shape specified
        pass
    
    def __eq__(self, other):
        # todo change that, it doesnt take into account that there 
        # might be different arrows between the same set of objects
        return str(self) == str(other)
    
    def __hash__(self):
        return hash(self.id)