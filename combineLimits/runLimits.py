import os,sys
from ROOT import TFile, TObject, RooArgSet

## Arguments: limit directory name; mass point; signal amount to inject; number of toys

## Make a datacard first with datacard.py!

limitdir = sys.argv[1]
path = limitdir+'/'
os.chdir(path)
blind = True
morph = False

print('====================================================================')
print('==   Launching limits for in',limitdir)
print('==   ...')

if blind:

    print('***** Running Asymptotic CLs limits for all masses in'+os.getcwd()+' *****')
    print('Running Asymptotic CLs limits for all masses')
    print('Command = combineTool.py -M AsymptoticLimits -d cmb/*/workspace.root --there -n .limit --run=blind')
    os.system('combineTool.py -M AsymptoticLimits -d cmb/*/workspace.root --there -n .limit --run=blind') #

    print('Making a JSON file')
    print('Command = combineTool.py -M CollectLimits cmb/*/*.limit.* --use-dirs -o limits_cmb.json')
    os.system('combineTool.py -M CollectLimits cmb/*/*.limit.* --use-dirs -o limits_cmb.json')

else:

    if not morph:
        print('***** Running Asymptotic CLs limits for all masses in'+os.getcwd()+' *****')
        print('Command = combineTool.py -M AsymptoticLimits -d cmb/*/workspace.root --there -n .limitUB --parallel 5')
        os.system('combineTool.py -M AsymptoticLimits -d cmb/*/workspace.root --there -n .limitUB --parallel 5')

        print('Making a JSON file')
        print('Command = combineTool.py -M CollectLimits cmb/*/*.limitUB.* --use-dirs -o limits_UB.json')
        os.system('combineTool.py -M CollectLimits cmb/*/*.limitUB.* --use-dirs -o limits_UB.json')
    
    else:
        masks = 'mask_TT_isSR_isE_notV01T1H_DeepAK8_0_Combine=0,mask_TT_isSR_isE_notV01T2pH_DeepAK8_0_Combine=0,mask_TT_isSR_isE_notV0T0H1pZ_DeepAK8_0_Combine=0,mask_TT_isSR_isE_notV1T0H_DeepAK8_0_Combine=0,mask_TT_isSR_isE_notV2pT_DeepAK8_0_Combine=0,mask_TT_isSR_isE_notVbW_DeepAK8_0_Combine=0,mask_TT_isSR_isE_notVtH_DeepAK8_0_Combine=0,mask_TT_isSR_isE_notVtZ_DeepAK8_0_Combine=0,mask_TT_isSR_isE_taggedbWbW_DeepAK8_0_Combine=0,mask_TT_isSR_isE_taggedtHbW_DeepAK8_0_Combine=0,mask_TT_isSR_isE_taggedtZHtZH_DeepAK8_0_Combine=0,mask_TT_isSR_isE_taggedtZbW_DeepAK8_0_Combine=0,mask_TT_isSR_isM_notV01T1H_DeepAK8_0_Combine=0,mask_TT_isSR_isM_notV01T2pH_DeepAK8_0_Combine=0,mask_TT_isSR_isM_notV0T0H1pZ_DeepAK8_0_Combine=0,mask_TT_isSR_isM_notV1T0H_DeepAK8_0_Combine=0,mask_TT_isSR_isM_notV2pT_DeepAK8_0_Combine=0,mask_TT_isSR_isM_notVbW_DeepAK8_0_Combine=0,mask_TT_isSR_isM_notVtH_DeepAK8_0_Combine=0,mask_TT_isSR_isM_notVtZ_DeepAK8_0_Combine=0,mask_TT_isSR_isM_taggedbWbW_DeepAK8_0_Combine=0,mask_TT_isSR_isM_taggedtHbW_DeepAK8_0_Combine=0,mask_TT_isSR_isM_taggedtZHtZH_DeepAK8_0_Combine=0,mask_TT_isSR_isM_taggedtZbW_DeepAK8_0_Combine=0'
        if 'tW' in BR: masks = (masks.replace(',mask_TT_isSR_isE_taggedtZHtZH_DeepAK8_0_Combine=0','').replace(',mask_TT_isSR_isM_taggedtZHtZH_DeepAK8_0_Combine=0','').replace('bW','tW').replace('tZ','bZ').replace('tH','bH').replace('TT','BB')).replace(',mask_BB_isSR_isE_notVbH_DeepAK8_0_Combine=0','').replace(',mask_BB_isSR_isE_notVbZ_DeepAK8_0_Combine=0','').replace(',mask_BB_isSR_isM_notVbH_DeepAK8_0_Combine=0','').replace(',mask_BB_isSR_isM_notVbZ_DeepAK8_0_Combine=0','')

        masks = masks+',signalShape=0.01' # reset to 1fb after CR-only fit
        
        print('Command = combineTool.py -M AsymptoticLimits -d cmb/*/morphedWorkspace.root --snapshotName initialFit --there -n .limitUBM --parallel 5 --setParameters '+masks)
        os.system('combineTool.py -M AsymptoticLimits -d cmb/*/morphedWorkspace.root --snapshotName initialFit --there -n .limitUBM --parallel 5 --setParameters '+masks) #

        print('Command = combineTool.py -M CollectLimits cmb/*/*.limitUBM.* --use-dirs -o limits_UBM.json')
        os.system('combineTool.py -M CollectLimits cmb/*/*.limitUBM.* --use-dirs -o limits_UBM.json')

print('Done!')
print('====================================================================')
