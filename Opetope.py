from typing import Set, Iterable


def flatten(ss):
    """
    Flatten a list - [[a, b], [c, d]] becomes [a, b, c, d]
    :param ss: list
    """
    return [x for s in ss for x in s]


# Generating unique ids not using RNG
ids = []


def generate_id(op: 'Opetope'):
    if not op.level:
        return ""

    ids.append(len(ids))
    return str(ids[-1])


def masks(n):
    """
    Generate all possible bit masks of length n
    :param n: length
    """
    if n == 1:
        return [[True], [False]]
    else:
        ms = masks(n - 1)
        return flatten([[[True] + m, [False] + m] for m in ms])


def unescape(x):
    """
    Remove ' and " from the string
    :param x: string
    """
    return x.replace("'", "").replace('"', "")


def first(iterable, default=None):
    """Return the first element of an iterable or the next element of a generator; or default.
    From norvig.com"""
    try:
        return iterable[0]
    except IndexError:
        return default
    except TypeError:
        return next(iterable, default)


class NegCounter():
    """
    I had to implement my own Counter class, because the default one doesn't support negative values...
    Or else, it does, but not consistently.
    I couldn't imagine how many bugs you could get from this simple fact.
    """

    def __init__(self, obj=None):
        self.counts = {}
        if obj:
            if isinstance(obj, dict):
                self.counts = {k: v for k, v in obj.items()}
            elif isinstance(obj, NegCounter):
                self.counts = {k: v for k, v in obj.counts.items()}
            elif isinstance(obj, Iterable):
                for t in obj:
                    self.counts[t] = self.counts.get(t, 0) + 1

    def __add__(self, other):
        return NegCounter({x: self.counts.get(x, 0) + other.counts.get(x, 0) for x in
                           set(self.counts.keys()) | set(other.counts.keys())})

    def __sub__(self, other):
        return NegCounter({x: self.counts.get(x, 0) - other.counts.get(x, 0) for x in
                           set(self.counts.keys()) | set(other.counts.keys())})

    def __or__(self, other):
        return NegCounter({x: self.counts.get(x, 0) + other.counts.get(x, 0) for x in
                           set(self.counts.keys()) | set(other.counts.keys())})

    def __and__(self, other):
        return NegCounter({x: self.counts.get(x, 0) + other.counts.get(x, 0) for x in
                           set(self.counts.keys()) & set(other.counts.keys())})

    def is_empty(self):
        return all(not v for v in self.counts.values())

    def __iadd__(self, other):
        return NegCounter({x: self.counts.get(x, 0) + other.counts.get(x, 0) for x in
                           set(self.counts.keys()) & set(other.counts.keys())})

    def __isub__(self, other):
        return NegCounter({x: self.counts.get(x, 0) - other.counts.get(x, 0) for x in
                           set(self.counts.keys()) & set(other.counts.keys())})

    def __getitem__(self, item):
        if item not in self.counts:
            self.counts[item] = 0
        return self.counts[item]

    def __setitem__(self, key, value):
        self.counts[key] = value

    def __repr__(self):
        return self.counts.__repr__()


class Opetope:

    __slots__ = ["name", "level", "ins", "out", "_shape", "_str", "_all_subopetopes", "_all_subouts", "id", "splus_order"]

    def __init__(self, ins=(), out=None, name=""):
        """
        :param ins: An iterable of opetopes one level lower
        :param out: A single opetope one level lower
        :param name: Name of this opetope - if not provided, a unique new one will be created
        """
        self.name = name

        if out:
            assert isinstance(out, Opetope)

            # check that levels are ok
            self.level = out.level + 1
            assert Opetope.match(ins, out, self.level)

            # check that lower level opetopes really "match"
            self.ins = tuple(ins)
            self.out = out

        else:
            self.level = 0
            self.ins = ()
            self.out = -1  # TODO change that - (-1) to not confuse replace_a_by_b, which uses the fact that None is not a valid opetope

        self.id = name if name else generate_id(self)

        # pre-calculating attributes
        self._shape = self.calculate_shape()
        self._str = self.calculate_to_string()
        self._all_subopetopes = frozenset(self.calculate_all_subopetopes())
        self._all_subouts = frozenset(self.calculate_all_subouts())

    @staticmethod
    def match(ins, out, level) -> bool:
        """
        Check if the out and ins provided match together, to create a new level-dimension opetope
        """

        if level == 0:
            return ins == () and out == None

        if level == 1:
            return out.level == 0 and len(ins) == 1 and ins[0].level == 0

        if not all([i.level == out.level for i in ins]) or out.level + 1 != level:
            return False

        ins_of_out = NegCounter(out.ins)
        for opetope in ins:
            ins_of_out = ins_of_out - NegCounter(opetope.ins)
            ins_of_out = ins_of_out + NegCounter({opetope.out})
        ins_of_out = ins_of_out - NegCounter({out.out})
        return ins_of_out.is_empty()

    def __str__(self) -> str:
        return self._str

    def __repr__(self) -> str:
        return self._str

    def is_unary(self) -> bool:
        """
        Check if the opetope is unary, eg it has exactly one face in the domain
        These kind of opetopes can be then degenerated
        :return:
        """
        return len(self.ins) == 1

    def calculate_shape(self):
        if not self.level:
            return "*"

        return "({} -> {})".format([i._shape for i in self.ins], self.out._shape)

    def calculate_to_string(self) -> str:
        """
        Return string representation of the opetope
        :param remove_names: This is used if one want's to have an "abstract" representation of an opetope - just the shape
        """
        if not self.level:
            return self.name

        return unescape("({}: {} -> {})".format(self.name, sorted([i._str for i in self.ins]), self.out._str))

    def calculate_all_subopetopes(self) -> 'FrozenSet[Opetope]':
        if not self.level:
            return frozenset({self})

        return frozenset(flatten([o.all_subopetopes() for o in self.ins])) | self.out.all_subopetopes() | frozenset({self})

    def calculate_all_subouts(self) -> 'FrozenSet[Opetope]':
        if not self.level:
            return frozenset()
        return frozenset({self.out}) | frozenset(flatten([o.all_subouts() for o in [*self.ins, self.out]]))

    def all_subopetopes(self):
        return self._all_subopetopes

    def all_subouts(self):
        return self._all_subouts

    def shape(self, remove_names=True):
        # "shape" of the opetope: not caring about the names, just the canonical names
        # I may use tree representation in the future
        # but for now, just as a "function"-type
        # returns a Representation(string representation, modifiers)
        return self._shape

    @staticmethod
    def from_shape(shape):
        # return Opetope with shape specified
        pass

    def __eq__(self, other):
        return str(self) == str(other)  # FIXME
        # if isinstance(self, int) or isinstance(other, int):
        #     return str(self) == str(other)
        # if not self.level and not other.level:
        #     return self.name == other.name
        # return not {self.ins} ^ {other.ins} and \
        #        self.out == other.out
        #        # self.name == other.name

    def __hash__(self):
        return hash(self._str)

    @staticmethod
    def is_valid_morphism(op1: 'Opetope', op2: 'Opetope') -> bool:
        """
        Check that op1, with vertices colored (named) by vertices of op2, is a valid contraction to op2
        One problem is that we can't use the top-level name
        :param op1:
        :param op2:
        :return:
        """

        # contract all things in op1
        def contract(op):
            if not op.level:
                return op
            out = contract(op.out)
            ins = [contract(i) for i in op.ins]
            ins = [i for i in ins if i.level == out.level]

            if all([i._str == out._str for i in ins]):
                return contract(op.out)
            return Opetope(ins=ins, out=out, name=op.name)

        op1.name = op2.name  # FIXME ALARM ugly hack because of "abecadło" problem
        return contract(op1)._str == op2._str

    def is_non_degenerated(self):
        # basically not having loops
        if not self.level:
            return True
        if self.level == 1:
            return self.ins[0] != self.out
        else:
            return all(i.is_non_degenerated() for i in [*self.ins, self.out])


class Face(Opetope):

    __slots__ = ["p1", "p2", "_str_full"]

    def __init__(self, p1: Opetope, p2: Opetope, ins: 'Iterable[Face]' = (), out=None, name=""):
        self.p1 = p1
        self.p2 = p2
        self._str_full = ""

        super().__init__(ins=ins, out=out, name=name)

        self._str_full = self.calculate_to_string(full=True)


    def calculate_to_string(self, full=False) -> str:
        if full:
            if not self.level:
                return "{}{}".format(self.p1, self.p2)

            return "{}{}{}{}{}".format(self.p1,
                                       self.p2,
                                       "".join(sorted([i._str_full for i in self.ins])),
                                       self.out._str_full,
                                       self.name)
        else:
            return "({}, {})!{}\n".format(self.p1._str, self.p2._str, self.level)

    @staticmethod
    def verify_construction(p1: Opetope, p2: Opetope, ins: 'Iterable[Face]' = (), out=None, name="") -> bool:
        if not Opetope.match(ins, out, out.level + 1):
            return False

        face = Face(p1, p2, ins, out, name)

        def get_pxs(f: 'Face', px) -> Opetope:
            if not f.level:
                return Opetope(name=px(f).name)

            out = get_pxs(f.out, px)
            ins = [get_pxs(i, px) for i in f.ins if i.level == out.level]
            return Opetope(ins=ins, out=out, name=px(f).name)  # (*)

        op1 = get_pxs(face, lambda x: x.p1)
        op2 = get_pxs(face, lambda x: x.p2)

        # FIXME remove these
        op1.name = "abecadło"  # I can trust in names of all things below me, but I can't in my name, as in (*)
        op2.name = "abecadło"  # I can trust in names of all things below me, but I can't in my name, as in (*)

        # We have to check here if this is a valid projection
        # eg if all (recursivly) faces of self, projected on p1, together get us p1
        # and similarly p2
        if not (Opetope.is_valid_morphism(op1, p1) and Opetope.is_valid_morphism(op2, p2)):
            return False

        return True

    @staticmethod
    def from_point_and_point(p1: Opetope, p2: Opetope) -> 'Face':
        assert (p1.level, p2.level) == (0, 0)
        return Face(p1, p2)

    @staticmethod
    def from_arrow_and_point(p1: Opetope, p2: Opetope) -> 'Face':
        assert (p1.level, p2.level) == (1, 0)
        return Face(p1, p2, ins=[Face.from_point_and_point(p1.ins[0], p2)],
                    out=Face.from_point_and_point(p1.out, p2))

    @staticmethod
    def from_point_and_arrow(p1: Opetope, p2: Opetope) -> 'Face':
        assert (p1.level, p2.level) == (0, 1)
        # we can't just use from_arrow_and_point, because the order p1, p2 is important
        return Face(p1, p2, ins=[Face.from_point_and_point(p1, p2.ins[0])],
                    out=Face.from_point_and_point(p1, p2.out))

    @staticmethod
    def from_arrow_and_arrow(p1: Opetope, p2: Opetope) -> 'Face':
        assert (p1.level, p2.level) == (1, 1)
        return Face(p1, p2, ins=[Face.from_point_and_point(p1.ins[0], p2.ins[0])],
                    out=Face.from_point_and_point(p1.out, p2.out))

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        return hash(self._str_full)

    def __str__(self):
        return self._str

    def __repr__(self):
        return self._str