import sys
import yaml
from copy import deepcopy

from collections import Iterable

from Opetope import Opetope
from Products import Product
from toposort import toposort_flatten


def run(test_path):
    with open(test_path, 'r') as stream:
        desc = yaml.load(stream)

    options = desc["options"]

    fst = desc["first"]
    if "square" in options and options["square"]:
        snd = deepcopy(desc["first"])
    else:
        snd = desc["second"]

    def append_to_names(obj, n: str):
        if not obj:
            return None

        if isinstance(obj, str):
            return obj + n

        if isinstance(obj, dict):
            newd = {}
            for k, v in obj.items():
                newd[append_to_names(k, n)] = append_to_names(v, n)
            return newd

        if isinstance(obj, Iterable):
            newi = type(obj)([append_to_names(k, n) for k in obj])
            return newi

        raise NotImplementedError

    if "uniue_names" in options and options["unique_names"]:
        fst = append_to_names(fst, "_f")
        snd = append_to_names(snd, '_s')

    def create_opetope(desc):
        def get_dependencies(desc):
            deps = {}
            for k, v in desc.items():
                deps[k] = set(v[0] + [v[1]]) if v else set()

            return deps

        faces = {}

        for f in toposort_flatten(get_dependencies(desc)):
            faces[f] = Opetope(name=f) if not desc[f] else Opetope(name=f, ins=[faces[x] for x in desc[f][0]], out=faces[desc[f][1]])

        return list(sorted(faces.values(), key=lambda v: v.level))[-1]

    f_ope = create_opetope(fst)
    s_ope = create_opetope(snd)

    prod = Product(f_ope, s_ope)
    return prod, len(prod.faces), prod.is_contractible()


if __name__=="__main__":
    _, l, c = run(sys.argv[1])
    print(l)
    print(c)
