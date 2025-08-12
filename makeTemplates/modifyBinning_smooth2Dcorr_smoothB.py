#!/usr/bin/python

import os,sys,time,math,fnmatch
from array import array
from numpy import linspace, sqrt
parent = os.path.dirname(os.getcwd())
sys.path.append(parent)
from ROOT import TFile, TH1D, TGraph, TGraphSmooth
start_time = time.time()

#cutString = 'splitLess/'#BB_templates/'
region = sys.argv[1]
postfix = sys.argv[2]
templateDir = os.getcwd()+'/templates'+region+'_'+postfix+'/'
print('templateDir:',templateDir)

smooth = False # KEEP FALSE. SMOOTH DONE IN THE LAST STEP IN A SEPARATE SCRIPT
rebin = False

#rebin = False
scaleLumi = False
#lumiScaleCoeffEl = 2530./2600.
#lumiScaleCoeffMu = 2621./2690.
#lumiscale = 2318./2258.

sigName = 'Bp' #MAKE SURE THIS WORKS FOR YOUR ANALYSIS PROPERLY!!!!!!!!!!!
upTag = 'Up'
downTag = 'Down'

def findfiles(path, filtre):
    for root, dirs, files in os.walk(path):
        for f in fnmatch.filter(files, filtre):
            yield os.path.join(root, f)

# add smoothing uncertainty after smoothing
rfiles = [file for file in findfiles(templateDir, 'templates_BpMass_ABCDnn_138fbfb.root')]
#rfiles = [file for file in findfiles(templateDir, 'templates_BpMass_ABCDnn_138fbfb_smoothedJJ_rebinned1_stat0p2_smoothedTV.root')]
tfile_smoothB = TFile(rfiles[0])
tfile_nom = TFile(rfiles[0].replace('smoothB','2Dsmooth'))
#tfile_nom = TFile(rfiles[0].replace('smoothB','2Dsmooth').replace('.root','_smoothedTV.root'))

checkscale = True

print("SMOOTHING FILE:",rfiles[0])
allHists = [k.GetName() for k in tfile_nom.GetListOfKeys() if '__smooth' not in k.GetName()]
majornames = [k.GetName() for k in tfile_nom.GetListOfKeys() if '__major' in k.GetName() and upTag not in k.GetName() and downTag not in k.GetName()]
print('Nominal major histograms:',majornames)

if rebin:
    outputRfile = TFile(rfiles[0].replace('.root','_smoothBUncert_rebinned.root'),'RECREATE')
else:
    outputRfile = TFile(rfiles[0].replace('.root','_smoothBUncert.root'),'RECREATE')
    
    
print("PROGRESS:")

# Save other histograms to file
for histName in allHists:
    hist = tfile_nom.Get(histName)
    hist.SetDirectory(0)
    outputRfile.cd()
    print(histName)
    if rebin:
        if (hist.GetNbinsX()%2)!=0:
            hist_new = TH1D(f'{histName}_new',f'{histName}',hist.GetNbinsX()-1,0,2500)
            hist_new.SetBinContent(1,hist.GetBinContent(1)+hist.GetBinContent(2))
            hist_new.SetBinError(1,sqrt(hist.GetBinError(1)**2+hist.GetBinError(2)**2))
            for i in range(3,hist.GetNbinsX()): # (nbins-1)+1
                hist_new.SetBinContent(i,hist.GetBinContent(i+1))
            hist_new.Rebin(2)
            hist_new.Write(histName)
            #print(f'Written {histName}')
            #continue
        else:
            hist.Rebin(2)
            hist.Write()
    else:
        #print(f'Written {histName}')
        hist.Write()

# Add smooth shift
for hist in majornames:
    histNom = tfile_nom.Get(hist).Clone(f'{hist}_nom')
    histDn = tfile_nom.Get(hist).Clone(f'{hist}_dn')
    histShift = tfile_smoothB.Get(hist).Clone(f'{hist}_shift') # full B nom as histUp
    histUp = tfile_smoothB.Get(hist).Clone(f'{hist}_up')
    
    # shift = up - nom
    histShift.Add(histNom,-1.0)
    
    # dn = nom - shift
    histDn.Add(histShift,-1.0)

    # if smooth:
    #     if 'jet' in hist:
    #         frac = 0.07 #0.05 
    #     else:
    #         frac = 0.07

    #     upratio = histUp.Clone('upratio')
    #     dnratio = histDn.Clone('dnratio')
    #     upratio.Divide(histNom)
    #     dnratio.Divide(histNom)
    #     upgraph = TGraph()
    #     dngraph = TGraph()
    #     for ibin in range(1,histDn.GetNbinsX()):
    #         upgraph.SetPoint(ibin-1, upratio.GetXaxis().GetBinCenter(ibin), upratio.GetBinContent(ibin))
    #         dngraph.SetPoint(ibin-1, dnratio.GetXaxis().GetBinCenter(ibin), dnratio.GetBinContent(ibin))
    #     upratio.Delete()
    #     dnratio.Delete()

    #     upsmooth = TGraphSmooth("normal")
    #     dnsmooth = TGraphSmooth("normal")
    #     upgraph = upsmooth.SmoothLowess(upgraph,"",frac)
    #     dngraph = dnsmooth.SmoothLowess(dngraph,"",frac)

    #     for ibin in range(1,histUp.GetNbinsX()+1):
    #         newupratio = upgraph.Eval(histUp.GetXaxis().GetBinCenter(ibin))
    #         newdnratio = dngraph.Eval(histDn.GetXaxis().GetBinCenter(ibin))
    #         centralval = histNom.GetBinContent(ibin)
    #         histUp.SetBinContent(ibin, max(0,newupratio*centralval))
    #         histDn.SetBinContent(ibin, max(0,newdnratio*centralval))

    if rebin:
        if (histUp.GetNbinsX()%2)!=0:
            histUp_new = TH1D(f'{hist}__smoothUp_new',f'{hist}__smoothUp',histUp.GetNbinsX()-1,0,2500)
            histDn_new = TH1D(f'{hist}__smoothDn_new',f'{hist}__smoothDn',histDn.GetNbinsX()-1,0,2500)
            histUp_new.SetBinContent(1,histUp.GetBinContent(1)+histUp.GetBinContent(2))
            histUp_new.SetBinError(1,sqrt(histUp.GetBinError(1)**2+histUp.GetBinError(2)**2))
            histDn_new.SetBinContent(1,histDn.GetBinContent(1)+histDn.GetBinContent(2))
            histDn_new.SetBinError(1,sqrt(histDn.GetBinError(1)**2+histDn.GetBinError(2)**2))
            
            for i in range(3,histUp.GetNbinsX()): # (nbins-1)+1
                histUp_new.SetBinContent(i,histUp.GetBinContent(i+1))
                histDn_new.SetBinContent(i,histDn.GetBinContent(i+1))
                
            histUp_new.Rebin(2)
            histDn_new.Rebin(2)
            outputRfile.cd()
            histUp_new.Write(f'{hist}__smoothBUp')
            histDn_new.Write(f'{hist}__smoothBDown')

            continue
        
        histUp.Rebin(2)
        histDn.Rebin(2)
        
    outputRfile.cd()
    histUp.Write(f'{hist}__smoothBUp')
    histDn.Write(f'{hist}__smoothBDown')
    
tfile_nom.Close()
tfile_smoothB.Close()
outputRfile.Close()
if rebin:
    print(f"Created {rfiles[0].replace('.root','_smoothBUncert_rebinned.root')}")
else:
    print(f"Created {rfiles[0].replace('.root','_smoothBUncert.root')}")
