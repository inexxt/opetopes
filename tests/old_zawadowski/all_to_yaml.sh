#!/bin/bash

export PYTHONPATH=/home/jack/licencjat/
for f in $(ls /home/jack/licencjat/tests/from_zawadowski | grep FS); do
	python3 zawadowski_to_yaml.py $f
done
