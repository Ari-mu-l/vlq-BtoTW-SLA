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

lowTh = {"tagTjet":{"correct":1520,
                    "train": 950
                    },
         "tagWjet":{"correct": 680,
                    "train": 1250
                    },
         "untagTlep":{"correct": 600,
                      "train": 1700
                      },
         "untagWlep":{"correct": 450,
                      "train": 9999
                      }
         }

medTh = {"tagTjet":{"correct": 1830,
                    "train": 9999
                    },
         "tagWjet":{"correct": 1540,
                    "train": 9999
                    },
         "untagTlep":{"correct": 1900,
                      "train": 9999
                      },
         "untagWlep":{"correct": 610,
                      "train": 9999
                      }
         }
highTh = {"tagTjet":{"correct": 9999,
                     "train": 9999
                     },
          "tagWjet":{"correct": 9999,
                     "train": 9999
                     },
          "untagTlep":{"correct": 9999,
                       "train": 9999
                       },
          "untagWlep":{"correct": 9999,
                       "train": 9999
                       }
          }

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
    print(f'Binning wrote to {templateDir}/binEdges{year}.json')
else:
    json_obj = json.dumps([lowTh, medTh, highTh])
    with open(f'{templateDir}/splitThresholds.json','w') as outfile:
        outfile.write(json_obj)
    print(f'Splitting thresholds wrote to {templateDir}/splitThresholds.json')
    
    rootFileOut = ROOT.TFile.Open(fileName.replace('.root','_UC.root'), 'RECREATE')
    
    uncertList = []
    if 'Train' in postFix:
        uncertList.Append('train')
    if 'CorrUncert' in postFix:
        uncertList.Append('correct')
        
    # save untouched hists
    if len(uncertList)==2:
        allHists = [hist.GetName() for hist in rootFileIn.GetListOfKeys() if 'train' not in hist.GetName() and 'correct' not in hist.GetName()]
    elif 'Train' in postFix:
        allHists = [hist.GetName() for hist in rootFileIn.GetListOfKeys() if 'train' not in hist.GetName()]
    elif 'CorrUC' in postFix:
        allHists = [hist.GetName() for hist in rootFileIn.GetListOfKeys() if 'correct' not in hist.GetName()]
            
    for histName in allHists:
        hist = rootFileIn.Get(histName).Clone()
        rootFileOut.cd()
        hist.Write()
    
    for tag in tagList:
        for uncert in uncertList:
            for shift in ['Up', 'Down']:
                histNomName = f'BpMass_ABCDnn_138fbfb_isL_{tag}_{region}__major'
                histShift = rootFileIn.Get(f'{histNomName}__{uncert}{shift}')
                histMassRange1 = rootFileIn.Get(histNomName).Clone(f'{histNomName}__{uncert}MassRange1{shift}')
                histMassRange2 = rootFileIn.Get(histNomName).Clone(f'{histNomName}__{uncert}MassRange2{shift}')
                histMassRange3 = rootFileIn.Get(histNomName).Clone(f'{histNomName}__{uncert}MassRange3{shift}')
                histMassRange4 = rootFileIn.Get(histNomName).Clone(f'{histNomName}__{uncert}MassRange4{shift}')

                binTh1 = histShift.FindBin(lowTh[tag][uncert]+1)
                binTh2 = histShift.FindBin(medTh[tag][uncert]+1)

                # TEMP TODO: add years to dictionary
                if 'tagTjet' in histName and year=='_2016':
                    binTh3 = histShift.FindBin(1980+1)
                else:
                    binTh3 = histShift.FindBin(highTh[tag][uncert]+1)

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
                if lowTh[tag][uncert]!=9999:
                    histMassRange2.Write()
                if medTh[tag][uncert]!=9999:
                    histMassRange3.Write()
                if highTh[tag][uncert]!=9999:
                    histMassRange4.Write()

    rootFileOut.Close()
rootFileIn.Close()
