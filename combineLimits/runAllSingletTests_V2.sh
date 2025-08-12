#!/bin/bash
echo "This script is iterative -- do a chunk, then comment what's done and uncomment the next step..."
echo "MAKE SURE YOU ARE ON EL9!!!"

# echo "--------------- Working on unblinded SR  -------------------"
#dir=limits_templatesABCDnn_D_Jan2025_RB1_2DcorrBtargetHoleCorrABCpABCTrain_2Dsmooth_rebin_alternative2 #_test #_moreSmooth #_test #_BB2k3a #k5b #_asym #_test #_largeRateUncert #_smooth2D_rebin #_test #_1Dtrain #nonBoosted #Boosted #_maskC3C4 #_largeRateUncert
#dir=limits_templatesABCDnn_D_Jan2025_RB1_2DcorrBtargetHoleCorrBTrain_smooth_rebin #_JumpExcC2Seg1 #_clip #_JumpAll
#mass=1200

#echo "Creating initial fit workspace:"
#python3 -u runInitialFit.py $dir $mass
#python3 -u runInitialFit.py $dir 1300
#python3 -u runInitialFit.py $dir 1800

#combine -M GoodnessOfFit $dir/cmb/$mass/workspace.root --algo KS
#combine -M GoodnessOfFit $dir/cmb/$mass/workspace.root --algo saturated --fixedSignalStrength 0 -t 5 --toysFrequentist

#echo "Submitting toys to condor for GOF:"
#python3 -u runCondorToys.py gof $dir $mass 500

#echo "Running impact test: "
#python3 -u runImpacts.py $dir $mass local 0

# ########## PAUSE UNTIL FINISHED ####################

#echo "Plotting GOF results:"python3 -u GoFPlotter.py $dir $mass
#python3 -u GoFPlotter.py $dir $mass

#python3 -u /uscms_data/d3/jmanagan/CombineV10/CMSSW_14_1_0_pre4/bin/el9_amd64_gcc12/plotImpacts.py --input $dir/cmb/$mass/impacts0p0.json --output $dir/cmb/$mass/impacts0p0 --summary --blind

# STEP 2
#python3 -u runInitialFit.py $dir 1300
#python3 -u runInitialFit.py $dir 1800
#python3 -u PostFitPlots.py $dir $mass 


# echo "--------------- Working on VR  -------------------"
dir=limits_templatesABCDnn_V2_Jan2025_RB1_2DcorrBtargetHoleCorrABCpABCTrain_2Dsmooth_rebin_alternative2_jecjer0p07
#dir=limits_templatesABCDnn_D_Jan2025_RB1_2DcorrBtargetHoleCorrBTrain2016
mass=1200

#echo "Creating initial fit workspace:"
#python3 -u runInitialFit.py $dir $mass

#echo "Running nuisance plot: CHECK LINES 382 and 411 FOR RANGES IF SYSTEMATICS CHANGE"
#python3 -u diffNuisances.py -g $dir/$BR/cmb/$mass/nuisancepulls.root $dir/$BR/cmb/$mass/fitDiagnosticsTest.root --abs >& $dir/$BR/cmb/$mass/nuisancepulls.txt

#echo "Running covariance plot: CHECK LINES 23/24 and 48/49 FOR RANGES IF SYSTEMATICS CHANGE"
#python3 -u covariancePlotter.py $dir $mass

#python3 -u PostFitPlots.py $dir $mass

#combine -M GoodnessOfFit $dir/cmb/$mass/workspace.root --algo saturated --fixedSignalStrength 0
#combine -M GoodnessOfFit $dir/cmb/$mass/workspace.root --algo saturated --fixedSignalStrength 0 -t 5 --toysFrequentist

## Make sure you have a grid proxy, then can submit condor jobs. EDIT THE FILES FIRST FOR OUTPUT PATHS!

#echo "Submitting toys to condor for R = 0:"
#python3 -u runCondorToys.py inject $dir $mass 0 500 

#echo "Submitting toys to condor for GOF:"
#python3 -u runCondorToys.py gof $dir $mass 500

########### STOP HERE! WAIT FOR CONDOR TO FINISH!! ##############

#echo "Plotting R = 0 injection results:"
#python3 -u signalInjectionPlotter.py $dir $mass 0

#echo "Plotting GOF results:"python3 -u GoFPlotter.py $dir $mass
python3 -u GoFPlotter.py $dir $mass

#echo "Done!"


#echo "--------------- Working on D+V2 for B -------------------"

#dir=limits_templatesABCDnn_DV2_Jan2025_RB1_2DcorrBtargetHoleCorrBTrain
#mass=1200

#echo "Creating initial fit workspace:"
#python3 -u runInitialFit.py $dir $mass 0 500   ## Mask D, unmask V. Then swap later...

# ## Make sure you have a grid proxy, then can submit condor jobs. NO MORE PATH EDITING NEEDED AFTER VR

#echo "Submitting toys to condor for 1200 R = 0:"
#python3 -u runCondorToys.py inject $dir $mass 0 500 

#mass=1800
#echo "Creating initial fit workspace:"
#python3 -u runInitialFit.py $dir $mass 0 500   ## Mask D, unmask V. Then swap later...

#echo "Submitting toys to condor for 1800 R = 0:"
#python3 -u runCondorToys.py inject $dir $mass 0.0 500 

#mass=1200
#echo "Running impact test: "
#python3 -u runImpacts.py $dir $mass local 0


######## STOP HERE! WAIT FOR CONDOR TO FINISH! ##########

#python3 -u /uscms_data/d3/jmanagan/CombineV10/CMSSW_14_1_0_pre4/bin/el9_amd64_gcc12/plotImpacts.py --input $dir/cmb/$mass/impacts0p0.json --output $dir/cmb/$mass/impacts0p0 --summary
#python3 -u signalInjectionPlotter.py $dir 1200 0     
#python3 -u signalInjectionPlotter.py $dir 1800 0




######## LIMITS BASED TESTS -- execute runLimits.py to get the numerical values for these tests

#mass=1200
#echo "Submitting toys to condor for 1200 R = exp0:"
#python3 -u runCondorToys.py inject $dir $mass 1.24609375 500

#mass=1800
#echo "Submitting toys to condor for 1800 R = exp0:"
#python3 -u runCondorToys.py inject $dir $mass 0.38671875 500

#mass=1200
#echo "Running impact test: "
#python3 -u runImpacts.py $dir $mass local 1.24609375

#python3 -u /uscms_data/d3/jmanagan/CombineV10/CMSSW_14_1_0_pre4/bin/el9_amd64_gcc12/plotImpacts.py --input $dir/cmb/$mass/impacts1p04.json --output $dir/cmb/$mass/impacts1p04 --summary

#echo "Plotting all injection results:"
#mass=1200
#python3 -u signalInjectionPlotter.py $dir $mass 1.24609375   # r-value of expected limit

#mass=1800
#python3 -u signalInjectionPlotter.py $dir $mass 0.38671875   # r-value of expected limit


# echo "Done!"

#12    "exp0": 1.040624976158142
#18    "exp0": 0.26171875
#08    "exp0": 7.875

#mass=1800
#echo "Running impact test: "
#python3 -u runImpacts.py $dir $mass local 0.38671875

#python3 -u /uscms_data/d3/jmanagan/CombineV10/CMSSW_14_1_0_pre4/bin/el9_amd64_gcc12/plotImpacts.py --input $dir/cmb/$mass/impacts0p262.json --output $dir/cmb/$mass/impacts0p262 --summary

#mass=800
#echo "Running impact test: "
#python3 -u runImpacts.py $dir $mass local 7.03125

#python3 -u /uscms_data/d3/jmanagan/CombineV10/CMSSW_14_1_0_pre4/bin/el9_amd64_gcc12/plotImpacts.py --input $dir/cmb/$mass/impacts7p03125.json --output $dir/cmb/$mass/impacts7p03125 --summary

### Old versions of impacts, if crab is needed

#mass=1200
#echo "Running impact test: "
#python3 -u runImpacts.py $dir $mass crab 0

#echo "Running impact test json-maker:"
#python3 -u runImpacts.py $dir $mass json

## then do the plotting, as above but with no number before .json


