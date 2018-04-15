import sys
import yaml

second = {"a": [], "b": [], "ab": [["a"], "b"]}
options = {"unique_names": True}

PATH="/home/jack/licencjat/tests/from_zawadowski/"

def run(FILE):
	first = {}
	with open(PATH+FILE, "r") as f:
	    for l in sorted(f.readlines(), key=lambda x: int(x.split()[0])):
	        l = l.replace("\n", "")
	        l = l.split(" ")
	        name = "a{}".format(l[0])
	        out = "a{}".format(l[1]) if l[1] != "0" else None
	        ins = ["a{}".format(t) for t in l[2:]]
	        
	        first[name] = [ins, out] if out else []

	del first["a0"]

	from collections import OrderedDict
	result = dict([("first", first), ("second", second), ("options", options)])
	
	number = FILE.split("/")[-1].split("FS.txt")[0].split("Data")[1]
	
	try:
		number = str(int(number))
	except:
		pass

	with open(PATH + "arrow_{}.yaml".format(number), "w") as f:
	    yaml.dump(result, f)

if __name__ == "__main__":
	FILE = sys.argv[1]
	run(FILE)
