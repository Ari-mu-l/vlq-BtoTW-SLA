#!/usr/bin/python

import os,sys,time,math,fnmatch
from array import array
from numpy import linspace
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
templateDir = os.getcwd()+'/templates'+region+'_Jan2025/'

rebin = False
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
rfiles = [file for file in findfiles(templateDir, '*.root') if 'rebinned' in file and 'stat0p2' in file and 'valUpDn' in file and 'smoothed' not in file and 'plots' not in file] #'corr' in file 
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

    outputRfiles[iRfile] = TFile(rfile.replace('.root','_smoothed_TVJJ.root'),'RECREATE')

    if rebin:
        #binslist = [400,425,450,475,500,525,550,575,600,625,650,675,700,725,750,775,800]
        #binslist = [500,525,550,575,600,625,650,675,700,725,750,775,800]
        binslist = linspace(400, 2350, 79).tolist()
        xbins = array('d', binslist)
        print('Will rebin to',xbins)
    
    print("PROGRESS:")
    rebinnedHists = {}
    for hist in allhists:

        rebinnedHists[hist]=tfiles[iRfile].Get(hist).Clone()
        rebinnedHists[hist].SetDirectory(0)
        
        if 'val' not in hist and 'train' not in hist and 'jec' not in hist and 'jer' not in hist:
            if rebin and 'untagWlep' in hist:
                tmphist = rebinnedHists[hist].Clone()
                rebinnedHists[hist] = tmphist.Rebin(len(xbins)-1,hist,xbins)

            rebinnedHists[hist].Write()

    valUphists = [k.GetName() for k in tfiles[iRfile].GetListOfKeys() if '__val' in k.GetName() and upTag in k.GetName()]
    trainUphists = [k.GetName() for k in tfiles[iRfile].GetListOfKeys() if '__train' in k.GetName() and upTag in k.GetName()]
    jecUphists = [k.GetName() for k in tfiles[iRfile].GetListOfKeys() if '__jec' in k.GetName() and upTag in k.GetName()]
    jerUphists = [k.GetName() for k in tfiles[iRfile].GetListOfKeys() if '__jer' in k.GetName() and upTag in k.GetName()]

    for hist in valUphists:
        # _corr files pre-smoothed for that correction
        if 'valUpDn' not in rfile:
            rebinnedHists[hist].Write()
            rebinnedHists[hist.replace(upTag,downTag)].Write()            
            continue
        
        print('\t',hist)

        frac = 0.1
        #if 'Wjet' in hist: frac = 0.3
        #if 'Tjet' in hist: frac = 0.3

        up = rebinnedHists[hist].Clone()
        down = rebinnedHists[hist.replace(upTag,downTag)].Clone()
        central = tfiles[iRfile].Get(hist[:hist.find('__val')]).Clone() # from the beginning to __je
        upratio = up.Clone('upratio')
        upratio.Divide(central)
        dnratio = down.Clone('dnratio')
        dnratio.Divide(central)
        upgraph = TGraph()
        dngraph = TGraph()
        for ibin in range(1,up.GetNbinsX()+1):
            upgraph.SetPoint(ibin-1, upratio.GetXaxis().GetBinCenter(ibin), upratio.GetBinContent(ibin))
            dngraph.SetPoint(ibin-1, dnratio.GetXaxis().GetBinCenter(ibin), dnratio.GetBinContent(ibin))
                        
        #upratio.Delete()
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
            #if 'Tjet' in hist:
            #    print('NewUp is ',newupratio,', changed from',upratio.GetBinContent(ibin))

        if central.Integral() > 0 and up.Integral() > 0:
            if rebin and 'untagWlep' in hist: 
                up = up.Rebin(len(xbins)-1,hist,xbins)
                down = down.Rebin(len(xbins)-1,hist.replace(upTag,downTag),xbins)
            up.Write()
            down.Write()
        else:
            rebinnedHists[hist].Write()
            rebinnedHists[hist.replace(upTag,downTag)].Write()

    for hist in trainUphists:
        print('\t',hist)

        frac = 0.1

        up = rebinnedHists[hist].Clone()
        down = rebinnedHists[hist.replace(upTag,downTag)].Clone()
        central = tfiles[iRfile].Get(hist[:hist.find('__train')]).Clone() # from the beginning to __je
        #central = rebinnedHists[hist[:hist.find('__train')]] # from the beginning to __je

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
            if rebin and 'untagWlep' in hist: 
                up = up.Rebin(len(xbins)-1,hist,xbins)
                down = down.Rebin(len(xbins)-1,hist.replace(upTag,downTag),xbins)
            up.Write()
            down.Write()
        else:
            rebinnedHists[hist].Write()
            rebinnedHists[hist.replace(upTag,downTag)].Write()

    print('\t JEC and JER...')
    for hist in jecUphists+jerUphists:
        #print('\t',hist)

        frac = 0.1

        up = rebinnedHists[hist].Clone()
        down = rebinnedHists[hist.replace(upTag,downTag)].Clone()
        central = tfiles[iRfile].Get(hist[:hist.find('__je')]).Clone() # from the beginning to __je
        #central = rebinnedHists[hist[:hist.find('__je')]] # from the beginning to __je

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
            if rebin and 'untagWlep' in hist:
                up = up.Rebin(len(xbins)-1,hist,xbins)
                down = down.Rebin(len(xbins)-1,hist.replace(upTag,downTag),xbins)
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



