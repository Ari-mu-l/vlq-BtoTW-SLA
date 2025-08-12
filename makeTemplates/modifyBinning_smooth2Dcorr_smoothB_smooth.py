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

upTag = 'Up'
downTag = 'Down'

def findfiles(path, filtre):
    for root, dirs, files in os.walk(path):
        for f in fnmatch.filter(files, filtre):
            yield os.path.join(root, f)

# add smoothing uncertainty after smoothing
rfiles = [file for file in findfiles(templateDir, 'templates_BpMass_ABCDnn_138fbfb_smoothBUncert_smoothedJJ_rebinned1_stat0p2_smoothedTV.root')]

tfile = TFile(rfiles[0])

print("SMOOTHING FILE:",rfiles[0])
allHists = [k.GetName() for k in tfile.GetListOfKeys() if '__smooth' not in k.GetName()]
nomHists = [k.GetName() for k in tfile.GetListOfKeys() if (upTag not in k.GetName()) and (downTag not in k.GetName()) and ('major' in k.GetName())]

outputRfile = TFile(rfiles[0].replace('.root','_smoothedB.root'),'RECREATE')
    
    
print("PROGRESS:")

# Save other histograms to file
for histName in allHists:
    hist = tfile.Get(histName)
    hist.SetDirectory(0)
    outputRfile.cd()
    hist.Write()

# Add smooth shift
for hist in nomHists:
    histNom = tfile.Get(hist).Clone(f'{hist}_nom')
    histUp = tfile.Get(f'{hist}__smoothBUp').Clone(f'{hist}_up')
    histShift =  tfile.Get(f'{hist}__smoothBUp').Clone(f'{hist}_up')
    histDn = tfile.Get(f'{hist}').Clone(f'{hist}_dn')

    # recenter
    histShift.Add(histNom,-1.0)
    histDn.Add(histShift,-1.0)

    frac = 0.05
    
    # if 'jet' in hist:
    #     frac = 0.07 #0.05 
    # else:
    #     frac = 0.07

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
    histUp.Write(f'{hist}__smoothBUp')
    histDn.Write(f'{hist}__smoothBDown')
    
tfile.Close()
outputRfile.Close()

print(f"Created {rfiles[0].replace('.root','_smoothedB.root')}")
