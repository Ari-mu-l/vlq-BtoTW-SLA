#!/bin/bash

echo "This script is iterative -- do a chunk, then comment what's done and uncomment the next step..."
echo "MAKE SURE YOU ARE ON EL9!!!"

# echo "--------------- Working on VR  -------------------"

dir=limits_templatesABCDnn_V2_Jan2025_RB25
mass=1200

#echo "Plotting R = 0 injection results:"
#python3 -u signalInjectionPlotter.py $dir $mass 0

#echo "Plotting GOF results:"
#python3 -u GoFPlotter.py $dir $mass

#echo "Done!"


#echo "--------------- Working on D+V2 for B -------------------"

dir=limits_templatesABCDnn_DV2_Jan2025_RB25
mass=1200

#python3 -u /uscms_data/d3/jmanagan/CombineV10/CMSSW_14_1_0_pre4/bin/el9_amd64_gcc12/plotImpacts.py --input $dir/cmb/$mass/impacts0.json --output $dir/cmb/$mass/impacts0 --summary
python3 -u signalInjectionPlotter.py $dir 1200 0     
python3 -u signalInjectionPlotter.py $dir 1800 0

#python3 -u /uscms_data/d3/jmanagan/CombineV10/CMSSW_14_1_0_pre4/bin/el9_amd64_gcc12/plotImpacts.py --input $dir/cmb/$mass/impacts0p966.json --output $dir/cmb/$mass/impacts0p966 --summary

mass=1200
python3 -u signalInjectionPlotter.py $dir $mass 1.04   # r-value of expected limit

mass=1800
python3 -u signalInjectionPlotter.py $dir $mass 0.262   # r-value of expected limit


# echo "Done!"

#    "exp0": 0.965624988079071
#    "exp0": 0.28203123807907104


### Old versions of impacts, if crab is needed

#mass=1200
#echo "Running impact test: "
#python3 -u runImpacts.py $dir $mass crab 0

#echo "Running impact test json-maker:"
#python3 -u runImpacts.py $dir $mass json

## then do the plotting, as above but with no number before .json


