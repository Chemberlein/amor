#! /bin/bash

# Auteur : zerhounb
# Version initiale : 12/01/2022

# Génération des certificats des solutions des instances de l'elementary shortest path with single slot.

for i in {1..100}
do
  echo
  echo "Instance $i"
  python3 python/vehicleroutingwithsingleslot.py -a checker -i data/vehicleroutingwithslots/instance_${i}.json -c certificates/vehicleroutingwithsingleslot/certificate${i}.json
done