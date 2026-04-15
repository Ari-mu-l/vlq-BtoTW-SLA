#!/usr/bin/python

# python3 -u plotHists.py BpMass A True 

import os,sys,time,math
parent = os.path.dirname(os.getcwd())
sys.path.append(parent)
from math import sqrt
from ROOT import *
from samples import lumiStr, systListShortPlots, systListFullPlots,  systListABCDnn, yieldUncertABCDnn, xsec_t, xsec_b
from utils import *

TH1.SetDefaultSumw2(True)
gROOT.SetBatch(1)
# set font to Helvetica for paper
# 4 for Helvetica
# 3 specify the precision
gStyle.SetTitleFont(42)
gStyle.SetTextFont(42)
# set tick marks on both sides
gStyle.SetPadTickX(1)
gStyle.SetPadTickY(1)

start_time = time.time()

lumi=138 #for plots #56.1 #
lumiInTemplates= lumiStr

isPrelim = False

iPlot='HT'
if len(sys.argv)>1: iPlot=str(sys.argv[1])
region='lowMT2pb'
if len(sys.argv)>2: region=str(sys.argv[2])
isCategorized=True
if len(sys.argv)>3: isCategorized=bool(eval(sys.argv[3]))
if isCategorized:
        pfix=f'templates{region}'
else:
        pfix=f'kinematics{region}'
if len(sys.argv)>4:
        pfix+=str(sys.argv[4])
else:
        pfix+='_Apr2024SysAll'
        #pfix+='_Apr2024SysAll_validation' # TEMP. validation only
templateDir = f'{os.getcwd()}/{pfix}/'

if 'BprimeT' in templateDir:
        xsec = xsec_t
else:
        xsec = xsec_b

blind = False
if len(sys.argv)>5: blind=bool(eval(sys.argv[5]))

yLog  = False
if len(sys.argv)>6: yLog=bool(eval(sys.argv[6]))
print('Plotting blind?',blind,' yLog?',yLog)
if yLog or 'V' in region or 'validation' in pfix: scaleSignals = False

partialBlind = False

year = 'all'
if len(sys.argv)>8: year=sys.argv[8]

print('Plotting',region,'is categorized?',isCategorized,' for year',year)

if len(sys.argv)>7:
        isRebinned=str(sys.argv[7])
else:
        isRebinned=''
        
saveKey = '' # tag for plot names

datalabel = 'data_obs'
shiftlist = ['Up','Down'] # change to Down for future
sig1='BpM800' #  choose the 1st signal to plot
sig1leg="B' (0.8 TeV, 1 pb)" # singlet 1% xsec
sig2='BpM1400' #  choose the 2nd signal to plot
sig2leg="B' (1.4 TeV, 1 pb)"
if isCategorized:
        if 'BprimeT' in templateDir:
                sig1leg="B' (0.8 TeV, 36.00 fb)"
                sig2leg="B' (1.4 TeV, 2.07 fb)"
        else:
                sig1leg="B' (0.8 TeV, 59.35 fb)"
                sig2leg="B' (1.4 TeV, 2.66 fb)"

scaleSignals = False # no x100 on signal. use log plot
#if not isCategorized: scaleSignals = True
sigScaleFact = 1
print('Scaling signals?',scaleSignals)
print('Scale factor = ',sigScaleFact)
tempsig='templates_'+iPlot+'_'+lumiInTemplates+''+isRebinned+'.root'#+'_Data18.root'
if year != 'all': tempsig='templates_'+iPlot+'_'+lumiInTemplates+'_'+year+''+isRebinned+'.root'#+'_Data18.root'

plotABCDnn = False
plotLowSide = True
if 'ABCDnn' in iPlot:
        plotABCDnn = True

#plotABCDnn = False # SWITCH. Added for ARC plot ABCDnn by category request

if len(isRebinned)>1 and 'ABCDnn' in iPlot: # SWITCH. Added for ARC plot ABCDnn by category request
        bkgProcList = ['ewk', 'ttx', 'major']
        ABCDnnProcList = ['major']
else:
        if 'ABCDnn' not in iPlot:
                bkgProcList = ['ttbar',
                               'qcd',
                               'ttx',
                               'ewk',
                               'singletop',
                               'wjets'
                               
                ]
                ABCDnnProcList = ['major']#'qcd','wjets','singletop','ttbar']
        else:
                bkgProcList = ['ttx',
                               'ewk',
                               'major'                       
                ]
        ABCDnnProcList = ['major']#'qcd','wjets','singletop','ttbar']
#bkgProcList = ['qcd','ttx','ewk','wjets','singletop','ttbar'] # SWITCH. Added for ARC plot ABCDnn by category request
#ABCDnnProcList = ['major'] # SWITCH. Added for ARC plot ABCDnn by category request
minorProcList = ['ttx','ewk']


# if plotABCDnn:
#         bkgHistColors = {'ABCDnn': kRed-7,'ewk':kMagenta-6,'ttx':kAzure+2}
# else:
#         bkgHistColors = {'ttbar':kAzure+8,'wjets':kMagenta-2,'qcd':kOrange-3,'ewk':kMagenta-6,'singletop':kGreen-6,'ttx':kAzure+2}

if plotABCDnn:
        bkgHistColors = {'ABCDnn': TColor.GetColor('#5790fc'),'ewk':TColor.GetColor('#964a8b'),'ttx':TColor.GetColor('#9c9ca1')}
else:
        bkgHistColors = {'ttbar':TColor.GetColor('#5790fc'),'wjets':TColor.GetColor('#7a21dd'),'qcd':TColor.GetColor('#f89c20'),'ewk':TColor.GetColor('#964a8b'),'singletop':TColor.GetColor('#e42536'),'ttx':TColor.GetColor('#9c9ca1')}

doAllSys = True

doNormByBinWidth=False
if len(isRebinned)>0 and 'stat1p1' not in isRebinned and 'mvagof' not in isRebinned:
        if 'rebinned1' not in isRebinned and 'Jan2025' in pfix:
                doNormByBinWidth = False
        else:
                doNormByBinWidth = True
#doNormByBinWidth = False # TEMP: Try for paper

doOneBand = True
if not doAllSys: doOneBand = True # Don't change this!
doRealPull = False
if doRealPull: doOneBand=False

plotNorm = False

isEMlist =['L']#'E','M']
taglist = ['all']
if isCategorized == True:
        #taglist=['tagTjet','tagWjet','untagTlep','untagWlep','allWlep','allTlep']
        taglist = ['tagTjet','tagWjet','untagWlep','untagTlep']
        #if region == 'V' or 'validation' in pfix:  # this should be fixed now
        #        taglist = ['untagWlep','untagTlep'] #
        if blind and ('D' in region or 'C' in region or 'Y' in region or region=='all') and 'BpMass' in iPlot and 'validation' not in pfix:
                partialBlind = True
                print(f'Partial blind {iPlot} for {region}.')

if year=='2016':
        partialBlind = False
#partialBlind = False # for making unblinded SR plots

lumiSys = 0.0073 # lumi uncertainty
factor = {'tagTjet':0.02,'tagWjet':0.02,'untagTlep':0.10,'untagWlep':0.08}

#### Consider: Did not set removeThreshold
####           No doPDF

def formatUpperHist(histogram,th1hist):
        histogram.GetXaxis().SetLabelSize(0)
        
        if plotLowSide:
                lowside = th1hist.GetBinLowEdge(1)
        else:
                lowside =  400.0 #TEMP: plotting only high BpM for ABCDnn
        highside = th1hist.GetBinLowEdge(th1hist.GetNbinsX()+1)
        #histogram.GetXaxis().SetRangeUser(lowside,highside)
        histogram.GetXaxis().SetLimits(lowside,highside)
        histogram.GetXaxis().SetNdivisions(506)

        if 'BpDecay' in histogram.GetName():
                histogram.GetXaxis().SetRangeUser(1,5)
        elif 'ST' in histogram.GetName():
                histogram.GetXaxis().SetRangeUser(0,2500)
        elif 'Jets' in histogram.GetName():
                histogram.GetXaxis().SetRangeUser(0,6)
        
        if blind == True:
                histogram.GetXaxis().SetLabelSize(0.045)
                histogram.GetXaxis().SetTitleSize(0.055)
                histogram.GetYaxis().SetLabelSize(0.04)
                histogram.GetYaxis().SetTitleSize(0.05)
                histogram.GetYaxis().SetTitleOffset(1.1)
                if 'YLD' in iPlot: histogram.GetXaxis().LabelsOption("u")
        else:
                histogram.GetYaxis().SetLabelSize(0.065)
                histogram.GetYaxis().SetTitleSize(0.07)
                if yLog:
                        histogram.GetYaxis().SetTitleOffset(0.96)
                else:
                        histogram.GetYaxis().SetTitleOffset(0.96)

        #histogram.GetYaxis().CenterTitle()
        if plotNorm:
                if yLog: uPad.SetLogy()
                histogram.SetMaximum(1.0)
        else:
                if not yLog: 
                        if region == 'SR' and isCategorized:
                                histogram.SetMinimum(0.000101);
                        else: 
                                histogram.SetMinimum(0.25)		

                if yLog:
                        uPad.SetLogy()
                        if not (doNormByBinWidth and 'jet' in tag):
                                histogram.SetMaximum(500*histogram.GetMaximum())
                        else: 
                                histogram.SetMaximum(200*histogram.GetMaximum())
                        if iPlot=='YLD': 
                                histogram.SetMaximum(200*histogram.GetMaximum())
                                histogram.SetMinimum(0.1)
                                

def formatLowerHist(histogram):
        histogram.GetXaxis().SetLabelSize(.15)
        histogram.GetXaxis().SetLabelOffset(0.04)
        histogram.GetXaxis().SetTitleSize(0.18)
        histogram.GetXaxis().SetTitleOffset(1.0) # 0.95
        histogram.GetXaxis().SetNdivisions(506)
        if 'YLD' in iPlot: histogram.GetXaxis().LabelsOption("u")

        if 'BpMass' in histogram.GetName():
                histogram.GetXaxis().SetTitle('#font[12]{m}_{tW} [GeV]')
        if 'ST' in histogram.GetName():
                histogram.GetXaxis().SetRangeUser(0,2500)
                histogram.GetXaxis().SetTitle('#font[12]{S}_{T} [GeV]')
        if 'NBJets' in histogram.GetName():
                labels = ['0','1','2','3','4','#geq 5','','','','']
                for ibin in range(1,histogram.GetNbinsX()+1):
                        histogram.GetXaxis().SetBinLabel(ibin,labels[ibin-1])
                histogram.GetXaxis().SetRangeUser(0,6)
                histogram.GetXaxis().SetLabelSize(0.24)
                histogram.GetXaxis().SetLabelOffset(0.03)
                histogram.GetXaxis().SetTitle('b-tagged jet multiplicity')
        if 'NJetsForward' in histogram.GetName():
                labels = ['0','1','2','3','4','#geq 5','','','','']
                for ibin in range(1,histogram.GetNbinsX()+1):
                        histogram.GetXaxis().SetBinLabel(ibin,labels[ibin-1])
                histogram.GetXaxis().SetRangeUser(0,6)
                histogram.GetXaxis().SetLabelSize(0.24)
                histogram.GetXaxis().SetLabelOffset(0.03)
                histogram.GetXaxis().SetTitle('forward jet multiplicity')
        if 'JetTag' in histogram.GetName():
                print('RELABELING!',histogram.GetName())
                labels = ['b/light','t','W','both']
                for ibin in range(1,histogram.GetNbinsX()+1):
                        histogram.GetXaxis().SetBinLabel(ibin,labels[ibin-1])
                histogram.GetXaxis().SetLabelSize(0.25)
                histogram.GetXaxis().SetTitleOffset(1.0)
                histogram.GetXaxis().SetTitle("AK8 ParticleNet tag")
        if 'BpDecay' in histogram.GetName():
                print('RELABELING!',histogram.GetName())
                labels = ['','Case 1','Case 2','Case 3','Case 4']
                for ibin in range(1,histogram.GetNbinsX()+1):
                        histogram.GetXaxis().SetBinLabel(ibin,labels[ibin-1])
                histogram.GetXaxis().SetLabelSize(0.24)
                histogram.GetXaxis().SetLabelOffset(0.03)
                histogram.GetXaxis().SetRangeUser(1,5)
                histogram.GetXaxis().SetTitleOffset(1.1)
                histogram.GetXaxis().SetTitle("B' quark decay mode")

        histogram.GetYaxis().SetLabelSize(0.15)
        histogram.GetYaxis().SetTitleSize(0.155)
        histogram.GetYaxis().SetTitleOffset(0.40)
        if not doRealPull: 
                histogram.GetYaxis().SetTitle('Data/Bkg.')
        else: 
                histogram.GetYaxis().SetTitle('#frac{(data-bkg)}{std. dev.}')
        histogram.GetYaxis().SetNdivisions(7)
        if doRealPull: 
                histogram.GetYaxis().SetRangeUser(-2.99,2.99)
        elif yLog and (doNormByBinWidth and 'jet' in tag):
                histogram.GetYaxis().SetRangeUser(0.1,1.9)
        else: 
                histogram.GetYaxis().SetRangeUser(0.1,1.9)
        #histogram.GetYaxis().CenterTitle()
        if not plotLowSide:
                lowside =  400 #TEMP
                highside = histogram.GetBinLowEdge(histogram.GetNbinsX()+1) #TEMP
                histogram.GetXaxis().SetRangeUser(lowside,highside) #TEMP

                
print(templateDir+tempsig)
RFile1 = TFile(templateDir+tempsig)
print(templateDir+tempsig)
print(RFile1)
bkghists = {}
bkghistsmerged = {}
systHists = {}
totBkgTemp1 = {}
totBkgTemp2 = {}
totBkgTemp3 = {}
for tag in taglist:
        perNGeV = 20 # choose what "unit" to use for bin widths, similar to the smaller bin widths in the plot. Values < 1 are ok for e.g. NN scores
        print('------------------ ',tag,' with perNGeV = ',perNGeV,' -----------------------')
        
        tagStr=tag
        for isEM in isEMlist:
                histPrefix=iPlot+'_'+lumiInTemplates+'_'
                catStr='is'+isEM+'_'+tagStr
                histPrefix+=catStr
                if isCategorized: histPrefix+='_'+region.replace('HST','highST')
                totBkg = 0.
                totMajor = 0.
                totMinor = 0.
                for proc in bkgProcList:
                        try:
                                if 'Jets' in iPlot or 'ST' in iPlot:
                                        tempHist = RFile1.Get(histPrefix+'__'+proc).Clone()
                                        binContent = 0
                                        binError = 0
                                        
                                        if 'Jets' in iPlot:
                                                startBin = 6
                                        else:
                                                startBin = tempHist.FindFixBin(2500-1)
                                                
                                        for ibin in range(startBin,tempHist.GetNbinsX()+1):
                                                binContent += tempHist.GetBinContent(ibin)
                                                binError += tempHist.GetBinError(ibin)**2
                                        tempHist.SetBinContent(startBin, binContent)
                                        tempHist.SetBinError(startBin, sqrt(binError))
                                        for ibin in range(startBin+1,tempHist.GetNbinsX()+1):
                                                tempHist.SetBinContent(ibin, 0)
                                                tempHist.SetBinError(ibin, 0)
                                        bkghists[proc+catStr] = tempHist
                                else:
                                        bkghists[proc+catStr] = RFile1.Get(histPrefix+'__'+proc).Clone()
                                if plotABCDnn: # and not partialBlind:
                                        if proc in minorProcList:
                                                totMinor += bkghists[proc+catStr].Integral()
                                        else:
                                                totMajor += bkghists[proc+catStr].Integral()
                        except:
                                print("There is no "+proc+"!!!!!!!!")
                                print("tried to open "+histPrefix+'__'+proc)
                                pass

                if plotNorm:
                        for proc in bkgProcList:
                                bkghists[proc+catStr].Scale(1/totBkg)
                        totBkg = 1.0

                #print(histPrefix+'__'+datalabel)
                hData = RFile1.Get(histPrefix+'__'+datalabel).Clone()
                if 'Jets' in iPlot or 'ST' in iPlot:
                        binContent = 0
                        binError = 0

                        if 'Jets' in iPlot:
                                startBin = 6
                        else:
                                startBin = hData.FindFixBin(2500-1)
                        
                        for ibin in range(startBin,hData.GetNbinsX()+1):
                                binContent += hData.GetBinContent(ibin)
                                binError += hData.GetBinError(ibin)**2
                        hData.SetBinContent(startBin, binContent)
                        hData.SetBinError(startBin, sqrt(binError))
                        for ibin in range(startBin+1,hData.GetNbinsX()+1):
                                hData.SetBinContent(ibin, 0)
                                hData.SetBinError(ibin, 0)
                        
                print('Data:',hData.Integral())
                if plotNorm:
                        hData.Scale(1/hData.Integral())

                #if plotABCDnn and not partialBlind and 'validation' not in pfix and 'V' not in region: # to scale training regions of ABCDnn
                #        print('IM SCALING BY THE FACTOR')
                #        factor = (hData.Integral()-totMinor)/totMajor
                #        for proc in ABCDnnProcList:
                #                bkghists[proc+catStr].Scale(factor)

                for proc in bkgProcList:
                        try:
                                totBkg += bkghists[proc+catStr].Integral()
                        except:
                                print('cant add',proc)
                                pass

                print('Total, Major, Minor:',totBkg,totMajor,totMinor)
                #histrange = [hData.GetBinLowEdge(1),hData.GetBinLowEdge(hData.GetNbinsX()+1)]

                if (partialBlind and (tag!="untagTlep" and tag!="untagWlep")): # Todo: generalize it for other branches
                        if ("BpMass" in iPlot) and ('validation' not in pfix):
                                start_bin = hData.GetXaxis().FindFixBin(800)+1 # specifically for BpMass
                                end_bin = hData.GetNbinsX()+1
                                for b in range(start_bin, end_bin):
                                        hData.SetBinContent(b, 0)
                                        hData.SetBinError(b, 0)
                        else:
                                sys.exit("Error: Edit partial unblinding for {}!".format(iPlot))

                #if doNormByBinWidth and tag=='tagTjet':
                #       gaeData = TGraphAsymmErrors(hData.Clone(hData.GetName().replace(datalabel,'gaeDATA')))
                #else:
                if not isCategorized and 'BpDecay' in iPlot:
                        gaeData = hData.Clone(hData.GetName().replace(datalabel,'gaeDATA'))
                else:
                        gaeData = TGraphAsymmErrors(hData.Clone(hData.GetName().replace(datalabel,'gaeDATA')))
                        if not (doNormByBinWidth and 'jet' in tag): # plot horizontal bar only for doNormByBinWidth
                                for binNo in range(0,hData.GetNbinsX()+2):
                                        gaeData.SetPointEXhigh(binNo-1,0)
                                        gaeData.SetPointEXlow(binNo-1,0)
                hsig1 = RFile1.Get(histPrefix+'__'+sig1).Clone(histPrefix+'__sig1')
                hsig2 = RFile1.Get(histPrefix+'__'+sig2).Clone(histPrefix+'__sig2')
                if 'Jets' in iPlot or 'ST' in iPlot:
                        binContent1 = 0
                        binError1 = 0
                        binContent2 = 0
                        binError2 = 0

                        if 'Jets' in iPlot:
                                startBin = 6
                        else:
                                startBin = hsig1.FindFixBin(2500-1)
                                
                        for ibin in range(startBin,hsig1.GetNbinsX()+1):
                                binContent1 += hsig1.GetBinContent(ibin)
                                binError1 += hsig1.GetBinError(ibin)**2
                                binContent2 += hsig2.GetBinContent(ibin)
                                binError2 += hsig2.GetBinError(ibin)**2
                        hsig1.SetBinContent(startBin, binContent1)
                        hsig1.SetBinError(startBin, sqrt(binError1))
                        hsig2.SetBinContent(startBin, binContent2)
                        hsig2.SetBinError(startBin, sqrt(binError2))
                        for ibin in range(startBin+1,hsig1.GetNbinsX()+1):
                                hsig1.SetBinContent(ibin, 0)
                                hsig1.SetBinError(ibin, 0)
                                hsig2.SetBinContent(ibin, 0)
                                hsig2.SetBinError(ibin, 0)
                if plotNorm:
                        hsig1.Scale(1/hsig1.Integral())
                        hsig2.Scale(1/hsig2.Integral())
                if isCategorized:
                        hsig1.Scale(0.5*xsec[sig1[3:]]) ## B singlet cross sections -- modbinning has the BR multiplier to get singlet!
                        hsig2.Scale(0.5*xsec[sig2[3:]])
                #if len(isRebinned) > 0: ## FIXME later
                #        hsig1.Scale(10) # 100fb input -> 1pb
                #        hsig2.Scale(10)
                if doNormByBinWidth and 'jet' in tag:
                        poissonNormByBinWidth(gaeData,hData,perNGeV)
                        for proc in bkgProcList:
                                try:
                                        print('normByBinWidth: '+proc)
                                        normByBinWidth(bkghists[proc+catStr],perNGeV)
                                except: pass
                        normByBinWidth(hsig1,perNGeV)
                        normByBinWidth(hsig2,perNGeV)
                        normByBinWidth(hData,perNGeV)
                elif not(not isCategorized and 'BpDecay' in iPlot): poissonErrors(gaeData) # Draw normal TH1 for easier formatting
                
                # Yes, there are easier ways using the TH1's but
                # it would be rough to swap objects lower down


                if plotABCDnn:
                        bkghists["ABCDnn"+catStr] = bkghists[ABCDnnProcList[0]+catStr].Clone()
                        for iproc in range(1,len(ABCDnnProcList)):
                                bkghists["ABCDnn"+catStr].Add(bkghists[ABCDnnProcList[iproc]+catStr])

                        bkgHT = bkghists["ABCDnn"+catStr].Clone() # perhaps redundant

                        for proc in minorProcList:
                                try:
                                        bkgHT.Add(bkghists[proc+catStr])
                                except: pass

                        print('BkgHT:',bkgHT.Integral())
                        gaeBkgHT = TGraphAsymmErrors(bkgHT.Clone("gaeBkgHT"))
                else:
                        bkgHT = bkghists[bkgProcList[0]+catStr].Clone()
                        for proc in bkgProcList:
                                if proc==bkgProcList[0]: continue
                                try: 
                                        bkgHT.Add(bkghists[proc+catStr])
                                except: pass
                        gaeBkgHT = TGraphAsymmErrors(bkgHT.Clone("gaeBkgHT"))

                #if doNormByBinWidth: poissonNormByBinWidth(gaeBkgHT,bkgHT,perNGeV)
                #else: poissonErrors(gaeBkgHT)

                #yvals = gaeBkgHT.GetY()
                #print('bkgHT = ',bkgHT.GetBinContent(25),'+/-',bkgHT.GetBinError(25))
                #print('gaeBkgHT = ',yvals[24],'+',gaeBkgHT.GetErrorYhigh(24),'-',gaeBkgHT.GetErrorYlow(24))

                if doAllSys:
                        for proc in bkgProcList:
                                if plotABCDnn and (proc in ABCDnnProcList):
                                        systematicList = systListABCDnn.copy()
                                        # try:
                                        #         systematicList.remove('factor')
                                        # except:
                                        #         print("Unable to remove factor")
                                else:
                                        if isCategorized:
                                                systematicList = systListFullPlots.copy()
                                                if isRebinned: #TEMP: update this later
                                                        try:
                                                                systematicList.remove('muR')
                                                                systematicList.remove('muF')
                                                                systematicList.remove('muRFcorrd')
                                                                systematicList.append('muRQCD')
                                                                systematicList.append('muREWK')
                                                                systematicList.append('muRST')
                                                                systematicList.append('muRTTX')
                                                                systematicList.append('muRTT')
                                                                systematicList.append('muRWJT')
                                                                systematicList.append('muFQCD')
                                                                systematicList.append('muFEWK')
                                                                systematicList.append('muFST')
                                                                systematicList.append('muFTTX')
                                                                systematicList.append('muFTT')
                                                                systematicList.append('muFWJT')
                                                                #systematicList.append('muRFcorrdNewQCD')
                                                                #systematicList.append('muRFcorrdNewEWK')
                                                                #systematicList.append('muRFcorrdNewST')
                                                                #systematicList.append('muRFcorrdNewTTX')
                                                                #systematicList.append('muRFcorrdNewTT')
                                                                #systematicList.append('muRFcorrdNewWJT')
                                                                systematicList.append('pdfNew')
                                                        except:
                                                                print("Unable to remove muR, muF, muRFcorrd and append New")
                                                else: # proxy rebinned by plotting only muRFcorrd
                                                        try:
                                                                systematicList.remove('muR')
                                                                systematicList.remove('muF')
                                                        except:
                                                                pass
                                        else:
                                                systematicList = systListShortPlots
                                for syst in systematicList:
                                        for ud in shiftlist:
                                                try:
                                                        if 'Jets' in iPlot or 'ST' in iPlot:
                                                                tempHist = RFile1.Get(f'{histPrefix}__{proc}__{syst}{ud}').Clone()
                                                                binContent = 0
                                                                binError = 0

                                                                if 'Jets' in iPlot:
                                                                        startBin = 6
                                                                else:
                                                                        startBin = tempHist.FindFixBin(2500-1)
                                                                
                                                                for ibin in range(startBin,tempHist.GetNbinsX()+1):
                                                                        binContent += tempHist.GetBinContent(ibin)
                                                                        binError += tempHist.GetBinError(ibin)**2
                                                                tempHist.SetBinContent(startBin, binContent)
                                                                tempHist.SetBinError(startBin, sqrt(binError))
                                                                for ibin in range(startBin+1,tempHist.GetNbinsX()+1):
                                                                        tempHist.SetBinContent(ibin, 0)
                                                                        tempHist.SetBinError(ibin, 0)
                                                                systHists[proc+catStr+syst+ud] = tempHist
                                                        else:
                                                                systHists[proc+catStr+syst+ud] = RFile1.Get(f'{histPrefix}__{proc}__{syst}{ud}').Clone()
                                                        
                                                        if doNormByBinWidth and 'jet' in tag: 
                                                                normByBinWidth(systHists[proc+catStr+syst+ud],perNGeV)
                                                except:
                                                        if 'Wtag' in syst and ('Tjet' in tag or 'Wlep' in tag): continue
                                                        if 'Ttag' in syst and ('Wjet' in tag or 'Tlep' in tag): continue
                                                        print(f'FAILED to open {histPrefix}__{proc}__{syst}{ud}')
                                                        pass

                totBkgTemp1[catStr] = TGraphAsymmErrors(bkgHT.Clone(bkgHT.GetName()+'shapeOnly'))
                totBkgTemp2[catStr] = TGraphAsymmErrors(bkgHT.Clone(bkgHT.GetName()+'shapePlusNorm'))
                totBkgTemp3[catStr] = TGraphAsymmErrors(bkgHT.Clone(bkgHT.GetName()+'All'))

                for ibin in range(1,bkghists[bkgProcList[0]+catStr].GetNbinsX()+1):
                        #print('--------------- bin',ibin,'--------------')
                        errorUp = 0.
                        errorDn = 0.
                        errorStatUp = gaeBkgHT.GetErrorYhigh(ibin-1)**2
                        errorStatDn = gaeBkgHT.GetErrorYlow(ibin-1)**2
                        errorNorm = (lumiSys**2)*(bkgHT.GetBinContent(ibin)**2)
                        if plotABCDnn:
                                errorNorm = (yieldUncertABCDnn[tag]*bkghists['major'+catStr].GetBinContent(ibin))**2 + (lumiSys*(bkghists['ewk'+catStr].GetBinContent(ibin)+bkghists['ttx'+catStr].GetBinContent(ibin)))**2
                        if doAllSys:
                                for syst in systematicList:
                                        for proc in bkgProcList:
                                                try:
                                                        #if ibin == 1:
                                                        #        print('for',syst,'in',proc,'found central bin',bkghists[proc+catStr].GetBinContent(ibin),'and up bin',systHists[proc+catStr+syst+shiftlist[0]].GetBinContent(ibin),'and down bin',systHists[proc+catStr+syst+shiftlist[1]].GetBinContent(ibin))
                                                        errorPlus = systHists[proc+catStr+syst+shiftlist[0]].GetBinContent(ibin)-bkghists[proc+catStr].GetBinContent(ibin)
                                                        errorMinus = bkghists[proc+catStr].GetBinContent(ibin)-systHists[proc+catStr+syst+shiftlist[1]].GetBinContent(ibin)
                                                        #if ibin == 1:
                                                        #        print('for',syst,'in',proc,'found errorPlus =',errorPlus,'and errorMinus =',errorMinus)
                                                        if errorPlus > 0:
                                                                errorUp += errorPlus**2
                                                        else: 
                                                                errorDn += errorPlus**2
                                                        if errorMinus > 0: 
                                                                errorDn += errorMinus**2
                                                        else: 
                                                                errorUp += errorMinus**2
                                                except: pass

                        totBkgTemp1[catStr].SetPointEYhigh(ibin-1,math.sqrt(errorUp))
                        totBkgTemp1[catStr].SetPointEYlow(ibin-1, math.sqrt(errorDn))
                        totBkgTemp2[catStr].SetPointEYhigh(ibin-1,math.sqrt(errorUp+errorNorm))
                        totBkgTemp2[catStr].SetPointEYlow(ibin-1, math.sqrt(errorDn+errorNorm))
                        totBkgTemp3[catStr].SetPointEYhigh(ibin-1,math.sqrt(errorUp+errorNorm+errorStatUp))
                        totBkgTemp3[catStr].SetPointEYlow(ibin-1, math.sqrt(errorDn+errorNorm+errorStatDn))

                bkgHTgerr = totBkgTemp3[catStr].Clone()

                scaleFact1 = int(bkgHT.GetMaximum()/hsig1.GetMaximum()) - int(bkgHT.GetMaximum()/hsig1.GetMaximum()) % 10
                scaleFact2 = int(bkgHT.GetMaximum()/hsig2.GetMaximum()) - int(bkgHT.GetMaximum()/hsig2.GetMaximum()) % 10
                if scaleFact1==0: scaleFact1=int(bkgHT.GetMaximum()/hsig1.GetMaximum())
                if scaleFact2==0: scaleFact2=int(bkgHT.GetMaximum()/hsig2.GetMaximum())
                if scaleFact1==0: scaleFact1=1
                if scaleFact2==0: scaleFact2=1
                if sigScaleFact>0:
                        scaleFact1=sigScaleFact
                        scaleFact2=sigScaleFact
                        if isCategorized:
                                scaleFact1 *= 0.25
                if not scaleSignals:
                        scaleFact1=1
                        scaleFact2=1
                        if isCategorized:
                                if yLog:
                                        if 'jet' in tag:
                                                if 'BprimeT' in templateDir:
                                                        scaleFact2=20
                                                else:
                                                        scaleFact2=5

                                                if 'x' not in sig2leg:
                                                        sig2leg+=f' x {scaleFact2}'
                                        else:
                                                sig2leg = sig2leg.split('x')[0]
                                else:
                                        if 'tagT' in tag and region=='D':
                                                scaleFact1 = 50
                                                scaleFact2 = 100
                                        else:
                                                scaleFact1=50
                                                scaleFact2=1000
                                        if 'x' not in sig1leg:
                                                sig1leg+=f' x {scaleFact1}'
                                        if 'x' not in sig2leg:
                                                sig2leg+=f' x {scaleFact2}'
                        else:
                                scaleFact1=100 # scale kinematicsAll to 1pb
                                scaleFact2=100
                hsig1.Scale(scaleFact1)
                hsig2.Scale(scaleFact2)

                ############################################################
                ############## Making Plots of e+jets, mu+jets and e/mu+jets 
                ############################################################

                if plotABCDnn:
                        drawQCD = False
                else:                        
                        drawQCD = True

                try: 
                        drawQCD = bkghists['qcd'+catStr].Integral()/bkgHT.Integral()>.005 #don't plot QCD if it is less than 0.5%
                except:
                        drawQCD = False
                        pass

                #drawQCD = True # SWITCH

                stackbkgHT = THStack("stackbkgHT","")
                bkgProcListNew = bkgProcList[:]
                if region=='WJCR':
                        bkgProcListNew[bkgProcList.index("top")],bkgProcListNew[bkgProcList.index("ewk")]=bkgProcList[bkgProcList.index("ewk")],bkgProcList[bkgProcList.index("top")]
                if plotABCDnn:
                        bkgProcListNew = minorProcList + ["ABCDnn"]
                        #print(bkgProcListNew)
                for proc in bkgProcListNew:
                        try: 
                                #bkghists[proc+catStr].Print()
                                if drawQCD or proc!='qcd': stackbkgHT.Add(bkghists[proc+catStr])
                        except: pass

                sig1Color= kBlack
                sig2Color= kBlack

                if plotABCDnn:
                        bkghists["ABCDnn"+catStr].SetLineColor(bkgHistColors["ABCDnn"])
                        bkghists["ABCDnn"+catStr].SetFillColor(bkgHistColors["ABCDnn"])
                        bkghists["ABCDnn"+catStr].SetLineWidth(2)
                        for proc in minorProcList:
                                try:
                                        bkghists[proc+catStr].SetLineColor(bkgHistColors[proc])
                                        bkghists[proc+catStr].SetFillColor(bkgHistColors[proc])
                                        bkghists[proc+catStr].SetLineWidth(2)
                                except: pass
                else:
                        for proc in bkgProcList:
                                try: 
                                        bkghists[proc+catStr].SetLineColor(bkgHistColors[proc])
                                        bkghists[proc+catStr].SetFillColor(bkgHistColors[proc])
                                        bkghists[proc+catStr].SetLineWidth(2)
                                except: pass                        
                hsig1.SetLineColor(sig1Color)
                hsig1.SetFillStyle(0)
                hsig1.SetLineWidth(3)
                hsig2.SetLineColor(sig2Color)
                hsig2.SetLineStyle(7)#5)
                hsig2.SetFillStyle(0)
                hsig2.SetLineWidth(3)

                gaeData.SetMarkerStyle(20)
                gaeData.SetMarkerSize(1.2)
                gaeData.SetLineWidth(2)
                gaeData.SetMarkerColor(kBlack)
                gaeData.SetLineColor(kBlack)

                #bkgHTgerr.SetMarkerStyle(21)
                #bkgHTgerr.SetMarkerColor(kBlack)
                bkgHTgerr.SetFillStyle(3004)
                bkgHTgerr.SetFillColor(kBlack)
                bkgHTgerr.SetLineColor(kBlack)

                gStyle.SetOptStat(0)
                #CMS.SetExtraText("") # "Preliminary"
                #CMS.SetLumi(138)
                #c1 = CMS.cmsCanvas("c1",0,1,0,1, 'B quark ', 'Events/GeV', extraSpace=0.01, iPos=0) # out-of-frame # paper
                c1 = TCanvas("c1","c1",1200,1000) # used to be 1200 and 1000, but the y-axis labels might overlap
                #if doNormByBinWidth and tag=='tagTjet':
                #       gStyle.SetErrorX(0.5)
                #else:
                #       gStyle.SetErrorX(0)
                gStyle.SetErrorX(0.5)
                yDiv=0.3 #0.25
                if blind == True: yDiv=0.01
                # for some reason the markers at 0 don't show with this setting:
                uMargin = 0.02 #0.00001
                if blind == True: uMargin = 0.12
                rMargin=.04
                # overlap the pads a little to hide the error bar gap:
                uPad={}
                if yLog and not blind:
                        #uPad=TPad("uPad","",0,yDiv-0.009,1,1) #for actual plots
                        uPad=TPad("uPad","",0,yDiv,1,1)
                else: 
                        uPad=TPad("uPad","",0,yDiv,1,1) #for actual plots
                uPad.SetTopMargin(0.09)
                #if isCategorized:
                #        uPad.SetTopMargin(0.08)
                #else:
                #        uPad.SetTopMargin(0.13)
                uPad.SetBottomMargin(uMargin)
                uPad.SetRightMargin(rMargin)
                uPad.SetLeftMargin(0.15) #used to be 0.105. y axis label overlaps with title
                uPad.Draw()
                
                if blind == False:
                        lPad=TPad("lPad","",0,0,1,yDiv) #for sigma runner
                        lPad.SetTopMargin(0)
                        lPad.SetBottomMargin(.4)
                        lPad.SetRightMargin(rMargin)
                        lPad.SetLeftMargin(0.15) #used to be 0.105. y axis label overlaps with title
                        lPad.SetGridy()
                        lPad.Draw()
                if not (doNormByBinWidth and 'jet' in tag): hData.SetMaximum(1.4*max(hData.GetMaximum(),bkgHT.GetMaximum()))
                hData.SetMinimum(0.015)
                hData.SetTitle("")
                # this is super important now!! gaeData has badly defined (negative) maximum
                gaeData.SetMaximum(1.2*max(hData.GetMaximum(),bkgHT.GetMaximum()))
                gaeData.SetMinimum(0.015)
                gaeData.SetTitle("")
                if doNormByBinWidth and 'jet' in tag:
                        if iPlot == 'DnnTprime' or (iPlot == 'HTNtag' and perNGeV < 10):
                                gaeData.GetYaxis().SetTitle("< Events / "+str(perNGeV)+" >")
                        else: 
                                gaeData.GetYaxis().SetTitle("< Events / "+str(perNGeV)+" GeV >")
                else:
                    if region == 'all':
                            if iPlot == 'BpMass':
                                    gaeData.GetYaxis().SetTitle("Events / 50 GeV")
                            elif iPlot == 'ST':
                                    gaeData.GetYaxis().SetTitle("Events / 100 GeV")
                    elif iPlot == 'BpMass' or isCategorized:
                            gaeData.GetYaxis().SetTitle("Events / 20 GeV")
                    else:
                        gaeData.GetYaxis().SetTitle("Events / bin")

                formatUpperHist(gaeData,hData)
                uPad.cd()
                gaeData.SetTitle("")
                #gaeData.GetXaxis().SetTickLength(0)
                if not blind:
                        # if doNormByBinWidth and tag=='tagTjet':
                        #         gaeData.Draw("apz")
                        # else:
                        #         gaeData.Draw("apz")
                        if not isCategorized and 'BpDecay' in iPlot:
                                gaeData.Draw("PEX0")
                        else:
                                gaeData.Draw("apz")
                                # if doNormByBinWidth and tag=='tagTjet':
                                #         gaeData.Draw("apz")
                                # else:
                                #         gaeData.Draw("apzex0")
                if blind: 
                        hsig1.SetMinimum(0.015)
                        if doNormByBinWidth and 'jet' in tag:
                                if iPlot == 'DnnTprime' or (iPlot == 'HTNtag' and perNGeV < 10): 
                                        hsig1.GetYaxis().SetTitle("< Events / "+str(perNGeV)+" >")
                                else: hsig1.GetYaxis().SetTitle("< Events / "+str(perNGeV)+" GeV >")
                        else: hsig1.GetYaxis().SetTitle("Events / bin")
                        hsig1.SetMaximum(1.5*hData.GetMaximum())
                        if iPlot=='Tau21Nm1': hsig1.SetMaximum(1.5*hData.GetMaximum())
                        formatUpperHist(hsig1,hsig1)
                        hsig1.Draw("HIST")
                if doNormByBinWidth and 'jet' in tag:
                        if iPlot == 'DnnTprime' or (iPlot == 'HTNtag' and perNGeV < 10): 
                                hData.GetYaxis().SetTitle("Events / "+str(perNGeV))
                        else: 
                                hData.GetYaxis().SetTitle("Events / "+str(perNGeV)+" GeV")
                else: hData.GetYaxis().SetTitle("Events / bin")

                stackbkgHT.Draw("SAME HIST")
                hsig1.Draw("SAME HIST")
                hsig2.Draw("SAME HIST")
                if not blind:
                        # if doNormByBinWidth and tag=="tagTjet":
                        #         gaeData.Draw("PZ") #redraw data so its not hidden
                        # else:
                        if not isCategorized and 'BpDecay' in iPlot:
                                gaeData.Draw("PEX0 SAME") #redraw data so its not hidden
                        else:
                                gaeData.Draw("PZ")
                                #gaeData.Draw("PZEX0") #redraw data so its not hidden
                uPad.RedrawAxis()
                bkgHTgerr.Draw("SAME E2")
                #bkgHTgerr.Draw("SAME PE")

                chLatex = TLatex()
                chLatex.SetNDC()
                chLatex.SetTextSize(0.07)
                if blind: chLatex.SetTextSize(0.04)
                chLatex.SetTextAlign(21) # align center
                flvString = ''
                tagString = ''
                if isEM=='E': flvString+='e+jets'
                if isEM=='M': flvString+='#mu+jets'
                if isEM=='L': flvString+='' #'e/#mu+jets'
                tagString = ''
                regionString = ''
                if isCategorized:
                        if tag == 'tagTjet':
                                tagString = 'Case 1'
                        elif tag == 'tagWjet':
                                tagString = 'Case 2'
                        elif tag == 'untagTlep':
                                tagString = 'Case 3'
                        else:
                                tagString = 'Case 4'
                        regionString = 'region '+region
                        if region == 'V' or (region == 'V2' and 'untag' not in tag):
                                regionString = 'VR'                                
                        elif region == 'V2' and 'untag' in tag:
                                regionString = 'VR'
                        elif region == 'D':
                                regionString = 'SR'
                if tagString.endswith(', '): tagString = tagString[:-2]		
                if not yLog:
                        # if isCategorized:
                        #         chLatex.DrawLatex(0.7, 0.54, flvString)
                        #         chLatex.DrawLatex(0.7, 0.48, tagString)
                        #         chLatex.DrawLatex(0.7, 0.42, regionString)
                        # else:
                        #         chLatex.DrawLatex(0.7, 0.49, flvString)
                        #         chLatex.DrawLatex(0.7, 0.43, tagString)
                        #         chLatex.DrawLatex(0.7, 0.37, regionString)
                        chLatex.SetTextAlign(12)
                        chLatex.DrawLatex(0.7, 0.54, flvString)
                        chLatex.DrawLatex(0.7, 0.48, tagString)
                        chLatex.DrawLatex(0.7, 0.42, regionString)
                else:
                        chLatex.SetTextAlign(12)
                        chLatex.DrawLatex(0.2, 0.80, flvString)
                        chLatex.DrawLatex(0.2, 0.74, tagString)
                        chLatex.DrawLatex(0.2, 0.84, regionString)
                        # if isCategorized:
                        #         chLatex.DrawLatex(0.3, 0.85, flvString)
                        #         chLatex.DrawLatex(0.3, 0.79, tagString)
                        #         chLatex.DrawLatex(0.3, 0.73, regionString)
                        # else:
                        #         chLatex.DrawLatex(0.3, 0.80, flvString)
                        #         chLatex.DrawLatex(0.3, 0.74, tagString)
                        #         chLatex.DrawLatex(0.3, 0.68, regionString)

                if isCategorized:
                        leg = TLegend(0.35,0.52,0.92,0.88)
                        # needs more horizontal space b/c xsecs
                else:
                        if iPlot == 'BpDecay':
                                leg = TLegend(0.19,0.41,0.71,0.77)
                        else:
                                leg = TLegend(0.40,0.52,0.92,0.88)
                #leg = TLegend(0.47,0.62,0.92,0.89)
                
                leg.SetShadowColor(0)
                leg.SetFillColor(0)
                leg.SetFillStyle(0)
                leg.SetLineColor(0)
                leg.SetLineStyle(0)
                leg.SetBorderSize(0) 
                leg.SetNColumns(2)
                #leg.SetTextFont(62)#42)
                scaleFact1Str = ' x'+str(scaleFact1)
                scaleFact2Str = ' x'+str(scaleFact2)
                if not scaleSignals:
                        scaleFact1Str = ''
                        scaleFact2Str = ''
                if drawQCD:
                        if not blind:
                                if doNormByBinWidth and "jet" in tag:
                                        leg.AddEntry(gaeData,"Data","pel")  #left
                                else:
                                        leg.AddEntry(gaeData,"Data","pex")  #left
                                try:
                                        leg.AddEntry(bkghists['ewk'+catStr],"DY+VV","f") #right
                                except: pass
                                leg.AddEntry(hsig1,sig1leg+scaleFact1Str,"l")  #left
                                try:
                                        leg.AddEntry(bkghists['ttx'+catStr],"t#bar{t}+(V,H)","f") #right
                                except: pass
                                leg.AddEntry(hsig2,sig2leg+scaleFact2Str,"l") #left
                                leg.AddEntry(bkghists['qcd'+catStr],"QCD","f") #right
                                try:
                                        leg.AddEntry(bkghists['wjets'+catStr],"W+jets","f") #left
                                except: pass
                                try:
                                        leg.AddEntry(bkghists['ttbar'+catStr],"t#bar{t}","f") #right
                                except: pass
                                try:
                                        leg.AddEntry(bkghists['singletop'+catStr],"single t","f") #left
                                except: pass
                                leg.AddEntry(bkgHTgerr,"Bkg. Uncert.","f") #right
                                #leg.AddEntry(0, "", "") #left
                        else:
                                leg.AddEntry(hsig1,sig1leg+scaleFact1Str,"l")  #left
                                try: 
                                        leg.AddEntry(bkghists['wjets'+catStr],"W+jets","f") #right 
                                except: pass
                                leg.AddEntry(hsig2,sig2leg+scaleFact2Str,"l") #left
                                try: 
                                        leg.AddEntry(bkghists['ewk'+catStr],"DY+VV","f") #right
                                except: pass
                                try: 
                                        leg.AddEntry(bkghists['ttbar'+catStr],"t#bar{t}","f") #left
                                except: pass
                                try: 
                                        leg.AddEntry(bkghists['ttx'+catStr],"t#bar{t}+(V,H)","f") #right
                                except: pass
                                try: 
                                        leg.AddEntry(bkghists['singletop'+catStr],"single t","f") #left
                                except: pass
                                leg.AddEntry(bkghists['qcd'+catStr],"QCD","f") #right
                                leg.AddEntry(0, "", "") #left
                                leg.AddEntry(bkgHTgerr,"Bkg. Uncert.","f") #right

                if not drawQCD:
                        if not blind:
                                if plotABCDnn:
                                        if doNormByBinWidth and "jet" in tag:
                                                leg.AddEntry(gaeData,"Data","pel")
                                        else:
                                                leg.AddEntry(gaeData,"Data","pex")
                                        leg.AddEntry(bkghists['ABCDnn'+catStr],"ABCDnn","f")
                                        leg.AddEntry(hsig1,sig1leg+scaleFact1Str,"l")  #left
                                        leg.AddEntry(bkghists['ewk'+catStr],"DY+VV","f")
                                        leg.AddEntry(hsig2,sig2leg+scaleFact2Str,"l") #left              
                                        leg.AddEntry(bkghists['ttx'+catStr],"t#bar{t}+(V,H)","f")
                                        leg.AddEntry(0,"","")  #left
                                        leg.AddEntry(bkgHTgerr,"Bkg. Uncert.","f")

                                else:
                                        try: 
                                                leg.AddEntry(bkghists['ttx'+catStr],"t#bar{t}+(V,H)","f") #right
                                        except: pass
                                        leg.AddEntry(hsig1,sig1leg+scaleFact1Str,"l")  #left
                                        try: 
                                                leg.AddEntry(bkghists['wjets'+catStr],"W+jets","f") #right
                                        except: pass
                                        leg.AddEntry(hsig2,sig2leg+scaleFact2Str,"l") #left
                                        try: 
                                                leg.AddEntry(bkghists['ewk'+catStr],"DY+VV","f") #right
                                        except: pass
                                        try: 
                                                leg.AddEntry(bkghists['ttbar'+catStr],"t#bar{t}","f") #left
                                        except: pass
                                        try: 
                                                leg.AddEntry(bkghists['singletop'+catStr],"single t","f") #left
                                        except: pass
                                        #leg.AddEntry(0, "", "") #left
                                        leg.AddEntry(bkgHTgerr,"Bkg. Uncert.","f") #right
                        else:
                                leg.AddEntry(hsig1,sig1leg+scaleFact1Str,"l")  #left
                                try: 
                                        leg.AddEntry(bkghists['ttx'+catStr],"t#bar{t}+(V,H)","f") #right
                                except: pass
                                leg.AddEntry(hsig2,sig2leg+scaleFact2Str,"l") #left
                                try: 
                                        leg.AddEntry(bkghists['wjets'+catStr],"W+jets","f") #right
                                except: pass
                                try: 
                                        leg.AddEntry(bkghists['ttbar'+catStr],"t#bar{t}","f") #left
                                except: pass
                                try: 
                                        leg.AddEntry(bkghists['ewk'+catStr],"DY+VV","f") #right
                                except: pass
                                try: 
                                        leg.AddEntry(bkghists['singletop'+catStr],"single t","f") #left
                                except: pass
                                leg.AddEntry(0, "", "") #left
                                leg.AddEntry(bkgHTgerr,"Bkg. Uncert.","f") #right


                leg.Draw("same")

                prelimTex=TLatex()
                prelimTex.SetNDC()
                prelimTex.SetTextAlign(31)
                prelimTex.SetTextSize(0.07)
                if blind: prelimTex.SetTextSize(0.05)
                prelimTex.SetLineWidth(2)
                prelimTex.DrawLatex(0.95,0.94,str(lumi)+" fb^{-1} (13 TeV)")

                prelimTex3=TLatex()
                prelimTex3.SetNDC()
                prelimTex3.SetTextAlign(11)

                prelimTex3.SetTextSize(0.10)
                if isCategorized:
                        prelimTex3.DrawLatex(0.15,0.93,"#bf{CMS}")
                else:
                        prelimTex3.DrawLatex(0.19,0.80,"#bf{CMS}")

                if isPrelim:
                        prelimTex4 = TLatex()
                        prelimTex4.SetNDC()
                        prelimTex4.SetTextFont(52)
                        prelimTex4.SetTextAlign(11)
                        prelimTex4.SetTextSize(0.07)
                        prelimTex4.SetLineWidth(2)
                        if isCategorized:
                                prelimTex4.DrawLatex(0.28,0.93,"Preliminary")
                        else:
                                if iPlot == 'BpDecay':
                                        prelimTex4.DrawLatex(0.32,0.80,"Preliminary")
                                else:
                                        prelimTex4.DrawLatex(0.19,0.72,"Preliminary")


                if blind == False and not doRealPull:
                        lPad.cd()
                        pull=hData.Clone(hData.GetName()+"pull")
                        pull.Divide(hData, bkgHT)
                        for binNo in range(0,hData.GetNbinsX()+2):
                                if bkgHT.GetBinContent(binNo)!=0:
                                        pull.SetBinError(binNo,hData.GetBinError(binNo)/bkgHT.GetBinContent(binNo))
                        pull.SetMaximum(3)
                        pull.SetMinimum(0)
                        pull.SetFillColor(1)
                        pull.SetLineColor(1)
                        pull.SetMarkerStyle(20)

                        formatLowerHist(pull)
                        if doNormByBinWidth and 'jet' in tag:
                                pull.Draw("E0") #E0
                        else:
                                pull.Draw("EX0")

                        BkgOverBkg = pull.Clone("bkgOverbkg")
                        BkgOverBkg.Divide(bkgHT, bkgHT)
                        pullUncBandTot=TGraphAsymmErrors(BkgOverBkg.Clone("pulluncTot"))
                        for binNo in range(0,hData.GetNbinsX()+2):
                                if bkgHT.GetBinContent(binNo)!=0:
                                        pullUncBandTot.SetPointEYhigh(binNo-1,totBkgTemp3[catStr].GetErrorYhigh(binNo-1)/bkgHT.GetBinContent(binNo))
                                        pullUncBandTot.SetPointEYlow(binNo-1,totBkgTemp3[catStr].GetErrorYlow(binNo-1)/bkgHT.GetBinContent(binNo))			
                        if not doOneBand:
                                pullUncBandTot.SetFillStyle(3001)
                        else:
                                #pullUncBandTot.SetFillStyle(3344)
                                pullUncBandTot.SetFillStyle(3004)
                        pullUncBandTot.SetFillColor(1)
                        pullUncBandTot.SetLineColor(1)
                        pullUncBandTot.SetMarkerSize(0)
                        gStyle.SetHatchesLineWidth(1)
                        pullUncBandTot.Draw("SAME E2")

                        pullUncBandNorm=TGraphAsymmErrors(BkgOverBkg.Clone("pulluncNorm"))
                        for binNo in range(0,hData.GetNbinsX()+2):
                                if bkgHT.GetBinContent(binNo)!=0:
                                        pullUncBandNorm.SetPointEYhigh(binNo-1,totBkgTemp2[catStr].GetErrorYhigh(binNo-1)/bkgHT.GetBinContent(binNo))
                                        pullUncBandNorm.SetPointEYlow(binNo-1,totBkgTemp2[catStr].GetErrorYlow(binNo-1)/bkgHT.GetBinContent(binNo))			

                        pullUncBandNorm.SetFillStyle(3001)
                        pullUncBandNorm.SetFillColor(2)
                        pullUncBandNorm.SetLineColor(2)
                        pullUncBandNorm.SetMarkerSize(0)
                        gStyle.SetHatchesLineWidth(1)
                        if not doOneBand: pullUncBandNorm.Draw("SAME E2")

                        pullUncBandStat=TGraphAsymmErrors(BkgOverBkg.Clone("pulluncStat"))
                        for binNo in range(0,hData.GetNbinsX()+2):
                                if bkgHT.GetBinContent(binNo)!=0:
                                        pullUncBandStat.SetPointEYhigh(binNo-1,totBkgTemp1[catStr].GetErrorYhigh(binNo-1)/bkgHT.GetBinContent(binNo))
                                        pullUncBandStat.SetPointEYlow(binNo-1,totBkgTemp1[catStr].GetErrorYlow(binNo-1)/bkgHT.GetBinContent(binNo))			

                        pullUncBandStat.SetFillStyle(3001)
                        pullUncBandStat.SetFillColor(3)
                        pullUncBandStat.SetLineColor(3)
                        pullUncBandStat.SetMarkerSize(0)
                        gStyle.SetHatchesLineWidth(1)
                        if not doOneBand: pullUncBandStat.Draw("SAME E2")

                        if doNormByBinWidth and	'jet' in tag:
                                pull.Draw("SAME E0") #E0
                        else:
                                pull.Draw("SAME EX0")
                        lPad.RedrawAxis()

                if blind == False and doRealPull:
                        formatUpperHist(hData,hData)
                        lPad.cd()
                        pull=hData.Clone(hData.GetName()+"pull")
                        for binNo in range(1,hData.GetNbinsX()+1):
                                # case for data < MC:
                                dataerror = gaeData.GetErrorYhigh(binNo-1)
                                MCerror = totBkgTemp3[catStr].GetErrorYlow(binNo-1)
                                # case for data > MC: 
                                if(hData.GetBinContent(binNo) > bkgHT.GetBinContent(binNo)):
                                        dataerror = gaeData.GetErrorYlow(binNo-1)
                                        MCerror = totBkgTemp3[catStr].GetErrorYhigh(binNo-1)
                                pull.SetBinContent(binNo,(hData.GetBinContent(binNo)-bkgHT.GetBinContent(binNo))/math.sqrt(MCerror**2+dataerror**2))
                        pull.SetMaximum(3)
                        pull.SetMinimum(-3)
                        pull.SetFillColor(kGray+2)
                        pull.SetLineColor(kGray+2)
                        formatLowerHist(pull)
                        pull.Draw("HIST")

                savePrefix = templateDir+templateDir.split('/')[-2]+'plots/'
                if not os.path.exists(savePrefix): os.system('mkdir '+savePrefix)
                savePrefix+=histPrefix+isRebinned.replace('_rebinned_stat1p1','')+saveKey
                if year != 'all': savePrefix=savePrefix.replace(lumiInTemplates,year)
                if doRealPull: savePrefix+='_pull'
                if doNormByBinWidth: savePrefix+='_NBBW'
                if yLog: savePrefix+='_logy'
                if blind: savePrefix+='_blind'
                if isPrelim: savePrefix+='_prelim'

                if doOneBand:
                        if plotNorm:
                                c1.SaveAs(f"{savePrefix}totBand_norm_paper.pdf")
                                c1.SaveAs(f"{savePrefix}totBand_norm_paper.png")
                        else:
                                c1.SaveAs(f"{savePrefix}totBand_paper.pdf")
                                c1.SaveAs(f"{savePrefix}totBand_paper.png")
                                #c1.SaveAs(savePrefix+"totBand.eps")
                                #c1.SaveAs(savePrefix+"totBand.root")
                                #c1.SaveAs(savePrefix+"totBand.C")
                else:
                        if plotNorm:
                                c1.SaveAs(f"{savePrefix}_norm_paper.pdf")
                                c1.SaveAs(f"{savePrefix}_norm_paper.png")
                        else:
                                c1.SaveAs(f"{savePrefix}_paper.pdf")
                                c1.SaveAs(f"{savePrefix}_paper.png")
                                #c1.SaveAs(savePrefix+".eps")
                                #c1.SaveAs(savePrefix+".root")
                                #c1.SaveAs(savePrefix+".C")
                for proc in bkgProcList:
                        try: 
                                del bkghists[proc+catStr]
                        except: pass


RFile1.Close()

print("--- %s minutes ---" % (round(time.time() - start_time, 2)/60))
