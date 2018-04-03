import sys

NUMBER = sys.argv[1]

INPUT = "~/licencjat/tests/from_zawadowski/Data{}FS.txt".format(NUMBER)
OUTPUT = "~/licencjat/tests/from_zawadowski/Data{}WalkProdFaces.txt".format(NUMBER)

for t in range(1):
    get_ipython().system('ipython tests/from_zawadowski/ZawadowskiInputToPythonFile.py {}'.format(INPUT))
    get_ipython().system('ipython tests/from_zawadowski/Data{}test.py'.format(NUMBER))
    get_ipython().system('ipython tests/from_zawadowski/ZawadowskiOutputToNormal.py {}'.format(OUTPUT))
