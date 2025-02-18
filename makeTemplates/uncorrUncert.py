# python3 uncorrUncert.py D False _2016
import os, sys
import ROOT
import json

iPlot = 'BpMass_ABCDnn'

if len(sys.argv)>1:
    region = sys.argv[1]
else:
    region = 'D'

if len(sys.argv)>2:
    scanThresholds = sys.argv[2]
else:
    scanThresholds = "True"
    
if len(sys.argv)>3:
    postFix = sys.argv[3]
else:
    postFix = f'Jan2025_105binsCorr{year[1:]}'

    
if len(sys.argv)>4:
    year = sys.argv[4]
else:
    year = ''
    
templateDir = f'templates{region}_{postFix}'
fileName = f'{templateDir}/templates_{iPlot}_138fbfb{year}_rebinned1_stat0p2_smoothed_TVJJ.root' # after rebin and smoothing

# if year=='_2016': # assuming _2016.root
#     lowTh  = 1180
#     medTh  = 1600
# else:
#     lowTh  = 1200 # TEMP: update this
#     medTh  = 1800

lowTh = {"correct": 1200, "train": 1240}
medTh = {"correct": 1400, "train": 1840}
highTh = {"correct": 2000}

tagList = ["tagTjet", "tagWjet", "untagTlep", "untagWlep"]

print(f'Opening {fileName}...')
rootFileIn = ROOT.TFile.Open(fileName, 'READ')

# Scan for thresholds
if scanThresholds=="True":
    print(f'scanThresholds set to True, creating json file... No rootfile will be made.')
    binEdgesDict = {}
    for tag in tagList:
        # get histogram binning
        histMajor = rootFileIn.Get(f'BpMass_ABCDnn_138fbfb_isL_{tag}_{region}__major').Clone(f'{tag}')
        binEdges = []
        for i in range(histMajor.GetNbinsX()+1):
            binEdges.append(histMajor.GetBinLowEdge(i))
        binEdgesDict[tag] = binEdges
    json_obj = json.dumps(binEdgesDict)
    with open(f'{templateDir}/binEdges{year}.json','w') as outfile:
        outfile.write(json_obj)
else:
    rootFileOut = ROOT.TFile.Open(fileName.replace('.root','_UC.root'), 'RECREATE')
    # save untouched hists
    if 'Train' in postFix:
        allHists = [hist.GetName() for hist in rootFileIn.GetListOfKeys() if 'correct' not in hist.GetName() or 'train' not in hist.GetName()]
        corrHists = [hist.GetName() for hist in rootFileIn.GetListOfKeys() if 'correct' in hist.GetName() or 'train' in hist.GetName()]
    else:
        allHists = [hist.GetName() for hist in rootFileIn.GetListOfKeys() if 'correct' not in hist.GetName()]
        corrHists = [hist.GetName() for hist in rootFileIn.GetListOfKeys() if 'correct' in hist.GetName()]
    for histName in allHists:
        hist = rootFileIn.Get(histName).Clone()
        rootFileOut.cd()
        hist.Write()

    for histName in corrHists:
        if 'Train' in postFix:
            uncertList = ['correct', 'train']
        else:
            uncertList = ['correct']
        for uncert in uncertList:
            if (uncert in histName) and uncert=="correct":
                histNomName = histName.replace('__'+histName.split('_')[-1],'')
                histShift = rootFileIn.Get(histName)
                histMassRange1 = rootFileIn.Get(histNomName).Clone(histName.replace(f'{uncert}',f'{uncert}MassRange1'))
                histMassRange2 = rootFileIn.Get(histNomName).Clone(histName.replace(f'{uncert}',f'{uncert}MassRange2'))
                histMassRange3 = rootFileIn.Get(histNomName).Clone(histName.replace(f'{uncert}',f'{uncert}MassRange3'))
                histMassRange4 = rootFileIn.Get(histNomName).Clone(histName.replace(f'{uncert}',f'{uncert}MassRange4'))

                binTh1 = histShift.FindBin(lowTh[uncert]+1)
                binTh2 = histShift.FindBin(medTh[uncert]+1)

                if uncert=="correct":
                    if 'tagTjet' in histName and year=='_2016':
                        binTh3 = histShift.FindBin(1980+1)
                    else:
                        binTh3 = histShift.FindBin(highTh[uncert]+1)
                else:
                    binTh3 = 999
                        
                nbins = histShift.GetNbinsX()

                for i in range(nbins+1):
                    if i<binTh1:
                        histMassRange1.SetBinContent(i,histShift.GetBinContent(i))
                        histMassRange1.SetBinError(i,histShift.GetBinError(i))
                    elif i>=binTh1 and i<binTh2:
                        histMassRange2.SetBinContent(i,histShift.GetBinContent(i))
                        histMassRange2.SetBinError(i,histShift.GetBinError(i))
                    elif i>=binTh2 and i<binTh3:
                        histMassRange3.SetBinContent(i,histShift.GetBinContent(i))
                        histMassRange3.SetBinError(i,histShift.GetBinError(i))
                    else:
                        histMassRange4.SetBinContent(i,histShift.GetBinContent(i))
                        histMassRange4.SetBinError(i,histShift.GetBinError(i))
                rootFileOut.cd()
                histMassRange1.Write()
                histMassRange2.Write()
                histMassRange3.Write()
                if uncert=="correct":
                    histMassRange4.Write()
        
    rootFileOut.Close()

rootFileIn.Close()
