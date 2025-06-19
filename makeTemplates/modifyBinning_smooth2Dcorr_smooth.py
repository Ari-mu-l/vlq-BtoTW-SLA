#!/usr/bin/python

import os,sys,time,math,fnmatch
from array import array
from numpy import linspace
parent = os.path.dirname(os.getcwd())
sys.path.append(parent)
from ROOT import TFile, TH1, TGraph, TGraphSmooth
start_time = time.time()

#cutString = 'splitLess/'#BB_templates/'
region = sys.argv[1]
postfix = sys.argv[2]
templateDir = os.getcwd()+'/templates'+region+'_'+postfix+'/'
print('templateDir:',templateDir)

smooth = True

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
#rfiles = [file for file in findfiles(templateDir, 'templates_BpMass_ABCDnn_138fbfb_rebinned1_stat0p2_smoothedTV.root')]
rfiles = [file for file in findfiles(templateDir, 'templates_BpMass_ABCDnn_138fbfb_smoothedJJ_rebinned1_stat0p2_smoothedTV.root')]
tfile = TFile(rfiles[0])

checkscale = True

print("SMOOTHING FILE:",rfiles[0])
allHists = [k.GetName() for k in tfile.GetListOfKeys() if '__smooth' not in k.GetName()]
majornames = [k.GetName() for k in tfile.GetListOfKeys() if '__major' in k.GetName() and upTag not in k.GetName() and downTag not in k.GetName()]
print('Nominal major histograms:',majornames)
    
outputRfile = TFile(rfiles[0].replace('.root','_smoothUncert.root'),'RECREATE')
    
print("PROGRESS:")

# Save other histograms to file
for hist in allHists:
    hist =  tfile.Get(hist)
    hist.SetDirectory(0)
    outputRfile.cd()
    hist.Write()

# Add smooth shift
for hist in majornames:
    histNom = tfile.Get(hist).Clone('nom')
    histDn = tfile.Get(hist).Clone('dn')
    histShift = tfile.Get(f'{hist}__smoothUp').Clone('shift')
    histUp = tfile.Get(f'{hist}__smoothUp').Clone('up')
    
    # shift = up - nom
    histShift.Add(histNom,-1.0)
    
    # dn = nom - shift
    histDn.Add(histShift,-1.0)

    if smooth:
        if 'jet' in hist:
            frac = 0.05
        else:
            frac = 0.04

        upratio = histUp.Clone('upratio')
        dnratio = histDn.Clone('dnratio')
        upratio.Divide(histNom)
        dnratio.Divide(histNom)
        upgraph = TGraph()
        dngraph = TGraph()
        for ibin in range(1,histDn.GetNbinsX()):
            upgraph.SetPoint(ibin-1, upratio.GetXaxis().GetBinCenter(ibin), upratio.GetBinContent(ibin))
            dngraph.SetPoint(ibin-1, dnratio.GetXaxis().GetBinCenter(ibin), dnratio.GetBinContent(ibin))
        upratio.Delete()
        dnratio.Delete()

        upsmooth = TGraphSmooth("normal")
        dnsmooth = TGraphSmooth("normal")
        upgraph = upsmooth.SmoothLowess(upgraph,"",frac)
        dngraph = dnsmooth.SmoothLowess(dngraph,"",frac)

        for ibin in range(1,histUp.GetNbinsX()+1):
            newupratio = upgraph.Eval(histUp.GetXaxis().GetBinCenter(ibin))
            newdnratio = dngraph.Eval(histDn.GetXaxis().GetBinCenter(ibin))
            centralval = histNom.GetBinContent(ibin)
            histUp.SetBinContent(ibin, max(0,newupratio*centralval))
            histDn.SetBinContent(ibin, max(0,newdnratio*centralval))
        
    outputRfile.cd()
    histUp.Write(f'{hist}__smoothUp')
    histDn.Write(f'{hist}__smoothDown')

outputRfile.Close()
print(f"Created {rfiles[0].replace('.root','_smoothUncert.root')}")
