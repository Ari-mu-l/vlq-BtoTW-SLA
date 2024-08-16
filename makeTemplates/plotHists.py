#!/usr/bin/python

# python3 -u plotHists.py BpMass A True 

import os,sys,time,math
parent = os.path.dirname(os.getcwd())
sys.path.append(parent)
from ROOT import *
from samples import lumiStr, systListShortPlots, systListFullPlots,  systListABCDnn
from utils import *

gROOT.SetBatch(1)
start_time = time.time()

lumi=138. #for plots #56.1 #
lumiInTemplates= lumiStr

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
sig1='BpM1000' #  choose the 1st signal to plot
sig1leg='B (1.0 TeV, 1 pb)'
sig2='BpM1800' #  choose the 2nd signal to plot
sig2leg='B (1.8 TeV, 1 pb)'


scaleSignals = False
if not isCategorized: scaleSignals = True
sigScaleFact = 100
print('Scaling signals?',scaleSignals)
print('Scale factor = ',sigScaleFact)
tempsig='templates_'+iPlot+'_'+lumiInTemplates+''+isRebinned+'.root'#+'_Data18.root'
if year != 'all': tempsig='templates_'+iPlot+'_'+year+''+isRebinned+'.root'#+'_Data18.root'

plotABCDnn = False
plotLowSide = True
if 'ABCDnn' in iPlot:
        plotABCDnn = True

if len(isRebinned)>1 and 'ABCDnn' in iPlot:
        bkgProcList = ['ewk', 'ttx', 'major']
        ABCDnnProcList = ['major']
else:
        bkgProcList = ['ttx',
                       'qcd',
                       'ewk',
                       'wjets',                       
                       'singletop',
                       'ttbar'
                       ]
        ABCDnnProcList = ['qcd','wjets','singletop','ttbar']
minorProcList = ['ewk', 'ttx']


if plotABCDnn:
        bkgHistColors = {'ABCDnn': kRed-7,'ewk':kMagenta-6,'ttx':kAzure+2}
else:
        bkgHistColors = {'ttbar':kAzure+8,'wjets':kMagenta-2,'qcd':kOrange-3,'ewk':kMagenta-6,'singletop':kGreen-6,'ttx':kAzure+2}

doAllSys = True

doNormByBinWidth=False
if len(isRebinned)>0 and 'stat1p1' not in isRebinned and 'mvagof' not in isRebinned: doNormByBinWidth = True

doOneBand = True
if not doAllSys: doOneBand = True # Don't change this!
doRealPull = False
if doRealPull: doOneBand=False

plotNorm = False

blind = False
if len(sys.argv)>5: blind=bool(eval(sys.argv[5]))

yLog  = False
if len(sys.argv)>6: yLog=bool(eval(sys.argv[6]))
print('Plotting blind?',blind,' yLog?',yLog)
if yLog: scaleSignals = False

partialBlind = False

isEMlist =['L']#'E','M']
taglist = ['all']
if isCategorized == True:
        #taglist=['tagTjet','tagWjet','untagTlep','untagWlep','allWlep','allTlep']
        taglist = ['tagTjet','tagWjet','untagWlep','untagTlep']
        #taglist = ['allWlep','allTlep']
        if ('D' in region or 'C' in region or region=='all') and 'BpMass' in iPlot and 'validation' not in pfix:
                partialBlind = True
                print(f'Partial blind {iPlot} for {region}.')

lumiSys = 0.018 # lumi uncertainty

#### Consider: Did not set removeThreshold
####           No doPDF

def getNormUnc(hist,ibin,modelingUnc):
        contentsquared = hist.GetBinContent(ibin)**2
        error = lumiSys*lumiSys*contentsquared  #might be others in future
        return error

def formatUpperHist(histogram,th1hist):
        histogram.GetXaxis().SetLabelSize(0)
        if plotLowSide:
                lowside = th1hist.GetBinLowEdge(1)
        else:
                lowside =  500 #TEMP: plotting only high BpM for ABCDnn
        highside = th1hist.GetBinLowEdge(th1hist.GetNbinsX()+1)
        histogram.GetXaxis().SetRangeUser(lowside,highside)
        histogram.GetXaxis().SetNdivisions(506)
                
        #if 'BpMass' in histogram.GetName():
        #        histogram.GetYaxis().SetTitleOffset(1.0)

        if 'JetTag' in histogram.GetName():
                print('RELABELING!',histogram.GetName())
                labels = ['b/light','t','W','both']
                for ibin in range(1,th1hist.GetNbinsX()+1):
                        histogram.GetXaxis().SetBinLabel(ibin,labels[ibin-1])
                histogram.GetXaxis().SetLabelSize(0.25)
                histogram.GetXaxis().SetTitleOffset(1.0)
        if 'BpDecay' in histogram.GetName():
                print('RELABELING!',histogram.GetName())
                labels = ['','T+lepW','W+lepT','X+lepT','X+lepW']
                for ibin in range(1,th1hist.GetNbinsX()+1):
                        histogram.GetXaxis().SetBinLabel(ibin,labels[ibin-1])
                histogram.GetXaxis().SetLabelSize(0.25)
                histogram.GetXaxis().SetTitleOffset(1.0)
                histogram.GetXaxis().SetTitle('B quark decay mode')

        if blind == True:
                histogram.GetXaxis().SetLabelSize(0.045)
                histogram.GetXaxis().SetTitleSize(0.055)
                histogram.GetYaxis().SetLabelSize(0.04)
                histogram.GetYaxis().SetTitleSize(0.05)
                histogram.GetYaxis().SetTitleOffset(1.1)
                if 'YLD' in iPlot: histogram.GetXaxis().LabelsOption("u")
        else:
                histogram.GetYaxis().SetLabelSize(0.05)
                histogram.GetYaxis().SetTitleSize(0.06)
                histogram.GetYaxis().SetTitleOffset(1.1) #used to be 0.82. overlaps with label

        histogram.GetYaxis().CenterTitle()
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
                        if not doNormByBinWidth:
                                histogram.SetMaximum(500*histogram.GetMaximum())
                        else: 
                                histogram.SetMaximum(200*histogram.GetMaximum())
                        if iPlot=='YLD': 
                                histogram.SetMaximum(200*histogram.GetMaximum())
                                histogram.SetMinimum(0.1)

def formatLowerHist(histogram):
        histogram.GetXaxis().SetLabelSize(.15)
        histogram.GetXaxis().SetTitleSize(0.18)
        histogram.GetXaxis().SetTitleOffset(0.95)
        histogram.GetXaxis().SetNdivisions(506)
        if 'YLD' in iPlot: histogram.GetXaxis().LabelsOption("u")

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
                labels = ['','T+lepW','W+lepT','X+lepT','X+lepW']
                for ibin in range(1,histogram.GetNbinsX()+1):
                        histogram.GetXaxis().SetBinLabel(ibin,labels[ibin-1])
                histogram.GetXaxis().SetLabelSize(0.25)
                histogram.GetXaxis().SetTitleOffset(1.0)
                histogram.GetXaxis().SetTitle('B quark decay mode')

        histogram.GetYaxis().SetLabelSize(0.15)
        histogram.GetYaxis().SetTitleSize(0.145)
        histogram.GetYaxis().SetTitleOffset(0.3)
        if not doRealPull: 
                histogram.GetYaxis().SetTitle('Data/Bkg')
        else: 
                histogram.GetYaxis().SetTitle('#frac{(data-bkg)}{std. dev.}')
        histogram.GetYaxis().SetNdivisions(7)
        if doRealPull: 
                histogram.GetYaxis().SetRangeUser(-2.99,2.99)
        elif yLog and doNormByBinWidth:
                histogram.GetYaxis().SetRangeUser(0.1,1.9)
        else: 
                histogram.GetYaxis().SetRangeUser(0.1,1.9)
        histogram.GetYaxis().CenterTitle()
        if not plotLowSide:
                lowside =  500 #TEMP
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
        perNGeV = 50 # choose what "unit" to use for bin widths, similar to the smaller bin widths in the plot. Values < 1 are ok for e.g. NN scores
        print('------------------ ',tag,' with perNGeV = ',perNGeV,' -----------------------')

        tagStr=tag
        for isEM in isEMlist:
                histPrefix=iPlot+'_'+lumiInTemplates+'_'
                catStr='is'+isEM+'_'+tagStr
                histPrefix+=catStr
                if isCategorized: histPrefix+='_'+region
                totBkg = 0.
                totMajor = 0.
                totMinor = 0.
                for proc in bkgProcList: 
                        try:
                                bkghists[proc+catStr] = RFile1.Get(histPrefix+'__'+proc).Clone()
                                if plotABCDnn and not partialBlind:
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
                if plotNorm:
                        hData.Scale(1/hData.Integral())

                if plotABCDnn and not partialBlind: # to scale training regions of ABCDnn
                        factor = (hData.Integral()-totMinor)/totMajor
                        for proc in ABCDnnProcList:
                                bkghists[proc+catStr].Scale(factor)

                for proc in bkgProcList:
                        try:
                                totBkg += bkghists[proc+catStr].Integral()
                        except:
                                print('cant add',proc)
                                pass

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

                gaeData = TGraphAsymmErrors(hData.Clone(hData.GetName().replace(datalabel,'gaeDATA')))
                hsig1 = RFile1.Get(histPrefix+'__'+sig1).Clone(histPrefix+'__sig1')
                hsig2 = RFile1.Get(histPrefix+'__'+sig2).Clone(histPrefix+'__sig2')
                if plotNorm:
                        hsig1.Scale(1/hsig1.Integral())
                        hsig2.Scale(1/hsig2.Integral())
                #hsig1.Scale(xsec[sig1]) ## FIXME later if we want non-1pb
                #hsig2.Scale(xsec[sig2])
                #if len(isRebinned) > 0: ## FIXME later
                #        hsig1.Scale(10) # 100fb input -> 1pb
                #        hsig2.Scale(10)
                if doNormByBinWidth:
                        poissonNormByBinWidth(gaeData,hData,perNGeV)
                        for proc in bkgProcList:
                                try:
                                        print('normByBinWidth: '+proc)
                                        normByBinWidth(bkghists[proc+catStr],perNGeV)
                                except: pass
                        normByBinWidth(hsig1,perNGeV)
                        normByBinWidth(hsig2,perNGeV)
                        normByBinWidth(hData,perNGeV)
                else: poissonErrors(gaeData)
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
                                        systematicList = systListABCDnn
                                else:
                                        if isCategorized:
                                                systematicList = systListFullPlots
                                                if isRebinned: #TEMP: update this later
                                                        try:
                                                                systematicList.remove('muR')
                                                                systematicList.remove('muF')
                                                                systematicList.remove('muRFcorrd')
                                                                systematicList.append('muRFcorrdNewQCD')
                                                                systematicList.append('muRFcorrdNewEWK')
                                                                systematicList.append('muRFcorrdNewST')
                                                                systematicList.append('muRFcorrdNewTTX')
                                                                systematicList.append('muRFcorrdNewTT')
                                                                systematicList.append('muRFcorrdNewWJT')
                                                                systematicList.append('pdfNew')
                                                        except:
                                                                "Unable to remove muR, muF, muRFcorrd and append New"
                                                else: # proxy rebinned by plotting only muRFcorrd
                                                        systematicList.remove('muR')
                                                        systematicList.remove('muF')
                                        else:
                                                systematicList = systListShortPlots
                                for syst in systematicList:
                                        for ud in shiftlist:
                                                try:
                                                        systHists[proc+catStr+syst+ud] = RFile1.Get(f'{histPrefix}__{proc}__{syst}{ud}').Clone()
                                                        if doNormByBinWidth: 
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
                        errorUp = 0.
                        errorDn = 0.
                        errorStatUp = gaeBkgHT.GetErrorYhigh(ibin-1)**2
                        errorStatDn = gaeBkgHT.GetErrorYlow(ibin-1)**2
                        errorNorm = (lumiSys**2)*(bkgHT.GetBinContent(ibin)**2)

                        if doAllSys:
                                for syst in systematicList:
                                        for proc in bkgProcList:
                                                try:
                                                        errorPlus = systHists[proc+catStr+syst+shiftlist[0]].GetBinContent(ibin)-bkghists[proc+catStr].GetBinContent(ibin)
                                                        errorMinus = bkghists[proc+catStr].GetBinContent(ibin)-systHists[proc+catStr+syst+shiftlist[1]].GetBinContent(ibin)
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
                if not scaleSignals:
                        scaleFact1=1
                        scaleFact2=1
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

                stackbkgHT = THStack("stackbkgHT","")
                bkgProcListNew = bkgProcList[:]
                if region=='WJCR':
                        bkgProcListNew[bkgProcList.index("top")],bkgProcListNew[bkgProcList.index("ewk")]=bkgProcList[bkgProcList.index("ewk")],bkgProcList[bkgProcList.index("top")]
                if plotABCDnn:
                        bkgProcListNew = ["ABCDnn"] + minorProcList
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

                bkgHTgerr.SetFillStyle(3004)
                bkgHTgerr.SetFillColor(kBlack)

                gStyle.SetOptStat(0)
                c1 = TCanvas("c1","c1",1200,1000) # used to be 1200 and 1000, but the y-axis labels might overlap
                gStyle.SetErrorX(0.5)
                yDiv=0.25
                if blind == True: yDiv=0.01
                # for some reason the markers at 0 don't show with this setting:
                uMargin = 0.00001
                if blind == True: uMargin = 0.12
                rMargin=.04
                # overlap the pads a little to hide the error bar gap:
                uPad={}
                if yLog and not blind: 
                        uPad=TPad("uPad","",0,yDiv-0.009,1,1) #for actual plots
                else: 
                        uPad=TPad("uPad","",0,yDiv,1,1) #for actual plots
                uPad.SetTopMargin(0.08)
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
                if not doNormByBinWidth: hData.SetMaximum(1.4*max(hData.GetMaximum(),bkgHT.GetMaximum()))
                hData.SetMinimum(0.015)
                hData.SetTitle("")
                # this is super important now!! gaeData has badly defined (negative) maximum
                gaeData.SetMaximum(1.2*max(gaeData.GetMaximum(),bkgHT.GetMaximum()))
                gaeData.SetMinimum(0.015)
                gaeData.SetTitle("")
                if doNormByBinWidth:
                        if iPlot == 'DnnTprime' or (iPlot == 'HTNtag' and perNGeV < 10):
                                gaeData.GetYaxis().SetTitle("< Events / "+str(perNGeV)+" >")
                        else: 
                                gaeData.GetYaxis().SetTitle("< Events / "+str(perNGeV)+" GeV >")
                else: gaeData.GetYaxis().SetTitle("Events / bin")
                formatUpperHist(gaeData,hData)
                uPad.cd()
                gaeData.SetTitle("")
                if not blind:
                        gaeData.Draw("apz")
                if blind: 
                        hsig1.SetMinimum(0.015)
                        if doNormByBinWidth:
                                if iPlot == 'DnnTprime' or (iPlot == 'HTNtag' and perNGeV < 10): 
                                        hsig1.GetYaxis().SetTitle("< Events / "+str(perNGeV)+" >")
                                else: hsig1.GetYaxis().SetTitle("< Events / "+str(perNGeV)+" GeV >")
                        else: hsig1.GetYaxis().SetTitle("Events / bin")
                        hsig1.SetMaximum(1.5*hData.GetMaximum())
                        if iPlot=='Tau21Nm1': hsig1.SetMaximum(1.5*hData.GetMaximum())
                        formatUpperHist(hsig1,hsig1)
                        hsig1.Draw("HIST")
                if doNormByBinWidth:
                        if iPlot == 'DnnTprime' or (iPlot == 'HTNtag' and perNGeV < 10): 
                                hData.GetYaxis().SetTitle("< Events / "+str(perNGeV)+" >")
                        else: 
                                hData.GetYaxis().SetTitle("< Events / "+str(perNGeV)+" GeV >")
                else: hData.GetYaxis().SetTitle("Events / bin")

                stackbkgHT.Draw("SAME HIST")
                hsig1.Draw("SAME HIST")
                hsig2.Draw("SAME HIST")
                if not blind: gaeData.Draw("PZ") #redraw data so its not hidden
                uPad.RedrawAxis()
                bkgHTgerr.Draw("SAME E2")

                chLatex = TLatex()
                chLatex.SetNDC()
                chLatex.SetTextSize(0.06)
                if blind: chLatex.SetTextSize(0.04)
                chLatex.SetTextAlign(21) # align center
                flvString = ''
                tagString = ''
                if isEM=='E': flvString+='e+jets'
                if isEM=='M': flvString+='#mu+jets'
                #if isEM=='L': flvString+='region '+region # TEMP
                tagString = ''
                if isCategorized: tagString = tag
                if tagString.endswith(', '): tagString = tagString[:-2]		
                chLatex.DrawLatex(0.7, 0.54, flvString)
                chLatex.DrawLatex(0.7, 0.48, tagString)


                leg = TLegend(0.5,0.62,0.95,0.89)
                leg.SetShadowColor(0)
                leg.SetFillColor(0)
                leg.SetFillStyle(0)
                leg.SetLineColor(0)
                leg.SetLineStyle(0)
                leg.SetBorderSize(0) 
                leg.SetNColumns(2)
                leg.SetTextFont(62)#42)
                scaleFact1Str = ' x'+str(scaleFact1)
                scaleFact2Str = ' x'+str(scaleFact2)
                if not scaleSignals:
                        scaleFact1Str = ''
                        scaleFact2Str = ''
                if drawQCD:
                        if not blind: 
                                leg.AddEntry(gaeData,"Data","pel")  #left
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
                                leg.AddEntry(bkghists['qcd'+catStr],"QCD","f") #right
                                try: 
                                        leg.AddEntry(bkghists['singletop'+catStr],"single t","f") #left
                                except: pass
                                #leg.AddEntry(0, "", "") #left
                                leg.AddEntry(bkgHTgerr,"Bkg. uncert.","f") #right
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
                                leg.AddEntry(bkghists['qcd'+catStr],"QCD","f") #right
                                leg.AddEntry(0, "", "") #left
                                leg.AddEntry(bkgHTgerr,"Bkg. uncert.","f") #right

                if not drawQCD:
                        if not blind:
                                if plotABCDnn:
                                        leg.AddEntry(gaeData,"Data","pel")
                                        leg.AddEntry(bkghists['ABCDnn'+catStr],"ABCDnn","f")
                                        leg.AddEntry(bkghists['ttx'+catStr],"t#bar{t}+(V,H)","f")
                                        leg.AddEntry(bkghists['ewk'+catStr],"DY+VV","f")
                                        leg.AddEntry(gaeData,"Data","pel")  #left
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
                                        leg.AddEntry(bkgHTgerr,"Bkg. uncert.","f") #right
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
                                leg.AddEntry(bkgHTgerr,"Bkg. uncert.","f") #right


                leg.Draw("same")

                prelimTex=TLatex()
                prelimTex.SetNDC()
                prelimTex.SetTextAlign(31) # align right
                prelimTex.SetTextFont(42)
                prelimTex.SetTextSize(0.05)
                if blind: prelimTex.SetTextSize(0.05)
                prelimTex.SetLineWidth(2)
                prelimTex.DrawLatex(0.95,0.94,str(lumi)+" fb^{-1} (13 TeV)")

                prelimTex2=TLatex()
                prelimTex2.SetNDC()
                prelimTex2.SetTextFont(61)
                prelimTex2.SetLineWidth(2)
                prelimTex2.SetTextSize(0.08)

                #if blind: prelimTex2.SetTextSize(0.08)
                #prelimTex2.DrawLatex(0.12,0.93,"CMS")


                prelimTex3=TLatex()
                prelimTex3.SetNDC()
                prelimTex3.SetTextAlign(12)

                #prelimTex3.SetTextFont(52)
                prelimTex3.SetTextFont(42)
                prelimTex3.SetTextSize(0.05)
                if blind: prelimTex3.SetTextSize(0.05)
                prelimTex3.SetLineWidth(2)
                # if not blind:
                #         prelimTex3.DrawLatex(0.23,0.945,"Private work (CMS data & simulation)") #"Preliminary")
                # if blind: 
                #         prelimTex3.DrawLatex(0.26,0.945,"Private work (CMS data & simulation)") #"Preliminary")
                prelimTex3.DrawLatex(0.12,0.94,"Private work (CMS data & simulation)") #"Preliminary")


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
                        pull.Draw("E0")

                        BkgOverBkg = pull.Clone("bkgOverbkg")
                        BkgOverBkg.Divide(bkgHT, bkgHT)
                        pullUncBandTot=TGraphAsymmErrors(BkgOverBkg.Clone("pulluncTot"))
                        for binNo in range(0,hData.GetNbinsX()+2):
                                if bkgHT.GetBinContent(binNo)!=0:
                                        pullUncBandTot.SetPointEYhigh(binNo-1,totBkgTemp3[catStr].GetErrorYhigh(binNo-1)/bkgHT.GetBinContent(binNo))
                                        pullUncBandTot.SetPointEYlow(binNo-1,totBkgTemp3[catStr].GetErrorYlow(binNo-1)/bkgHT.GetBinContent(binNo))			
                        if not doOneBand: 
                                pullUncBandTot.SetFillStyle(3001)
                        else: pullUncBandTot.SetFillStyle(3344)
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

                        pullLegend=TLegend(0.14,0.87,0.85,0.96)
                        SetOwnership( pullLegend, 0 )   # 0 = release (not keep), 1 = keep
                        pullLegend.SetShadowColor(0)
                        pullLegend.SetNColumns(3)
                        pullLegend.SetFillColor(0)
                        pullLegend.SetFillStyle(0)
                        pullLegend.SetLineColor(0)
                        pullLegend.SetLineStyle(0)
                        pullLegend.SetBorderSize(0)
                        pullLegend.SetTextFont(42)
                        if not doOneBand: 
                                pullLegend.AddEntry(pullUncBandStat , "Bkg. uncert. (shape syst.)" , "f")
                                pullLegend.AddEntry(pullUncBandNorm , "Bkg. uncert. (shape #oplus norm. syst.)" , "f")
                                pullLegend.AddEntry(pullUncBandTot , "Bkg. uncert. (stat. #oplus all syst.)" , "f")
                        else: 
                                if doAllSys: 
                                        pullLegend.AddEntry(pullUncBandTot , "Bkg. uncert. (stat. #oplus syst.)" , "f")
                                else: 
                                        pullLegend.AddEntry(pullUncBandTot , "Bkg. uncert. (stat. #oplus lumi)" , "f")
                        pullLegend.Draw("SAME")
                        pull.Draw("SAME E0")
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

                #c1.Write()
                savePrefix = templateDir+templateDir.split('/')[-2]+'plots/'
                if not os.path.exists(savePrefix): os.system('mkdir '+savePrefix)
                savePrefix+=histPrefix+isRebinned.replace('_rebinned_stat1p1','')+saveKey
                if year != 'all': savePrefix=savePrefix.replace(lumiInTemplates,year)
                if doRealPull: savePrefix+='_pull'
                if doNormByBinWidth: savePrefix+='_NBBW'
                if yLog: savePrefix+='_logy'
                if blind: savePrefix+='_blind'

                if doOneBand:
                        if plotNorm:
                                c1.SaveAs(f"{savePrefix}totBand_norm.pdf")
                                c1.SaveAs(f"{savePrefix}totBand_norm.png")
                        else:
                                c1.SaveAs(f"{savePrefix}totBand.pdf")
                                c1.SaveAs(f"{savePrefix}totBand.png")
                                #c1.SaveAs(savePrefix+"totBand.eps")
                                #c1.SaveAs(savePrefix+"totBand.root")
                                #c1.SaveAs(savePrefix+"totBand.C")
                else:
                        if plotNorm:
                                c1.SaveAs(f"{savePrefix}_norm.pdf")
                                c1.SaveAs(f"{savePrefix}_norm.png")
                        else:
                                c1.SaveAs(f"{savePrefix}.pdf")
                                c1.SaveAs(f"{savePrefix}.png")
                                #c1.SaveAs(savePrefix+".eps")
                                #c1.SaveAs(savePrefix+".root")
                                #c1.SaveAs(savePrefix+".C")
                for proc in bkgProcList:
                        try: 
                                del bkghists[proc+catStr]
                        except: pass

        # Making plots for e+jets/mu+jets combined #

        # histPrefixE = iPlot+'_'+lumiInTemplates+'fb_isE_'+tagStr
        # histPrefixM = iPlot+'_'+lumiInTemplates+'fb_isM_'+tagStr
        # if isCategorized:
        #         if region=='CR': 
        #                 histPrefixE = histPrefixE.replace('isE','isCR_isE')
        #                 histPrefixM = histPrefixM.replace('isM','isCR_isM')
        #         else:
        #                 histPrefixE = histPrefixE.replace('isE','isSR_isE')
        #                 histPrefixM = histPrefixM.replace('isM','isSR_isM')
        # totBkgMerged = 0.
        # for proc in bkgProcList:
        #      try: 
	# 		bkghistsmerged[proc+'isL'+tagStr] = RFile1.Get(histPrefixE+'__'+proc).Clone()
	# 		bkghistsmerged[proc+'isL'+tagStr].Add(RFile1.Get(histPrefixM+'__'+proc))
	# 		totBkgMerged += bkghistsmerged[proc+'isL'+tagStr].Integral()
	# 	except:pass
	# hDatamerged = RFile1.Get(histPrefixE+'__'+datalabel).Clone()
	# hsig1merged = RFile1.Get(histPrefixE+'__'+siglabel).Clone(histPrefixE+'__sig1merged')
	# hsig1merged.Add(RFile1.Get(histPrefixM+'__'+siglabel).Clone())

        # if isCategorized:
        #         hsig2merged = RFile1.Get(histPrefixE+'__'+siglabel.replace(sig1,sig2)).Clone(histPrefixE+'__sig2merged')
        #         hsig2merged.Add(RFile1.Get(histPrefixM+'__'+siglabel.replace(sig1,sig2)).Clone())
        # else:
        #         hsig2merged = RFile2.Get(histPrefixE+'__'+siglabel).Clone(histPrefixE+'__sig2merged')
        #         hsig2merged.Add(RFile2.Get(histPrefixM+'__'+siglabel).Clone())
	# hDatamerged.Add(RFile1.Get(histPrefixM+'__'+datalabel).Clone())
	# hsig1merged.Scale(xsec[sig1])
	# hsig2merged.Scale(xsec[sig2])

        # if len(isRebinned) > 0: 
        #         hsig1merged.Scale(10) # 100fb input -> typical 1pb
        #         hsig2merged.Scale(10)                
        # histrange = [hDatamerged.GetBinLowEdge(1),hDatamerged.GetBinLowEdge(hDatamerged.GetNbinsX()+1)]
	# gaeDatamerged = TGraphAsymmErrors(hDatamerged.Clone(hDatamerged.GetName().replace(datalabel,"gaeDATA")))
	# if doNormByBinWidth:
	# 	poissonNormByBinWidth(gaeDatamerged,hDatamerged,perNGeV)
	# 	for proc in bkgProcList:
	# 		try: normByBinWidth(bkghistsmerged[proc+'isL'+tagStr],perNGeV)
	# 		except: pass
	# 	normByBinWidth(hsig1merged,perNGeV)
	# 	normByBinWidth(hsig2merged,perNGeV)
	# 	normByBinWidth(hDatamerged,perNGeV)
	# else: poissonErrors(gaeDatamerged)
	# # Yes, there are easier ways using the TH1's but
	# # it would be rough to swap objects lower down	

	# bkgHTmerged = bkghistsmerged[bkgProcList[0]+'isL'+tagStr].Clone()
	# for proc in bkgProcList:
	# 	if proc==bkgProcList[0]: continue
	# 	try: bkgHTmerged.Add(bkghistsmerged[proc+'isL'+tagStr])
	# 	except: pass
	# gaeBkgHTmerged = TGraphAsymmErrors(bkgHTmerged.Clone("gaeBkgHTmerged"))

	# #if doNormByBinWidth: poissonNormByBinWidth(gaeBkgHTmerged,bkgHTmerged)
	# #else: poissonErrors(gaeBkgHTmerged)

	# if doAllSys:
	# 	for syst in systematicList:
	# 		for ud in shiftlist:
	# 			for proc in bkgProcList:
	# 				try: 
	# 					systHists[proc+'isL'+tagStr+syst+ud] = systHists[proc+'isE_'+tagStr+syst+ud].Clone()
	# 					systHists[proc+'isL'+tagStr+syst+ud].Add(systHists[proc+'isM_'+tagStr+syst+ud])
	# 				except: pass

	# totBkgTemp1['isL'+tagStr] = TGraphAsymmErrors(bkgHTmerged.Clone(bkgHTmerged.GetName()+'shapeOnly'))
	# totBkgTemp2['isL'+tagStr] = TGraphAsymmErrors(bkgHTmerged.Clone(bkgHTmerged.GetName()+'shapePlusNorm'))
	# totBkgTemp3['isL'+tagStr] = TGraphAsymmErrors(bkgHTmerged.Clone(bkgHTmerged.GetName()+'All'))
	
	# for ibin in range(1,bkghistsmerged[bkgProcList[0]+'isL'+tagStr].GetNbinsX()+1):
	# 	errorUp = 0.
	# 	errorDn = 0.
	# 	errorStatUp = gaeBkgHTmerged.GetErrorYhigh(ibin-1)**2
	# 	errorStatDn = gaeBkgHTmerged.GetErrorYlow(ibin-1)**2
	# 	errorNorm = (lumiSys**2)*(bkgHTmerged.GetBinContent(ibin)**2)

	# 	if doAllSys:
	# 		for syst in systematicList:
	# 			for proc in bkgProcList:
	# 				try:
	# 					errorPlus = systHists[proc+'isL'+tagStr+syst+shiftlist[0]].GetBinContent(ibin)-bkghistsmerged[proc+'isL'+tagStr].GetBinContent(ibin)
	# 					errorMinus = bkghistsmerged[proc+'isL'+tagStr].GetBinContent(ibin)-systHists[proc+'isL'+tagStr+syst+shiftlist[1]].GetBinContent(ibin)
	# 					if errorPlus > 0: errorUp += errorPlus**2
	# 					else: errorDn += errorPlus**2
	# 					if errorMinus > 0: errorDn += errorMinus**2
	# 					else: errorUp += errorMinus**2
	# 				except: pass

	# 	totBkgTemp1['isL'+tagStr].SetPointEYhigh(ibin-1,math.sqrt(errorUp))
	# 	totBkgTemp1['isL'+tagStr].SetPointEYlow(ibin-1, math.sqrt(errorDn))
	# 	totBkgTemp2['isL'+tagStr].SetPointEYhigh(ibin-1,math.sqrt(errorUp+errorNorm))
	# 	totBkgTemp2['isL'+tagStr].SetPointEYlow(ibin-1, math.sqrt(errorDn+errorNorm))
	# 	totBkgTemp3['isL'+tagStr].SetPointEYhigh(ibin-1,math.sqrt(errorUp+errorNorm+errorStatUp))
	# 	totBkgTemp3['isL'+tagStr].SetPointEYlow(ibin-1, math.sqrt(errorDn+errorNorm+errorStatDn))
	
	# bkgHTgerrmerged = totBkgTemp3['isL'+tagStr].Clone()

	# scaleFact1merged = int(bkgHTmerged.GetMaximum()/hsig1merged.GetMaximum()) - int(bkgHTmerged.GetMaximum()/hsig1merged.GetMaximum()) % 10
	# scaleFact2merged = int(bkgHTmerged.GetMaximum()/hsig2merged.GetMaximum()) - int(bkgHTmerged.GetMaximum()/hsig2merged.GetMaximum()) % 10
	# if scaleFact1merged==0: scaleFact1merged=int(bkgHTmerged.GetMaximum()/hsig1merged.GetMaximum())
	# if scaleFact2merged==0: scaleFact2merged=int(bkgHTmerged.GetMaximum()/hsig2merged.GetMaximum())
	# if scaleFact1merged==0: scaleFact1merged=1
	# if scaleFact2merged==0: scaleFact2merged=1
	# if sigScaleFact>0:
	# 	scaleFact1merged=sigScaleFact
	# 	scaleFact2merged=sigScaleFact*2
	# if not scaleSignals:
	# 	scaleFact1merged=1
	# 	scaleFact2merged=1
	# hsig1merged.Scale(scaleFact1merged)
	# hsig2merged.Scale(scaleFact2merged)
	
	# drawQCDmerged = False
	# try: drawQCDmerged = bkghistsmerged['qcdisL'+tagStr].Integral()/bkgHTmerged.Integral()>.005
	# except: pass

	# stackbkgHTmerged = THStack("stackbkgHTmerged","")
	# bkgProcListNew = bkgProcList[:]
	# if region=='WJCR':
	# 	bkgProcListNew[bkgProcList.index("top")],bkgProcListNew[bkgProcList.index("ewk")]=bkgProcList[bkgProcList.index("ewk")],bkgProcList[bkgProcList.index("top")]
	# for proc in bkgProcListNew:
	# 	try: 
	# 		if drawQCDmerged or proc!='qcd': stackbkgHTmerged.Add(bkghistsmerged[proc+'isL'+tagStr])
	# 	except: pass

	# for proc in bkgProcList:
	# 	try: 
	# 		bkghistsmerged[proc+'isL'+tagStr].SetLineColor(bkgHistColors[proc])
	# 		bkghistsmerged[proc+'isL'+tagStr].SetFillColor(bkgHistColors[proc])
	# 		bkghistsmerged[proc+'isL'+tagStr].SetLineWidth(2)
	# 	except: pass
	# hsig1merged.SetLineColor(sig1Color)
	# hsig1merged.SetFillStyle(0)
	# hsig1merged.SetLineWidth(3)
	# hsig2merged.SetLineColor(sig2Color)
	# hsig2merged.SetLineStyle(7)#5)
	# hsig2merged.SetFillStyle(0)
	# hsig2merged.SetLineWidth(3)
	
	# gaeDatamerged.SetMarkerStyle(20)
	# gaeDatamerged.SetMarkerSize(1.2)
	# gaeDatamerged.SetLineWidth(2)
	# gaeDatamerged.SetMarkerColor(kBlack)
	# gaeDatamerged.SetLineColor(kBlack)

	# bkgHTgerrmerged.SetFillStyle(3004)
	# bkgHTgerrmerged.SetFillColor(kBlack)

	# gStyle.SetOptStat(0)
	# c1merged = TCanvas("c1merged","c1merged",1200,1000)
	# gStyle.SetErrorX(0.5)
	# yDiv=0.25
	# if blind == True: yDiv=0.01
	# uMargin = 0.00001
	# if blind == True: uMargin = 0.12
	# rMargin=.04
	# uPad={}
	# if yLog and not blind: uPad=TPad("uPad","",0,yDiv-0.009,1,1) #for actual plots
	# else: uPad=TPad("uPad","",0,yDiv,1,1) #for actual plots
	# uPad.SetTopMargin(0.08)
	# uPad.SetBottomMargin(uMargin)
	# uPad.SetRightMargin(rMargin)
	# uPad.SetLeftMargin(.105)
	# uPad.Draw()
	# if blind == False:
	# 	lPad=TPad("lPad","",0,0,1,yDiv) #for sigma runner
	# 	lPad.SetTopMargin(0)
	# 	lPad.SetBottomMargin(.4)
	# 	lPad.SetRightMargin(rMargin)
	# 	lPad.SetLeftMargin(.105)
	# 	lPad.SetGridy()
	# 	lPad.Draw()
	# gaeDatamerged.SetMaximum(1.6*max(gaeDatamerged.GetMaximum(),bkgHTmerged.GetMaximum()))
	# if iPlot=='PrunedHNm1': gaeDatamerged.SetMaximum(1.7*max(gaeDatamerged.GetMaximum(),bkgHTmerged.GetMaximum()))
	# gaeDatamerged.SetMinimum(0.015)
	# if doNormByBinWidth:
        #         if iPlot == 'DnnTprime' or (iPlot == 'HTNtag' and perNGeV < 10): 
        #                 gaeDatamerged.GetYaxis().SetTitle("< Events / "+str(perNGeV)+" >")
        #         else: gaeDatamerged.GetYaxis().SetTitle("< Events / "+str(perNGeV)+" GeV >")
	# else: gaeDatamerged.GetYaxis().SetTitle("Events / bin")
	# formatUpperHist(gaeDatamerged,hData)
	# uPad.cd()
	# gaeDatamerged.SetTitle("")
	# stackbkgHTmerged.SetTitle("")
	# if not blind: gaeDatamerged.Draw("apz")
	# if blind: 
	# 	hsig1merged.SetMinimum(0.015)
	# 	if doNormByBinWidth:
        #                 if iPlot == 'DnnTprime' or (iPlot == 'HTNtag' and perNGeV < 10): 
        #                         hsig1merged.GetYaxis().SetTitle("< Events / "+str(perNGeV)+" >")
        #                 else: hsig1merged.GetYaxis().SetTitle("< Events / "+str(perNGeV)+" GeV >")
	# 	else: hsig1merged.GetYaxis().SetTitle("Events / bin")
	# 	hsig1merged.SetMaximum(1.5*hDatamerged.GetMaximum())
	# 	if iPlot=='Tau21Nm1': hsig1merged.SetMaximum(1.5*hDatamerged.GetMaximum())
	# 	formatUpperHist(hsig1merged,hsig1merged)
	# 	hsig1merged.Draw("HIST")
	# stackbkgHTmerged.Draw("SAME HIST")
	# hsig1merged.Draw("SAME HIST")
	# hsig2merged.Draw("SAME HIST")
	# if not blind: gaeDatamerged.Draw("PZ") #redraw data so its not hidden
	# uPad.RedrawAxis()
	# bkgHTgerrmerged.Draw("SAME E2")

	# chLatexmerged = TLatex()
	# chLatexmerged.SetNDC()
	# chLatexmerged.SetTextSize(0.06)
	# if blind: chLatexmerged.SetTextSize(0.04)
	# chLatexmerged.SetTextAlign(21) # align center
	# flvString = 'e/#mu+jets'
	# tagString = ''
	# algoString = ''
	# if isCategorized or 'algos' in region: algoString = tag[1]
	# if tagString.endswith(', '): tagString = tagString[:-2]
	# if algoString.endswith(', '): algoString = algoString[:-2]
	# if iPlot != 'deltaRAK8': chLatexmerged.DrawLatex(0.28, 0.85, flvString)
	# else: chLatexmerged.DrawLatex(0.75,0.85,flvString)
	# if iPlot != 'YLD':
	# 	chLatexmerged.DrawLatex(0.28, 0.78, algoString)
	# 	chLatexmerged.DrawLatex(0.28, 0.72, tagString)

	# if drawQCDmerged: 
	# 	legmerged = TLegend(0.45,0.52,0.95,0.87)
	# 	if iPlot == 'deltaRAK8': legmerged = TLegend(0.15,0.52,0.55,0.82)
	# if not drawQCDmerged or blind: 
	# 	legmerged = TLegend(0.45,0.64,0.95,0.89)
	# 	if iPlot == 'deltaRAK8': legmerged = TLegend(0.12,0.65,0.62,0.90)
	# legmerged.SetShadowColor(0)
	# legmerged.SetFillColor(0)
	# legmerged.SetFillStyle(0)
	# legmerged.SetLineColor(0)
	# legmerged.SetLineStyle(0)
	# legmerged.SetBorderSize(0) 
	# legmerged.SetNColumns(2)
	# legmerged.SetTextFont(62)#42)
	# scaleFact1Str = ' x'+str(scaleFact1)
	# scaleFact2Str = ' x'+str(scaleFact2)
	# if not scaleSignals:
	# 	scaleFact1Str = ''
	# 	scaleFact2Str = ''
	# if drawQCDmerged:
	# 	if not blind: 
	# 			#legmerged.AddEntry(0, "", "")
	# 		legmerged.AddEntry(gaeDatamerged,"Data","pel")  #left
	# 		legmerged.AddEntry(bkghistsmerged['qcdisL'+tagStr],"QCD","f") #right
	# 		legmerged.AddEntry(hsig1merged,sig1leg+scaleFact1Str,"l")  #left
	# 		try: legmerged.AddEntry(bkghistsmerged['topisL'+tagStr],"TOP","f") #right
	# 		except: pass
	# 		legmerged.AddEntry(hsig2merged,sig2leg+scaleFact2Str,"l") #left
	# 		try: legmerged.AddEntry(bkghistsmerged['ewkisL'+tagStr],"EW","f") #right
	# 		except: pass
	# 		#legmerged.AddEntry(0, "", "") #left
	# 		legmerged.AddEntry(bkgHTgerrmerged,"Bkg. uncert.","f") #right
	# 	else:
	# 		legmerged.AddEntry(hsig1merged,sig1leg+scaleFact1Str,"l")  #left
	# 		legmerged.AddEntry(bkghistsmerged['qcdisL'+tagStr],"QCD","f") #right
	# 		legmerged.AddEntry(hsig2merged,sig2leg+scaleFact2Str,"l") #left
	# 		try: legmerged.AddEntry(bkghistsmerged['topisL'+tagStr],"TOP","f") #right
	# 		except: pass
	# 		legmerged.AddEntry(bkgHTgerrmerged,"Bkg. uncert.","f") #left
	# 		try: legmerged.AddEntry(bkghistsmerged['ewkisL'+tagStr],"EW","f") #right
	# 		except: pass
				
	# if not drawQCDmerged:
	# 	if not blind: 
	# 		legmerged.AddEntry(gaeDatamerged,"Data","pel") #left 
	# 		try: legmerged.AddEntry(bkghistsmerged['topisL'+tagStr],"TOP","f") #right
	# 		except: pass
	# 		legmerged.AddEntry(hsig1merged,sig1leg+scaleFact1Str,"l") #left
	# 		try: legmerged.AddEntry(bkghistsmerged['ewkisL'+tagStr],"EW","f") #right
	# 		except: pass
	# 		legmerged.AddEntry(hsig2merged,sig2leg+scaleFact2Str,"l") #left
	# 		legmerged.AddEntry(bkgHTgerrmerged,"Bkg. uncert.","f") #right
	# 	else:
	# 		legmerged.AddEntry(hsig1merged,sig1leg+scaleFact1Str,"l") #left
	# 		try: legmerged.AddEntry(bkghistsmerged['topisL'+tagStr],"TOP","f") #right
	# 		except: pass
	# 		legmerged.AddEntry(hsig2merged,sig2leg+scaleFact2Str,"l") #left
	# 		try: legmerged.AddEntry(bkghistsmerged['ewkisL'+tagStr],"EW","f") #right
	# 		except: pass
	# 		#legmerged.AddEntry(0, "", "") #left
	# 		legmerged.AddEntry(bkgHTgerrmerged,"Bkg. uncert.","f") #right
	# legmerged.Draw("same")

	# prelimTex=TLatex()
	# prelimTex.SetNDC()
	# prelimTex.SetTextAlign(31) # align right
	# prelimTex.SetTextFont(42)
	# prelimTex.SetTextSize(0.05)
	# if blind: prelimTex.SetTextSize(0.05)
	# prelimTex.SetLineWidth(2)
	# prelimTex.DrawLatex(0.95,0.94,str(lumi)+" fb^{-1} (13 TeV)")
	
	# prelimTex2=TLatex()
	# prelimTex2.SetNDC()
	# prelimTex2.SetTextFont(61)
	# prelimTex2.SetLineWidth(2)
	# prelimTex2.SetTextSize(0.08)
	# if blind: prelimTex2.SetTextSize(0.08)
	# prelimTex2.DrawLatex(0.12,0.93,"CMS")
	
	# prelimTex3=TLatex()
	# prelimTex3.SetNDC()
	# prelimTex3.SetTextAlign(12)
	# prelimTex3.SetTextFont(52)
	# prelimTex3.SetTextSize(0.055)
	# if blind: prelimTex3.SetTextSize(0.055)
	# prelimTex3.SetLineWidth(2)
	# if not blind: prelimTex3.DrawLatex(0.23,0.945,"Private work") #"Preliminary")
	# if blind: prelimTex3.DrawLatex(0.26,0.945,"Private work") #"Preliminary")
	
	# if blind == False and not doRealPull:
	# 	lPad.cd()
	# 	pullmerged=bkgHTmerged.Clone(hDatamerged.GetName()+"pullmerged")
        #         #scale = str(hDatamerged.Integral()/bkgHTmerged.Integral())
        #         #print('SCALING TOTAL BACKGOUND FOR RATIO: data =',hDatamerged.Integral(),', mc =',bkgHTmerged.Integral())
        #         #pullmerged.Scale(hDatamerged.Integral()/bkgHTmerged.Integral())
	# 	pullmerged.Divide(hDatamerged, pullmerged)                

        #         # if 'probj' in iPlot:
        #         #         print('probjratio = {')
        #         #         for binNo in range(0,hDatamerged.GetNbinsX()+2):
        #         #                 print(str(pullmerged.GetBinContent(binNo))+',')
        #         #                 if bkgHTmerged.GetBinContent(binNo)!=0:
        #         #                         pullmerged.SetBinError(binNo,hDatamerged.GetBinError(binNo)/bkgHTmerged.GetBinContent(binNo))
        #         #         print('};')
	# 	pullmerged.SetMaximum(3)
	# 	pullmerged.SetMinimum(0)
	# 	pullmerged.SetFillColor(1)
	# 	pullmerged.SetLineColor(1)
	# 	pullmerged.SetMarkerStyle(20)
	# 	formatLowerHist(pullmerged)
	# 	pullmerged.Draw("E0")
		
	# 	BkgOverBkgmerged = pullmerged.Clone("bkgOverbkgmerged")
	# 	BkgOverBkgmerged.Divide(bkgHTmerged, bkgHTmerged)
	# 	pullUncBandTotmerged=TGraphAsymmErrors(BkgOverBkgmerged.Clone("pulluncTotmerged"))
	# 	for binNo in range(0,hDatamerged.GetNbinsX()+2):
	# 		if bkgHTmerged.GetBinContent(binNo)!=0:
	# 			pullUncBandTotmerged.SetPointEYhigh(binNo-1,totBkgTemp3['isL'+tagStr].GetErrorYhigh(binNo-1)/bkgHTmerged.GetBinContent(binNo))
	# 			pullUncBandTotmerged.SetPointEYlow(binNo-1, totBkgTemp3['isL'+tagStr].GetErrorYlow(binNo-1)/bkgHTmerged.GetBinContent(binNo))			
	# 	if not doOneBand: pullUncBandTotmerged.SetFillStyle(3001)
	# 	else: pullUncBandTotmerged.SetFillStyle(3344)
	# 	pullUncBandTotmerged.SetFillColor(1)
	# 	pullUncBandTotmerged.SetLineColor(1)
	# 	pullUncBandTotmerged.SetMarkerSize(0)
	# 	gStyle.SetHatchesLineWidth(1)
	# 	pullUncBandTotmerged.Draw("SAME E2")
		
	# 	pullUncBandNormmerged=TGraphAsymmErrors(BkgOverBkgmerged.Clone("pulluncNormmerged"))
	# 	for binNo in range(0,hData.GetNbinsX()+2):
	# 		if bkgHTmerged.GetBinContent(binNo)!=0:
	# 			pullUncBandNormmerged.SetPointEYhigh(binNo-1,totBkgTemp2['isL'+tagStr].GetErrorYhigh(binNo-1)/bkgHTmerged.GetBinContent(binNo))
	# 			pullUncBandNormmerged.SetPointEYlow(binNo-1, totBkgTemp2['isL'+tagStr].GetErrorYlow(binNo-1)/bkgHTmerged.GetBinContent(binNo))			
	# 	pullUncBandNormmerged.SetFillStyle(3001)
	# 	pullUncBandNormmerged.SetFillColor(2)
	# 	pullUncBandNormmerged.SetLineColor(2)
	# 	pullUncBandNormmerged.SetMarkerSize(0)
	# 	gStyle.SetHatchesLineWidth(1)
	# 	if not doOneBand: pullUncBandNormmerged.Draw("SAME E2")
		
	# 	pullUncBandStatmerged=TGraphAsymmErrors(BkgOverBkgmerged.Clone("pulluncStatmerged"))
	# 	for binNo in range(0,hDatamerged.GetNbinsX()+2):
	# 		if bkgHTmerged.GetBinContent(binNo)!=0:
	# 			pullUncBandStatmerged.SetPointEYhigh(binNo-1,totBkgTemp1['isL'+tagStr].GetErrorYhigh(binNo-1)/bkgHTmerged.GetBinContent(binNo))
	# 			pullUncBandStatmerged.SetPointEYlow(binNo-1, totBkgTemp1['isL'+tagStr].GetErrorYlow(binNo-1)/bkgHTmerged.GetBinContent(binNo))			
	# 	pullUncBandStatmerged.SetFillStyle(3001)
	# 	pullUncBandStatmerged.SetFillColor(3)
	# 	pullUncBandStatmerged.SetLineColor(3)
	# 	pullUncBandStatmerged.SetMarkerSize(0)
	# 	gStyle.SetHatchesLineWidth(1)
	# 	if not doOneBand: pullUncBandStatmerged.Draw("SAME E2")

	# 	pullLegendmerged=TLegend(0.14,0.87,0.85,0.96)
	# 	SetOwnership( pullLegendmerged, 0 )   # 0 = release (not keep), 1 = keep
	# 	pullLegendmerged.SetShadowColor(0)
	# 	pullLegendmerged.SetNColumns(3)
	# 	pullLegendmerged.SetFillColor(0)
	# 	pullLegendmerged.SetFillStyle(0)
	# 	pullLegendmerged.SetLineColor(0)
	# 	pullLegendmerged.SetLineStyle(0)
	# 	pullLegendmerged.SetBorderSize(0)
	# 	pullLegendmerged.SetTextFont(42)

        #         #pullLegendmerged.AddEntry(pullmerged,"Data/(MC*"+scale+")","pl")
        #         pullLegendmerged.AddEntry(pullmerged,"Data/MC","pl")
	# 	if not doOneBand: pullLegendmerged.AddEntry(pullUncBandStat , "Bkg. uncert. (shape syst.)" , "f")
	# 	if not doOneBand: pullLegendmerged.AddEntry(pullUncBandNorm , "Bkg. uncert. (shape #oplus norm. syst.)" , "f")
	# 	if not doOneBand: pullLegendmerged.AddEntry(pullUncBandTot , "Bkg. uncert. (stat. #oplus all syst.)" , "f")
	# 	else: 
	# 		if doAllSys: pullLegendmerged.AddEntry(pullUncBandTot , "Bkg. uncert. (stat. #oplus syst.)" , "f")
	# 		else: pullLegendmerged.AddEntry(pullUncBandTot , "Bkg. uncert. (stat. #oplus lumi)" , "f")
	# 	pullLegendmerged.Draw("SAME")
	# 	pullmerged.Draw("SAME E0")
	# 	lPad.RedrawAxis()

	# if blind == False and doRealPull:
	# 	formatUpperHist(hDatamerged,hDatamerged)
	# 	lPad.cd()
	# 	pullmerged=hDatamerged.Clone(hDatamerged.GetName()+"pullmerged")
	# 	for binNo in range(1,hDatamerged.GetNbinsX()+1):
	# 		# case for data < MC:
	# 		dataerror = gaeDatamerged.GetErrorYhigh(binNo-1)
	# 		MCerror = totBkgTemp3['isL'+tagStr].GetErrorYlow(binNo-1)
	# 		# case for data > MC:
	# 		if(hDatamerged.GetBinContent(binNo) > bkgHTmerged.GetBinContent(binNo)):
	# 			dataerror = gaeDatamerged.GetErrorYlow(binNo-1)
	# 			MCerror = totBkgTemp3['isL'+tagStr].GetErrorYhigh(binNo-1)
	# 		pullmerged.SetBinContent(binNo,(hDatamerged.GetBinContent(binNo)-bkgHTmerged.GetBinContent(binNo))/math.sqrt(MCerror**2+dataerror**2))
	# 	pullmerged.SetMaximum(3)
	# 	pullmerged.SetMinimum(-3)
	# 	if '53' in sig1:
	# 		pullmerged.SetFillColor(2)
	# 		pullmerged.SetLineColor(2)
	# 	else:
	# 		pullmerged.SetFillColor(kGray+2)
	# 		pullmerged.SetLineColor(kGray+2)
	# 	formatLowerHist(pullmerged)
	# 	pullmerged.Draw("HIST")

	# #c1merged.Write()
	# savePrefixmerged = templateDir+templateDir.split('/')[-2]+'plots/'
	# if not os.path.exists(savePrefixmerged): os.system('mkdir '+savePrefixmerged)
	# savePrefixmerged+=histPrefixE.replace('isE','isL')+isRebinned.replace('_rebinned_stat1p1','')+saveKey
	# if doRealPull: savePrefixmerged+='_pull'
	# if doNormByBinWidth: savePrefixmerged+='_NBBW'
	# if yLog: savePrefixmerged+='_logy'
	# if blind: savePrefixmerged+='_blind'

	# if doOneBand: 
	# 	c1merged.SaveAs(savePrefixmerged+"totBand.pdf")
	# 	c1merged.SaveAs(savePrefixmerged+"totBand.png")
	# 	#c1merged.SaveAs(savePrefixmerged+"totBand.eps")
	# 	c1merged.SaveAs(savePrefixmerged+"totBand.root")
	# 	#c1merged.SaveAs(savePrefixmerged+"totBand.C")
	# else: 
	# 	c1merged.SaveAs(savePrefixmerged+".pdf")
	# 	c1merged.SaveAs(savePrefixmerged+".png")
	# 	#c1merged.SaveAs(savePrefixmerged+".eps")
	# 	#c1merged.SaveAs(savePrefixmerged+".root")
	# 	#c1merged.SaveAs(savePrefixmerged+".C")
	# for proc in bkgProcList:
	# 	try: del bkghistsmerged[proc+'isL'+tagStr]
	# 	except: pass

RFile1.Close()

print("--- %s minutes ---" % (round(time.time() - start_time, 2)/60))
