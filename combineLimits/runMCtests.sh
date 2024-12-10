#!/bin/bash

echo "MAKE SURE YOU ARE ON EL9!!!"

# echo "--------------- Working on VR for TT -------------------"

dir=limits_templatesMC_V2_Oct2024_500
mass=1200

echo "Creating initial fit workspace:" 
python3 -u runInitialFit.py $dir $mass

## For V2:
# baseline with CDMS0 and rMin < 0, covmat 2 on both fits
# Remove small uncerts, lnN for some muRF & lepSF: not really any better
# 500 bins, 0p1 rebinning: helpful for muQCD pull, jec very constrained (smooth?)


## For ABCV2V2:
## All params baseline, keeping CDMS0 and rMin: covmat 2 on both, lots of pulling

echo "Running nuisance plot: CHECK LINES 382 and 411 FOR RANGES"
python3 -u diffNuisances.py -g $dir/$BR/cmb/$mass/nuisancepulls.root $dir/$BR/cmb/$mass/fitDiagnosticsTest.root >& $dir/$BR/cmb/$mass/nuisancepulls.txt

echo "Running covariance plot: CHECK LINES 23/24 and 48/49 FOR RANGES"
python3 -u covariancePlotter.py $dir $mass

#echo "Submitting toys to condor for R = 0:"
#python3 -u runCondorToys.py inject $dir $mass 0 500 

#echo "Submitting toys to condor for GOF:"
#python3 -u runCondorToys.py gof $dir $mass 500

########### STOP HERE! WAIT FOR CONDOR TO FINISH!! ##############

#echo "Plotting R = 0 injection results:"
#python3 -u signalInjectionPlotter.py $dir $mass 0

#echo "Plotting GOF results:"
#python3 -u GoFPlotter.py $dir $mass

#echo "Done!"

# echo "--------------- Working on D+V2 for B -------------------"

# dir=limits_templatesABCDnn_DV2_Oct2024
# mass=1200

#echo "Creating initial fit workspace:"
#python3 -u runInitialFit.py $dir $mass 0 500   ## Mask D, unmask V. Then swap later...

#echo "Submitting toys to condor for 1200 R = 0:"
#python3 -u runCondorToys.py inject $dir $mass 0 500 

#echo "Running impact test: "
#python3 -u runImpacts.py $dir $mass local

# echo "---- LIMIT-BASED TOYS (run limits and set values first!) ----"

# echo "Submitting toys to condor for 1200 R = exp0:"
# python3 -u runCondorToys.py inject $dir $mass 1.90 500 

# mass=1800
# echo "Submitting toys to condor for 1800 R = 0:"
# python3 -u runCondorToys.py inject $dir $mass 0.0 500 

# echo "Submitting toys to condor for 1800 R = exp0:"
# python3 -u runCondorToys.py inject $dir $mass 0.38 500


######## STOP HERE! WAIT FOR CRAB/CONDOR TO FINISH! ##########

# echo "Running impact test json-maker:"
# python3 -u runImpacts.py $dir $mass json

#python3 -u /uscms_data/d3/jmanagan/CombineV10/CMSSW_14_1_0_pre4/bin/el9_amd64_gcc12/plotImpacts.py --input $dir/cmb/1200/impacts.json --output $dir/cmb/1200/impacts --summary

# echo "Plotting all injection results:"
# mass=1200
# python3 -u signalInjectionPlotter.py $dir $mass 0     
# python3 -u signalInjectionPlotter.py $dir $mass 1.90   # r-value of expected limit

# mass=1800
# python3 -u signalInjectionPlotter.py $dir $mass 0
# python3 -u signalInjectionPlotter.py $dir $mass 0.38   # r-value of expected limit


# echo "Done!"

