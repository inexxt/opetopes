#!/bin/bash

OUT="./true_asnwers.txt"
rm $OUT

for l in $(cat AListOfOpetopes.txt); do
	NUMBER=$(echo $l | tr -d '\n\r')
	OUTPUT="/home/jack/licencjat/tests/from_zawadowski/Data${NUMBER}WalkProdFaces.txt"
	echo "Number $NUMBER" >> $OUT
	python tests/ZawadowskiOutputToNormal.py $OUTPUT >> $OUT
done;