#!/usr/bin/python

import os,sys,time,math,fnmatch
from array import array
from numpy import linspace
parent = os.path.dirname(os.getcwd())
sys.path.append(parent)
from ROOT import TFile, TH1D, TGraph, TGraphSmooth
start_time = time.time()

region = sys.argv[1] #'V2'
inputBin = 210
inputDir = f'templates{region}_Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST'
outputDir = f'{inputDir}_clipped'

newBinLo = 600
newBinHi = 2500

#filename = 'templates_BpMass_ABCDnn_138fbfb.root'
filename = 'templates_BpMass_ABCDnn_138fbfb_smoothedJJ_rebinned1_stat0p2_smoothedTV_smoothUncert.root'
inFile = TFile.Open(f'{inputDir}/{filename}', 'READ')
try:
    outFile = TFile.Open(f'{outputDir}/{filename}', 'RECREATE')
except:
    os.mkdir(outputDir)
    outFile = TFile.Open(f'{outputDir}/{filename}', 'RECREATE')

keyExample = inFile.GetListOfKeys()[0]
histExample = inFile.Get(keyExample.GetName())
print('Original hist axis range: ', histExample.GetXaxis().GetXmin(), histExample.GetXaxis().GetXmax(), histExample.GetNbinsX())
binWidth = (histExample.GetXaxis().GetXmax()-histExample.GetXaxis().GetXmin())/histExample.GetNbinsX()
print('Original bin width: ', binWidth)
newNbin = int((newBinHi - newBinLo)/binWidth)
print('New number of bins: ', newNbin)

for k in inFile.GetListOfKeys():
    histName = k.GetName()
    print(histName)
    hist_original = inFile.Get(histName)
    hist_new = TH1D(histName, histName, newNbin, newBinLo, newBinHi)
    for ibin in range(1,newNbin+1):
        binCenter = hist_new.GetBinCenter(ibin)
        original_binNo = hist_original.FindFixBin(hist_new.GetBinCenter(ibin))
        hist_new.SetBinContent(ibin, hist_original.GetBinContent(original_binNo))
    outFile.cd()
    hist_new.Write(histName)

print(f'Written all clipped histograms to {outFile}')


