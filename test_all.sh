#!/bin/bash

for l in $(cat AListOfOpetopes.txt); do
	echo $l
	ipython testing.py $(echo $l | tr -d '\r')
done
