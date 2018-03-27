from collections import namedtuple, defaultdict
import string
import random

def flatten(ss):
    return [x for s in ss for x in s]

def generate_id():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))

def masks(n):
    if n == 1:
        return [[True], [False]]
    else:
        ms = masks(n-1)
        return flatten([[[True] + m, [False] + m] for m in ms])

def unescape(x):
    return x.replace("'", "").replace('"', "")


Representation = namedtuple("Representation", ["rep", "mods"])


class Opetope:


    def __init__(self, ins=None, out=None, name=""):
        """ins is list of opetopes one level lower,
        out is a single opetope one level lower
        """
        self.name = name
        self.id = name if name else generate_id()

        # modifiers used in degenerations

        # is this opetope merged into point?
        self.degenerated = False
        
        # if the opetope has only one input, the input and 
        # output can be glued together, with main opetope arrow
        # transformed to the main arrow of output
        self.glued = False
        
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
            self.subnames = [x.name for x in Opetope.all_subopetopes(self)]
        else:
            self.level = 0
            self.ins = self, 
            self.out = self
            self.points = [self.name]

        

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
        return len([x for x in self.ins if not x.degenerated]) == 1

    def to_string(self, remove_names=False):
        # if remove_names, returns (opetope without names, "")
        # else returns (opetope without names, modifiers)
        # where modifiers are gluations and degenerations

        if not self.level:
            return Representation("*", "") if remove_names else Representation(self.name, "")

        if self.degenerated:
            if remove_names:
                return Representation("", "")
            else:
                return Representation("", "{}".format("=".join(self.subnames)))
        if self.glued:
            if remove_names:
                return Representation("", "")
            else:
                the_only_in = [x for x in self.ins if not x.degenerated][0]
                return Representation("", "{}|{}|{}".format(self.name, self.out.name, the_only_in.name))

        ins_strs = []
        modifiers = []
        for i in self.ins:
            i_str, m = i.to_string(remove_names)
            modifiers.append(m)
            if i_str:
                ins_strs.append(i_str)

        out_str, m = self.out.to_string(remove_names)
        modifiers.append(m)
        modifiers = [x for x in modifiers if x]
        modifiers = unescape(str(sorted(modifiers))) if modifiers else ""

        return Representation(unescape("{} -> {}".format(ins_strs, out_str)), modifiers)
    

    @staticmethod
    def all_subopetopes(opetope):
        if not opetope.level or opetope.degenerated:
            return {opetope}
        
        ins = flatten([Opetope.all_subopetopes(o) for o in opetope.ins])
        return set(ins) | Opetope.all_subopetopes(opetope.out) | {opetope}
    
    @staticmethod
    def all_subouts(opetope):
        if not opetope.level or opetope.degenerated:
            return {}
        return {opetope.out} | set(flatten([Opetope.all_subouts(o) for o in [*opetope.ins, opetope.out]]))
    
    @staticmethod
    def generate_morphisms(op1, op2):
        degs = op1.degenerations()
        subs = Opetope.all_subopetopes(op2)
        
        morphisms = set()
        
        return {s.shape() for s in subs if s.shape() in degs}
    
    @staticmethod
    def degenerations(opetope, remove_names=False):
        # todo add memoization
        if not opetope.level:
            return "*" # ugly, change that later
        else:
            degenerations = defaultdict(set)
            all_subs = Opetope.all_subopetopes(opetope)
            all_outs = Opetope.all_subouts(opetope)
            all_degenerable = list(all_subs - all_outs)
            
            # it doesn't make sense to degenerate points
            all_degenerable = {a for a in all_degenerable if a.level}

            # here we perform all possible degenerations
            for md in masks(len(all_degenerable)):

                for (x, d) in zip(md, all_degenerable):
                    d.degenerated = x
                
                # now we have to perform all possible gluations
                all_gluable = [x for x in all_degenerable if x.is_gluable()]
                if len(all_gluable):
                    print("Found gluable")
                for mg in masks(len(all_gluable)):
                    for (x, d) in zip(mg, all_gluable):
                        d.glued = x

                    shape, modifiers = opetope.shape(remove_names)
                    degenerations[shape].add(modifiers)
                        
            # clean up
            for d in all_degenerable:
                d.degenerated = False
                d.glued = False

            # unfortunately, in the case of  remove_names, the whole opetope
            # degenerates just to "" so in this special case 
            # we have to replace "" with just a point 

            if remove_names:
                degenerations["*"] = degenerations[""]
                del degenerations[""]

            return dict(degenerations)
            
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