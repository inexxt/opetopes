import os
import dill as pickle

fname = f"./pickles/{os.listdir('pickles')[0]}"

with open(fname, "rb") as f:
	t = pickle.load(f)

print(t)