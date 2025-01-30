# python3 makeDV2.py D2V 5
import os, sys
from ROOT import *
import numpy as np

makeRegion = sys.argv[1] #'D2V'
modifyBinTag = 'stat0p1' #'stat1p1' # 'stat0p2'
RB = sys.argv[2] #5
Nbins= 420
smoothTag = '_smoothed' #''
modifyHist = True
rebinHist = False

outDir = f'templates{makeRegion}_Oct2024_{Nbins}bins_valUpDn'
if not os.path.exists(outDir):
    os.makedirs(outDir)

outFileDV2 = TFile.Open(f'{outDir}/templates_BpMass_ABCDnn_138fbfb_rebinned{RB}_{modifyBinTag}{smoothTag}.root', 'RECREATE')

def touchupHist(region):
    inFileName = f'templates{region}_Oct2024_{Nbins}bins/templates_BpMass_ABCDnn_138fbfb_rebinned{RB}_{modifyBinTag}{smoothTag}.root'
    inFile = TFile.Open(inFileName, 'READ')

    if modifyHist:
        outFileName = f'templates{region}_Oct2024_{Nbins}bins/templates_BpMass_ABCDnn_138fbfb_modified.root'
        outFile = TFile.Open(outFileName, 'RECREATE')
    if rebinHist:
        outFile = TFile.Open(f'templates{region}_Oct2024_{Nbins}bins/templates_BpMass_ABCDnn_138fbfb_rebin42.root', 'RECREATE')

    print(f'Opened {inFileName}...')
    for hist in inFile.GetListOfKeys():
        hist_out = inFile.Get(hist.GetName()).Clone()

        if modifyHist:
            if 'major' in hist.GetName():
                nBins = hist_out.GetNbinsX()
                for i in range(nBins):
                    if hist_out.GetBinContent(i)<0:
                        print(f'Bin{i} in {hist.GetName()} has negative content. Setting to 0...')
                        hist_out.SetBinContent(i, 0)
                    #hist_out.SetBinError(i, np.sqrt(hist_out.GetBinContent(i))) # for creation bin diff from fit bin
            outFile.WriteObject(hist_out, hist.GetName())
        if rebinHist:
            hist_out.Rebin(10) #sanity check
            outFile.WriteObject(hist_out, hist.GetName())

        outFileDV2.WriteObject(hist_out, hist.GetName())
            
    inFile.Close()
    if modifyHist or rebinHist:
        outFile.Close()
        os.system(f'rm {inFileName}')
        os.system(f'mv {outFileName} {inFileName}')
        

if makeRegion=="DV2":
    touchupHist("D")
    touchupHist("V2")
elif makeRegion=="D2V":
    touchupHist("D2")
    touchupHist("V")
else:
    print("Invalid makeRegion!")

outFileDV2.Close()
