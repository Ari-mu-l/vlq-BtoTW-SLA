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

if not morph:
    masks = 'mask_Case1_D=0,mask_Case2_D=0,mask_Case3_D=0,mask_Case4_D=0,mask_Case1_V2=1,mask_Case2_V2=1,mask_Case3_V2=1,mask_Case4_V2=1' # unmask D, mask V
    if 'MC' in limitdir:
        masks = 'mask_Case1_D=0,mask_Case2_D=0,mask_Case3_D=1,mask_Case4_D=1,mask_Case1_V=1,mask_Case2_V=1,mask_Case3_V=1,mask_Case4_V=1,mask_Case3_A=1,mask_Case4_A=1,mask_Case3_B=1,mask_Case3_B=1,mask_Case3_C=1,mask_Case4_C=1' # unmask D, mask V
    if '36fb' not in limitdir:
        masks = masks+',signalScale=0.01' # 10 fb

    if blind:

        print('***** Running Asymptotic CLs limits for all masses in'+os.getcwd()+' *****')
        print('Running Asymptotic CLs limits for all masses')
        print('Command = combineTool.py -M AsymptoticLimits -d cmb/*/workspace.root --there -n .limit --run=blind --setParameters '+masks)
        os.system('combineTool.py -M AsymptoticLimits -d cmb/*/workspace.root --there -n .limit --run=blind --setParameters '+masks) #
        
        print('Making a JSON file')
        print('Command = combineTool.py -M CollectLimits cmb/*/*.limit.* --use-dirs -o limits_cmb.json')
        os.system('combineTool.py -M CollectLimits cmb/*/*.limit.* --use-dirs -o limits_cmb.json')

    else:
        print('***** Running Asymptotic CLs limits for all masses in'+os.getcwd()+' *****')
        print('Running Asymptotic CLs limits for all masses')
        print('Command = combineTool.py -M AsymptoticLimits -d cmb/*/workspace.root --there -n .limitUB --setParameters '+masks)
        os.system('combineTool.py -M AsymptoticLimits -d cmb/*/workspace.root --there -n .limitUB') #
        
        print('Making a JSON file')
        print('Command = combineTool.py -M CollectLimits cmb/*/*.limitUB.* --use-dirs -o limitsUB_cmb.json --setParameters '+masks)
        os.system('combineTool.py -M CollectLimits cmb/*/*.limitUB.* --use-dirs -o limitsUB_cmb.json')

else:

    masks = 'mask_Case1_D=1,mask_Case2_D=1,mask_Case3_D=1,mask_Case4_D=1,mask_Case1_V2=0,mask_Case2_V2=0,mask_Case3_V2=0,mask_Case4_V2=0,signalScale=1' # mask D for initial fit on untested masses, 1pb for V2 fit

    for mass in ['800','1000','1200','1300','1400','1500','1600','1700','1800','2000']:

        if os.path.exists('cmb/'+mass+'/morphedWorkspace.root'): continue

        os.chdir('cmb/'+mass+'/')
        # CMDS0 needed for tests in 1200. rMin/Max wasn't needed, but shouldn't hurt (will allow < 0)
        # Some messages about uncert matrix in s+b, but none about b-only
        print("Running Fit Diagnostics for initial workspace with SR channels masked")
        print('Command = combine -M FitDiagnostics -d workspace.root --rMin -2 --rMax 2 --saveWorkspace -n Masked --cminDefaultMinimizerStrategy 0 --setParameters '+masks)
        os.system('combine -M FitDiagnostics -d workspace.root --rMin -2 --rMax 2 --saveWorkspace -n Masked --cminDefaultMinimizerStrategy 0 --setParameters '+masks)
        
        print("Creating initialFit snapshot file: morphedWorkspace.root")
        w_f = TFile.Open('higgsCombineMasked.FitDiagnostics.mH120.root')
        w = w_f.Get('w')
        fr_f = TFile.Open('fitDiagnosticsMasked.root')
        fr = fr_f.Get('fit_b')
        myargs = RooArgSet(fr.floatParsFinal())
        w.saveSnapshot('initialFit',myargs,True)
        fout = TFile('morphedWorkspace.root', "recreate")
        fout.WriteTObject(w,'w')
        fout.Close()
        os.chdir('../../')
        
    # now unmask D, remask V
    masks = 'mask_Case1_D=0,mask_Case2_D=0,mask_Case3_D=0,mask_Case4_D=0,mask_Case1_V2=1,mask_Case2_V2=1,mask_Case3_V2=1,mask_Case4_V2=1' # unmask D, mask V after initial fit
    masks = masks+',signalScale=0.01' # 10 fb
    
    print('Command = combineTool.py -M AsymptoticLimits -d cmb/*/morphedWorkspace.root --snapshotName initialFit --there -n .limitM --parallel 5 --run=blind --setParameters '+masks)
    os.system('combineTool.py -M AsymptoticLimits -d cmb/*/morphedWorkspace.root --snapshotName initialFit --there -n .limitM --parallel 5 --run=blind --setParameters '+masks) #

    print('Command = combineTool.py -M CollectLimits cmb/*/*.limitM.* --use-dirs -o limitsM_cmb.json')
    os.system('combineTool.py -M CollectLimits cmb/*/*.limitM.* --use-dirs -o limitsM_cmb.json')

print('Done!')
print('====================================================================')
