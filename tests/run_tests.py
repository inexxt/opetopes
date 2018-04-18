from run_test import run
from os import listdir

def prepend(s, l):
    return [s + x for x in l]

my_short = ["arrow_arrow.yaml", "arrow_7.yaml", "eye_eye.yaml", "arrow_eye.yaml", "7_7.yaml"]
my_long = ["9_9.yaml", "eye_2eye.yaml", "2eye_2eye.yaml", "11_11.yaml"]
arrow_tests = ["arrow_tests/" + k for k in sorted(listdir("./tests/arrow_tests")) if k[0] != "."]

tests = my_short + my_long + arrow_tests
tests = prepend("./tests/", tests)

for t in tests:
    print(t)
    prod, l, c = run(t)
    print(prod)
    print(c)
    print(l)
    prod.save()
