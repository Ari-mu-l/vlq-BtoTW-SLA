#!/usr/bin/python

# activate python env first: source /uscms/home/xshen/nobackup/cmsstyle/bin/activate
# python3 -u plotHists.py BpMass A True 

import os,sys,time,math
parent = os.path.dirname(os.getcwd())
sys.path.append(parent)
from ROOT import *
from samples import lumiStr, systListShortPlots, systListFullPlots,  systListABCDnn, yieldUncertABCDnn, xsec
from utils import *
import cmsstyle as CMS

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
if isCategorized:
        sig1leg='B (1.0 TeV, 36 fb)'
        sig2leg='B (1.8 TeV, 1 fb)'

scaleSignals = True
#if not isCategorized: scaleSignals = True
sigScaleFact = 100
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
                bkgProcList = ['qcd',
                               'ttx',
                               'ewk',
                               'wjets',                       
                               'singletop',
                               'ttbar'
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

if plotABCDnn:
        bkgHistColors = {'ABCDnn': TColor.GetColor('#e42536'),'ewk':TColor.GetColor('#964a8b'),'ttx':TColor.GetColor('#5790fc')}
else:
        bkgHistColors = {'ttbar':TColor.GetColor('#e42536'),'wjets':TColor.GetColor('#7a21dd'),'qcd':TColor.GetColor('#f89c20'),'ewk':TColor.GetColor('#964a8b'),'singletop':TColor.GetColor('#9c9ca1'),'ttx':TColor.GetColor('#5790fc')}

doAllSys = True

doNormByBinWidth=False
if len(isRebinned)>0 and 'stat1p1' not in isRebinned and 'mvagof' not in isRebinned:
        if 'rebinned1' not in isRebinned and 'Jan2025' in pfix:
                doNormByBinWidth = False
        else:
                doNormByBinWidth = True
#doNormByBinWidth = False # TEMP: unblinding review

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
if yLog or 'V' in region or 'validation' in pfix: scaleSignals = False

partialBlind = False

isEMlist =['L']#'E','M']
taglist = ['all']
if isCategorized == True:
        #taglist=['tagTjet','tagWjet','untagTlep','untagWlep','allWlep','allTlep']
        taglist = ['tagTjet','tagWjet','untagWlep','untagTlep']
        #if region == 'V' or 'validation' in pfix:  # this should be fixed now
        #        taglist = ['untagWlep','untagTlep'] #
        if ('D' in region or 'C' in region or 'Y' in region or region=='all') and 'BpMass' in iPlot and 'validation' not in pfix:
                partialBlind = True
                print(f'Partial blind {iPlot} for {region}.')

if year=='2016':
        partialBlind = False
#partialBlind = False # for making unblinded SR plots

lumiSys = 0.016 # lumi uncertainty
factor = {'tagTjet':0.02,'tagWjet':0.02,'untagTlep':0.10,'untagWlep':0.08}

#### Consider: Did not set removeThreshold
####           No doPDF


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
        perNGeV = 10 # choose what "unit" to use for bin widths, similar to the smaller bin widths in the plot. Values < 1 are ok for e.g. NN scores
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

                gaeData = TGraphAsymmErrors(hData.Clone(hData.GetName().replace(datalabel,'gaeDATA')))
                hsig1 = RFile1.Get(histPrefix+'__'+sig1).Clone(histPrefix+'__sig1')
                hsig2 = RFile1.Get(histPrefix+'__'+sig2).Clone(histPrefix+'__sig2')
                if plotNorm:
                        hsig1.Scale(1/hsig1.Integral())
                        hsig2.Scale(1/hsig2.Integral())
                if isCategorized:
                        hsig1.Scale(xsec[sig1[3:]]) ## B singlet cross sections -- modbinning has the BR multiplier to get singlet!
                        hsig2.Scale(xsec[sig2[3:]])
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

                gStyle.SetOptStat(0)
                CMS.SetExtraText("Simulation Preliminary")
                CMS.SetLumi(138)
                c1 = CMS.cmsCanvas('', 0, 1, 0, 1, '', '', extraSpace=0.01, iPos=0)
                
                if not doNormByBinWidth: hData.SetMaximum(1.4*max(hData.GetMaximum(),bkgHT.GetMaximum()))
                hData.SetMinimum(0.015)
                hData.SetTitle("")
                # this is super important now!! gaeData has badly defined (negative) maximum
                gaeData.SetMaximum(1.2*max(hData.GetMaximum(),bkgHT.GetMaximum()))
                gaeData.SetMinimum(0.015)
                gaeData.SetTitle("")
                if doNormByBinWidth:
                        if iPlot == 'DnnTprime' or (iPlot == 'HTNtag' and perNGeV < 10):
                                gaeData.GetYaxis().SetTitle("< Events / "+str(perNGeV)+" >")
                        else: 
                                gaeData.GetYaxis().SetTitle("< Events / "+str(perNGeV)+" GeV >")
                else: gaeData.GetYaxis().SetTitle("Events / bin")
                
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
                                c1.SaveAs(f"{savePrefix}totBand_norm_paper.pdf")
                                c1.SaveAs(f"{savePrefix}totBand_norm_paper.png")
                        else:
                                c1.SaveAs(f"{savePrefix}totBand_paper.pdf")
                                c1.SaveAs(f"{savePrefix}totBand_paper.png")
                                #c1.SaveAs(savePrefix+"totBand_paper.eps")
                                #c1.SaveAs(savePrefix+"totBand_paper.root")
                                #c1.SaveAs(savePrefix+"totBand_paper.C")
                else:
                        if plotNorm:
                                c1.SaveAs(f"{savePrefix}_norm_paper.pdf")
                                c1.SaveAs(f"{savePrefix}_norm_paper.png")
                        else:
                                c1.SaveAs(f"{savePrefix}_paper.pdf")
                                c1.SaveAs(f"{savePrefix}_paper.png")
                                #c1.SaveAs(savePrefix+"_paper.eps")
                                #c1.SaveAs(savePrefix+"_paper.root")
                                #c1.SaveAs(savePrefix+"_paper.C")
                for proc in bkgProcList:
                        try: 
                                del bkghists[proc+catStr]
                        except: pass

