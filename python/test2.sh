#!/bin/bash
for i in {1..100}
do
	python3 elementaryshortestpathwithslots.py -a iterative_beam_search  -i ../data/elementaryshortestpathwithslots/instance_$i.json -c certificate.json
done