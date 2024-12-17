#!/usr/bin/python

import os,sys,time,math,fnmatch
parent = os.path.dirname(os.getcwd())
sys.path.append(parent)
from ROOT import *
start_time = time.time()

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Run as:
# > python modifyBinning.py
# 
# Optional arguments:
# -- statistical uncertainty threshold
#
# Notes:
# -- Finds certain root files in a given directory and rebins all histograms in each file
# -- A selection of subset of files in the input directory can be done below under "#Setup the selection ..."
# -- A custom binning choice can also be given below and this choice can be activated by giving a stat unc 
#    threshold larger than 100% (>1.) in the argument
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

#cutString = 'splitLess/'#BB_templates/'
region = sys.argv[1]
templateDir = os.getcwd()+'/templates'+region+'_Oct2024_420bins/'

doTwoSided = True
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

#Setup the selection of the files to be rebinned: HiggsTagTemplate_tW1p0_bZ0p0_bH0p0_BBM1800.root
rfiles = [file for file in findfiles(templateDir, '*.root') if 'rebinned' in file and 'stat0p2' in file and 'smoothed' not in file and 'plots' not in file] 
tfile = TFile(rfiles[0])

iRfile=0
yieldsAll = {}
yieldsErrsAll = {}
yieldsSystErrsAll = {}
checkscale = True
for rfile in rfiles: 
    print("SMOOTHING FILE:",rfile)
    tfiles = {}
    outputRfiles = {}
    tfiles[iRfile] = TFile(rfile)
    allhists = [hist.GetName() for hist in tfiles[iRfile].GetListOfKeys()]

    outputRfiles[iRfile] = TFile(rfile.replace('.root','_smoothed.root'),'RECREATE')

    print("PROGRESS:")
    rebinnedHists = {}
    for hist in allhists:

        rebinnedHists[hist]=tfiles[iRfile].Get(hist)
        rebinnedHists[hist].SetDirectory(0)

        if doTwoSided:
            if 'val' not in hist and 'train' not in hist:
                rebinnedHists[hist].Write()
        else:
            if 'valUp' not in hist and 'train' not in hist:
                rebinnedHists[hist].Write()   

    valUphists = [k.GetName() for k in tfiles[iRfile].GetListOfKeys() if '__val' in k.GetName() and upTag in k.GetName()]
    trainUphists = [k.GetName() for k in tfiles[iRfile].GetListOfKeys() if '__train' in k.GetName() and upTag in k.GetName()]
    
    for hist in valUphists:
        print('\t',hist)

        frac = 0.1
        #if 'Wjet' in hist: frac = 0.3
        #if 'Tjet' in hist: frac = 0.3

        up = rebinnedHists[hist].Clone()
            
        central = rebinnedHists[hist[:hist.find('__val')]] # from the beginning to __je
        upratio = up.Clone('upratio')
        upratio.Divide(central)
        upgraph = TGraph()

        for ibin in range(1,up.GetNbinsX()+1):
            upgraph.SetPoint(ibin-1, upratio.GetXaxis().GetBinCenter(ibin), upratio.GetBinContent(ibin))
        
        #upratio.Delete()

        upsmooth = TGraphSmooth("normal")
        upgraph = upsmooth.SmoothLowess(upgraph,"",frac)

        for ibin in range(1,up.GetNbinsX()+1):
            newupratio = upgraph.Eval(up.GetXaxis().GetBinCenter(ibin))
            centralval = central.GetBinContent(ibin)
            up.SetBinContent(ibin, newupratio*centralval)
            if 'Tjet' in hist:
                print('NewUp is ',newupratio,', changed from',upratio.GetBinContent(ibin))

        if central.Integral() > 0 and up.Integral() > 0:
            up.Write()
        else:
            rebinnedHists[hist].Write()
            
        if doTwoSided:
            down = rebinnedHists[hist.replace(upTag,downTag)].Clone()
            dnratio = down.Clone('dnratio')
            dnratio.Divide(central)
            dngraph = TGraph()
            
            for ibin in range(1,down.GetNbinsX()+1):
                dngraph.SetPoint(ibin-1, dnratio.GetXaxis().GetBinCenter(ibin), dnratio.GetBinContent(ibin))

            dnsmooth = TGraphSmooth("normal")
            dngraph = dnsmooth.SmoothLowess(dngraph,"",frac)

            for ibin in range(1,down.GetNbinsX()+1):
                newdnratio = dngraph.Eval(down.GetXaxis().GetBinCenter(ibin))
                centralval = central.GetBinContent(ibin)
                down.SetBinContent(ibin, max(0,newdnratio*centralval))
                if 'Tjet' in hist:
                    print('NewDown is ',newdnratio,', changed from',dnratio.GetBinContent(ibin))
            
            if central.Integral() > 0 and down.Integral() > 0:
                down.Write()

    for hist in trainUphists:
        print('\t',hist)

        frac = 0.1

        up = rebinnedHists[hist].Clone()
        down = rebinnedHists[hist.replace(upTag,downTag)].Clone()
        central = rebinnedHists[hist[:hist.find('__train')]] # from the beginning to __je

        # for ibin in range(1,up.GetNbinsX()+1):
        #     if down.GetBinContent(ibin) < 0:
        #         down.SetBinContent(ibin,0)
        
        upratio = up.Clone('upratio')
        upratio.Divide(central)
        dnratio = down.Clone('dnratio')
        dnratio.Divide(central)
        upgraph = TGraph()
        dngraph = TGraph()
        for ibin in range(1,up.GetNbinsX()+1):
            upgraph.SetPoint(ibin-1, upratio.GetXaxis().GetBinCenter(ibin), upratio.GetBinContent(ibin))
            dngraph.SetPoint(ibin-1, dnratio.GetXaxis().GetBinCenter(ibin), dnratio.GetBinContent(ibin))
        upratio.Delete()
        dnratio.Delete()

        upsmooth = TGraphSmooth("normal")
        dnsmooth = TGraphSmooth("normal")

        upgraph = upsmooth.SmoothLowess(upgraph,"",frac)
        dngraph = dnsmooth.SmoothLowess(dngraph,"",frac)

        for ibin in range(1,up.GetNbinsX()+1):
            newupratio = upgraph.Eval(up.GetXaxis().GetBinCenter(ibin))
            newdnratio = dngraph.Eval(down.GetXaxis().GetBinCenter(ibin))
            centralval = central.GetBinContent(ibin)
            up.SetBinContent(ibin, max(0,newupratio*centralval))
            down.SetBinContent(ibin, max(0,newdnratio*centralval))

        if central.Integral() > 0 and up.Integral() > 0:
            up.Write()
            down.Write()
        else:
            rebinnedHists[hist].Write()
            rebinnedHists[hist.replace(upTag,downTag)].Write()

    tfiles[iRfile].Close()
    outputRfiles[iRfile].Close()
    iRfile+=1
tfile.Close()
print(">> Smoothing Done!")

print("--- %s minutes ---" % (round((time.time() - start_time)/60,2)))



