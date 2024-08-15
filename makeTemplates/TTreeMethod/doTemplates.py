#!/usr/bin/python

import os,sys,time,math,datetime,pickle,itertools,fnmatch
from ROOT import gROOT,TFile,TH1F, TH2D
parent = os.path.dirname(os.getcwd())
sys.path.append(parent)
from samples import targetlumi, lumiStr, systListShort, systListFull, samples_data, samples_signal, samples_electroweak, samples_wjets, samples_ttbar, samples_singletop, samples_ttbarx, samples_qcd
from utils import *

gROOT.SetBatch(1)
start_time = time.time()

region='A' # BAX, DCY, individuals, or all
isCategorized=True
year='all' # all

pfix='templates'+region
if not isCategorized: pfix='kinematics'+region
pfix+='_Oct2023statsonly_ABCDnn'
outDir = os.getcwd()+'/'+pfix+'/'

removeThreshold = 0.0005

scaleSignalXsecTo1pb = False # Set to True if analyze.py ever uses a non-1 cross section
doAllSys = False
doPDF = False
if isCategorized: doPDF=False # FIXME later

systematicList = systListShort
if isCategorized: systematicList = systListFull

bkgProcs = {'ewk':samples_electroweak,'wjets':samples_wjets,'ttbar':samples_ttbar,'singletop':samples_singletop,'ttx':samples_ttbarx,'qcd':samples_qcd}
massList = [800,1000,1200,1300,1400,1500,1600,1700,1800,2000,2200]
sigList = ['BpM'+str(mass) for mass in massList]

isEMlist = ['L'] #['E','M'], 'L' #
if '2D' in outDir: 
        isEMlist =['L']
taglist = ['all']
if isCategorized: 
        #taglist=['tagTjet','tagWjet','untagTlep','untagWlep','allWlep','allTlep']
        taglist=['allWlep','allTlep']
	
catList = ['is'+item[0]+'_'+item[1] for item in list(itertools.product(isEMlist,taglist))]

lumiSys = 0.018 #lumi uncertainty

###########################################################
#################### CATEGORIZATION #######################
###########################################################
def makeThetaCats(datahists,sighists,bkghists,discriminant):
        yieldTable = {}
        yieldStatErrTable = {}

        # Initialize empty yields dictionaries for table printing
        for cat in catList:
                histoPrefix=discriminant+'_'+lumiStr+'_'+cat
                yieldTable[histoPrefix]={}
                yieldStatErrTable[histoPrefix]={}
                if doAllSys:
                        for syst in systematicList:
                                for ud in ['Up','Dn']:
                                        yieldTable[histoPrefix+syst+ud]={}

        # Initialize dictionaries for histograms
        hists={}
        for cat in catList:
                print("              processing cat: "+cat)
                histoPrefix=discriminant+'_'+lumiStr+'_'+cat # set up in analyze.py. For syst it's discrim+syst+ud+'_'+lumiStr...

                #Group data processes
                idat = 0
                for dat in samples_data.keys():
                        #if year != 'all' and (year not in dat or (year == '2016' and '2016APV' in dat)): continue
                        if idat == 0:
                                hists['data'+cat] = datahists[histoPrefix+'_'+samples_data[dat].prefix].Clone(histoPrefix+'__data_obs')
                        else: 
                                hists['data'+cat].Add(datahists[histoPrefix+'_'+samples_data[dat].prefix])
                        idat += 1

                #Group background processes
                for proc in bkgProcs.keys(): # proc is a label like "ttbar" 
                        ibkg = 0
                        for bkg in bkgProcs[proc].keys(): # looping over the samples in a certain list
                                #if year != 'all' and (year not in bkg or (year == '2016' and '2016APV' in bkg)): continue
                                if ibkg == 0:
                                        hists[proc+cat] = bkghists[proc][histoPrefix+'_'+bkgProcs[proc][bkg].prefix].Clone(histoPrefix+'__'+proc)
                                        #hists[proc+cat].Scale(bkgProcs[proc][bkg].kfactor)
                                        #print('\t\t\t - scaled',bkg,'by kfactor',bkgProcs[proc][bkg].kfactor)
                                        if doAllSys:
                                                for syst in systematicList:
                                                        if syst == 'toppt' and proc != 'ttbar': continue
                                                        for ud in ['Up','Dn']:
                                                                hists[proc+cat+syst+ud] = bkghists[proc][histoPrefix.replace(discriminant,discriminant+syst+ud)+'_'+bkgProcs[proc][bkg].prefix].Clone(histoPrefix+'__'+proc+'__'+syst+'__'+ud.replace('Dn','Down'))
                                                                #hists[proc+cat+syst+ud].Scale(bkgProcs[proc][bkg].kfactor)
                                        if doPDF:
                                                for pdfInd in range(30):
                                                        hists[proc+cat+'pdf'+str(pdfInd)] = bkghists[proc][histoPrefix.replace(discriminant,discriminant+'pdf'+str(pdfInd))+'_'+bkgProcs[proc][bkg].prefix].Clone(histoPrefix+'__'+proc+'__pdf'+str(pdfInd))
                                                        #hists[proc+cat+'pdf'+str(pdfInd)].Scale(bkgProcs[proc][bkg].kfactor)
                                else: 
                                        histtemp = bkghists[proc][histoPrefix+'_'+bkgProcs[proc][bkg].prefix]
                                        #histtemp.Scale(bkgProcs[proc][bkg].kfactor)
                                        #print('\t\t\t - scaled',bkg,'by kfactor',bkgProcs[proc][bkg].kfactor)
                                        hists[proc+cat].Add(histtemp)
                                        if doAllSys:
                                                for syst in systematicList:
                                                        if syst == 'toppt' and proc != 'ttbar': continue
                                                        for ud in ['Up','Dn']:
                                                                histtemp = bkghists[proc][histoPrefix.replace(discriminant,discriminant+syst+ud)+'_'+bkgProcs[proc][bkg].prefix]
                                                                #histtemp.Scale(bkgProcs[proc][bkg].kfactor)
                                                                hists[proc+cat+syst+ud].Add(histtemp)
                                        if doPDF:
                                                for pdfInd in range(30):
                                                        histtemp = bkghists[proc][histoPrefix.replace(discriminant,discriminant+'pdf'+str(pdfInd))+'_'+bkgProcs[proc][bkg].prefix]
                                                        #histtemp.Scale(bkgProcs[proc][bkg].kfactor)
                                                        hists[proc+cat+'pdf'+str(pdfInd)].Add(histtemp)
                                ibkg += 1

                #Store signal
                for mass in massList:
                        isig = 0
                        for signal in samples_signal.keys():
                                #if year != 'all' and (year not in signal or (year == '2016' and '2016APV' in signal)): continue
                                if 'M'+str(mass) not in samples_signal[signal].prefix: 
                                        continue
                                if isig == 0:
                                        hists['BpM'+str(mass)+cat] = sighists[histoPrefix+'_'+samples_signal[signal].prefix].Clone(histoPrefix+'__BpM'+str(mass))
                                        if doAllSys:
                                                for syst in systematicList:
                                                        if syst=='toppt': continue
                                                        for ud in ['Up','Dn']:
                                                                hists['BpM'+str(mass)+cat+syst+ud] = sighists[histoPrefix.replace(discriminant,discriminant+syst+ud)+'_'+samples_signal[signal].prefix].Clone(histoPrefix+'__BpM'+str(mass)+'__'+syst+'__'+ud.replace('Dn','Down'))
                                        if doPDF:
                                                for pdfInd in range(30):
                                                        hists['BpM'+str(mass)+cat+'pdf'+str(pdfInd)] = sighists[histoPrefix.replace(discriminant,discriminant+'pdf'+str(pdfInd))+'_'+samples_signal[signal].prefix].Clone(histoPrefix+'__BpM'+str(mass)+'__pdf'+str(pdfInd))
                                else:
                                        hists['BpM'+str(mass)+cat].Add(sighists[histoPrefix+'_'+samples_signal[signal].prefix])
                                        if doAllSys:
                                                for syst in systematicList:
                                                        if syst=='toppt': continue
                                                        for ud in ['Up','Dn']:
                                                                hists['BpM'+str(mass)+cat+syst+ud].Add(sighists[histoPrefix.replace(discriminant,discriminant+syst+ud)+'_'+samples_signal[signal].prefix])
                                        if doPDF:
                                                for pdfInd in range(30):
                                                        hists['BpM'+str(mass)+cat+'pdf'+str(pdfInd)].Add(sighists[histoPrefix.replace(discriminant,discriminant+'pdf'+str(pdfInd))+'_'+samples_signal[signal].prefix])
                                isig += 1

                # Store integrals of all systematic hists in the table dictionary
                if doAllSys:
                        for syst in systematicList:
                                for ud in ['Up','Dn']:
                                        for proc in list(bkgProcs.keys())+sigList:
                                                if syst=='toppt' and proc != 'ttbar': continue
                                                yieldTable[histoPrefix+syst+ud][proc] = hists[proc+cat+syst+ud].Integral()
                #prepare yield table and MC yield error table
                for proc in list(bkgProcs.keys())+sigList+['data']: 
                        yieldTable[histoPrefix][proc] = hists[proc+cat].Integral()
                        yieldStatErrTable[histoPrefix][proc] = 0.
                        for ibin in range(1,hists['ewk'+cat].GetXaxis().GetNbins()+1):
                                yieldStatErrTable[histoPrefix][proc] += hists[proc+cat].GetBinError(ibin)**2

                yieldTable[histoPrefix]['totBkg'] = sum([hists[proc+cat].Integral() for proc in bkgProcs.keys()])
                yieldTable[histoPrefix]['dataOverBkg']= yieldTable[histoPrefix]['data']/yieldTable[histoPrefix]['totBkg']
                yieldStatErrTable[histoPrefix]['totBkg'] = 0.
                yieldStatErrTable[histoPrefix]['dataOverBkg']= 0.
                for ibin in range(1,hists['ewk'+cat].GetXaxis().GetNbins()+1):
                        yieldStatErrTable[histoPrefix]['totBkg'] += sum([hists[proc+cat].GetBinError(ibin)**2 for proc in bkgProcs.keys()])
                for key in yieldStatErrTable[histoPrefix].keys(): 
                        yieldStatErrTable[histoPrefix][key] = math.sqrt(yieldStatErrTable[histoPrefix][key])

        #scale signal cross section to 1pb
        if scaleSignalXsecTo1pb:
                print("       SCALING SIGNAL TEMPLATES TO 1pb ...")
                for signal in sigList:
                        for cat in catList:
                                hists[signal+cat].Scale(1./xsec[signal])
                                if doAllSys:
                                        for syst in systematicList:
                                                if syst=='toppt': continue
                                                hists[signal+cat+syst+'Up'].Scale(1./xsec[signal])
                                                hists[signal+cat+syst+'Dn'].Scale(1./xsec[signal])
                                        if doPDF:
                                                for pdfInd in range(30): 
                                                        hists[signal+cat+'pdf'+str(pdfInd)].Scale(1./xsec[signal])

        print("       WRITING COMBINE TEMPLATES: ")
        combineRfileName = outDir+'/templates_'+discriminant+'_'+lumiStr+'.root'
        if year != 'all': combineRfileName = outDir+'/templates_'+discriminant+'_'+year+'.root'
        combineRfile = TFile(combineRfileName,'RECREATE')
        for cat in catList:
                print("              ... "+cat)
                for signal in sigList:
                        hists[signal+cat].Write()
                        if doAllSys:
                                for syst in systematicList:
                                        if syst=='toppt': continue
                                        hists[signal+cat+syst+'Up'].Write()
                                        hists[signal+cat+syst+'Dn'].Write()
                        if doPDF:
                                for pdfInd in range(30): 
                                        hists[signal+cat+'pdf'+str(pdfInd)].Write()

                totBkg_ = sum([hists[proc+cat].Integral() for proc in bkgProcs.keys()])
                for proc in bkgProcs.keys():
                        if hists[proc+cat].Integral()/totBkg_ < removeThreshold:
                                print(proc+cat,"IS EMPTY OR < "+str(removeThreshold*100)+"% OF TOTAL BKG! SKIPPING ...")
                                continue
                        hists[proc+cat].Write()
                        if doAllSys:
                                for syst in systematicList:
                                        if syst=='toppt' and proc != 'ttbar': continue
                                        hists[proc+cat+syst+'Up'].Write()
                                        hists[proc+cat+syst+'Dn'].Write()
                        if doPDF:
                                for pdfInd in range(30): 
                                        hists[proc+cat+'pdf'+str(pdfInd)].Write()
                hists['data'+cat].Write()
        combineRfile.Close()

        # Create a table and write it out to a file
        table = []
        table.append(['break'])
        table.append(['break'])

        #yields without background grouping
        table.append(['YIELDS']+[proc for proc in list(bkgProcs.keys())+['data']])
        for cat in catList:
                row = [cat]
                histoPrefix=discriminant+'_'+lumiStr+'_'+cat
                for proc in list(bkgProcs.keys())+['data']:
                        row.append(str(yieldTable[histoPrefix][proc])+' $\pm$ '+str(yieldStatErrTable[histoPrefix][proc]))
                table.append(row)
        table.append(['break'])
        table.append(['break'])

        #yields for signals
        table.append(['YIELDS']+[proc for proc in sigList])
        for cat in catList:
                row = [cat]
                histoPrefix=discriminant+'_'+lumiStr+'_'+cat
                for proc in sigList:
                        row.append(str(yieldTable[histoPrefix][proc])+' $\pm$ '+str(yieldStatErrTable[histoPrefix][proc]))
                table.append(row)

        #yields for AN tables (yields in e/m channels)
        for isEM in isEMlist:
                corrdSys = lumiSys  # maybe additional later?
                table.append(['break'])
                table.append(['','is'+isEM+'_yields'])
                table.append(['break'])
                table.append(['YIELDS']+[cat for cat in catList if 'is'+isEM in cat]+['\\\\'])
                for proc in list(bkgProcs.keys())+['totBkg','data','dataOverBkg']+sigList:
                        row = [proc]
                        for cat in catList:
                                if not ('is'+isEM in cat): continue
                                histoPrefix=discriminant+'_'+lumiStr+'_'+cat
                                yieldtemp = 0.
                                yielderrtemp = 0.
                                if proc=='totBkg' or proc=='dataOverBkg':
                                        for bkg in bkgProcs.keys():
                                                try:
                                                        yieldtemp += yieldTable[histoPrefix][bkg]
                                                        yielderrtemp += yieldStatErrTable[histoPrefix][bkg]**2
                                                except:
                                                        print("Missing",bkg,"for channel:",cat)
                                                        pass
                                        yielderrtemp += (corrdSys*yieldtemp)**2
                                        if proc=='dataOverBkg':
                                                dataTemp = yieldTable[histoPrefix]['data']+1e-20
                                                dataTempErr = yieldStatErrTable[histoPrefix]['data']**2
                                                yielderrtemp = ((dataTemp/yieldtemp)**2)*(dataTempErr/dataTemp**2+yielderrtemp/yieldtemp**2)
                                                yieldtemp = dataTemp/yieldtemp
                                else:
                                        try:
                                                yieldtemp += yieldTable[histoPrefix][proc]
                                                yielderrtemp += yieldStatErrTable[histoPrefix][proc]**2
                                        except:
                                                print("Missing",proc,"for channel:",cat)
                                                pass
                                        yielderrtemp += (corrdSys*yieldtemp)**2
                                yielderrtemp = math.sqrt(yielderrtemp)
                                if proc=='data': 
                                        row.append(' & '+str(int(yieldTable[histoPrefix][proc])))
                                else: 
                                        row.append(' & '+str(round_sig(yieldtemp,5))+' $\pm$ '+str(round_sig(yielderrtemp,2)))
                        row.append('\\\\')
                        table.append(row)

        #yields for PAS tables (yields in e/m channels combined)
        if isEMlist == ['E','M']: # don't try this for other lists
                table.append(['break'])
                table.append(['','isL'+'_yields'])
                table.append(['break'])
                table.append(['YIELDS']+[cat.replace('isE','isL') for cat in catList if 'isE' in cat]+['\\\\'])
                for proc in list(bkgProcs.keys())+['totBkg','data','dataOverBkg']+sigList:
                        row = [proc]
                        for cat in catList:
                                if not ('isE' in cat): continue
                                histoPrefixE = discriminant+'_'+lumiStr+'_'+cat
                                histoPrefixM = histoPrefixE.replace('isE','isM')
                                yieldtemp = 0.
                                yieldtempE = 0.
                                yieldtempM = 0.
                                yielderrtemp = 0. 
                                if proc=='totBkg' or proc=='dataOverBkg':
                                        for bkg in bkgProcs.keys():
                                                try:
                                                        yieldtempE += yieldTable[histoPrefixE][bkg]
                                                        yieldtempM += yieldTable[histoPrefixM][bkg]
                                                        yieldtemp  += yieldTable[histoPrefixE][bkg]+yieldTable[histoPrefixM][bkg]
                                                        yielderrtemp += yieldStatErrTable[histoPrefixE][bkg]**2+yieldStatErrTable[histoPrefixM][bkg]**2
                                                except:
                                                        print("Missing",bkg,"for channel:",cat)
                                                        pass
                                        yielderrtemp += (corrdSys*yieldtempE)**2+(corrdSys*yieldtempM)**2
                                        if proc=='dataOverBkg':
                                                dataTemp = yieldTable[histoPrefixE]['data']+yieldTable[histoPrefixM]['data']+1e-20
                                                dataTempErr = yieldStatErrTable[histoPrefixE]['data']**2+yieldStatErrTable[histoPrefixM]['data']**2
                                                yielderrtemp = ((dataTemp/yieldtemp)**2)*(dataTempErr/dataTemp**2+yielderrtemp/yieldtemp**2)
                                                yieldtemp = dataTemp/yieldtemp
                                else:
                                        try:
                                                yieldtempE += yieldTable[histoPrefixE][proc]
                                                yieldtempM += yieldTable[histoPrefixM][proc]
                                                yieldtemp  += yieldTable[histoPrefixE][proc]+yieldTable[histoPrefixM][proc]
                                                yielderrtemp += yieldStatErrTable[histoPrefixE][proc]**2+yieldStatErrTable[histoPrefixM][proc]**2
                                        except:
                                                print("Missing",proc,"for channel:",cat)
                                                pass
                                        yielderrtemp += (corrdSys*yieldtempE)**2+(corrdSys*yieldtempM)**2
                                yielderrtemp = math.sqrt(yielderrtemp)
                                if proc=='data': 
                                        row.append(' & '+str(int(yieldTable[histoPrefixE][proc]+yieldTable[histoPrefixM][proc])))
                                else: 
                                        row.append(' & '+str(round_sig(yieldtemp,5))+' $\pm$ '+str(round_sig(yielderrtemp,2)))
                        row.append('\\\\')
                        table.append(row)

        #systematics
        if doAllSys:
                table.append(['break'])
                table.append(['','Systematics'])
                table.append(['break'])
                for proc in list(bkgProcs.keys())+sigList:
                        table.append([proc]+[cat for cat in catList]+['\\\\'])
                        for syst in sorted(systematicList):
                                for ud in ['Up','Dn']:
                                        row = [syst+ud]
                                        for cat in catList:
                                                histoPrefix = discriminant+'_'+lumiStr+'_'+cat
                                                nomHist = histoPrefix
                                                shpHist = histoPrefix+syst+ud
                                                try: 
                                                        row.append(' & '+str(round(yieldTable[shpHist][proc]/(yieldTable[nomHist][proc]+1e-20),2)))
                                                except:
                                                        if not ((syst=='toppt' and proc != 'ttbar')):
                                                                print("Missing",proc,"for channel:",cat,"and systematic:",syst)
                                                        pass
                                        row.append('\\\\')
                                        table.append(row)
                        table.append(['break'])

        tabFile = outDir+'/yields_'+discriminant+'_'+lumiStr+'.txt'
        if year != 'all': tabFile = outDir+'/yields_'+discriminant+'_'+year+'.txt'
        out=open(tabFile,'w')
        printTable(table,out)

def findfiles(path, filtre):
    for root, dirs, files in os.walk(path):
        for f in fnmatch.filter(files, filtre):
            yield os.path.join(root, f)

iPlotList = []
print('outDir:',outDir,'catList[0][2:]',catList[0][2:])
for file in findfiles(outDir+'/'+catList[0][2:]+'/', '*.p'):
    if 'sighists' not in file: continue
    if not os.path.exists(file.replace('sighists','datahists')): continue
    pFile = file.split('/')[-1]
    iPlotList.append(('_'.join(pFile.split('_')[1:]))[:-2])
print('Plot list:',iPlotList)

checkprint = False
for iPlot in iPlotList:
        #if year != 'all' and iPlot != 'HT': continue
        datahists = {} 
        bkghists  = {'ewk':{},'wjets':{},'ttbar':{},'singletop':{},'ttx':{},'qcd':{}}
        sighists  = {}
        #if iPlot!='HT': continue
        
        print("LOADING DISTRIBUTION: "+iPlot)
        for cat in catList:
                print("         ",cat[2:])
                datahists.update(pickle.load(open(outDir+'/'+cat[2:]+'/datahists_'+iPlot+'.p','rb')))
                sighists.update(pickle.load(open(outDir+'/'+cat[2:]+'/sighists_'+iPlot+'.p','rb')))
                bkghists['ewk'].update(pickle.load(open(outDir+'/'+cat[2:]+'/bkghists0_'+iPlot+'.p','rb')))
                bkghists['wjets'].update(pickle.load(open(outDir+'/'+cat[2:]+'/bkghists1_'+iPlot+'.p','rb')))
                bkghists['ttbar'].update(pickle.load(open(outDir+'/'+cat[2:]+'/bkghists2_'+iPlot+'.p','rb')))
                bkghists['singletop'].update(pickle.load(open(outDir+'/'+cat[2:]+'/bkghists3_'+iPlot+'.p','rb')))
                bkghists['ttx'].update(pickle.load(open(outDir+'/'+cat[2:]+'/bkghists4_'+iPlot+'.p','rb')))
                bkghists['qcd'].update(pickle.load(open(outDir+'/'+cat[2:]+'/bkghists5_'+iPlot+'.p','rb')))

        print("       MAKING CATEGORIES FOR TOTAL SIGNALS ...")

        #print(bkghists["ttbar"].keys())
        try:
                makeThetaCats(datahists,sighists,bkghists,iPlot)
        except:
                print('FAILED for',iPlot)
                pass

print("--- %s minutes ---" % (round((time.time() - start_time)/60,2)))
