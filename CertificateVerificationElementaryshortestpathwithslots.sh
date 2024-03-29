#! /bin/bash

# Auteur : zerhounb
# Version initiale : 12/01/2022

# Génération des certificats des solutions des instances de l'elementary shortest path with single slot.

for i in {1..100}
do
  echo
  echo "Instance $i"
  python3 python/elementaryshortestpathwithslots.py -a checker -i data/elementaryshortestpathwithslots/instance_${i}.json -c certificates/elementaryshortestpathwithslots/certificate${i}.json
done