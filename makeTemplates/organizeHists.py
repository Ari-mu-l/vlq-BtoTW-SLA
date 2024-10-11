#!/usr/bin/python

import os,sys,time,math,datetime,itertools,ctypes
from ROOT import gROOT,TFile,TH1F, TH2D
parent = os.path.dirname(os.getcwd())
sys.path.append(parent)
from samples import targetlumi, lumiStr, systListFull, systListABCDnn, samples_data, samples_signal, samples_electroweak, samples_wjets, samples_singletop, samples_ttbarx, samples_qcd
from utils import *

gROOT.SetBatch(1)
start_time = time.time()

region='A' # BAX, DCY, individuals, or all
if len(sys.argv)>1: region = str(sys.argv[1])

isCategorized=True
year='all' # all

pfix='templates'+region
if not isCategorized: pfix='kinematics'+region

pfix+='_Oct2024StatsOnly' 
outDir = os.getcwd()+'/'+pfix+'/'

removeThreshold = 0.0005 # TODO: add if necessary

scaleSignalXsecTo1pb = False # Set to True if analyze.py ever uses a non-1 cross section
doAllSys = False # TEMP
doPDF = False
if isCategorized: doPDF=False # FIXME later

iPlot = "BpMass"
#iPlot = "OS1FatJetProbJ"
#iPlot = "BpMass_ABCDnn"


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
        taglist=['tagTjet','tagWjet','untagTlep','untagWlep','allWlep','allTlep']
        #taglist=['allWlep','allTlep']
        #taglist=['tagTjet','tagWjet','untagTlep','untagWlep']
        
catList = ['is'+item[0]+'_'+item[1] for item in list(itertools.product(isEMlist,taglist))]

lumiSys = 0.018 #lumi uncertainty

groupHists = True # TEMP
getYields = False # TEMP

plotList = ['ST',
            'BpMass',
            'HT',
            'lepPt',
            'lepEta',
            'lepPhi',
            'lepIso',
            'MET',
            'METphi',
            'JetEta',
            'JetPt'
            'JetPhi',
            'JetBtag',
            'ForwJetEta',
            'ForwJetPt' ,
            'ForwJetPhi',
            'FatJetEta',
            'FatJetPt' ,
            'FatJetPhi',
            'FatJetSD' ,
            'FatJetMatch',
            'OS1FatJetEta',
            'OS1FatJetPt' ,
            'OS1FatJetPhi',
            'OS1FatJetSD' ,
            'NJetsCentral' ,
            'NJetsForward' ,
            'NBJets',
            'NOSJets',
            'NSSJets',
            'NOSBJets',
            'NSSBJets',
            'NFatJets',
            'NOSFatJets',
            'NSSFatJets',
            'minDR_twoAK8s',
            'minDR_twoAK4s',
            'PtRel',
            'PtRelAK8',
            'minDR',
            'minDRAK8',
            'FatJetTau21'  ,
            'FatJetTau32'  ,
            'OS1FatJetTau21'  ,
            'OS1FatJetTau32'  ,
            'FatJetProbJ',
            'FatJetProbT',
            'FatJetProbW',
            'FatJetProbTvJ',
            'FatJetProbWvJ',
            'FatJetTag',
            'OS1FatJetProbJ',
            'OS1FatJetProbT',
            'OS1FatJetProbW',
            'OS1FatJetProbTvJ',
            'OS1FatJetProbWvJ',
            'OS1FatJetTag',
            'nT',
            'nW',
            'Wmass',
            'Wpt',
            'Weta',
            'Wphi',
            'WMt',
            'Wdrlep',
            'minMlj',
            'tmassMLJ',
            'tptMLJ',
            'tetaMLJ',
            'tphiMLJ',
            'tmassSSB',
            'tptSSB',
            'tetaSSB',
            'tphiSSB',
            'tdrWbMLJ',
            'tdrWbSSB',
            'BpPt',
            'BpEta',
            'BpPhi',
            'BpDeltaR',
            'BpPtBal',
            'BpChi2',
            'BpDecay',
            'BpMass_ABCDnn',
            'OS1FatJetProbJ_ABCDnn',
            # 'ST_ABCDnn'
]

### Group histograms
### TODO: add Up and Dn
### TODO: ABCDnn
if groupHists:
        outHistFile = TFile.Open(f'{outDir}templates_{iPlot}_{lumiStr}.root', "RECREATE")
        for cat in catList:
                print("PROGRESS: "+cat)
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
                        systHists = {}
                        isFirstHist = True

                        if doABCDnn and (proc=="ttbar" or proc=="qcd" or proc=="wjets" or proc=="singletop"):
                                systematicList = systListABCDnn
                        else:
                                systematicList = systListFull

                        for bkg in bkgGrp:
                                if not doABCDnn and 'QCDHT200' in bkg:
                                        print("Plotting without QCDHT200.")
                                        continue
                                if isFirstHist:
                                        hists = bkgHistFile.Get(histoPrefix+'_'+bkgGrp[bkg].prefix).Clone(histoPrefix+'__'+proc)
                                        isFirstHist = False
                                        if doAllSys:
                                                for syst in systematicList:
                                                        systHists[f'{histoPrefix}__{proc}__{syst}Up'] = bkgHistFile.Get(f'{histoPrefix}_{syst}Up_{bkgGrp[bkg].prefix}').Clone(f'{histoPrefix}__{proc}__{syst}Up')
                                                        systHists[f'{histoPrefix}__{proc}__{syst}Down'] = bkgHistFile.Get(f'{histoPrefix}_{syst}Dn_{bkgGrp[bkg].prefix}').Clone(f'{histoPrefix}__{proc}__{syst}Down')
                                else:
                                        print(histoPrefix+'_'+bkgGrp[bkg].prefix)
                                        hists.Add(bkgHistFile.Get(histoPrefix+'_'+bkgGrp[bkg].prefix))
                                        if doAllSys:
                                                for syst in systematicList:
                                                        try:
                                                                systHists[f'{histoPrefix}__{proc}__{syst}Up'].Add(bkgHistFile.Get(f'{histoPrefix}_{syst}Up_{bkgGrp[bkg].prefix}').Clone(f'{histoPrefix}__{proc}__{syst}Up'))
                                                                systHists[f'{histoPrefix}__{proc}__{syst}Down'].Add(bkgHistFile.Get(f'{histoPrefix}_{syst}Dn_{bkgGrp[bkg].prefix}').Clone(f'{histoPrefix}__{proc}__{syst}Down'))
                                                        except:
                                                                print('could not process '+syst+' for '+bkg)

                        outHistFile.cd()
                        hists.Write()
                        for systHist in systHists:
                                systHists[systHist].Write()
                        bkgHistFile.Close()

                sigHistFile = TFile.Open(f'{outDir}{cat[2:]}/sighists_{iPlot}.root', "READ")
                systematicList = systListFull

                for mass in massList:
                        systHists = {}
                        isFirstHist = True
                        for signal in samples_signal:
                                if f'Bprime_M{mass}' in signal:
                                        if isFirstHist:
                                                hists = sigHistFile.Get(histoPrefix+'_'+signal).Clone(histoPrefix+'__BpM'+str(mass))
                                                isFirstHist = False
                                                if doAllSys:
                                                        for syst in systematicList:
                                                                try:
                                                                	systHists[f'{histoPrefix}__BpM{mass}__{syst}Up'] = sigHistFile.Get(f'{histoPrefix}_{syst}Up_{samples_signal[signal].prefix}').Clone(f'{histoPrefix}__BpM{mass}__{syst}Up')
                                                                	systHists[f'{histoPrefix}__BpM{mass}__{syst}Down'] = sigHistFile.Get(f'{histoPrefix}_{syst}Dn_{samples_signal[signal].prefix}').Clone(f'{histoPrefix}__BpM{mass}__{syst}Down')
                                                                except:
                                                                        print('could not process '+syst+' for '+str(mass))
                                        else:
                                                hists.Add(sigHistFile.Get(histoPrefix+'_'+signal))
                                                if doAllSys:
                                                        for syst in systematicList:
                                                                #print(f'{histoPrefix}_{syst}Up_{bkgGrp[bkg].prefix}')
                                                                try:
                                                                        systHists[f'{histoPrefix}__BpM{mass}__{syst}Up'].Add(sigHistFile.Get(f'{histoPrefix}_{syst}Up_{samples_signal[signal].prefix}').Clone(f'{histoPrefix}__BpM{mass}__{syst}Up'))
                                                                        systHists[f'{histoPrefix}__BpM{mass}__{syst}Down'].Add(sigHistFile.Get(f'{histoPrefix}_{syst}Dn_{samples_signal[signal].prefix}').Clone(f'{histoPrefix}__BpM{mass}__{syst}Down'))
                                                                except:
                                                                        print('could not process '+syst+' for '+str(mass))
                        outHistFile.cd()
                        hists.Write()
                        for systHist in systHists:
                                systHists[systHist].Write()
                sigHistFile.Close()
        outHistFile.Close()

###################
### Yield Table ###
###################
# Does not record data yield. Update if needed. Sample code in doTemplates_RDF.py

yieldTable = {}
yieldStatErrTable = {}

combinedHistFile = TFile.Open(f'{outDir}templates_{iPlot}_{lumiStr}.root', "READ")

# Initialize empty yields dictionaries for table printing
for cat in catList:
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

        if doAllSys:
                for syst in systListFull+systListABCDnn:
                        for ud in ['Up', 'Down']:
                                yieldTable[f'{histoPrefix}{syst}{ud}']={}
                for proc in list(bkgProcs.keys())+sigList:
                        if doABCDnn and (proc=="ttbar" or proc=="qcd" or proc=="wjets" or proc=="singletop"):
                                systematicList = systListABCDnn
                                dummyList = systListFull
                        else:
                                systematicList = systListFull
                                dummyList = systListABCDnn
                        for syst in systematicList:
                                for ud in ['Up', 'Down']:
                                        yieldTable[f'{histoPrefix}{syst}{ud}'][proc]=combinedHistFile.Get(f'{histoPrefix}__{proc}__{syst}{ud}').Integral()
                        for syst in dummyList:
                                for ud in ['Up', 'Down']:
                                        yieldTable[f'{histoPrefix}{syst}{ud}'][proc]=0

        
table = []
table.append(['break'])
table.append(['break'])
table.append(['YIELDS']+[proc for proc in list(bkgProcs.keys())+['data']])

# yields for bkg and data
for cat in catList:
        row = [cat]
        histoPrefix = f'{iPlot}_{lumiStr}_{cat}_{region}'
        for proc in list(bkgProcs.keys())+['data']:
                row.append(str(round(yieldTable[histoPrefix][proc],3))+' $\pm$ '+str(round(yieldStatErrTable[histoPrefix][proc],3)))
        table.append(row)
table.append(['break'])
table.append(['break'])

table.append(['YIELDS']+sigList)
# yields for signals
for cat in catList:
        row = [cat]
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
        for proc in list(bkgProcs.keys())+['totBkg','data','dataOverBkg']+sigList:
                row = [proc]
                for cat in catList:
                        if not ('is'+isEM in cat): continue
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
        for proc in list(bkgProcs.keys())+sigList:
                table.append([proc]+[cat for cat in catList]+['\\\\'])
                for syst in systListFull+systListABCDnn:
                        for ud in ['Up', 'Down']:
                                row = [syst+ud]
                                for cat in catList:
                                        histoPrefix = f'{iPlot}_{lumiStr}_{cat}_{region}'
                                        nomHist = histoPrefix
                                        shpHist = f'{histoPrefix}{syst}{ud}'
                                        try:
                                                row.append(' & '+str(round(yieldTable[shpHist][proc]/(yieldTable[nomHist][proc]+1e-20),2)))
                                        except:
                                                print(f'Missing {proc} for systematic: {syst}')
                                row.append('\\\\')
                                table.append(row)
                table.append(['break'])
#print(table)
#exit()       

tabFile = f'{outDir}yields_{iPlot}_{lumiStr}.txt'
#if year != 'all': tabFile = outDir+'/yields_'+discriminant+'_'+year+'.txt'
out=open(tabFile,'w')
printTable(table,out)
