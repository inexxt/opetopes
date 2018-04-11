from run_test import run

short_tests = ["arrow_arrow.yaml", "arrow_7.yaml", "eye_eye.yaml", "arrow_eye.yaml", "7_7.yaml"]
long_tests = ["9_9.yaml, 11_11.yaml"]

tests = short_tests

for t in tests:
    print(t)
    run(t)
    print()
