import os,sys
from ROOT import TFile, TObject, RooArgSet

## Arguments: limit directory name; mass point; signal amount to inject; number of toys

## Make a datacard first with datacard.py!

limitdir = sys.argv[1]
mass = sys.argv[2]
docrab = sys.argv[3]
expsig = sys.argv[4]
blind = True

name = limitdir.replace('limits_templatesABCDnn_V2_Oct2024_','').replace('limits_templatesABCDnn_DV2_Oct2024_','')
path = limitdir+'/cmb/'+mass

isSR = False
if '_D' in limitdir: isSR = True

if not blind:
    filename = 'workspace.root'
    options = ''
else:
    if isSR: 
        masks = 'mask_Case1_D=0,mask_Case2_D=0,mask_Case3_D=0,mask_Case4_D=0,mask_Case1_V2=1,mask_Case2_V2=1,mask_Case3_V2=1,mask_Case4_V2=1' # unmask D, remask V after V-only fit
        masks = masks+',signalScale=0.01' # set to 1fb after V-only fit, or 10fb for expected limit 1200 of 19fb

        filename = 'morphedWorkspace.root'
        options = ' --snapshotName initialFit --bypassFrequentistFit -t -1 --expectSignal '+str(expsig)+' --setParameters '+masks

        ## Options to test non-morphed file
        #filename = 'workspace.root'
        #options = ' --bypassFrequentistFit -t -1 --expectSignal 0'


customcrab = '/uscms_data/d3/jmanagan/BtoTW/CMSSW_13_0_18/src/vlq-BtoTW-SLA/combineLimits/custom_crab_impacts.py'

os.chdir(path)

if docrab == 'local': #Bp likely doesn't need crab, fits are fast and not as many nuisances
    print("Running Impacts initial fit")
    print('Command = combineTool.py -M Impacts -d '+filename+' -m '+str(mass)+' --doInitialFit --robustFit 1 --rMin -10 --rMax 10 '+options) #--cminDefaultMinimizerStrategy 0 
    os.system('combineTool.py -M Impacts -d '+filename+' -m '+str(mass)+' --doInitialFit --robustFit 1 --rMin -10 --rMax 10 '+options)#--cminDefaultMinimizerStrategy 0 
    #Notes: with 1fb+CDMS0 got 0.44 +/- 6. With Robust same result +/- 8. Will try with just Robust for everything

    print("Running over each nuisance")
    print('Command = combineTool.py -M Impacts -d '+filename+' -m '+str(mass)+' --robustFit 1 --rMin -10 --rMax 10 --doFits'+options) #--cminDefaultMinimizerStrategy 0 
    os.system('combineTool.py -M Impacts -d '+filename+' -m '+str(mass)+' --robustFit 1 --rMin -10 --rMax 10 --doFits'+options)#--cminDefaultMinimizerStrategy 0 

    print("Making json file")
    print('Command = combineTool.py -M Impacts -d '+filename+' -m '+str(mass)+' -o impacts'+str(expsig).replace('.','p')+'.json'+options)
    os.system('combineTool.py -M Impacts -d '+filename+' -m '+str(mass)+' -o impacts'+str(expsig).replace('.','p')+'.json'+options)


    
elif docrab == 'crab':
    print("Running Impacts initial fit")
    print('Command = combineTool.py -M Impacts -d '+filename+' -m '+str(mass)+' --doInitialFit --cminDefaultMinimizerStrategy 0 --rMin -10 --rMax 10 '+options) #--robustFit 1 
    os.system('combineTool.py -M Impacts -d '+filename+' -m '+str(mass)+' --doInitialFit --cminDefaultMinimizerStrategy 0 --rMin -10 --rMax 10 '+options)#--robustFit 1 
    #Notes: with scales set to 1 doesn't converge (fails outright with robust) unless CDMS0. With scales 0.01 CDMS0=CDMS0+robust, still fails outright with just robust. 

    print("Running over each nuisance")
    print('Command = combineTool.py -M Impacts -d '+filename+' -m '+str(mass)+' --cminDefaultMinimizerStrategy 0 --robustFit 1 --rMin -10 --rMax 10 --doFits'+options+' --job-mode crab3 --task-name impacts'+name+' --custom-crab '+customcrab) #
    os.system('combineTool.py -M Impacts -d '+filename+' -m '+str(mass)+' --cminDefaultMinimizerStrategy 0 --robustFit 1 --rMin -10 --rMax 10 --doFits'+options+' --job-mode crab3 --task-name impacts'+name+' --custom-crab '+customcrab)# 

else:
    print("Making json file")
    print('Command = combineTool.py -M Impacts -d '+filename+' -m '+str(mass)+' -o impacts.json'+options)
    os.system('combineTool.py -M Impacts -d '+filename+' -m '+str(mass)+' -o impacts.json'+options)
