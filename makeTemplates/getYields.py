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
        bkgProcs = {'ewk':samples_electroweak,'ttx':samples_ttbarx, 'major':None}
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

# ###################
# ### Yield Table ###
# ###################
# # Does not record data yield. Update if needed. Sample code in doTemplates_RDF.py
        
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
                yieldTable[histoPrefix]['ABCDnn'] = yieldTable[histoPrefix]['major']
                yieldStatErrTable[histoPrefix]['ABCDnn'] = yieldStatErrTable[histoPrefix]['major']
        else:
                yieldTable[histoPrefix]['ABCDnn'] = 0
                yieldStatErrTable[histoPrefix]['ABCDnn'] = 0

        if doAllSys:
                for syst in systListFullUCOC+systListABCDnn:
                        if 'pdf' in syst or syst == 'muR' or syst == 'muF': continue
                        for ud in ['Up', 'Down']:
                                yieldTable[f'{histoPrefix}{syst}{ud}']={}
                for proc in list(bkgProcs.keys())+sigList:
                        if proc=='major':
                                systematicList = systListABCDnn
                        else:
                                systematicList = systListFullUCOC
                                
                        for syst in systematicList:
                                if 'pdf' in syst or syst == 'muR' or syst == 'muF': continue
                                for ud in ['Up', 'Down']:
                                        try:
                                                yieldTable[f'{histoPrefix}{syst}{ud}'][proc]=combinedHistFile.Get(f'{histoPrefix}__{proc}__{syst}{ud}').Integral()
                                        except:
                                                if ('pNet' in syst and ('untag' in cat or ('Wtag' in syst and 'Tjet' in cat) or ('Ttag' in syst and 'Wjet' in cat))):
                                                        yieldTable[f'{histoPrefix}{syst}{ud}'][proc] = 0
                                                else:
                                                        print('could not store integral of '+syst+' for '+proc)

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

