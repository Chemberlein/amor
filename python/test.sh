#!/bin/bash
for i in {1..100}
do
	python3 elementaryshortestpathwithsingleslot.py -a dynamic_programming  -i ../data/elementaryshortestpathwithslots/instance_$i.json -c certificate.json
done