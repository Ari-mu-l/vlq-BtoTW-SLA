# python3 combineDV2.py Jan2025_210binsCorrBCorrUC3
import os, sys
from ROOT import *
import numpy as np

#templatesD_Jan2025_105binsCorr/templates_BpMass_ABCDnn_138fbfb_rebinned1_stat0p2_smoothed_TVJJ_UC.root

dirPostFix = sys.argv[1]
filePostFix = sys.argv[2] #'_rebinned1_stat0p2_smoothed_TVJJ'
outDir = f'templatesDV2_{dirPostFix}'
if not os.path.exists(outDir):
    os.makedirs(outDir)

outFileName = f'{outDir}/templates_BpMass_ABCDnn_138fbfb{filePostFix}.root'
outFileDV2 = TFile.Open(outFileName, 'RECREATE') 

#def touchupHist(region):
for region in ['D', 'V2']:
    inFileName = f'{outDir}/templates_BpMass_ABCDnn_138fbfb{filePostFix}.root'.replace('DV2',region)
    if 'UC' not in inFileName:
        print('Not combining uncorrelated files!')
    inFile = TFile.Open(inFileName, 'READ')

    # if modifyHist:
    #     outFileName = f'templates{region}_Oct2024_{Nbins}bins/templates_BpMass_ABCDnn_138fbfb_modified.root'
    #     outFile = TFile.Open(outFileName, 'RECREATE')
    # if rebinHist:
    #     outFile = TFile.Open(f'templates{region}_Oct2024_{Nbins}bins/templates_BpMass_ABCDnn_138fbfb_rebin42.root', 'RECREATE')

    print(f'Opened {inFileName}...')
    for hist in inFile.GetListOfKeys():
        hist_out = inFile.Get(hist.GetName()).Clone()

        # if modifyHist:
        if 'major' in hist.GetName():
            nBins = hist_out.GetNbinsX()
            for i in range(nBins):
                #if hist_out.GetBinContent(i)==0:
                #print(f'Bin{i} in {hist.GetName()} has 0 content.')
                if hist_out.GetBinContent(i)<0:
                    print(f'Bin{i} in {hist.GetName()} has negative content. Setting to 0...')
                    hist_out.SetBinContent(i, 0)
                    #hist_out.SetBinError(i, np.sqrt(hist_out.GetBinContent(i))) # for creation bin diff from fit bin
        #     outFile.WriteObject(hist_out, hist.GetName())
        # if rebinHist:
        #     hist_out.Rebin(10) #sanity check
        #     outFile.WriteObject(hist_out, hist.GetName())

        outFileDV2.WriteObject(hist_out, hist.GetName())
            
    inFile.Close()
    # if modifyHist or rebinHist:
    #     outFile.Close()
    #     os.system(f'rm {inFileName}')
    #     os.system(f'mv {outFileName} {inFileName}')
        


# if makeRegion=="DV2":
#     touchupHist("D")
#     touchupHist("V2")
# elif makeRegion=="D2V":
#     touchupHist("D2")
#     touchupHist("V")
# else:
#     print("Invalid makeRegion!")

outFileDV2.Close()
