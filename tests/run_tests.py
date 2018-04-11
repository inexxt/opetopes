from run_test import run
from os import listdir
my_short = ["arrow_arrow.yaml", "arrow_7.yaml", "eye_eye.yaml", "arrow_eye.yaml", "7_7.yaml"]
my_long = ["9_9.yaml, 11_11.yaml"]
arrow_tests = ["arrow_tests/" + k for k in sorted(listdir("./arrow_tests")) if k[0] != "."]

tests = my_short + arrow_tests[:10]

for t in ["11_11.yaml"]:
    print(t)
    _, l, c = run(t)
    assert(c)
    print(l)