#!/usr/bin/python

import os,sys,time,math,fnmatch
from array import array
from numpy import linspace
parent = os.path.dirname(os.getcwd())
sys.path.append(parent)
from ROOT import TFile, TH1D, TGraph, TGraphSmooth
start_time = time.time()

region = sys.argv[1] #'V2'
inputDir = f'templates{region}_Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST'
outputDir = f'{inputDir}_clipped'

newBinLo = 600
newBinHi = 2500

filename = 'templates_BpMass_ABCDnn_138fbfb_smoothedJJ_rebinned1_stat0p2_smoothedTV_smoothUncert.root'
inFile = TFile.Open(f'{inputDir}/{filename}', 'READ')
try:
    outFile = TFile.Open(f'{outputDir}/{filename}', 'RECREATE')
except:
    os.mkdir(outputDir)
    outFile = TFile.Open(f'{outputDir}/{filename}', 'RECREATE')

for k in inFile.GetListOfKeys():
    histName = k.GetName()
    hist_original = inFile.Get(histName)
    nbins = hist_original.GetXaxis().GetNbins()
    binEdges = []
    for ibin in range(1,nbins+1):
        if hist_original.GetBinLowEdge(ibin)>=newBinLo:
            binEdges.append(hist_original.GetBinLowEdge(ibin))
    if newBinLo not in binEdges:
        sys.exit(f'{newBinLo} not in one of the bin edges of {histName}!')
    binEdges.append(2500)
    
    hist_new = TH1D(histName, histName, len(binEdges)-1, array('d',binEdges))
    for ibin in range(1,nbins+1):
        binCenter = hist_new.GetBinCenter(ibin)
        original_binNo = hist_original.FindFixBin(hist_new.GetBinCenter(ibin))
        hist_new.SetBinContent(ibin, hist_original.GetBinContent(original_binNo))
        hist_new.SetBinError(ibin, hist_original.GetBinError(original_binNo))
    outFile.cd()
    hist_new.Write(histName)

print(f'Written all clipped histograms to {outFile}')
outFile.Close()


