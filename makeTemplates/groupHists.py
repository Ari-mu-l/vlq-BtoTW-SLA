#!/usr/bin/python
# python3 groupHists.py $iPlot $region $isCategorized $pfix
# python3 groupHists.py BpMass D True _Apr2024SysAll
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
        iPlot = 'BpMass'
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
        pfix+='_Apr2024SysAll'
outDir=f'{os.getcwd()}/{pfix}/'

print('Grouping hists for iPlot',iPlot,', region',region,', isCategorized',isCategorized,', and folder',pfix)

#year='all'

removeThreshold = 0.0005 # TODO: add if necessary

scaleSignalXsecTo1pb = False # Set to True if analyze.py ever uses a non-1 cross section
doAllSys = True
doPDF = False
if isCategorized: doPDF=False # FIXME later
skipQCD300 = False # we have enough number of events per bin in control plots for BpM, so it's okay to include it. actually provides better data/MC agreement

if 'ABCDnn' in iPlot:
        doABCDnn = True
        from samples import samples_ttbar_abcdnn as samples_ttbar
else:
        doABCDnn = False
        from samples import samples_ttbar

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

groupHists = True # TEMP: turn this on to group histograms
getYields = True # TEMP: turn this on to get yield tables

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
if groupHists:                                                  
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

                        if doABCDnn and (proc=="ttbar" or proc=="qcd" or proc=="wjets" or proc=="singletop"):
                                systematicList = systListABCDnn
                                corrList = systListABCDnn
                                uncorrList = []
                        else:
                                systematicList = mySystList
                                corrList = corrList_sf
                                uncorrList = uncorrList_sf
                
                        for bkg in bkgGrp:
                                if doABCDnn:
                                        if 'QCDHT200' in bkg:
                                                print("Plotting without QCDHT200.") # abcdnn trained without having qcd200 as input (only has two unweighted evets)
                                                continue
                                else:
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
                                                                        systHists[f'{histoPrefix}__{proc}__{syst}{year}'] = bkgHistFile.Get(f'{histoPrefix}_{syst}_{bkgPrefix}').Clone(f'{histoPrefix}__{proc}__{syst}{year}')
                                                                else: # let's add nominal for WW, etc, rather than have nothing...
                                                                        systHists[f'{histoPrefix}__{proc}__{syst}{year}'] = bkgHistFile.Get(f'{histoPrefix}_{bkgPrefix}').Clone(f'{histoPrefix}__{proc}__{syst}{year}')
                                                        else:
                                                                try:
                                                                        systHists[f'{histoPrefix}__{proc}__{syst}{year}Up'] = bkgHistFile.Get(f'{histoPrefix}_{syst}Up_{bkgPrefix}').Clone(f'{histoPrefix}__{proc}__{syst}{year}Up')
                                                                        systHists[f'{histoPrefix}__{proc}__{syst}{year}Down'] = bkgHistFile.Get(f'{histoPrefix}_{syst}Dn_{bkgPrefix}').Clone(f'{histoPrefix}__{proc}__{syst}{year}Down')
                                                                except:                                                                
                                                                        if ('pNet' in syst and 'tag' in cat):
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
                                                                        if ('pNet' in syst and 'tag' in cat):
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
                                                if ('pNet' in syst and 'tag' in cat):
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
                                                                if ('pNet' in syst and 'tag' in cat):
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
                                for syst in systematicList:
                                        if 'pdf' in syst:
                                                systHists[f'{histoPrefix}__BpM{mass}__{syst}'] = sigHistFile.Get(f'{histoPrefix}_{syst}_Bprime_M{mass}_2016APV').Clone(f'{histoPrefix}__BpM{mass}__{syst}')
                                        else:
                                                try:
                                                        systHists[f'{histoPrefix}__BpM{mass}__{syst}Up'] = sigHistFile.Get(f'{histoPrefix}_{syst}Up_Bprime_M{mass}_2016APV').Clone(f'{histoPrefix}__BpM{mass}__{syst}Up')
                                                        systHists[f'{histoPrefix}__BpM{mass}__{syst}Down'] = sigHistFile.Get(f'{histoPrefix}_{syst}Dn_Bprime_M{mass}_2016APV').Clone(f'{histoPrefix}__BpM{mass}__{syst}Down')
                                                except:
                                                        if ('pNet' in syst and 'tag' in cat):
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
                                                                if ('pNet' in syst and 'tag' in cat):
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

# ###################
# ### Yield Table ###
# ###################
# # Does not record data yield. Update if needed. Sample code in doTemplates_RDF.py

if not getYields:
        exit()
        
yieldTable = {}
yieldStatErrTable = {}

systListFullUCOC = corrList_sf.copy()
for syst in uncorrList_sf:
        for year in yearList:
                systListFullUCOC.append(f'{syst}{year}')

combinedHistFile = TFile.Open(f'{outDir}templates_{iPlot}_{lumiStr}.root', "READ")

# Initialize empty yields dictionaries for table printing
for cat in catList:
        if region=="all":
                histoPrefix = f'{iPlot}_{lumiStr}_{cat}'
        else:
                histoPrefix = f'{iPlot}_{lumiStr}_{cat}_{region}'        
        yieldTable[histoPrefix]={}
        yieldStatErrTable[histoPrefix]={}

        lastBin = combinedHistFile.Get(f'{histoPrefix}__ewk').GetXaxis().GetNbins()+1
        binerr = ctypes.c_double()
        
        yieldTable[histoPrefix]['data'] = combinedHistFile.Get(f'{histoPrefix}__data_obs').IntegralAndError(1,lastBin,binerr,"")
        yieldStatErrTable[histoPrefix]['data'] = binerr.value
        
        for sig in sigList:
                yieldTable[histoPrefix][sig] = combinedHistFile.Get(f'{histoPrefix}__{sig}').IntegralAndError(1,lastBin,binerr,"")
                yieldStatErrTable[histoPrefix][sig] = binerr.value
        
        yieldTable[histoPrefix]['totBkg'] = 0.
        yieldStatErrTable[histoPrefix]['totBkg'] = 0.
        for proc in bkgProcs:
                yieldTable[histoPrefix][proc] = combinedHistFile.Get(f'{histoPrefix}__{proc}').IntegralAndError(1,lastBin,binerr,"")
                yieldStatErrTable[histoPrefix][proc] = binerr.value
                yieldTable[histoPrefix]['totBkg'] += yieldTable[histoPrefix][proc]
                yieldStatErrTable[histoPrefix]['totBkg'] += binerr.value**2
        yieldStatErrTable[histoPrefix]['totBkg'] = math.sqrt(yieldStatErrTable[histoPrefix]['totBkg'])

        yieldTable[histoPrefix]['dataOverBkg'] = yieldTable[histoPrefix]['data']/yieldTable[histoPrefix]['totBkg']
        yieldStatErrTable[histoPrefix]['dataOverBkg'] = yieldStatErrTable[histoPrefix]['data']/yieldStatErrTable[histoPrefix]['totBkg']
        if doABCDnn:
                yieldTable[histoPrefix]['ABCDnn'] = yieldTable[histoPrefix]['ttbar'] + yieldTable[histoPrefix]['wjets'] + yieldTable[histoPrefix]['qcd'] + yieldTable[histoPrefix]['singletop']
                yieldStatErrTable[histoPrefix]['ABCDnn'] = math.sqrt(yieldStatErrTable[histoPrefix]['ttbar']**2 + yieldStatErrTable[histoPrefix]['wjets']**2 + yieldStatErrTable[histoPrefix]['qcd']**2 + yieldStatErrTable[histoPrefix]['singletop']**2)
        else:
                yieldTable[histoPrefix]['ABCDnn'] = 0
                yieldStatErrTable[histoPrefix]['ABCDnn'] = 0

        if doAllSys:
                for syst in systListFullUCOC+systListABCDnn:
                        if 'pdf' in syst or syst == 'muR' or syst == 'muF': continue
                        for ud in ['Up', 'Down']:
                                yieldTable[f'{histoPrefix}{syst}{ud}']={}
                for proc in list(bkgProcs.keys())+sigList:
                        if doABCDnn and (proc=='ttbar' or proc=='qcd' or proc=='wjets' or proc=='singletop'):
                                systematicList = systListABCDnn
                        else:
                                systematicList = systListFullUCOC
                                
                        for syst in systematicList:
                                if 'pdf' in syst or syst == 'muR' or syst == 'muF': continue
                                for ud in ['Up', 'Down']:
                                        try:
                                                yieldTable[f'{histoPrefix}{syst}{ud}'][proc]=combinedHistFile.Get(f'{histoPrefix}__{proc}__{syst}{ud}').Integral()
                                        except:
                                                if ('pNet' in syst and 'tag' in cat):
                                                        yieldTable[f'{histoPrefix}{syst}{ud}'][proc] = 0
                                                else:
                                                        print('could not store integral of '+syst+' for '+proc)

                if doABCDnn:
                        for syst in systListABCDnn:
                                yieldTable[f'{histoPrefix}{syst}Up']['ABCDnn'] = yieldTable[f'{histoPrefix}{syst}Up']['ttbar'] + yieldTable[f'{histoPrefix}{syst}Up']['wjets'] + yieldTable[histoPrefix]['qcd'] + yieldTable[f'{histoPrefix}{syst}Up']['singletop']
                                yieldTable[f'{histoPrefix}{syst}Down']['ABCDnn'] = yieldTable[f'{histoPrefix}{syst}Down']['ttbar'] + yieldTable[f'{histoPrefix}{syst}Down']['wjets'] + yieldTable[histoPrefix]['qcd'] + yieldTable[f'{histoPrefix}{syst}Down']['singletop']

table = []
table.append(['break'])
table.append(['break'])
table.append(['YIELDS']+[proc for proc in list(bkgProcs.keys())+['ABCDnn', 'data']])

# yields for bkg and data
for cat in catList:
        row = [cat]
        if region=="all":
                histoPrefix = f'{iPlot}_{lumiStr}_{cat}'
        else:
                histoPrefix = f'{iPlot}_{lumiStr}_{cat}_{region}'
        for proc in list(bkgProcs.keys())+['ABCDnn', 'data']:
                row.append(str(round(yieldTable[histoPrefix][proc],3))+' $\pm$ '+str(round(yieldStatErrTable[histoPrefix][proc],3)))
        table.append(row)
table.append(['break'])
table.append(['break'])

table.append(['YIELDS']+sigList)
# yields for signals
for cat in catList:
        row = [cat]
        if region == "all":
                histoPrefix = f'{iPlot}_{lumiStr}_{cat}'
        else:
                histoPrefix = f'{iPlot}_{lumiStr}_{cat}_{region}'
        for proc in sigList:
                row.append(str(round(yieldTable[histoPrefix][proc],3))+' $\pm$ '+str(round(yieldStatErrTable[histoPrefix][proc],3)))
        table.append(row)

# yields for AN tables
for isEM in isEMlist:
        corrdSys = lumiSys  # maybe additional later?
        table.append(['break'])
        table.append(['','is'+isEM+'_yields'])
        table.append(['break'])
        #table.append(['YIELDS']+[cat for cat in catList if 'is'+isEM in cat]+['\\\\'])
        table.append(['YIELDS']+catList+['\\\\'])
        for proc in list(bkgProcs.keys())+['ABCDnn', 'totBkg','data','dataOverBkg']+sigList:
                row = [proc]
                for cat in catList:
                        if not ('is'+isEM in cat): continue
                        if region=="all":
                                histoPrefix = f'{iPlot}_{lumiStr}_{cat}'
                        else:
                                histoPrefix = f'{iPlot}_{lumiStr}_{cat}_{region}'
                        if proc=='data': 
                                row.append(' & '+str(int(yieldTable[histoPrefix][proc])))
                        else:
                                #row.append(' & '+str(round_sig(yieldTable[histoPrefix][proc],5))+' $\pm$ '+str(round_sig(yieldStatErrTable[histoPrefix][proc],2)))
                                row.append(' & '+str(round(yieldTable[histoPrefix][proc],2))+' $\pm$ '+str(round(yieldStatErrTable[histoPrefix][proc],2)))
                row.append('\\\\')
                table.append(row)

# TODO: yields for PAS tables (yields in e/m channels combined)
# skip for now

# systematics
if doAllSys:
        table.append(['break'])
        table.append(['','Systematics'])
        table.append(['break'])
        for proc in list(bkgProcs.keys())+sigList+['ABCDnn']:
                table.append([proc]+[cat for cat in catList]+['\\\\'])
                for syst in systListFullUCOC+systListABCDnn:
                        if 'pdf' in syst or syst == 'muR' or syst == 'muF': continue
                        for ud in ['Up', 'Down']:
                                row = [syst+ud]
                                for cat in catList:
                                        if region=="all":
                                                histoPrefix = f'{iPlot}_{lumiStr}_{cat}'
                                        else:
                                                histoPrefix = f'{iPlot}_{lumiStr}_{cat}_{region}'
                                        nomHist = histoPrefix
                                        shpHist = f'{histoPrefix}{syst}{ud}'
                                        try:
                                                row.append(' & '+str(round(yieldTable[shpHist][proc]/(yieldTable[nomHist][proc]+1e-20),2)))
                                        except:
                                                pass
                                row.append('\\\\')
                                table.append(row)
                table.append(['break'])
#print(table)
#exit()       

tabFile = f'{outDir}yields_{iPlot}_{lumiStr}.txt'
#if year != 'all': tabFile = outDir+'/yields_'+discriminant+'_'+year+'.txt'
out=open(tabFile,'w')
printTable(table,out)
