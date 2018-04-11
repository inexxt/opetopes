#!/bin/bash

SMALLER_THAN=200

for l in $(cat AListOfOpetopesSizes.txt); do
	LINE=$(echo $l | tr -d '\n\r')
	# echo $LINE
	IFS=, read NUM SIZE <<< $LINE
	export PYTHONPATH=`pwd`
	if [ $SIZE -lt $SMALLER_THAN ] && [ $SIZE -gt 0 ]; then
		INPUT="/home/jack/licencjat/tests/from_zawadowski/Data${NUM}FS.txt"
		echo "Number $NUM"
		python tests/ZawadowskiInputToPythonFile.py $INPUT
		pypy3 "/home/jack/licencjat/tests/from_zawadowski/Data${NUM}test.py"
	fi;
done;
