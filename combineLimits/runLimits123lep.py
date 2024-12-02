import os,sys
from ROOT import TFile, TObject, RooArgSet

## Arguments: limit directory name; mass point; signal amount to inject; number of toys
##Run one branching fraction with exclusively our data cards. Check we can run our limtis again. 
##Another thing: look @ initial fits. Grab initial fit (r) for each mass point with down uncertainty and up uncertainty. Maybe correlation between printout and which mass points didn't set limits 
##Options for fits exist in Dr H's area.
## Make a datacard first with datacard.py!

limitdir = sys.argv[1]
BR = sys.argv[2]
path = limitdir+'/'+BR+'/'
os.chdir(path)
blind = False

masks = ''

if blind:
    for mass in [900,1100,1200,1300,1400,1500,1600,1700,1800]:

        if os.path.exists('cmb/'+str(mass)) and not os.path.exists('cmb/'+str(mass)+'/morphedWorkspace.root'):
            masks = 'mask_ch1_TT_isSR_isE_notV01T1H_DeepAK8_0_Combine=1,mask_ch1_TT_isSR_isE_notV01T2pH_DeepAK8_0_Combine=1,mask_ch1_TT_isSR_isE_notV0T0H1pZ_DeepAK8_0_Combine=1,mask_ch1_TT_isSR_isE_notV1T0H_DeepAK8_0_Combine=1,mask_ch1_TT_isSR_isE_notV2pT_DeepAK8_0_Combine=1,mask_ch1_TT_isSR_isE_notVbW_DeepAK8_0_Combine=1,mask_ch1_TT_isSR_isE_notVtH_DeepAK8_0_Combine=1,mask_ch1_TT_isSR_isE_notVtZ_DeepAK8_0_Combine=1,mask_ch1_TT_isSR_isE_taggedbWbW_DeepAK8_0_Combine=1,mask_ch1_TT_isSR_isE_taggedtHbW_DeepAK8_0_Combine=1,mask_ch1_TT_isSR_isE_taggedtZHtZH_DeepAK8_0_Combine=1,mask_ch1_TT_isSR_isE_taggedtZbW_DeepAK8_0_Combine=1,mask_ch1_TT_isSR_isM_notV01T1H_DeepAK8_0_Combine=1,mask_ch1_TT_isSR_isM_notV01T2pH_DeepAK8_0_Combine=1,mask_ch1_TT_isSR_isM_notV0T0H1pZ_DeepAK8_0_Combine=1,mask_ch1_TT_isSR_isM_notV1T0H_DeepAK8_0_Combine=1,mask_ch1_TT_isSR_isM_notV2pT_DeepAK8_0_Combine=1,mask_ch1_TT_isSR_isM_notVbW_DeepAK8_0_Combine=1,mask_ch1_TT_isSR_isM_notVtH_DeepAK8_0_Combine=1,mask_ch1_TT_isSR_isM_notVtZ_DeepAK8_0_Combine=1,mask_ch1_TT_isSR_isM_taggedbWbW_DeepAK8_0_Combine=1,mask_ch1_TT_isSR_isM_taggedtHbW_DeepAK8_0_Combine=1,mask_ch1_TT_isSR_isM_taggedtZHtZH_DeepAK8_0_Combine=1,mask_ch1_TT_isSR_isM_taggedtZbW_DeepAK8_0_Combine=1,mask_ch2_TT_elel2016BD_0_2016=1,mask_ch2_TT_elel2016EH_0_2016=1,mask_ch2_TT_elmu2016BD_0_2016=1,mask_ch2_TT_elmu2016EH_0_2016=1,mask_ch2_TT_mumu2016BD_0_2016=1,mask_ch2_TT_mumu2016EH_0_2016=1,mask_ch3_TT_elel2017BF_0_2017=1,mask_ch3_TT_elmu2017BF_0_2017=1,mask_ch3_TT_mumu2017BF_0_2017=1,mask_ch4_TT_elel2018AD_0_2018=1,mask_ch4_TT_elmu2018AD_0_2018=1,mask_ch4_TT_mumu2018AD_0_2018=1,mask_ch5_TT_triLep2016EEE_0_2016=1,mask_ch5_TT_triLep2016EEM_0_2016=1,mask_ch5_TT_triLep2016EMM_0_2016=1,mask_ch5_TT_triLep2016MMM_0_2016=1,mask_ch6_TT_triLep2017EEE_0_2017=1,mask_ch6_TT_triLep2017EEM_0_2017=1,mask_ch6_TT_triLep2017EMM_0_2017=1,mask_ch6_TT_triLep2017MMM_0_2017=1,mask_ch7_TT_triLep2018EEE_0_2018=1,mask_ch7_TT_triLep2018EEM_0_2018=1,mask_ch7_TT_triLep2018EMM_0_2018=1,mask_ch7_TT_triLep2018MMM_0_2018=1'
            if 'tW' in BR: masks = (masks.replace(',mask_ch1_TT_isSR_isE_taggedtZHtZH_DeepAK8_0_Combine=1','').replace(',mask_ch1_TT_isSR_isM_taggedtZHtZH_DeepAK8_0_Combine=1','').replace('bW','tW').replace('tZ','bZ').replace('tH','bH').replace('TT','BB')).replace(',mask_ch1_BB_isSR_isE_notVbH_DeepAK8_0_Combine=1','').replace(',mask_ch1_BB_isSR_isE_notVbZ_DeepAK8_0_Combine=1','').replace(',mask_ch1_BB_isSR_isM_notVbH_DeepAK8_0_Combine=1','').replace(',mask_ch1_BB_isSR_isM_notVbZ_DeepAK8_0_Combine=1','').replace('TT','BB')

            masks = masks+',signalScale=1' # set to 100fb for CR-only fit
            
            os.chdir('cmb/'+str(mass))

            print "Running Fit Diagnostics for initial workspace with SR channels masked: Mass =",mass
            print 'Command = combine -M FitDiagnostics -d workspace.root --saveWorkspace -n Masked --cminDefaultMinimizerStrategy 0 --setParameters '+masks
            os.system('combine -M FitDiagnostics -d workspace.root --saveWorkspace -n Masked --cminDefaultMinimizerStrategy 0 --setParameters '+masks)

            print "Creating initialFit snapshot file: morphedWorkspace.root" 
            w_f = TFile.Open('higgsCombineMasked.FitDiagnostics.mH120.root')
            w = w_f.Get('w')
            fr_f = TFile.Open('fitDiagnosticsMasked.root')
            fr = fr_f.Get('fit_b')
            myargs = RooArgSet(fr.floatParsFinal())
            w.saveSnapshot('initialFit',myargs,True)
            fout = TFile('morphedWorkspace.root', "recreate")
            fout.WriteTObject(w,'w')
            fout.Close()
            w_f.Close()
            fr_f.Close()
        
            os.chdir('../../')

    masks='mask_ch5_TT_triLep2016EEE_0_2016=0,mask_ch5_TT_triLep2016EEM_0_2016=0,mask_ch5_TT_triLep2016EMM_0_2016=0,mask_ch5_TT_triLep2016MMM_0_2016=0,mask_ch6_TT_triLep2017EEE_0_2017=0,mask_ch6_TT_triLep2017EEM_0_2017=0,mask_ch6_TT_triLep2017EMM_0_2017=0,mask_ch6_TT_triLep2017MMM_0_2017=0,mask_ch7_TT_triLep2018EEE_0_2018=0,mask_ch7_TT_triLep2018EEM_0_2018=0,mask_ch7_TT_triLep2018EMM_0_2018=0,mask_ch7_TT_triLep2018MMM_0_2018=0'
    masks+=',mask_ch1_TT_isCR_isE_dnnLargeJttbar_DeepAK8_0_Combine=0,mask_ch1_TT_isCR_isE_dnnLargeJwjet_DeepAK8_0_Combine=0,mask_ch1_TT_isCR_isE_dnnLargeTHZWB_DeepAK8_0_Combine=0,mask_ch1_TT_isCR_isM_dnnLargeJttbar_DeepAK8_0_Combine=0,mask_ch1_TT_isCR_isM_dnnLargeJwjet_DeepAK8_0_Combine=0,mask_ch1_TT_isCR_isM_dnnLargeTHZWB_DeepAK8_0_Combine=0'
    masks+=',mask_ch2_TT_elel2016BD_0_2016=0,mask_ch2_TT_elel2016EH_0_2016=0,mask_ch2_TT_elmu2016BD_0_2016=0,mask_ch2_TT_elmu2016EH_0_2016=0,mask_ch2_TT_mumu2016BD_0_2016=0,mask_ch2_TT_mumu2016EH_0_2016=0,mask_ch3_TT_elel2017BF_0_2017=0,mask_ch3_TT_elmu2017BF_0_2017=0,mask_ch3_TT_mumu2017BF_0_2017=0,mask_ch4_TT_elel2018AD_0_2018=0,mask_ch4_TT_elmu2018AD_0_2018=0,mask_ch4_TT_mumu2018AD_0_2018=0'
    masks += ',mask_ch1_TT_isSR_isE_notV01T1H_DeepAK8_0_Combine=0,mask_ch1_TT_isSR_isE_notV01T2pH_DeepAK8_0_Combine=0,mask_ch1_TT_isSR_isE_notV0T0H1pZ_DeepAK8_0_Combine=0,mask_ch1_TT_isSR_isE_notV1T0H_DeepAK8_0_Combine=0,mask_ch1_TT_isSR_isE_notV2pT_DeepAK8_0_Combine=0,mask_ch1_TT_isSR_isE_notVbW_DeepAK8_0_Combine=0,mask_ch1_TT_isSR_isE_notVtH_DeepAK8_0_Combine=0,mask_ch1_TT_isSR_isE_notVtZ_DeepAK8_0_Combine=0,mask_ch1_TT_isSR_isE_taggedbWbW_DeepAK8_0_Combine=0,mask_ch1_TT_isSR_isE_taggedtHbW_DeepAK8_0_Combine=0,mask_ch1_TT_isSR_isE_taggedtZHtZH_DeepAK8_0_Combine=0,mask_ch1_TT_isSR_isE_taggedtZbW_DeepAK8_0_Combine=0,mask_ch1_TT_isSR_isM_notV01T1H_DeepAK8_0_Combine=0,mask_ch1_TT_isSR_isM_notV01T2pH_DeepAK8_0_Combine=0,mask_ch1_TT_isSR_isM_notV0T0H1pZ_DeepAK8_0_Combine=0,mask_ch1_TT_isSR_isM_notV1T0H_DeepAK8_0_Combine=0,mask_ch1_TT_isSR_isM_notV2pT_DeepAK8_0_Combine=0,mask_ch1_TT_isSR_isM_notVbW_DeepAK8_0_Combine=0,mask_ch1_TT_isSR_isM_notVtH_DeepAK8_0_Combine=0,mask_ch1_TT_isSR_isM_notVtZ_DeepAK8_0_Combine=0,mask_ch1_TT_isSR_isM_taggedbWbW_DeepAK8_0_Combine=0,mask_ch1_TT_isSR_isM_taggedtHbW_DeepAK8_0_Combine=0,mask_ch1_TT_isSR_isM_taggedtZHtZH_DeepAK8_0_Combine=0,mask_ch1_TT_isSR_isM_taggedtZbW_DeepAK8_0_Combine=0'
    if 'tW' in BR: masks = (masks.replace(',ch1_TT_isSR_isE_taggedtZHtZH_DeepAK8_0_Combine=0','').replace(',mask_ch1_TT_isSR_isM_taggedtZHtZH_DeepAK8_0_Combine=0','').replace('bW','tW').replace('tZ','bZ').replace('tH','bH').replace('TT','BB')).replace(',mask_ch1_BB_isSR_isE_notVbH_DeepAK8_0_Combine=0','').replace(',mask_ch1_BB_isSR_isE_notVbZ_DeepAK8_0_Combine=0','').replace(',mask_ch1_BB_isSR_isM_notVbH_DeepAK8_0_Combine=0','').replace(',mask_ch1_BB_isSR_isM_notVbZ_DeepAK8_0_Combine=0','').replace('TT','BB')

    if 'tW0p0' in BR: 
        masks = masks+',signalScale=0.1' # set to 10fb after CR-only fit
    else:
        masks = masks+',signalScale=0.01' # reset to 1fb after CR-only fit

print 'Running Asymptotic CLs limits for all masses'
if blind:
    print 'Command = combineTool.py -M AsymptoticLimits -v 9 -d cmb/*/morphedWorkspace.root --snapshotName initialFit --there -n .limit --run=blind --parallel 5 --setParameters '+masks
    os.system('combineTool.py -M AsymptoticLimits -v 9 -d cmb/*/morphedWorkspace.root --snapshotName initialFit --there -n .limit --run=blind --parallel 5 --setParameters '+masks) #
else: 
    if 'tW0p0' in BR: masks = 'signalScale=0.1'
    else : masks = 'signalScale=0.01'
    print 'Command = combineTool.py -M AsymptoticLimits -d cmb/*/workspace.root --there -n .limit --parallel 5 --setParameters '+masks
    os.system('combineTool.py -M AsymptoticLimits -d cmb/*/workspace.root --there -n .limit --parallel 5 --setParameters '+masks) #

## Options to run without morphing (for 1500 GeV tZ1p0 point)
#print 'Command = combineTool.py -M AsymptoticLimits -d cmb/1500/workspace.root --there -n .limitNM --run=blind --setParameters '+masks
#os.system('combineTool.py -M AsymptoticLimits -d cmb/1500/workspace.root --there -n .limitNM --run=blind --setParameters '+masks) #

print 'Making a JSON file'
print 'Command = combineTool.py -M CollectLimits cmb/*/*.limit.* --use-dirs -o limits_cmb.json'
os.system('combineTool.py -M CollectLimits cmb/*/*.limit.* --use-dirs -o limits_cmb.json')

## Options to run without morphing (for 1500 GeV tZ1p0 point)
#print 'Command = combineTool.py -M CollectLimits cmb/1500/*.limitNM.* --use-dirs -o limits_cmbNM.json'
#os.system('combineTool.py -M CollectLimits cmb/1500/*.limitNM.* --use-dirs -o limits_cmbNM.json')

print 'Done!'
