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
    #postFix = f'Jan2025_105binsCorr{year[1:]}'
    postFix = 'Jan2025BprimeT'

    
if len(sys.argv)>4:
    year = sys.argv[4]
else:
    year = ''
    
templateDir = f'templates{region}_{postFix}'
fileName = f'{templateDir}/templates_{iPlot}_138fbfb{year}_smoothedJJ_rebinned1_stat0p2_smoothedTV_smooth2DUncert_smoothedCorr.root'


if year=='_2016':
    lowTh = {"tagTjet"  :{"correct":1620,"train": 9999}, #, 1080
             "tagWjet"  :{"correct": 840,"train": 840},
             "untagTlep":{"correct": 9999,"train": 840},
             "untagWlep":{"correct": 9999,"train": 740} #preapp5
             }
    medTh = {"tagTjet"  :{"correct": 9999,"train": 9999},
             "tagWjet"  :{"correct": 9999,"train": 9999}, #, 1520
             "untagTlep":{"correct": 9999,"train": 1720},
             "untagWlep":{"correct": 9999,"train": 1780} # preapp 5
             }
    highTh = {"tagTjet"  :{"correct": 9999,"train": 9999},
              "tagWjet"  :{"correct": 9999,"train": 9999},
              "untagTlep":{"correct": 9999,"train": 9999},
              "untagWlep":{"correct": 9999,"train": 9999}
              }
else:
    # lowTh = {"tagTjet"  :{"correct": 470,"train": 950}, #470,950
    #          "tagWjet"  :{"correct": 680,"train": 900},
    #          "untagTlep":{"correct": 610,"train": 1710}, #610, 610
    #          "untagWlep":{"correct": 490,"train": 9999} #490,820 #{"correct": 450,"train": 810} #preapp5
    #          }
    # medTh = {"tagTjet"  :{"correct": 920,"train": 9999}, #920,9999
    #          "tagWjet"  :{"correct": 1540,"train": 1080}, #1540,1080
    #          "untagTlep":{"correct": 1500,"train": 9999}, #1500, 1710
    #          "untagWlep":{"correct": 610,"train": 9999} #610,2100#{"correct": 610,"train": 2100}#preapp5
    #          }
    # highTh = {"tagTjet"  :{"correct": 9999,"train": 9999},
    #           "tagWjet"  :{"correct": 9999,"train": 9999},
    #           "untagTlep":{"correct": 1920, "train": 9999}, #1920,9999
    #           "untagWlep":{"correct": 9999, "train": 9999}
    #           }

    lowTh = {"tagTjet"  :{"correct": 9999,"train": 9999,"smooth2D":680}, #470,950 
             "tagWjet"  :{"correct": 930,"train": 890,"smooth2D":680},
             "untagTlep":{"correct": 9999,"train": 9999,"smooth2D":9999}, #610, 610
             "untagWlep":{"correct": 9999,"train": 970,"smooth2D":9999} #490,820 #{"correct": 450,"train": 810} #preapp5
             }
    medTh = {"tagTjet"  :{"correct": 9999,"train": 9999,"smooth2D":9999}, #920,9999
             "tagWjet"  :{"correct": 1260,"train": 1310,"smooth2D":9999}, #1540,1080
             "untagTlep":{"correct": 9999,"train": 9999,"smooth2D":9999}, #1500, 1710
             "untagWlep":{"correct": 9999,"train": 9999,"smooth2D":9999} #610,2100#{"correct": 610,"train": 2100}#preapp5
             }
    highTh = {"tagTjet"  :{"correct": 9999,"train": 9999,"smooth2D":9999},
              "tagWjet"  :{"correct": 9999,"train": 9999,"smooth2D":9999},
              "untagTlep":{"correct": 9999, "train": 9999,"smooth2D":9999}, #1920,9999
              "untagWlep":{"correct": 9999, "train": 9999,"smooth2D":9999}
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
    
    
    #uncertList = []
    #if 'Train' in postFix:
    #    uncertList.append('train')
    #if 'CorrUC' in postFix:
    #    uncertList.append('correct')

    uncertList = ['train','correct','smooth2D']

    if len(uncertList)==3:
        rootFileOut = ROOT.TFile.Open(fileName.replace('.root','_TrainCorrectSmoothUC.root'), 'RECREATE')
    elif len(uncertList)==2:
        rootFileOut = ROOT.TFile.Open(fileName.replace('.root','_TrainCorrectUC.root'), 'RECREATE')
    elif 'train' in uncertList:
        rootFileOut = ROOT.TFile.Open(fileName.replace('.root','_TrainUC.root'), 'RECREATE')
    elif 'correct' in uncertList:
        rootFileOut = ROOT.TFile.Open(fileName.replace('.root','_CorrectUC.root'), 'RECREATE')

    
        
    # save untouched hists
    if len(uncertList)==3:
        allHists = [hist.GetName() for hist in rootFileIn.GetListOfKeys() if 'train' not in hist.GetName() and 'correct' not in hist.GetName() and 'smooth' not in hist.GetName()]
    elif len(uncertList)==2:
        allHists = [hist.GetName() for hist in rootFileIn.GetListOfKeys() if 'train' not in hist.GetName() and 'correct' not in hist.GetName()]
    elif 'train' in uncertList:
        allHists = [hist.GetName() for hist in rootFileIn.GetListOfKeys() if 'train' not in hist.GetName()]
    elif 'correct' in uncertList:
        allHists = [hist.GetName() for hist in rootFileIn.GetListOfKeys() if 'correct' not in hist.GetName()]
            
    for histName in allHists:
        hist = rootFileIn.Get(histName).Clone()
        rootFileOut.cd()
        hist.Write(histName)
    
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
                print(lowTh[tag][uncert])
                if lowTh[tag][uncert]!=9999:
                    histMassRange2.Write()
                    print('histMassRange2 written')
                if medTh[tag][uncert]!=9999:
                    histMassRange3.Write()
                if highTh[tag][uncert]!=9999:
                    histMassRange4.Write()

    rootFileOut.Close()
rootFileIn.Close()
