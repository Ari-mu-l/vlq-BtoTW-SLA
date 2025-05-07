from ROOT import *

region = 'D'
year = ''
option = 'JumpExcC2Seg2' #'TurnOn','JumpAll', 'JumpExcC1Seg1', 'JumpExcC1Seg2', 'JumpExcC1Seg3', 'JumpExcC2Seg1','JumpExcC2Seg2'
inDirPostFix = f'Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin{year}'
rfilePostFix = '_smoothedJJ_rebinned1_stat0p2_smoothedTV'
infileName = f'templates{region}_{inDirPostFix}/templates_BpMass_ABCDnn_138fbfb{year}{rfilePostFix}.root'
outfileName = infileName.replace('.root',f'_clipped{option}.root')

infile = TFile(infileName, 'READ')
outfile = TFile(outfileName, 'RECREATE')
histNameList = [hist.GetName() for hist in infile.GetListOfKeys()]

if option=='TurnOn':
    cutOff = 750
    for histName in histNameList:
        hist = infile.Get(histName).Clone(f'{histName}_clip')
        if 'jet' in histName:
            startBin = hist.FindFixBin(cutOff)
            nBin = hist.GetNbinsX()
            for i in range(1,startBin):
                hist.SetBinContent(i,0)
                hist.SetBinError(i,0)
        outfile.WriteObject(hist, histName)
elif 'Jump' in option:
    clipCase1 = [[25,32],[50,65],[89,100]]
    clipCase2 = [[165,184],[218,240]]
    for histName in histNameList:
        hist = infile.Get(histName).Clone(f'{histName}_clip')
        nBin = hist.GetNbinsX()
        if 'tagTjet' in histName:
            if 'ExcC1Seg1' not in option:
                for i in range(clipCase1[0][0],clipCase1[0][1]+1):
                    hist.SetBinContent(i,0)
                    hist.SetBinError(i,0)
            if 'ExcC1Seg2' not in option:
                for i in range(clipCase1[1][0],clipCase1[1][1]+1):
                    hist.SetBinContent(i,0)
                    hist.SetBinError(i,0)
            if 'ExcC1Seg3' not in option:
                for i in range(clipCase1[2][0],clipCase1[2][1]+1):
                    hist.SetBinContent(i,0)
                    hist.SetBinError(i,0)
        if 'tagWjet' in	histName:
            if 'ExcC2Seg1' not in option:
                for i in range(clipCase2[0][0],clipCase2[0][1]+1):
                    hist.SetBinContent(i,0)
                    hist.SetBinError(i,0)
            if 'ExcC2Seg2' not in option:
                for i in range(clipCase2[1][0],clipCase2[1][1]+1):
                    hist.SetBinContent(i,0)
                    hist.SetBinError(i,0)
        outfile.WriteObject(hist, histName)
                
infile.Close()
outfile.Close()
        
