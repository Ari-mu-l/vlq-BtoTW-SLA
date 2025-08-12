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

smooth = True
rebin = False

scaleLumi = False
#lumiScaleCoeffEl = 2530./2600.
#lumiScaleCoeffMu = 2621./2690.
#lumiscale = 2318./2258.

tfile_smoothfrac = TFile(f'{templateDir}/templates_BpMass_ABCDnn_138fbfb_smoothedJJ_rebinned1_stat0p2_smoothedTV_smoothfracUncert.root')
tfile_smooth2D   = TFile(f'{templateDir}/templates_BpMass_ABCDnn_138fbfb_smoothedJJ_rebinned1_stat0p2_smoothedTV_smooth2DUncert.root')

checkscale = True

print("SMOOTHFRAC FILE:",f'{templateDir}/templates_BpMass_ABCDnn_138fbfb_smoothedJJ_rebinned1_stat0p2_smoothedTV_smoothfracUncert.root')
print("SMOOTH2D FILE:",f'{templateDir}/templates_BpMass_ABCDnn_138fbfb_smoothedJJ_rebinned1_stat0p2_smoothedTV_smooth2DUncert.root')
allHists = [k.GetName() for k in tfile_smooth2D.GetListOfKeys() if '__smooth' not in k.GetName()]
#majornames = [k.GetName() for k in tfile_smooth2D.GetListOfKeys() if '__major' in k.GetName() and 'Up' not in k.GetName() and 'Down' not in k.GetName()]
smooth2DHists = [k.GetName() for k in tfile_smooth2D.GetListOfKeys() if ('__smooth2D' in k.GetName())]
smoothfracHists = [k.GetName() for k in tfile_smoothfrac.GetListOfKeys() if ('__smoothfrac' in k.GetName())]
#print('Nominal major histograms:',majornames)

if rebin:
    outputRfile = TFile(f'{templateDir}/templates_BpMass_ABCDnn_138fbfb_smoothedJJ_rebinned1_stat0p2_smoothedTV_smooth2DfracUncert_rebinned.root','RECREATE')
else:
    outputRfile = TFile(f'{templateDir}/templates_BpMass_ABCDnn_138fbfb_smoothedJJ_rebinned1_stat0p2_smoothedTV_smooth2DfracUncert.root','RECREATE')
    
    
print("PROGRESS:")

# Save other histograms to file
for histName in allHists:
    hist = tfile_smoothfrac.Get(histName)
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

for histName in smooth2DHists:
    hist = tfile_smooth2D.Get(histName)
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
        else:
            hist.Rebin(2)
            hist.Write(histName)
    else:
        hist.Write(histName)

for histName in smoothfracHists:
    hist = tfile_smoothfrac.Get(histName)
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
        else:
            hist.Rebin(2)
            hist.Write(histName)
    else:
        hist.Write(histName)
    
tfile_smoothfrac.Close()
tfile_smooth2D.Close()

outputRfile.Close()
if rebin:
    print(f'{templateDir}/templates_BpMass_ABCDnn_138fbfb_smoothedJJ_rebinned1_stat0p2_smoothedTV_smooth2DfracUncert_rebinned.root')
else:
    print(f'{templateDir}/templates_BpMass_ABCDnn_138fbfb_smoothedJJ_rebinned1_stat0p2_smoothedTV_smooth2DfracUncert.root')

