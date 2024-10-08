#!/usr/bin/python

import os,sys,time,math,fnmatch
parent = os.path.dirname(os.getcwd())
sys.path.append(parent)
from array import array
from samples import lumiStr, systListShort, systListFull,  systListABCDnn
from utils import *
from ROOT import TFile, TH1, gROOT

gROOT.SetBatch(1)
start_time = time.time()

lumi=138. #for plots #56.1 #
lumiInTemplates= lumiStr

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Run as:
# > python modifyBinning.py

# Optional arguments:
# -- statistical uncertainty threshold
#
# Notes:
# -- Finds certain root files in a given directory and rebins all histograms in each file
# -- A selection of subset of files in the input directory can be done below under "#Setup the selection ..."
# -- A custom binning choice can also be given by manually filling "xbinsList[chn]" for each channel
#    with the preferred choice of binning
# -- If no rebinning is wanted, but want to add PDF and R/F uncertainties, use a stat unc threshold 
#    that is larger than 100% (i.e, >1.)
# -- Use "removalKeys" to remove specific systematics from the output file.
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

iPlot='BpMass_ABCDnn'
#iPlot='BpMass' #TEMP
if len(sys.argv)>1: iPlot=str(sys.argv[1])
folder = 'templatesD_Aug2024SysAll'

if len(sys.argv)>2: folder=str(sys.argv[2])
cutString = ''
templateDir = os.getcwd()+'/'+folder+'/'+cutString
print("templateDir: "+templateDir)
combinefile = 'templates_'+iPlot+'_'+lumiInTemplates+'.root'
print("file: "+combinefile)

normalizeRENORM = True #only for signals
normalizePDF    = True #only for signals
if 'kinematics' in folder:
	normalizeRENORM = False #only for signals
	normalizePDF    = False #only for signals

massList = [800,1000,1200,1300,1400,1500,1600,1700,1800,2000,2200]
sigProcList = ['BpM'+str(mass) for mass in massList]
bkgProcList = ['ttbar','singletop','wjets','ttx','ewk','qcd'] #put the most dominant process first
#ABCDProcList = ['',]

stat_saved = 0.2 #statistical uncertainty requirement (enter >1.0 for no rebinning; i.g., "1.1")
if len(sys.argv)>3: stat_saved=float(sys.argv[3])

rebin4chi2 = False

FullMu = True
if len(sys.argv)>4: FullMu=bool(eval(sys.argv[4]))
print("FullMu: "+str(FullMu))

dataName = 'data_obs'
upTag = 'Up'
downTag = 'Down'
sigName = 'Bp'

addCRsys = False
addShapes = True
lumiSys = math.sqrt(0.018**2) #lumi uncertainty plus higgs prop

removalKeys = {} # True == keep, False == remove
removalKeys['__muRUp'] = False
removalKeys['__muRDown'] = False
removalKeys['__muF'] = False
if 'kinematics' not in folder: removalKeys['__muRFcorrd'] = False
removalKeys['__pdf'] = False
if 'ABCDnn' in iPlot:
        removalKeys['__ttbar'] = False
        removalKeys['__wjets'] = False
        removalKeys['__singletop'] = False
        removalKeys['__qcd'] = False

def findfiles(path, filtre):
    for root, dirs, files in os.walk(path):
        for f in fnmatch.filter(files, filtre):
            yield os.path.join(root, f)

#Setup the selection of the files to be rebinned: templates_BpMass_138fbfb.root
rfiles = [file for file in findfiles(templateDir, '*.root') if 'rebinned' not in file and combinefile in file]

print("templateDir: "+templateDir)
print("iPlot: "+iPlot)

#Open the lowest mass signal for consistency
print(rfiles)
tfile = TFile(rfiles[0])
print (tfile)

datahists = [k.GetName() for k in tfile.GetListOfKeys() if '__'+dataName in k.GetName()]
#print datahists
channels = [hist[hist.find('fb_')+3:hist.find('__')] for hist in datahists]
allhists = {chn:[hist.GetName() for hist in tfile.GetListOfKeys() if chn in hist.GetName()] for chn in channels}

DataHists = {}
for hist in datahists:
	channel = hist[hist.find('fb_')+3:hist.find('__')]
	DataHists[channel] = tfile.Get(hist).Clone()

totBkgHists = {}
for hist in datahists:
	channel = hist[hist.find('fb_')+3:hist.find('__')]
	totBkgHists[channel]=tfile.Get(hist.replace('__'+dataName,'__'+bkgProcList[0])).Clone()
	for proc in bkgProcList:
		if proc == bkgProcList[0]: continue
		try: totBkgHists[channel].Add(tfile.Get(hist.replace('__'+dataName,'__'+proc)))
		except: 
			print("Missing "+proc+" for category: "+hist)
			print("WARNING! Skipping this process!!!!")
			pass

## Not currently using this -- it's for rebinning on signal stats.
##SigHists = {}
# for hist in datahists:
# 	channel = hist[hist.find('fb_')+3:hist.find('__')]
# 	if not rebinCombine: SigHists[channel]=tfile.Get(hist.replace('__'+dataName,'__sig')).Clone()
# 	else: 
# 		for proc in sigProcList:
# 			SigHists[channel+proc]=tfile.Get(hist.replace('__'+dataName,'__'+proc)).Clone()

xbinsListTemp = {}
for chn in totBkgHists.keys():
	stat = stat_saved

	#print 'Channel',chn,'integral is',totBkgHists[chn].Integral()
	print('Processing '+chn)

	Nbins = 0
	if 'templates' in folder:
                xbinsListTemp[chn]=[tfile.Get(datahists[0]).GetXaxis().GetBinUpEdge(tfile.Get(datahists[0]).GetXaxis().GetNbins())]
                Nbins = tfile.Get(datahists[0]).GetNbinsX()
                
	totTempBinContent = 0.
	totTempBinErrSquared = 0.
	totTempDataContent = 0.
	totTempDataErrSquared = 0.
	totTempSigContent = 0;
	for iBin in range(1,Nbins+1):
                totTempBinContent += totBkgHists[chn].GetBinContent(Nbins+1-iBin)
                totTempBinErrSquared += totBkgHists[chn].GetBinError(Nbins+1-iBin)**2
                try:
                        totTempSigContent += SigHists[chn].GetBinContent(Nbins+1-iBin)
                except: pass
                totTempDataContent += DataHists[chn].GetBinContent(Nbins+1-iBin)
                totTempDataErrSquared += totBkgHists[chn].GetBinError(Nbins+1-iBin)**2
		
		#print 'totTempBinContent =',totTempBinContent,' ',totTempBinContent_M,', totTempBinErrSquared =',totTempBinErrSquared,' ',totTempBinErrSquared_M
		#print 'totTempSigContent =',totTempSigContent,' ',totTempSigContent_M

                if totTempBinContent>0.:
                        if rebin4chi2 and (totTempDataContent == 0): continue
                        if math.sqrt(totTempBinErrSquared)/totTempBinContent<=stat:
                                if not rebin4chi2 or (math.sqrt(totTempDataErrSquared)/totTempDataContent<=stat):
                                        totTempBinContent = 0.
                                        totTempBinErrSquared = 0.
                                        totTempDataContent = 0.
                                        totTempDataErrSquared = 0.
                                        totTempSigContent = 0.
                                        #print 'Appending bin edge',totBkgHists[chn].GetXaxis().GetBinLowEdge(Nbins+1-iBin)
                                        xbinsListTemp[chn].append(totBkgHists[chn].GetXaxis().GetBinLowEdge(Nbins+1-iBin))

	## Going right to left -- if the last entry isn't 0 add it
	if xbinsListTemp[chn][-1]!=0: xbinsListTemp[chn].append(0)

        ## Placeholder: if needed for some plot, can add 1 at the end if rebinning left to right
	#if 'Large' in chn and 'LargeJ' not in chn and 'templatesCR' in folder and xbinsListTemp[chn][-1]!=1: xbinsListTemp[chn].append(1)

        ## Placeholder: add some other limit at the end as needed...
	# if (iPlot == 'DnnTprime' or iPlot == 'DnnBprime') and 'templatesSR' in folder:
	# 	if xbinsListTemp[chn][-1]>0.5: xbinsListTemp[chn].append(0.5)
	# 	elif xbinsListTemp[chn][-1]!=0.5: xbinsListTemp[chn][-1] = 0.5
	# elif (iPlot == 'DnnTprime' or iPlot == 'DnnBprime') and 'CR' in folder and 'SCR' not in folder and xbinsListTemp[chn][0]!=0.5: xbinsListTemp[chn][0] = 0.5 
	
	## If the 1st bin is empty or too small, make the left side wider
	if totBkgHists[chn].GetBinContent(1)==0.: 
		if len(xbinsListTemp[chn])>2: del xbinsListTemp[chn][-2]
	elif totBkgHists[chn].GetBinError(1)/totBkgHists[chn].GetBinContent(1)>stat: 
		if len(xbinsListTemp[chn])>2: del xbinsListTemp[chn][-2]

	## Ignore all this if stat is > 1
	if stat>1.0:
		xbinsListTemp[chn] = [tfile.Get(datahists[0]).GetXaxis().GetBinUpEdge(tfile.Get(datahists[0]).GetXaxis().GetNbins())]
		for iBin in range(1,Nbins+1): 
			xbinsListTemp[chn].append(totBkgHists[chn].GetXaxis().GetBinLowEdge(Nbins+1-iBin))

print("==> Here is the binning I found with "+str(stat_saved*100)+"% uncertainty threshold: ")
print("//"*40)
xbinsList = {}
for chn in xbinsListTemp.keys():
	xbinsList[chn] = []
	for bin in range(len(xbinsListTemp[chn])): xbinsList[chn].append(xbinsListTemp[chn][len(xbinsListTemp[chn])-1-bin])
	print(chn+" = "+str(xbinsList[chn]))
print("//"*40)

xbins = {}
for key in xbinsList.keys(): xbins[key] = array('d', xbinsList[key])

#os._exit(1)

### FIXME: not computed yet for Bprime...we will go for shape-only for now, very reasonable
muSFsUp = {'TTM900':0.744,'TTM1000':0.744,'TTM1100':0.747,'TTM1200':0.742,'TTM1300':0.741,'TTM1400':0.738,'TTM1500':0.740,'TTM1600':0.735,'TTM1700':0.721,'TTM1800':0.746}
muSFsDn = {'TTM900':1.312,'TTM1000':1.312,'TTM1100':1.306,'TTM1200':1.315,'TTM1300':1.316,'TTM1400':1.322,'TTM1500':1.319,'TTM1600':1.329,'TTM1700':1.354,'TTM1800':1.311}
pdfSFsUp = {'TTM900':0.997,'TTM1000':0.997,'TTM1100':0.996,'TTM1200':0.995,'TTM1300':0.994,'TTM1400':0.991,'TTM1500':0.986,'TTM1600':0.984,'TTM1700':0.980,'TTM1800':0.966}
pdfSFsDn = {'TTM900':1.005,'TTM1000':1.005,'TTM1100':1.007,'TTM1200':1.008,'TTM1300':1.011,'TTM1400':1.015,'TTM1500':1.022,'TTM1600':1.027,'TTM1700':1.031,'TTM1800':1.050}

iRfile=0
yieldsAll = {}
yieldsErrsAll = {}
yieldsSystErrsAll = {}
stat = stat_saved
binValue=0
for rfile in rfiles: 
        print("REBINNING FILE: "+rfile)
        tfiles = {}
        outputRfiles = {}
        tfiles[iRfile] = TFile(rfile)	
        if not rebin4chi2: 
                if not FullMu: 
                        outputRfiles[iRfile] = TFile(rfile.replace('.root','_BKGNORM_rebinned_stat'+str(stat).replace('.','p')+'.root'),'RECREATE')
                else: 
                        outputRfiles[iRfile] = TFile(rfile.replace('.root','_rebinned_stat'+str(stat).replace('.','p')+'.root'),'RECREATE')
        else: 
                outputRfiles[iRfile] = TFile(rfile.replace('.root','_chi2_rebinned_stat'+str(stat).replace('.','p')+'.root'),'RECREATE')

        signame = rfile.split('/')[-1].split('_')[1]

        print("PROGRESS:")
        for chn in channels:
                print("         "+chn)
                rebinnedHists = {}
                #Rebinning histograms
                for hist in allhists[chn]:
                        rebinnedHists[hist] = tfiles[iRfile].Get(hist).Rebin(len(xbins[chn])-1,hist,xbins[chn])
                        rebinnedHists[hist].SetDirectory(0)
                        if rebinnedHists[hist].Integral() < 1e-12: 
                                print("Empty hist found, skipping: "+hist)
                                continue
                        if '__pdf' in hist:
                                if 'Up' not in hist or 'Down' not in hist: continue
                        if any([item in hist and not removalKeys[item] for item in removalKeys.keys()]): continue
                        rebinnedHists[hist].Write()
                        yieldHistName = hist
                        yieldsAll[yieldHistName] = rebinnedHists[hist].Integral()
                        yieldsErrsAll[yieldHistName] = 0.
                        for ibin in range(1,rebinnedHists[hist].GetXaxis().GetNbins()+1):
                                yieldsErrsAll[yieldHistName] += rebinnedHists[hist].GetBinError(ibin)**2
                        yieldsErrsAll[yieldHistName] = math.sqrt(yieldsErrsAll[yieldHistName])

			
                ##Check for empty signal bins
                #sighist = rebinnedHists[iPlot+'_36p814fb_'+chn+'__sig']
                #for ibin in range(1,sighist.GetNbinsX()+1):
                #	if sighist.GetBinContent(ibin) == 0: print 'chn = '+chn+', mass = '+sigName+', empty minMlb > '+str(sighist.GetBinLowEdge(ibin))

                #For ABCDnn, combine the major backgrounds into one histogram
                if 'ABCDnn' in iPlot:
                        ttbarhists = [k.GetName() for k in tfiles[iRfile].GetListOfKeys() if '__ttbar' in k.GetName() and chn in k.GetName()]
                        #print(str(ttbarhists))
                        for hist in ttbarhists:
                                majorhist = rebinnedHists[hist].Clone(hist.replace('__ttbar','__major'))
                                majorhist.Add(rebinnedHists[hist.replace('__ttbar','__wjets')])
                                majorhist.Add(rebinnedHists[hist.replace('__ttbar','__singletop')])
                                majorhist.Add(rebinnedHists[hist.replace('__ttbar','__qcd')])
                                print('\t Writing majorhist: '+majorhist.GetName())
                                majorhist.Write()
                                yieldsAll[majorhist.GetName()] = majorhist.Integral()
                                yieldsErrsAll[majorhist.GetName()] = 0.
                                for ibin in range(1,majorhist.GetXaxis().GetNbins()+1):
                                        yieldsErrsAll[majorhist.GetName()] += majorhist.GetBinError(ibin)**2
                                yieldsErrsAll[majorhist.GetName()] = math.sqrt(yieldsErrsAll[majorhist.GetName()])

                #Constructing muRF shapes
                muRUphists = [k.GetName() for k in tfiles[iRfile].GetListOfKeys() if 'muR'+upTag in k.GetName() and chn in k.GetName()]
                for hist in muRUphists:
                        newMuRFNameBase = 'muRFcorrdNew'
                        if 'qcd__' in hist: newMuRFName = newMuRFNameBase+'QCD'
                        if 'ewk__' in hist: newMuRFName = newMuRFNameBase+'EWK'
                        if 'wjets__' in hist: newMuRFName = newMuRFNameBase+'WJT'
                        if 'ttbar__' in hist: newMuRFName = newMuRFNameBase+'TT'
                        if 'singletop__' in hist: newMuRFName = newMuRFNameBase+'ST'
                        if 'ttx__' in hist: newMuRFName = newMuRFNameBase+'TTX'
                        if '__'+sigName in hist: newMuRFName = newMuRFNameBase+'SIG'
                        muRFcorrdNewUpHist = rebinnedHists[hist].Clone(hist.replace('muR'+upTag,newMuRFName+upTag))
                        muRFcorrdNewDnHist = rebinnedHists[hist].Clone(hist.replace('muR'+upTag,newMuRFName+downTag))
                        histList = [
                                rebinnedHists[hist[:hist.find('__mu')]], #nominal
                                rebinnedHists[hist],
                                rebinnedHists[hist.replace('muR'+upTag,'muR'+downTag)],
                                rebinnedHists[hist.replace('muR'+upTag,'muF'+upTag)],
                                rebinnedHists[hist.replace('muR'+upTag,'muF'+downTag)],
                                rebinnedHists[hist.replace('muR'+upTag,'muRFcorrd'+upTag)],
                                rebinnedHists[hist.replace('muR'+upTag,'muRFcorrd'+downTag)]
                        ]
                        if histList[0].Integral() < 1e-6: 
                                print("muRF: Empty hist found, skipping: "+hist)
                                continue
                        for ibin in range(1,histList[0].GetNbinsX()+1):
                                weightList = [histList[ind].GetBinContent(ibin) for ind in range(len(histList))]
                                indCorrdUp = weightList.index(max(weightList))
                                indCorrdDn = weightList.index(min(weightList))
                                muRFcorrdNewUpHist.SetBinContent(ibin,histList[indCorrdUp].GetBinContent(ibin))
                                muRFcorrdNewDnHist.SetBinContent(ibin,histList[indCorrdDn].GetBinContent(ibin))
                                muRFcorrdNewUpHist.SetBinError(ibin,histList[indCorrdUp].GetBinError(ibin))
                                muRFcorrdNewDnHist.SetBinError(ibin,histList[indCorrdDn].GetBinError(ibin))
                        if ('__'+sigName in hist and '__mu' in hist and normalizeRENORM): #normalize the renorm/fact shapes to nominal
                                signame = hist.split('__')[1]
                                if sigName not in signame: print("DIDNT GET SIGNAME "+signame)
                                #scalefactorUp = muSFsUp[signame]
                                #scalefactorDn = muSFsDn[signame]
                                #muRFcorrdNewUpHist.Scale(scalefactorUp) #drop down .7   ### FIXME, NEED THIS FOR BPRIME
                                #muRFcorrdNewDnHist.Scale(scalefactorDn) #raise up 1.3
                                renormNomHist = histList[0]
                                muRFcorrdNewUpHist.Scale(renormNomHist.Integral()/muRFcorrdNewUpHist.Integral())
                                muRFcorrdNewDnHist.Scale(renormNomHist.Integral()/muRFcorrdNewDnHist.Integral())
                        if ('__'+sigName not in hist and normalizeRENORM and not FullMu):
                                renormNomHist = histList[0]
                                muRFcorrdNewUpHist.Scale(renormNomHist.Integral()/muRFcorrdNewUpHist.Integral())
                                muRFcorrdNewDnHist.Scale(renormNomHist.Integral()/muRFcorrdNewDnHist.Integral())
                        muRFcorrdNewUpHist.Write()
                        #print('Writing histogram: '+muRFcorrdNewUpHist.GetName())
                        muRFcorrdNewDnHist.Write()
                        #print('Writing histogram: '+muRFcorrdNewDnHist.GetName())

                        yieldsAll[muRFcorrdNewUpHist.GetName().replace('_sig','_'+rfile.split('_')[-2])] = muRFcorrdNewUpHist.Integral()
                        yieldsAll[muRFcorrdNewDnHist.GetName().replace('_sig','_'+rfile.split('_')[-2])] = muRFcorrdNewDnHist.Integral()

                #Constructing PDF shapes -- FIXME LATER FOR BPRIME!
                pdfUphists = [k.GetName() for k in tfiles[iRfile].GetListOfKeys() if 'pdf0' in k.GetName() and chn in k.GetName()]
                newPDFName = 'pdfNew'
                for hist in pdfUphists:
                        pdfNomHist = rebinnedHists[hist[:hist.find('__pdf')]]
                        pdfNewUpHist = rebinnedHists[hist].Clone(hist.replace('pdf0',newPDFName+upTag))
                        pdfNewDnHist = rebinnedHists[hist].Clone(hist.replace('pdf0',newPDFName+downTag))
                        for ibin in range(1,pdfNewUpHist.GetNbinsX()+1):
                                weightList = [rebinnedHists[hist.replace('pdf0','pdf'+str(pdfInd))].GetBinContent(ibin) for pdfInd in range(101)]
                                indPDFUp = sorted(range(len(weightList)), key=lambda k: weightList[k])[83]
                                indPDFDn = sorted(range(len(weightList)), key=lambda k: weightList[k])[15]
                                pdfNewUpHist.SetBinContent(ibin,rebinnedHists[hist.replace('pdf0','pdf'+str(indPDFUp))].GetBinContent(ibin))
                                pdfNewDnHist.SetBinContent(ibin,rebinnedHists[hist.replace('pdf0','pdf'+str(indPDFDn))].GetBinContent(ibin))
                                pdfNewUpHist.SetBinError(ibin,rebinnedHists[hist.replace('pdf0','pdf'+str(indPDFUp))].GetBinError(ibin))
                                pdfNewDnHist.SetBinError(ibin,rebinnedHists[hist.replace('pdf0','pdf'+str(indPDFDn))].GetBinError(ibin))
                        if ('__'+sigName in hist and '__pdf' in hist and normalizePDF): #normalize the renorm/fact shapes to nominal
                                signame = hist.split('__')[1]
                                if sigName not in signame: print("DIDNT GET SIGNAME "+signame)
                                #scalefactorUp = pdfSFsUp[signame]
                                #scalefactorDn = pdfSFsDn[signame]
                                #pdfNewUpHist.Scale(scalefactorUp)
                                #pdfNewDnHist.Scale(scalefactorDn)
                                pdfNewUpHist.Scale(pdfNomHist.Integral()/pdfNewUpHist.Integral())
                                pdfNewDnHist.Scale(pdfNomHist.Integral()/pdfNewDnHist.Integral())
                        pdfNewUpHist.Write()
                        # print 'Writing histogram: ',pdfNewUpHist.GetName()
                        pdfNewDnHist.Write()
                        # print 'Writing histogram: ',pdfNewDnHist.GetName()
                        yieldsAll[pdfNewUpHist.GetName().replace('_sig','_'+rfile.split('_')[-2])] = pdfNewUpHist.Integral()
                        yieldsAll[pdfNewDnHist.GetName().replace('_sig','_'+rfile.split('_')[-2])] = pdfNewDnHist.Integral()
			
        tfiles[iRfile].Close()
        outputRfiles[iRfile].Close()
        iRfile+=1
tfile.Close()
print(">> Rebinning Done!")

isEMlist =[]
taglist = []
for chn in channels:
        #isL_allTlep_D
	if chn.split('_')[0] not in isEMlist: isEMlist.append(chn.split('_')[0])
	if chn.split('_')[1] not in taglist: taglist.append(chn.split('_')[1])

if 'ABCDnn' in iPlot:
        bkgProcList = ['major','ttx','ewk'] #put the most dominant process first
print("List of systematics for "+bkgProcList[0]+" process and "+channels[0]+" channel:")
print("        "+str(sorted([hist[hist.find(bkgProcList[0])+len(bkgProcList[0])+2:hist.find(upTag)] for hist in yieldsAll.keys() if channels[0] in hist and '__'+bkgProcList[0]+'__' in hist and upTag in hist])))

def getShapeSystUnc(proc,chn):
	if not addShapes: return 0
	systematicList = sorted([hist[hist.find(proc)+len(proc)+2:hist.find(upTag)] for hist in yieldsAll.keys() if chn in hist and '__'+proc+'__' in hist and upTag in hist])
	totUpShiftPrctg=0
	totDnShiftPrctg=0
	histoPrefix = allhists[chn][0][:allhists[chn][0].find('__')+2]
	nomHist = histoPrefix+proc
	for syst in systematicList:
		for ud in [upTag,downTag]:
			shpHist = histoPrefix+proc+'__'+syst+ud
			shift = yieldsAll[shpHist]/(yieldsAll[nomHist]+1e-20)-1
			if shift>0.: totUpShiftPrctg+=shift**2
			if shift<0.: totDnShiftPrctg+=shift**2
	shpSystUncPrctg = (math.sqrt(totUpShiftPrctg)+math.sqrt(totDnShiftPrctg))/2 #symmetrize the total shape uncertainty up/down shifts
	return shpSystUncPrctg	

table = []
taglist = ['tag','untag']
if 'kinematics' in folder: taglist = ['all']
for isEM in isEMlist:
        if isEM=='isE': corrdSys = elcorrdSys
        if isEM=='isM': corrdSys = mucorrdSys
        if isEM=='isL': corrdSys = lumiSys
        for tag in taglist:
                table.append(['break'])
                table.append(['',isEM+'_'+tag+'_yields'])
                table.append(['break'])
                table.append(['YIELDS']+[chn for chn in channels if isEM in chn and tag in chn]+['\\\\'])
                for proc in bkgProcList+['totBkg',dataName,'dataOverBkg']+sigProcList:
                        row = [proc]
                        for chn in channels:
                                if not (isEM in chn and tag in chn): continue
                                modTag = chn[chn.find('is'):]
                                histoPrefix = allhists[chn][0][:allhists[chn][0].find('__')+2]
                                yieldtemp = 0.
                                yielderrtemp = 0.
                                if proc=='totBkg' or proc=='dataOverBkg':
                                        for bkg in bkgProcList:
                                                try:
                                                        yieldtemp += yieldsAll[histoPrefix+bkg]
                                                        yielderrtemp += yieldsErrsAll[histoPrefix+bkg]**2
                                                        yielderrtemp += (getShapeSystUnc(bkg,chn)*yieldsAll[histoPrefix+bkg])**2
                                                except:
                                                        if bkg != 'qcd': print("Missing "+bkg+" for channel in totBkg or dataOverBkg: "+chn)
                                                        pass
                                        yielderrtemp += (corrdSys*yieldtemp)**2
                                        if proc=='dataOverBkg':
                                                dataTemp = yieldsAll[histoPrefix+dataName]+1e-20
                                                dataTempErr = yieldsErrsAll[histoPrefix+dataName]**2
                                                yielderrtemp = ((dataTemp/yieldtemp)**2)*(dataTempErr/dataTemp**2+yielderrtemp/yieldtemp**2)
                                                yieldtemp = dataTemp/yieldtemp
                                else:
                                        try:
                                                yieldtemp += yieldsAll[histoPrefix+proc]
                                                yielderrtemp += yieldsErrsAll[histoPrefix+proc]**2
                                                yielderrtemp += (getShapeSystUnc(proc,chn)*yieldsAll[histoPrefix+proc])**2
                                        except:
                                                if proc != 'qcd': print("Missing "+proc+" for channel individual: "+chn)
                                                pass
                                        if proc in sigProcList:
                                                signal=proc
                                                if 'left' in signal: signal=proc.replace('left','')+'left'
                                                if 'right' in signal: signal=proc.replace('right','')+'right'
                                                #yieldtemp*=xsec[signal]  ### FIXME using the new dicts if we want non-1pb
                                                #yielderrtemp*=xsec[signal]**2
                                        yielderrtemp += (corrdSys*yieldtemp)**2
                                yielderrtemp = math.sqrt(yielderrtemp)
				#print "yieldsAll: ",yieldsAll
                                if proc==dataName: 
                                        row.append(' & '+str(int(yieldsAll[histoPrefix+proc])))
                                else: 
                                        row.append(' & '+str(round_sig(yieldtemp,5))+' $\pm$ '+str(round_sig(yielderrtemp,2)))
                        row.append('\\\\')
                        table.append(row)

## FIXME: put this back if we end up splitting E and M			
# for tag in taglist:
# 	table.append(['break'])
# 	table.append(['','isL_'+tag+'_yields'])
# 	table.append(['break'])
# 	table.append(['YIELDS']+[chn.replace('isE','isL') for chn in channels if 'isE' in chn and tag in chn]+['\\\\'])
# 	for proc in bkgProcList+['totBkg',dataName,'dataOverBkg']+sigProcList:
# 		row = [proc]
# 		for chn in channels:
# 			if not ('isE' in chn and tag in chn): continue
# 			modTag = chn[chn.find('is'):]
# 			histoPrefixE = allhists[chn][0][:allhists[chn][0].find('__')+2]
# 			histoPrefixM = histoPrefixE.replace('isE','isM')
# 			yieldtemp = 0.
# 			yieldtempE = 0.
# 			yieldtempM = 0.
# 			yielderrtemp = 0. 
# 			if proc=='totBkg' or proc=='dataOverBkg':
# 				for bkg in bkgProcList:
# 					yieldEplusMtemp = 0
# 					try:
# 						yieldtempE += yieldsAll[histoPrefixE+bkg]
# 						yieldtemp += yieldsAll[histoPrefixE+bkg]
# 						yieldEplusMtemp += yieldsAll[histoPrefixE+bkg]
# 						yielderrtemp += yieldsErrsAll[histoPrefixE+bkg]**2
# 						yielderrtemp += (getShapeSystUnc(bkg,chn)*yieldsAll[histoPrefixE+bkg])**2
# 					except:
# 						if bkg != 'qcd': print "Missing",bkg,"for channel in totBkg:",chn
# 						pass
# 					try:
# 						yieldtempM += yieldsAll[histoPrefixM+bkg]
# 						yieldtemp += yieldsAll[histoPrefixM+bkg]
# 						yieldEplusMtemp += yieldsAll[histoPrefixM+bkg]
# 						yielderrtemp += yieldsErrsAll[histoPrefixM+bkg]**2
# 						yielderrtemp += (getShapeSystUnc(bkg,chn.replace('isE','isM'))*yieldsAll[histoPrefixM+bkg])**2
# 					except:
# 						if bkg != 'qcd': print "Missing",bkg,"for channel in totBkg:",chn.replace('isE','isM')
# 						pass
# 					yielderrtemp += (modelingSys[bkg+'_'+modTag]*yieldEplusMtemp)**2 #(addSys*(Nelectron+Nmuon))**2 --> correlated across e/m
# 				yielderrtemp += (elcorrdSys*yieldtempE)**2+(mucorrdSys*yieldtempM)**2
# 				if proc=='dataOverBkg':
# 					dataTemp = yieldsAll[histoPrefixE+dataName]+yieldsAll[histoPrefixM+dataName]+1e-20
# 					dataTempErr = yieldsErrsAll[histoPrefixE+dataName]**2+yieldsErrsAll[histoPrefixM+dataName]**2
# 					yielderrtemp = ((dataTemp/yieldtemp)**2)*(dataTempErr/dataTemp**2+yielderrtemp/yieldtemp**2)
# 					yieldtemp = dataTemp/yieldtemp
# 			else:
# 				try:
# 					yieldtempE += yieldsAll[histoPrefixE+proc]
# 					yieldtemp  += yieldsAll[histoPrefixE+proc]
# 					yielderrtemp += yieldsErrsAll[histoPrefixE+proc]**2
# 					yielderrtemp += (getShapeSystUnc(proc,chn)*yieldsAll[histoPrefixE+proc])**2
# 				except:
# 					if proc != 'qcd': print "Missing",proc,"for channel individual:",chn
# 					pass
# 				try:
# 					yieldtempM += yieldsAll[histoPrefixM+proc]
# 					yieldtemp  += yieldsAll[histoPrefixM+proc]
# 					yielderrtemp += yieldsErrsAll[histoPrefixM+proc]**2
# 					yielderrtemp += (getShapeSystUnc(proc,chn.replace('isE','isM'))*yieldsAll[histoPrefixM+proc])**2
# 				except:
# 					if proc != 'qcd': print "Missing",proc,"for channel individual:",chn.replace('isE','isM')
# 					pass
# 				if proc in sigProcList:
# 					signal=proc
# 					if 'left' in signal: signal=proc.replace('left','')+'left'
# 					if 'right' in signal: signal=proc.replace('right','')+'right'
# 					yieldtempE*=xsec[signal]
# 					yieldtempM*=xsec[signal]
# 					yieldtemp*=xsec[signal]
# 					yielderrtemp*=xsec[signal]**2
# 				else: yielderrtemp += (modelingSys[proc+'_'+modTag]*yieldtemp)**2 #(addSys*(Nelectron+Nmuon))**2 --> correlated across e/m
# 				yielderrtemp += (elcorrdSys*yieldtempE)**2+(mucorrdSys*yieldtempM)**2
# 			yielderrtemp = math.sqrt(yielderrtemp)
# 			if proc==dataName: row.append(' & '+str(int(yieldsAll[histoPrefixE+proc]+yieldsAll[histoPrefixM+proc])))
# 			else: row.append(' & '+str(round_sig(yieldtemp,5))+' $\pm$ '+str(round_sig(yielderrtemp,2)))
# 		row.append('\\\\')
# 		table.append(row)
	
#systematics
table.append(['break'])
table.append(['','Systematics'])
table.append(['break'])
for proc in bkgProcList+sigProcList:
        table.append([proc]+[chn for chn in channels]+['\\\\'])
        systematicList = sorted([hist[hist.find(proc)+len(proc)+2:hist.find(upTag)] for hist in yieldsAll.keys() if channels[0] in hist and '__'+proc+'__' in hist and upTag in hist])
        systematicList.append('pNetWtag')
        for syst in systematicList:
                for ud in [upTag,downTag]:
                        row = [syst+ud]
                        for chn in channels:
                                histoPrefix = allhists[chn][0][:allhists[chn][0].find('__')+2]
                                nomHist = histoPrefix+proc
                                shpHist = histoPrefix+proc+'__'+syst+ud
                                try:
                                        row.append(' & '+str(round(yieldsAll[shpHist]/(yieldsAll[nomHist]+1e-20),2)))
                                except:
                                        if 'Wtag' in syst and ('Tjet' in chn or 'Wlep' in chn): row.append(' & \\NA')
                                        elif 'Ttag' in syst and ('Wjet' in chn or 'Tlep' in chn): row.append(' & \\NA')
                                        elif proc != 'qcd': print("Missing "+proc+" for channel: "+chn+" and systematic: "+syst)
                                        pass
                        row.append('\\\\')
                        table.append(row)
        table.append(['break'])

postFix = ''
out=open(templateDir+'/'+combinefile.replace('templates','yields').replace('.root','_rebinned_stat'+str(stat).replace('.','p'))+postFix+'.txt','w')

printTable(table,out)

print("--- %s minutes ---" % (round((time.time() - start_time)/60,2)))



