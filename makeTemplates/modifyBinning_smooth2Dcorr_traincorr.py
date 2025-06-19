#!/usr/bin/python

import os,sys,time,math,fnmatch
from array import array
from numpy import linspace
parent = os.path.dirname(os.getcwd())
sys.path.append(parent)
from ROOT import TFile, TH1, TGraph, TGraphSmooth
start_time = time.time()

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Run as:
# > python modifyBinning.py
# 
# Optional arguments:
# -- statistical uncertainty threshold
#
# Notes:
# -- Finds certain root files in a given directory and rebins all histograms in each file
# -- A selection of subset of files in the input directory can be done below under "#Setup the selection ..."
# -- A custom binning choice can also be given below and this choice can be activated by giving a stat unc 
#    threshold larger than 100% (>1.) in the argument
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

#cutString = 'splitLess/'#BB_templates/'
region = sys.argv[1]
postfix = sys.argv[2]
templateDir = os.getcwd()+'/templates'+region+'_'+postfix+'/'
print('templateDir:',templateDir)

rebin = False
scaleLumi = False
#lumiScaleCoeffEl = 2530./2600.
#lumiScaleCoeffMu = 2621./2690.
#lumiscale = 2318./2258.

sigName = 'Bp' #MAKE SURE THIS WORKS FOR YOUR ANALYSIS PROPERLY!!!!!!!!!!!
upTag = 'Up'
downTag = 'Down'

def findfiles(path, filtre):
    for root, dirs, files in os.walk(path):
        for f in fnmatch.filter(files, filtre):
            yield os.path.join(root, f)

#Setup the selection of the files to be rebinned: HiggsTagTemplate_tW1p0_bZ0p0_bH0p0_BBM1800.root
# smooth AFTER rebin
#rfiles = [file for file in findfiles(templateDir, '*.root') if 'rebinned' in file and 'smoothed' not in file and 'plots' not in file] #'corr' in file
#rfiles = [f'{templateDir}/templates_BpMass_ABCDnn_138fbfb_smoothedJJ_rebinned1_stat0p2.root']
#rfiles = [file for file in findfiles(templateDir, 'templates_BpMass_ABCDnn*_smoothedJJ_rebinned1_stat0p2.root')]
#rfiles = [file for file in findfiles(templateDir, 'templates_BpMass_ABCDnn_138fbfb_rebinned1_stat0p2.root')]
rfiles = [file for file in findfiles(templateDir, 'templates_BpMass_ABCDnn_138fbfb_smoothedJJ_rebinned1_stat0p2.root')]
# smooth BEFORE rebin
#rfiles = [file for file in findfiles(templateDir, '*.root') if 'rebinned' not in file and 'smoothed' not in file and 'plots' not in file]
tfile = TFile(rfiles[0])

iRfile=0
yieldsAll = {}
yieldsErrsAll = {}
yieldsSystErrsAll = {}
checkscale = True
for rfile in rfiles: 
    print("SMOOTHING FILE:",rfile)
    tfiles = {}
    outputRfiles = {}
    tfiles[iRfile] = TFile(rfile)
    allhists = [hist.GetName() for hist in tfiles[iRfile].GetListOfKeys()]
    print('Example of allhists:',allhists[0])
    
    outputRfiles[iRfile] = TFile(rfile.replace('.root','_smoothedTV.root'),'RECREATE')

    if rebin:
        #binslist = [400,425,450,475,500,525,550,575,600,625,650,675,700,725,750,775,800]
        #binslist = [500,525,550,575,600,625,650,675,700,725,750,775,800]
        binslist = linspace(400, 2350, 79).tolist()
        xbins = array('d', binslist)
        print('Will rebin to',xbins)
    
    print("PROGRESS:")
    rebinnedHists = {}
    for hist in allhists:

        majornames = [k.GetName() for k in tfiles[iRfile].GetListOfKeys() if '__major' in k.GetName() and upTag not in k.GetName() and downTag not in k.GetName()]
        
        if hist not in majornames and 'correct' not in hist and 'train' not in hist and 'major__pNet' not in hist:
            tmphist=tfiles[iRfile].Get(hist).Clone()
            tmphist.SetDirectory(0)
            if rebin and 'untagWlep' in hist:
                tmphist.Rebin(len(xbins)-1,hist,xbins)

            tmphist.Write()
        else:
            rebinnedHists[hist]=tfiles[iRfile].Get(hist).Clone(hist)
            rebinnedHists[hist].SetDirectory(0)

    print('Majornames has:',majornames)
    
    valUphists = [k.GetName() for k in tfiles[iRfile].GetListOfKeys() if '__correct' in k.GetName() and upTag in k.GetName()]
    trainUphists = [k.GetName() for k in tfiles[iRfile].GetListOfKeys() if '__train' in k.GetName() and upTag in k.GetName()]
    pNetUphists = [k.GetName() for k in tfiles[iRfile].GetListOfKeys() if '__pNet' in k.GetName() and upTag in k.GetName() and 'major' in k.GetName()]

    print('TrainUphists has:',trainUphists)

    # smooth major first
    majorhists = {}
    for hist in majornames:
        print('\t',hist)
        majorhist = rebinnedHists[hist].Clone()
        majorhist_original = majorhist.Clone(f'{hist}_beforeSmooth')
        print('\t\t',majorhist.GetName())
        majorgraph = TGraph()
        majorgraph2 = TGraph()
        for ibin in range(1,majorhist.GetNbinsX()):
            majorgraph.SetPoint(ibin-1, majorhist.GetXaxis().GetBinCenter(ibin), majorhist.GetBinContent(ibin))
            majorgraph2.SetPoint(ibin-1, majorhist.GetXaxis().GetBinCenter(ibin), majorhist.GetBinContent(ibin))
        majorsmooth = TGraphSmooth("normal")
        majorsmooth2 = TGraphSmooth("normal")

        #frac = 0.09 #worked but bad postfit plot
        #if 'jet' in hist:
        #    frac = 0.09
        #else:
        #    frac =0.07

        # best setting for 1D smoothing without smoothUncert
        # not enough for smoothUncert
        # if region=="D":
        #     if 'tagTjet' in hist:
        #         frac = 0.005
        #     elif 'tagWjet' in hist:
        #         frac = 0.005
        #     else:
        #         frac = 0.04
        # else:
        #     if 'tagTjet' in hist:
        #         frac = 0.06
        #     elif 'tagWjet' in hist:
        #         frac = 0.05
        #     else:
        #         frac = 0.04

        frac = 0.09
        if region=="D":
            frac = 0.07
        if 'untag' in hist:
            frac = 0.07
            
        
        # if region=="V2":
        #     if 'tagTjet' in hist:
        #         frac = 0.09
        #     else:
        #         frac = 0.06
        
        frac2 = 0.01 # 0.1 had p-value of 0.025 # 0.005 had a p-value of 0.03
        #if '2016' not in templateDir and '2017' not in templateDir and '2018' not in templateDir: # full run2 smoothing
            #print('GETTING FULL RUN2') # for debug
            #frac = 0.07
            # if region=="V2":
            #     if 'tagTjet' in hist:
            #         frac = 0.1
            #     if 'tagWjet' in hist:
            #         frac = 0.1
            #     if 'untag' in hist:
            #         frac = 0.07
            # elif region=="D":
            #     if 'tagTjet' in hist:
            #         frac = 0.1 #0.1
            #     if 'tagWjet' in hist:
            #         frac = 0.08
            #     if 'untagWlep' in hist:
            #         frac = 0.04
            # else:
            #     print('Region not considered!')
            #     exit()
        # else:
        #     if '2016APV' in templateDir:
        #         if 'jet' in hist:
        #             frac = 0.1
        #         else:
        #             frac = 0.05
        #     elif '2016' in templateDir:
        #         if 'tagT' in hist:
        #             frac = 0.1
        #         else:
        #             frac = 0.08
        #     elif '2017' in templateDir:
        #         frac = 0.08
        #     elif '2018' in templateDir:
        #         if 'jet' in hist:
        #             frac = 0.05
        #         else:
        #             frac = 0.07
            
        majorgraph = majorsmooth.SmoothLowess(majorgraph,"",frac)
        majorgraph2 = majorsmooth2.SmoothLowess(majorgraph,"",frac2)
        binThreshold = majorhist.GetXaxis().FindFixBin(700)
        for ibin in range(1,majorhist.GetNbinsX()):
            newbin = majorgraph.Eval(majorhist.GetXaxis().GetBinCenter(ibin))
            oldbin = majorhist.GetBinContent(ibin)
            # smooth all
            #majorhist.SetBinContent(ibin,majorgraph.Eval(majorhist.GetXaxis().GetBinCenter(ibin)))
            # partial smooth
            if region=="D" and 'jet' in hist:
               # smooth only the unblinded BpM in SR
               if ibin<binThreshold:
                   majorhist.SetBinContent(ibin,majorgraph.Eval(majorhist.GetXaxis().GetBinCenter(ibin)))
               else:
                   majorhist.SetBinContent(ibin,majorgraph2.Eval(majorhist.GetXaxis().GetBinCenter(ibin)))
                   #majorhist.SetBinContent(ibin,majorhist_original.GetBinContent(ibin))
                   #majorhist.SetBinContent(ibin,majorgraph.Eval(majorhist.GetXaxis().GetBinCenter(ibin)))
            else:
               majorhist.SetBinContent(ibin,majorgraph.Eval(majorhist.GetXaxis().GetBinCenter(ibin)))
            if oldbin != 0:
                if newbin/oldbin > 2:
                    print('Smoothing changed by > 100%: hist',hist,', bin',ibin,', new/old = ',newbin/oldbin,', current error/content = ',majorhist.GetBinError(ibin)/oldbin)
                majorhist.SetBinError(ibin,majorhist.GetBinError(ibin)*newbin/oldbin) #scale error...
        majorhist.Write()
        majorhists[hist] = majorhist

    print('majorhists has keys:',majorhists.keys())
        
    # find smoothed correction and apply as Up
    # correction = smoothedMajor - correctDown
    # up = correctDown + 2*correction
    for hist in valUphists:
        print('\t',hist)

        frac = 0.05

        # if region=="D":
        #     if 'tagTjet' in hist:
        #         frac = 0.005
        #     elif 'tagWjet' in hist:
        #         frac = 0.005
        #     else:
        #         frac = 0.04
        # else:
        #     if 'tagTjet' in hist:
        #         frac = 0.06
        #     elif 'tagWjet' in hist:
        #         frac = 0.05
        #     else:
        #         frac = 0.04

        majorhist = majorhists[hist[:hist.find('__correct')]]  # smoothed
        up = rebinnedHists[hist].Clone()                       # to be replaced
        down = rebinnedHists[hist.replace(upTag,downTag)].Clone()  # original major

        #frac = 0.05 # preApp5
        #if '2016' not in templateDir and '2017' not in templateDir and '2018' not in templateDir: # full run2 corr
            #frac = 0.1
            # if region=="V2":
            #     if 'tagTjet' in hist:
            #         frac = 0.1
            #     if 'tagWjet' in hist:
            #         frac = 0.1
            #     if 'untagWlep' in hist:
            #         frac = 0.04 #0.01
            # elif region=="D":
            #     if 'tagTjet' in hist:
            #         frac = 0.1
            #     if 'tagWjet' in hist:
            #         frac = 0.08
            #     if 'untagWlep' in hist:
            #         frac = 0.04
            # else:
            #     print('Region not considered!')
            #     exit()
        # else:
        #     if '2016APV' in templateDir:
        #         if 'jet' in hist:
        #             frac = 0.1
        #         else:
        #             frac = 0.05
        #     elif '2016' in templateDir:
        #         if 'tagT' in hist:
        #             frac = 0.1
        #         else:
        #             frac = 0.08
        #     elif '2017' in templateDir:
        #         frac = 0.08
        #     elif '2018'	in templateDir:
        #         if 'jet' in hist:
        #             frac = 0.05
        #         else:
        #             frac = 0.07
                
        downgraph = TGraph()
        for ibin in range(1,down.GetNbinsX()):
            downgraph.SetPoint(ibin-1, down.GetXaxis().GetBinCenter(ibin), down.GetBinContent(ibin))
        downsmooth = TGraphSmooth("normal")
        downgraph = downsmooth.SmoothLowess(downgraph,"",frac)
        for ibin in range(1,down.GetNbinsX()):
            down.SetBinContent(ibin,downgraph.Eval(down.GetXaxis().GetBinCenter(ibin)))

        corr = majorhist.Clone("corr")
        corr_copy = majorhist.Clone("corrCopy")
        corr.Add(down,-1)
        up.Add(down,corr,1.0,2.0)
        for ibin in range(1,up.GetNbinsX()+1):
            if up.GetBinContent(ibin) < 0:
                print(hist)
                print('after smoothing:')
                print(f'bin {ibin}, nominal: {corr_copy.GetBinContent(ibin)}, corr: {corr.GetBinContent(ibin)}, down: {down.GetBinContent(ibin)}, up: {up.GetBinContent(ibin)}')
                up.SetBinContent(ibin,0)
        
        # origmajorname = hist[:hist.find('__correct')]
        # origmajorhist = rebinnedHists[origmajorname]

        # upratio = up.Clone('upratio')
        # upratio.Divide(origmajorhist)
        # upgraph = TGraph()
        # dnratio = down.Clone('dnratio')
        # dnratio.Divide(origmajorhist)
        # dngraph = TGraph()
        # for ibin in range(1,up.GetNbinsX()+1):
        #     upgraph.SetPoint(ibin-1, upratio.GetXaxis().GetBinCenter(ibin), upratio.GetBinContent(ibin))
        #     dngraph.SetPoint(ibin-1, dnratio.GetXaxis().GetBinCenter(ibin), dnratio.GetBinContent(ibin))
                        
        # upratio.Delete()
        # dnratio.Delete()
        # upsmooth = TGraphSmooth("normal")
        # dnsmooth = TGraphSmooth("normal")
        # upgraph = upsmooth.SmoothLowess(upgraph,"",frac)
        # dngraph = dnsmooth.SmoothLowess(dngraph,"",frac)

        # for ibin in range(1,up.GetNbinsX()+1):
        #     newupratio = upgraph.Eval(up.GetXaxis().GetBinCenter(ibin))
        #     newdnratio = dngraph.Eval(down.GetXaxis().GetBinCenter(ibin))
        #     centralval = majorhist.GetBinContent(ibin)
        #     up.SetBinContent(ibin, max(0,newupratio*centralval))
        #     down.SetBinContent(ibin, max(0,newdnratio*centralval))
        #     #if 'Tjet' in hist:
        #     #    print('NewUp is ',newupratio,', changed from',upratio.GetBinContent(ibin))

        if majorhist.Integral() > 0 and up.Integral() > 0:
            if rebin and 'untagWlep' in hist: 
                up = up.Rebin(len(xbins)-1,hist,xbins)
                down = down.Rebin(len(xbins)-1,hist.replace(upTag,downTag),xbins)
            up.Write()
            down.Write()
        else:
            rebinnedHists[hist].Write()
            rebinnedHists[hist.replace(upTag,downTag)].Write()

    # smooth and center
    for hist in trainUphists:
        print('\t',hist)

        frac = 0.05

        majorhist = majorhists[hist[:hist.find('__train')]]
        up = rebinnedHists[hist].Clone()
        down = rebinnedHists[hist.replace(upTag,downTag)].Clone()
        origmajorname = hist[:hist.find('__train')] #+'__correctDown'
        origmajorhist = rebinnedHists[origmajorname]
        
        upratio = up.Clone('upratio')
        upratio.Divide(origmajorhist)
        dnratio = down.Clone('dnratio')
        dnratio.Divide(origmajorhist)
        upgraph = TGraph()
        dngraph = TGraph()
        for ibin in range(1,up.GetNbinsX()+1):
            upgraph.SetPoint(ibin-1, upratio.GetXaxis().GetBinCenter(ibin), upratio.GetBinContent(ibin))
            dngraph.SetPoint(ibin-1, dnratio.GetXaxis().GetBinCenter(ibin), dnratio.GetBinContent(ibin))
        upratio.Delete()
        dnratio.Delete()

        upsmooth = TGraphSmooth("normal")
        dnsmooth = TGraphSmooth("normal")

        upgraph = upsmooth.SmoothLowess(upgraph,"",frac)
        dngraph = dnsmooth.SmoothLowess(dngraph,"",frac)

        for ibin in range(1,up.GetNbinsX()+1):
            newupratio = upgraph.Eval(up.GetXaxis().GetBinCenter(ibin))
            newdnratio = dngraph.Eval(down.GetXaxis().GetBinCenter(ibin))
            centralval = majorhist.GetBinContent(ibin)
            up.SetBinContent(ibin, max(0,newupratio*centralval))
            down.SetBinContent(ibin, max(0,newdnratio*centralval))

        if majorhist.Integral() > 0 and up.Integral() > 0:
            if rebin and 'untagWlep' in hist: 
                up = up.Rebin(len(xbins)-1,hist,xbins)
                down = down.Rebin(len(xbins)-1,hist.replace(upTag,downTag),xbins)
            up.Write()
            down.Write()
        else:
            rebinnedHists[hist].Write()
            rebinnedHists[hist.replace(upTag,downTag)].Write()

    # center only
    for hist in pNetUphists:
        print('\t',hist)

        frac = 0.05

        majorhist = majorhists[hist[:hist.find('__pNet')]]
        up = rebinnedHists[hist].Clone()
        down = rebinnedHists[hist.replace(upTag,downTag)].Clone()
        origmajorname = hist[:hist.find('__pNet')] #+'__correctDown'
        origmajorhist = rebinnedHists[origmajorname]
        
        upratio = up.Clone('upratio')
        upratio.Divide(origmajorhist)
        dnratio = down.Clone('dnratio')
        dnratio.Divide(origmajorhist)
        up.Multiply(upratio,majorhist,1,1)
        down.Multiply(dnratio,majorhist,1,1)
        
        if majorhist.Integral() > 0 and up.Integral() > 0:
            if rebin and 'untagWlep' in hist: 
                up = up.Rebin(len(xbins)-1,hist,xbins)
                down = down.Rebin(len(xbins)-1,hist.replace(upTag,downTag),xbins)
            up.Write()
            down.Write()
        else:
            rebinnedHists[hist].Write()
            rebinnedHists[hist.replace(upTag,downTag)].Write()

    tfiles[iRfile].Close()
    outputRfiles[iRfile].Close()
    iRfile+=1
tfile.Close()
print(">> Smoothing Done!")

print("--- %s minutes ---" % (round((time.time() - start_time)/60,2)))
