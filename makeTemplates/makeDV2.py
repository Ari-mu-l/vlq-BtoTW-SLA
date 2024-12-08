import os
from ROOT import *
import numpy as np

makeRegion = 'D2V'
modifyBinTag = 'stat1p1' #'stat1p1' # 'stat0p2'
modifyHist = False
rebinHist = False

outDir = 'templates{makeRegion}_Oct2024_42bins'
if not os.path.exists(outDir):
    os.makedirs(outDir)

outFileDV2 = TFile.Open(f'{outDir}/templates_BpMass_ABCDnn_138fbfb_rebinned1_{modifyBinTag}.root', 'RECREATE')

def touchupHist(region):
    inFile = TFile.Open(f'templates{region}_Oct2024_42bins/templates_BpMass_ABCDnn_138fbfb_rebinned1_{modifyBinTag}.root', 'READ')

    if modifyHist:
        outFile = TFile.Open(f'templates{region}_Oct2024_42bins/templates_BpMass_ABCDnn_138fbfb_modified.root', 'RECREATE')
    if rebinHist:
        outFile = TFile.Open(f'templates{region}_Oct2024_420bins/templates_BpMass_ABCDnn_138fbfb_rebin42.root', 'RECREATE')

    print(f'Opened templates{region}_Oct2024_42bins/templates_BpMass_ABCDnn_138fbfb.root...')
    for hist in inFile.GetListOfKeys():
        hist_out = inFile.Get(hist.GetName()).Clone()

        if modifyHist:
            if 'major' in hist.GetName():
                nBins = hist_out.GetNbinsX()
                for i in range(nBins):
                    if hist_out.GetBinContent(i)<0:
                        print(f'Bin{i} in {hist.GetName()} has negative content. Setting to 0...')
                        hist_out.SetBinContent(i, 0)
                    hist_out.SetBinError(i, np.sqrt(hist_out.GetBinContent(i))) # for creation bin diff from fit bin
            outFile.WriteObject(hist_out, hist.GetName())
        if rebinHist:
            hist_out.Rebin(10) #sanity check
            outFile.WriteObject(hist_out, hist.GetName())
            
        if region!="V":
            outFileDV2.WriteObject(hist_out, hist.GetName())
        #else:
        #    print(f'Region{region} irrelevant to DV2.')
            
    inFile.Close()
    if modifyHist or rebinHist:
        outFile.Close()

if makeRegion=="DV2":
    touchupHist("D")
    touchupHist("V2")
    #touchupHist("V")
elif makeRegion=="D2V":
    touchupHist("D2")
    touchupHist("V")
else:
    print("Invalid makeRegion!")

outFileDV2.Close()

