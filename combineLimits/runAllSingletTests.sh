#!/bin/bash

echo "MAKE SURE YOU ARE ON EL9!!!"

# echo "--------------- Working on VR for TT -------------------"

#dir=limits_templatesABCDnn_V2_Oct2024_420RB2
#mass=1200

#echo "Creating initial fit workspace:" 
#python3 -u runInitialFit.py $dir $mass 0 500 

#echo "Running nuisance plot: CHECK LINES 382 and 411 FOR RANGES"
#python3 -u diffNuisances.py -g $dir/$BR/cmb/$mass/nuisancepulls.root $dir/$BR/cmb/$mass/fitDiagnostics.root >& $dir/$BR/cmb/$mass/nuisancepulls.txt

#echo "Running covariance plot: CHECK LINES 23/24 and 48/49 FOR RANGES"
#python3 -u covariancePlotter.py $dir $mass

# Not included in Kuan-Yu's list
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

# echo "--------------- Working on SR+CR for TT -------------------"

dir=limits_templatesABCDnn_DV2_Oct2024_420RB2
mass=1200

#echo "Creating initial fit workspace:"
#python3 -u runInitialFit.py $dir $mass 0 500   ## Mask D, unmask V. Then swap later...

#echo "Running impact test: (Note: might crash waiting for proxy password if piped to a log!)"
#python -u runImpacts.py $dir $mass crab 1 ## Xiaohe: expsig = 1
python3 -u runImpacts.py $dir $mass local 0 ## Xiaohe: crab didn't work

# echo "Submitting toys to condor for 1200 R = 0:"
# python3 -u runCondorToys.py inject $dir $mass 0 500 

# echo "---- LIMIT-BASED TOYS (run limits and set values first!) ----"

# echo "Submitting toys to condor for 1200 R = exp0:"
# python3 -u runCondorToys.py inject $dir $mass 1.46 500 

# mass=1800
# echo "Submitting toys to condor for 1800 R = 0:"
# python3 -u runCondorToys.py inject $dir $mass 0.0 500 

# echo "Submitting toys to condor for 1800 R = exp0:"
# python3 -u runCondorToys.py inject $dir $mass 0.38 500


######## STOP HERE! WAIT FOR CRAB/CONDOR TO FINISH! ##########

#echo "Running impact test json-maker:"
#python3 -u runImpacts.py $dir $mass json 1 # Xiaohe: expsig = 1

#python3 -u plotImpacts.py --input $dir/cmb/1200/impacts.json --output $dir/cmb/1200/impacts

#echo "Plotting all injection results:"
#mass=1200
#python3 -u signalInjectionPlotter.py $dir $mass 0     
#python3 -u signalInjectionPlotter.py $dir $mass 1.46   # r-value of expected limit

#mass=1800
#python3 -u signalInjectionPlotter.py $dir $mass 0
#python3 -u signalInjectionPlotter.py $dir $mass 0.38   # r-value of expected limit


# echo "Done!"

