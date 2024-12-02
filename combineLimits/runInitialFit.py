import os,sys
from ROOT import TFile, TObject, RooArgSet

## Arguments: limit directory name; mass point; signal amount to inject; number of toys

## Make a datacard first with datacard.py!

limitdir = sys.argv[1]
mass = sys.argv[2]

style = 'ABCDnn'
if 'ABCDnn' not in limitdir: style = 'MC'
path = limitdir+'/cmb/'+mass

isSR = False
if '_DV2' in limitdir or '_ABCDCV2V2' in limitdir: isSR = True

os.chdir(path)

filename = 'initialFitWorkspace.root'
if isSR: filename = 'morphedWorkspace.root'

if not isSR and not os.path.exists(filename):

    # no masking is needed here since only V will be in the workspace.
    # check whether the 1 pb normalization is fine for getting r ~ 1

    print("Running Fit Diagnostics for initial workspace")
    print('Command = combine -M FitDiagnostics -d workspace.root --saveWorkspace --cminDefaultMinimizerStrategy 0 --rMin -1  --verbose 1 --saveShapes --plots --setParameters signalScale=1')# 
    os.system('combine -M FitDiagnostics -d workspace.root --saveWorkspace --cminDefaultMinimizerStrategy 0 --rMin -1  --verbose 1 --saveShapes --plots --setParameters signalScale=1') # 
    
    print("Creating initialFit snapshot file: initialFitWorkspace.root")
    w_f = TFile.Open('higgsCombineTest.FitDiagnostics.mH120.root')
    w = w_f.Get('w')
    fr_f = TFile.Open('fitDiagnosticsTest.root')
    fr = fr_f.Get('fit_b')
    myargs = RooArgSet(fr.floatParsFinal())
    w.saveSnapshot('initialFit',myargs,True)
    fout = TFile('initialFitWorkspace.root',"recreate")
    fout.WriteTObject(w,'w')
    fout.Close()

print('looking for',filename,'in',path)
if isSR and not os.path.exists(filename):
    if style == 'MC':
        if 'ABCD' in limitdir:
            masks = 'mask_Case1_D=1,mask_Case2_D=1,mask_Case3_D=1,mask_Case4_D=1,mask_Case1_C=1,mask_Case2_C=1,mask_Case3_C=1,mask_Case4_C=1,signalScale=1'
    else:
            masks = 'mask_Case1_D=1,mask_Case2_D=1,mask_Case3_D=1,mask_Case4_D=1,signalScale=1'

    print("Running Fit Diagnostics for initial workspace with SR channels masked: Mass =",mass)
    print('Command = combine -M FitDiagnostics -d workspace.root --saveWorkspace -n Masked --cminDefaultMinimizerStrategy 0 --setParameters '+masks)
    os.system('combine -M FitDiagnostics -d workspace.root --saveWorkspace -n Masked --cminDefaultMinimizerStrategy 0 --setParameters '+masks)
    #print "Running Fit Diagnostics for initial workspace with SR channels masked"
    #print 'Command = combine -M FitDiagnostics -d workspace.root --saveWorkspace --saveShapes --plots -n Masked --setParameters '+masks
    #os.system('combine -M FitDiagnostics -d workspace.root --saveWorkspace --saveShapes --plots -n Masked --setParameters '+masks)

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


print("Done!")
