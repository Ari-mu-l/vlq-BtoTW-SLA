#!/usr/bin/python

import os,sys,time,math,fnmatch
from array import array
import numpy as np
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
symmetrize = True

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
#smoothFrac = ['0p01','0p02','0p03','0p04','0p05','0p06','0p07','0p08','0p09']
#smoothFrac = ['0p01','0p045','0p18','0p035','0p14']
#smoothFrac = ['0p005','0p01','0p02','0p035','0p14']
smoothFrac = ['0p01','0p005','0p02','0p03','0p12']
#smoothFrac = ['0p01','0p03','0p12']
#smoothFrac = ['0p01','0p025','0p1']
# nominal file
rfiles = [f'{templateDir}/templates_BpMass_ABCDnn_138fbfb_smoothedJJ_rebinned1_stat0p2_smoothedTV.root']
tfile = TFile(rfiles[0])

checkscale = True

print("SMOOTHING FILE:",rfiles[0])
allHists = [k.GetName() for k in tfile.GetListOfKeys() if '__smooth' not in k.GetName()]
majornames = [k.GetName() for k in tfile.GetListOfKeys() if '__major' in k.GetName() and upTag not in k.GetName() and downTag not in k.GetName()]
print('Nominal major histograms:',majornames)
    
outputRfile = TFile(rfiles[0].replace('.root','_smoothUncert.root'),'RECREATE')
    
print("PROGRESS:")

# Save other histograms to file
for histName in allHists:
    hist =  tfile.Get(histName)
    hist.SetDirectory(0)
    outputRfile.cd()
    hist.Write()

# get lists of major histograms with different smoothing
alternativeHists = {}
for frac in smoothFrac:
    rfile = TFile(f'{templateDir[:-1]}_{frac}/templates_BpMass_ABCDnn_138fbfb_smoothedJJ_rebinned1_stat0p2_smoothedTV.root')
    alternativeHists[frac] = {}
    for histName in majornames:
        hist = rfile.Get(histName)
        hist.SetDirectory(0)
        alternativeHists[frac][histName.split('_')[4]] = hist
    rfile.Close()

# get smooth envelope
nominal_smoothFrac = {#"V2":{"tagTjet":"0p09", "tagWjet":"0p09", "untagTlep": "0p07", "untagWlep": "0p07"},
                      "V2":{"tagTjet":"0p06", "tagWjet":"0p06", "untagTlep": "0p06", "untagWlep": "0p06"},
                      "D":{"tagTjet":"0p06", "tagWjet":"0p06", "untagTlep": "0p06", "untagWlep": "0p06"}}

shiftHists = {}
for histName in majornames:
    histNom = tfile.Get(histName).Clone('nom')
    tag = histName.split('_')[4] # tagTjet, tagWjet, untagTlep, untagWlep
    Nbins = alternativeHists['0p01'][tag].GetNbinsX()
    binDn = 999999 * np.ones(Nbins)
    binUp = -999 * np.ones(Nbins)
    for frac in smoothFrac:
        if frac==nominal_smoothFrac[region][tag]:
            print(f'Frac {frac} used in nominal. Skip.')
        else:
            hist = alternativeHists[frac][tag]
            for i in range(1,Nbins+1):
                binContent = hist.GetBinContent(i)
                if binContent<binDn[i-1]: # histogram bin starts with 1. numpy array starts with 0.
                    binDn[i-1] = binContent
                if binContent>binUp[i-1]:
                    binUp[i-1] = binContent

    # fill shift histograms
    # envelope method
    #histUp = tfile.Get(f'{histName}__smoothUp').Clone(f'{tag}_up')
    #histDn = tfile.Get(f'{histName}__smoothDown').Clone(f'{tag}_dn')

    #for i in range(1,Nbins+1):
    #    histUp.SetBinContent(i,binUp[i-1])
    #    histDn.SetBinContent(i,binDn[i-1])
        
    # alternative smoothing method 1: down = 0.01, up = 0.09
    #histDn = alternativeHists["0p01"][tag].Clone(f'{tag}_dn')
    #histUp = alternativeHists["0p09"][tag].Clone(f'{tag}_up')

    # alternative smoothing method 2: down = frac/2, up = frac*2
    # 0.09->0.045,0.18, 0.07->0.035,0.14
    histDn = alternativeHists[str(float(nominal_smoothFrac[region][tag].replace('p','.'))/2).replace('.','p')][tag].Clone(f'{tag}_dn')
    histUp = alternativeHists[str(float(nominal_smoothFrac[region][tag].replace('p','.'))*2).replace('.','p')][tag].Clone(f'{tag}_up')

            
    # treat region D taile differently
    if region=="D" and "jet" in tag:
        print(f'Ideal frac for {tag} is 0.01.')
        histDn_tail = alternativeHists['0p005'][tag].Clone(f'{tag}_dn')
        histUp_tail = alternativeHists['0p02'][tag].Clone(f'{tag}_up')

        #print(f'Ideal frac for {tag} is None.')
        #histDn_tail = tfile.Get(histName).Clone(f'{tag}_dn')
        #histUp_tail = tfile.Get(histName).Clone(f'{tag}_up')

        for ibin in range(histUp.GetXaxis().FindFixBin(700),histUp.GetNbinsX()+1):
            histUp.SetBinContent(ibin, histUp_tail.GetBinContent(ibin))
            histDn.SetBinContent(ibin, histDn_tail.GetBinContent(ibin))


    if symmetrize:
        for i in range(1,Nbins+1):
            ################################################
            # symmetrize method1: symmetrize by enveloping #
            ################################################
            # # shift histogram one-sided: up all up, down all down.
            # if abs(histDn.GetBinContent(i) - histNom.GetBinContent(i)) < abs(histUp.GetBinContent(i) - histNom.GetBinContent(i)):
            #     shift = abs(histUp.GetBinContent(i) - histNom.GetBinContent(i))
            # else:
            #     shift = abs(histDn.GetBinContent(i) - histNom.GetBinContent(i))
            # histDn.SetBinContent(i, histNom.GetBinContent(i) - shift)
            # histUp.SetBinContent(i, histNom.GetBinContent(i) + shift)

            ################################################
            # symmetrize method2: symmetrize by enveloping #
            ################################################
            # # shift histogram two-sided: up fluctuates, down fluctuates
            # if abs(histDn.GetBinContent(i) - histNom.GetBinContent(i)) < abs(histUp.GetBinContent(i) - histNom.GetBinContent(i)):
            #     shift = histUp.GetBinContent(i) - histNom.GetBinContent(i)
            # else:
            #     shift = histDn.GetBinContent(i) - histNom.GetBinContent(i)
            # histDn.SetBinContent(i, histNom.GetBinContent(i) - shift)
            # histUp.SetBinContent(i, histNom.GetBinContent(i) + shift)

            ########################################
            # symmetrize method3: symmetrize by up #
            ########################################
            shift = histUp.GetBinContent(i) - histNom.GetBinContent(i)
            histDn.SetBinContent(i, histNom.GetBinContent(i) - shift)
            
            ########################################
            # symmetrize method4: symmetrize by dn #
            ########################################
            #shift = histNom.GetBinContent(i) - histDn.GetBinContent(i)
            #histUp.SetBinContent(i, histNom.GetBinContent(i) + shift)

    if smooth and region=='D' and 'jet' in histName:
        frac = 0.04
        # else:
        #     frac = 0.04

        #histNom = tfile.Get(histName).Clone('nom')

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
    histUp.Write(f'{histName}__smoothUp')
    histDn.Write(f'{histName}__smoothDown')

outputRfile.Close()
print(f"Created {rfiles[0].replace('.root','_smoothUncert.root')}")
