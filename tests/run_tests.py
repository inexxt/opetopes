from run_test import run
from os import listdir

my_short = ["arrow_arrow.yaml", "arrow_7.yaml", "eye_eye.yaml", "arrow_eye.yaml", "7_7.yaml"]
my_long = ["9_9.yaml", "eye_2eye.yaml", "2eye_2eye.yaml", "11_11.yaml"]
arrow_tests = ["arrow_tests/" + k for k in sorted(listdir("./arrow_tests")) if k[0] != "."]

tests = my_short + my_long[:2] + arrow_tests[:12]

for t in tests:
    print(t)
    prod, l, c = run(t)
    print(prod)
    print(c)
    print(l)