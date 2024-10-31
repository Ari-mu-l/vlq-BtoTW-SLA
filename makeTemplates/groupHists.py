#!/usr/bin/python
# python3 groupHists.py $iPlot $region $isCategorized $pfix
# python3 groupHists.py BpMass D True _Oct2024SysAll
import os,sys,time,math,datetime,itertools,ctypes
from ROOT import gROOT,TFile,TH1F, TH2D
parent = os.path.dirname(os.getcwd())
sys.path.append(parent)
from samples import targetlumi, lumiStr, systListShort, systListFull, systListABCDnn, samples_data, samples_signal, samples_electroweak, samples_wjets, samples_singletop, samples_ttbarx, samples_qcd, uncorrList_sf, yearList
from utils import *

gROOT.SetBatch(1)
start_time = time.time()

if len(sys.argv)>1:
	iPlot = str(sys.argv[1])
else:   
        iPlot = 'BpMass_ABCDnn'
if len(sys.argv)>2:
        region = str(sys.argv[2])
else:
        region='D' # BAX, DCY, individuals, or all
if len(sys.argv)>3:
        isCategorized = bool(eval(sys.argv[3]))
else:
        isCategorized=True

if isCategorized:
        pfix='templates'+region
else:
        pfix='kinematics'+region
if len(sys.argv)>4:
        pfix+=str(sys.argv[4])
else:
        pfix+='_Oct20224'
outDir=f'{os.getcwd()}/{pfix}/'

print('Grouping hists for iPlot',iPlot,', region',region,', isCategorized',isCategorized,', and folder',pfix)

#year='all'
doAllSys = True
if doAllSys:
    pfix+='SysAll'
else:
    pfix+='StatsOnly'

outDir = os.getcwd()+'/'+pfix+'/'
outDir = f'templates{region}_Oct2024_42bins/' # TEMP

removeThreshold = 0.0005 # TODO: add if necessary

scaleSignalXsecTo1pb = False # Set to True if analyze.py ever uses a non-1 cross section
doPDF = False
if isCategorized: doPDF=False # FIXME later
skipQCD300 = False # we have enough number of events per bin in control plots for BpM, so it's okay to include it. actually provides better data/MC agreement

if 'ABCDnn' in iPlot:
        doABCDnn = True
        #from samples import samples_ttbar_abcdnn as samples_ttbar
else:
        doABCDnn = False
        from samples import samples_ttbar

if doABCDnn:
        bkgProcs = {'ewk':samples_electroweak,'ttx':samples_ttbarx}
else:
        bkgProcs = {'ewk':samples_electroweak,'wjets':samples_wjets,'ttbar':samples_ttbar,'singletop':samples_singletop,'ttx':samples_ttbarx,'qcd':samples_qcd}
massList = [800,1000,1200,1300,1400,1500,1600,1700,1800,2000,2200]
sigList = ['BpM'+str(mass) for mass in massList]

isEMlist = ['L'] #['E','M'], 'L' #
if '2D' in outDir: 
        isEMlist =['L']
taglist = ['all']
if isCategorized: 
        #taglist=['tagTjet','tagWjet','untagTlep','untagWlep','allWlep','allTlep']
        #taglist=['allWlep','allTlep'] # TEMP: for code developing only
        taglist=['tagTjet','tagWjet','untagTlep','untagWlep']

catList = ['is'+item[0]+'_'+item[1] for item in list(itertools.product(isEMlist,taglist))]

lumiSys = 0.018 #lumi uncertainty

corrList_sf = systListFull.copy()
mySystList = systListFull
if not isCategorized:
        corrList_sf = systListShort.copy()
        mySystList = systListShort
else:
        for i in range(101):
                mySystList.append('pdf'+str(i))
                corrList_sf.append('pdf'+str(i))
for syst in uncorrList_sf:
        corrList_sf.remove(syst)        
        
### Group histograms
outHistFile = TFile.Open(f'{outDir}templates_{iPlot}_{lumiStr}.root', "RECREATE")
for cat in catList:
        print("PROGRESS: "+cat)
        if region=="all":
                histoPrefix = f'{iPlot}_{lumiStr}_{cat}'
        else:
                histoPrefix = f'{iPlot}_{lumiStr}_{cat}_{region}'

        dataHistFile = TFile.Open(f'{outDir}{cat[2:]}/datahists_{iPlot}.root', "READ")
        isFirstHist = True
        for dat in samples_data:
                if isFirstHist:
                        hists = dataHistFile.Get(histoPrefix+'_'+samples_data[dat].prefix).Clone(f'{histoPrefix}__data_obs')
                        isFirstHist = False
                else:
                        hists.Add(dataHistFile.Get(histoPrefix+'_'+samples_data[dat].prefix))
        outHistFile.cd()
        hists.Write()
        dataHistFile.Close()

        for proc in bkgProcs:
                # DID NOT IMPLEMENT REMOVETHRESHOLD
                bkgHistFile = TFile.Open(f'{outDir}{cat[2:]}/bkghists_{proc}_{iPlot}.root', "READ")
                bkgGrp = bkgProcs[proc]
                nomHists = {}
                systHists = {}
                systHistsWrite = {}
                isFirstHistDir = {"2016APV":True, "2016":True, "2017":True, "2018":True}

                systematicList = mySystList
                corrList = corrList_sf
                uncorrList = uncorrList_sf

                for bkg in bkgGrp:
                        # if doABCDnn:
                        #         if 'QCDHT200' in bkg:
                        #                 print("Plotting without QCDHT200.") # abcdnn trained without having qcd200 as input (only has two unweighted evets)
                        #                 continue
                        #else:
                        if 'QCDHT300' in bkg and skipQCD300:
                                print("Plotting without QCDHT300.") # some QCD300 has anomalously large genweights. visible when not having enough events per bin
                                continue
                        # uncomment this if QCD200 not in rdf outputs
                        if 'QCDHT200' in bkg: #TEMP
                                print("Plotting without QCDHT200.")
                                continue

                        year = bkgGrp[bkg].year
                        bkgPrefix = bkgGrp[bkg].prefix
                        doMuRF = True
                        if (bkgPrefix).find('WW') == 0 or (bkgPrefix).find('WZ') == 0 or (bkgPrefix).find('ZZ') == 0:
                                doMuRF = False

                        # Group nominal and correlated systs for each year
                        if isFirstHistDir[year]:
                                nomHists[f'{histoPrefix}__{proc}{year}'] = bkgHistFile.Get(f'{histoPrefix}_{bkgPrefix}').Clone(f'{histoPrefix}__{proc}{year}')
                                isFirstHistDir[year] = False
                                if doAllSys:
                                        for syst in systematicList:
                                                if 'pdf' in syst:
                                                        if doMuRF:
                                                                print(f'{histoPrefix}_{syst}_{bkgPrefix}')
                                                                systHists[f'{histoPrefix}__{proc}__{syst}{year}'] = bkgHistFile.Get(f'{histoPrefix}_{syst}_{bkgPrefix}').Clone(f'{histoPrefix}__{proc}__{syst}{year}')
                                                        else: # let's add nominal for WW, etc, rather than have nothing...
                                                                systHists[f'{histoPrefix}__{proc}__{syst}{year}'] = bkgHistFile.Get(f'{histoPrefix}_{bkgPrefix}').Clone(f'{histoPrefix}__{proc}__{syst}{year}')
                                                else:
                                                        try:
                                                                systHists[f'{histoPrefix}__{proc}__{syst}{year}Up'] = bkgHistFile.Get(f'{histoPrefix}_{syst}Up_{bkgPrefix}').Clone(f'{histoPrefix}__{proc}__{syst}{year}Up')
                                                                systHists[f'{histoPrefix}__{proc}__{syst}{year}Down'] = bkgHistFile.Get(f'{histoPrefix}_{syst}Dn_{bkgPrefix}').Clone(f'{histoPrefix}__{proc}__{syst}{year}Down')
                                                        except:                                                               
                                                                if ('pNet' in syst and ('untag' in cat or ('Wtag' in syst and 'Tjet' in cat) or ('Ttag' in syst and 'Wjet' in cat))):
                                                                        pass
                                                                else:
                                                                        print('could not process '+syst+' for '+bkg)
                        else:
                                nomHists[f'{histoPrefix}__{proc}{year}'].Add(bkgHistFile.Get(f'{histoPrefix}_{bkgPrefix}'))
                                if doAllSys:
                                        for syst in systematicList:
                                                if 'pdf' in syst:
                                                        if doMuRF:
                                                                systHists[f'{histoPrefix}__{proc}__{syst}{year}'].Add(bkgHistFile.Get(f'{histoPrefix}_{syst}_{bkgPrefix}'))
                                                        else:
                                                                systHists[f'{histoPrefix}__{proc}__{syst}{year}'].Add(bkgHistFile.Get(f'{histoPrefix}_{bkgPrefix}'))
                                                else:
                                                        try:
                                                                systHists[f'{histoPrefix}__{proc}__{syst}{year}Up'].Add(bkgHistFile.Get(f'{histoPrefix}_{syst}Up_{bkgPrefix}'))
                                                                systHists[f'{histoPrefix}__{proc}__{syst}{year}Down'].Add(bkgHistFile.Get(f'{histoPrefix}_{syst}Dn_{bkgPrefix}'))
                                                        except:
                                                                if ('pNet' in syst and ('untag' in cat or ('Wtag' in syst and 'Tjet' in cat) or ('Ttag' in syst and 'Wjet' in cat))):
                                                                        pass
                                                                else:
                                                                        print('could not process '+syst+' for '+bkg)

                # add years for corr uncertainties
                nomHistAllYears = nomHists[f'{histoPrefix}__{proc}2016APV'].Clone(f'{histoPrefix}__{proc}')
                for syst in corrList:
                        if 'pdf' in syst: # now even VV will have pdf hists in the list (even though fake)
                                systHistsWrite[f'{histoPrefix}__{proc}__{syst}'] = systHists[f'{histoPrefix}__{proc}__{syst}2016APV'].Clone(f'{histoPrefix}__{proc}__{syst}')
                        else:
                                try:
                                        systHistsWrite[f'{histoPrefix}__{proc}__{syst}Up'] = systHists[f'{histoPrefix}__{proc}__{syst}2016APVUp'].Clone(f'{histoPrefix}__{proc}__{syst}Up')
                                        systHistsWrite[f'{histoPrefix}__{proc}__{syst}Down'] = systHists[f'{histoPrefix}__{proc}__{syst}2016APVDown'].Clone(f'{histoPrefix}__{proc}__{syst}Down')
                                except:
                                        if ('pNet' in syst and ('untag' in cat or ('Wtag' in syst and 'Tjet' in cat) or ('Ttag' in syst and 'Wjet' in cat))):
                                                pass
                                        else:
                                                print('could not process '+syst+' for '+bkg)

                for year in yearList:
                        if year!="2016APV":
                                nomHistAllYears.Add(nomHists[f'{histoPrefix}__{proc}{year}'])
                                for syst in corrList:
                                        if 'pdf' in syst:
                                                systHistsWrite[f'{histoPrefix}__{proc}__{syst}'].Add(systHists[f'{histoPrefix}__{proc}__{syst}{year}'])
                                        else:
                                                try:
                                                        systHistsWrite[f'{histoPrefix}__{proc}__{syst}Up'].Add(systHists[f'{histoPrefix}__{proc}__{syst}{year}Up'])
                                                        systHistsWrite[f'{histoPrefix}__{proc}__{syst}Down'].Add(systHists[f'{histoPrefix}__{proc}__{syst}{year}Down'])
                                                except:
                                                        if ('pNet' in syst and ('untag' in cat or ('Wtag' in syst and 'Tjet' in cat) or ('Ttag' in syst and 'Wjet' in cat))):
                                                                pass
                                                        else:
                                                                print('could not process '+syst+' for '+bkg)

                # uncorr years
                for syst in uncorrList:
                        for shiftyear in yearList:
                                systHistsWrite[f'{histoPrefix}__{proc}__{syst}{shiftyear}Up'] = systHists[f'{histoPrefix}__{proc}__{syst}{shiftyear}Up'].Clone()
                                systHistsWrite[f'{histoPrefix}__{proc}__{syst}{shiftyear}Down'] = systHists[f'{histoPrefix}__{proc}__{syst}{shiftyear}Down'].Clone()
                                for nomyear in yearList:
                                        if nomyear!=shiftyear:
                                                systHistsWrite[f'{histoPrefix}__{proc}__{syst}{shiftyear}Up'].Add(nomHists[f'{histoPrefix}__{proc}{nomyear}'])
                                                systHistsWrite[f'{histoPrefix}__{proc}__{syst}{shiftyear}Down'].Add(nomHists[f'{histoPrefix}__{proc}{nomyear}'])

                outHistFile.cd()
                nomHistAllYears.Write()
                for systHist in systHistsWrite:
                        systHistsWrite[systHist].Write()
                bkgHistFile.Close()

        sigHistFile = TFile.Open(f'{outDir}{cat[2:]}/sighists_{iPlot}.root', "READ")
        systematicList = mySystList
        for mass in massList:
                systHists = {}
                # add nominal and correlated systs
                nomHistsAllYears = sigHistFile.Get(f'{histoPrefix}_Bprime_M{mass}_2016APV').Clone(histoPrefix+'__BpM'+str(mass)) # no 2016APV for signal MCs ?????
                if doAllSys:
                        for syst in corrList_sf:
                                if 'pdf' in syst:
                                        systHists[f'{histoPrefix}__BpM{mass}__{syst}'] = sigHistFile.Get(f'{histoPrefix}_{syst}_Bprime_M{mass}_2016APV').Clone(f'{histoPrefix}__BpM{mass}__{syst}')
                                else:
                                        try:
                                                systHists[f'{histoPrefix}__BpM{mass}__{syst}Up'] = sigHistFile.Get(f'{histoPrefix}_{syst}Up_Bprime_M{mass}_2016APV').Clone(f'{histoPrefix}__BpM{mass}__{syst}Up')
                                                systHists[f'{histoPrefix}__BpM{mass}__{syst}Down'] = sigHistFile.Get(f'{histoPrefix}_{syst}Dn_Bprime_M{mass}_2016APV').Clone(f'{histoPrefix}__BpM{mass}__{syst}Down')
                                        except:
                                                if ('pNet' in syst and ('untag' in cat or ('Wtag' in syst and 'Tjet' in cat) or ('Ttag' in syst and 'Wjet' in cat))):
                                                        pass
                                                else:
                                                        print('could not process '+syst+' for '+bkg)

                for year in ['2016','2017', '2018']:
                        nomHistsAllYears.Add(sigHistFile.Get(f'{histoPrefix}_Bprime_M{mass}_{year}'))
                        if doAllSys:
                                for syst in corrList_sf:
                                        if 'pdf' in syst:
                                                systHists[f'{histoPrefix}__BpM{mass}__{syst}'].Add(sigHistFile.Get(f'{histoPrefix}_{syst}_Bprime_M{mass}_{year}'))
                                        else:
                                                try:
                                                        systHists[f'{histoPrefix}__BpM{mass}__{syst}Up'].Add(sigHistFile.Get(f'{histoPrefix}_{syst}Up_Bprime_M{mass}_{year}'))
                                                        systHists[f'{histoPrefix}__BpM{mass}__{syst}Down'].Add(sigHistFile.Get(f'{histoPrefix}_{syst}Dn_Bprime_M{mass}_{year}'))
                                                except:
                                                        if ('pNet' in syst and ('untag' in cat or ('Wtag' in syst and 'Tjet' in cat) or ('Ttag' in syst and 'Wjet' in cat))):
                                                                pass
                                                        else:
                                                                print('could not process '+syst+' for '+bkg)

                # make hists for uncorrleated systs
                for syst in uncorrList_sf:
                        for shiftyear in ['2016APV','2016', '2017', '2018']:
                                systHists[f'{histoPrefix}__BpM{mass}__{syst}{shiftyear}Up'] = sigHistFile.Get(f'{histoPrefix}_{syst}Up_Bprime_M{mass}_{shiftyear}').Clone(f'{histoPrefix}__BpM{mass}__{syst}{shiftyear}Up')
                                systHists[f'{histoPrefix}__BpM{mass}__{syst}{shiftyear}Down'] = sigHistFile.Get(f'{histoPrefix}_{syst}Dn_Bprime_M{mass}_{shiftyear}').Clone(f'{histoPrefix}__BpM{mass}__{syst}{shiftyear}Down')
                                for year in ['2016APV','2016', '2017', '2018']:
                                        if year!=shiftyear:
                                                systHists[f'{histoPrefix}__BpM{mass}__{syst}{shiftyear}Up'].Add(sigHistFile.Get(f'{histoPrefix}_Bprime_M{mass}_{year}'))
                                                systHists[f'{histoPrefix}__BpM{mass}__{syst}{shiftyear}Down'].Add(sigHistFile.Get(f'{histoPrefix}_Bprime_M{mass}_{year}'))

                outHistFile.cd()
                nomHistsAllYears.Write()
                for systHist in systHists:
                        systHists[systHist].Write()
        sigHistFile.Close()
outHistFile.Close()
