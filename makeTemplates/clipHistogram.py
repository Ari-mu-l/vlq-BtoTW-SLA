#!/usr/bin/python

# python3 clipHistogram.py D _smoothedJJ_rebinned1_stat0p2_smoothedTV_smooth2DUncert
import os,sys,time,math,fnmatch
from array import array
from numpy import linspace
parent = os.path.dirname(os.getcwd())
sys.path.append(parent)
from ROOT import TFile, TH1D, TGraph, TGraphSmooth
start_time = time.time()

region = sys.argv[1] #'V2'
if len(sys.argv)>2:
    postFix = sys.argv[2]
else:
    postFix = ''
inputDir = f'templates{region}_Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST' # b-associated
#inputDir = f'templates{region}_Jan2025BprimeT'#_rebinned' #_C2' # t-associated

rebin = True
byMassRange = False
byCase = False
caseList = ['C1', 'C2', 'C3', 'C4']
#caseList = ['C1C2']
tagList = {'C1': 'tagTjet',
           'C2': 'tagWjet',
           'C3': 'untagTlep',
           'C4': 'untagWlep',
           }

filename = f'templates_BpMass_ABCDnn_138fbfb{postFix}.root'
inFile = TFile.Open(f'{inputDir}/{filename}', 'READ')

if rebin:
    rebin_factor = 2
    outputDir = f'{inputDir}_rebinned{rebin_factor}'
    if not os.path.isdir(outputDir):
        os.mkdir(outputDir)
    outFile = TFile.Open(f'{outputDir}/{filename}', 'RECREATE')

    for k in inFile.GetListOfKeys():
        histName = k.GetName()
        hist_original = inFile.Get(histName).Clone(histName)
        hist_original.Rebin(rebin_factor)
        outFile.cd()
        hist_original.Write(histName)

    print(f'Written all clipped histograms to {outFile}')
    outFile.Close()  
elif byMassRange:
    outputDir = f'{inputDir}_clipped'
    if not os.path.isdir(outputDir):
        os.mkdir(outputDir)
    outFile = TFile.Open(f'{outputDir}/{filename}', 'RECREATE')
        
    newBinLo = 500
    newBinHi = 2500
    for k in inFile.GetListOfKeys():
        histName = k.GetName()
        hist_original = inFile.Get(histName)
        nbins = hist_original.GetXaxis().GetNbins()
        binEdges = []
        for ibin in range(1,nbins+1):
            if hist_original.GetBinLowEdge(ibin)>=newBinLo and hist_original.GetBinLowEdge(ibin)<newBinHi:
                binEdges.append(hist_original.GetBinLowEdge(ibin))
        if newBinLo not in binEdges:
            sys.exit(f'{newBinLo} not in one of the bin edges of {histName}!')
        binEdges.append(newBinHi)
        #binEdges.append(2500)

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
    
elif byCase:
    for case in caseList:
        if not os.path.isdir(f'{inputDir}_{case}'):
            os.mkdir(f'{inputDir}_{case}')
        outFileDir={}
        outFileDir[case] = TFile.Open(f'{inputDir}_{case}/{filename}', 'RECREATE')
        
        for k in inFile.GetListOfKeys():
            histName = k.GetName()
            if tagList[case] in histName:
                hist_original = inFile.Get(histName).Clone(histName)
                outFileDir[case].cd()
                hist_original.Write(histName)
        
        print(f'Written all clipped histograms to {outFileDir[case]}')
        outFileDir[case].Close()
else:
    sys.exit('Exit without doing anything... Check the setting.')



