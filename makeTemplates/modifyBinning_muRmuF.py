#!/usr/bin/python

import os,sys,time,math,fnmatch,copy
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
if len(sys.argv)>1: iPlot=str(sys.argv[1])
folder = 'templatesD_Apr2024SysAll_correctQCD300'

if len(sys.argv)>2: folder=str(sys.argv[2])
cutString = ''
templateDir = os.getcwd()+'/'+folder+'/'+cutString
print("templateDir: "+templateDir)
combinefile = 'templates_'+iPlot+'_'+lumiInTemplates+'.root'
print("file: "+combinefile)

doTwoSided = False
doTruncated = False
if 'templatesD_' not in folder: doTruncated = False
normalizeRENORM = True #only for signals
normalizePDF    = True #only for signals
if 'kinematics' in folder:
	normalizeRENORM = False #only for signals
	normalizePDF    = False #only for signals

massList = [800,1000,1200,1300,1400,1500,1600,1700,1800,2000,2200]
sigProcList = ['BpM'+str(mass) for mass in massList]
bkgProcList = ['ttbar','singletop','wjets','ttx','ewk','qcd'] #put the most dominant process first
if 'ABCDnn' in iPlot:
        bkgProcList = ['major','ttx','ewk'] #put the most dominant process first
#ABCDProcList = ['',]

stat_saved = 0.2 #statistical uncertainty requirement (enter >1.0 for no rebinning; i.g., "1.1")
if len(sys.argv)>3: stat_saved=float(sys.argv[3])

rebin4chi2 = False

rebinX = 1
if len(sys.argv)>4: rebinX = int(sys.argv[4])
print("Initial rebin of factor "+str(rebinX))

doVRunc = False
if len(sys.argv)>5: doVRunc=bool(eval(sys.argv[5]))
print("Adding VR uncert?: "+str(doVRunc))


dataName = 'data_obs'
upTag = 'Up'
downTag = 'Down'
sigName = 'Bp'

addCRsys = False
addShapes = True
lumiSys = math.sqrt(0.018**2) #lumi uncertainty plus higgs prop

removalKeys = {} # True == keep, False == remove
removalKeys['__factor'] = False
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
rfiles = [file for file in findfiles(templateDir, '*.root') if 'rebinned' not in file and 'smoothed' not in file and iPlot in file]
print(rfiles)

print("templateDir: "+templateDir)
print("iPlot: "+iPlot)

#Open the lowest mass signal for consistency
tfile = TFile(rfiles[0])

datahists = [k.GetName() for k in tfile.GetListOfKeys() if '__'+dataName in k.GetName()]
#print datahists
channels = [hist[hist.find('fb_')+3:hist.find('__')] for hist in datahists]
if 'validation' in folder:
        channels.remove('isL_tagTjet_D')
        channels.remove('isL_tagWjet_D')
        
allhists = {chn:[hist.GetName() for hist in tfile.GetListOfKeys() if chn in hist.GetName()] for chn in channels}

DataHists = {}
for hist in datahists:
        channel = hist[hist.find('fb_')+3:hist.find('__')]
        DataHists[channel] = tfile.Get(hist).Clone()
        if rebinX > 1:
                DataHists[channel].Rebin(rebinX)

totBkgHists = {}
for hist in datahists:
        channel = hist[hist.find('fb_')+3:hist.find('__')]
        totBkgHists[channel]=tfile.Get(hist.replace('__'+dataName,'__'+bkgProcList[0])).Clone()
        if rebinX > 1:
                totBkgHists[channel].Rebin(rebinX)
        ##### Use this if the "major" histogram needs statistical uncertainties added
        # if bkgProcList[0] == 'major':
        #         temphist = totBkgHists[channel].Clone()
        #         for ibin in range(1,temphist.GetNbinsX()+1):
        #                 totBkgHists[channel].SetBinContent(ibin,temphist.GetBinContent(ibin))
        #                 totBkgHists[channel].SetBinError(ibin,math.sqrt(temphist.GetBinContent(ibin)))
        #                 #print("CHECK: content = ",totBkgHists[channel].GetBinContent(ibin),' and error = ',totBkgHists[channel].GetBinError(ibin))
        for proc in bkgProcList:
                if proc == bkgProcList[0]: continue
                try:
                        if rebinX > 1:
                                totBkgHists[channel].Add(tfile.Get(hist.replace('__'+dataName,'__'+proc)).Rebin(rebinX))
                        else:
                                totBkgHists[channel].Add(tfile.Get(hist.replace('__'+dataName,'__'+proc)))
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
                Nbins = DataHists[chn].GetNbinsX() #-1 ## TEMPORARY REMOVE -1!
                xbinsListTemp[chn]=[DataHists[chn].GetXaxis().GetBinUpEdge(Nbins)] #[tfile.Get(datahists[0]).GetXaxis().GetBinUpEdge(tfile.Get(datahists[0]).GetXaxis().GetNbins()-1)]
                if doTruncated and 'jet' in chn:
                        xbinsListTemp[chn]=[800.0] # partialBlind D
                
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
                except:
                        pass
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
                                        
                                        if doTruncated and 'jet' in chn and totBkgHists[chn].GetXaxis().GetBinLowEdge(Nbins+1-iBin)>=800: pass
                                        else:
                                                xbinsListTemp[chn].append(totBkgHists[chn].GetXaxis().GetBinLowEdge(Nbins+1-iBin))

        ## Going right to left -- if the last entry isn't 0 add it
        if '_42' in folder or 'Jan2025' in folder:
                if xbinsListTemp[chn][-1]!=400: xbinsListTemp[chn].append(400)
        else:
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

### FIXME: not computed yet for Bprime...we will go for shape-only , very reasonable
#muSFsUp = {'TTM900':0.744,'TTM1000':0.744,'TTM1100':0.747,'TTM1200':0.742,'TTM1300':0.741,'TTM1400':0.738,'TTM1500':0.740,'TTM1600':0.735,'TTM1700':0.721,'TTM1800':0.746}
#muSFsDn = {'TTM900':1.312,'TTM1000':1.312,'TTM1100':1.306,'TTM1200':1.315,'TTM1300':1.316,'TTM1400':1.322,'TTM1500':1.319,'TTM1600':1.329,'TTM1700':1.354,'TTM1800':1.311}
#pdfSFsUp = {'TTM900':0.997,'TTM1000':0.997,'TTM1100':0.996,'TTM1200':0.995,'TTM1300':0.994,'TTM1400':0.991,'TTM1500':0.986,'TTM1600':0.984,'TTM1700':0.980,'TTM1800':0.966}
#pdfSFsDn = {'TTM900':1.005,'TTM1000':1.005,'TTM1100':1.007,'TTM1200':1.008,'TTM1300':1.011,'TTM1400':1.015,'TTM1500':1.022,'TTM1600':1.027,'TTM1700':1.031,'TTM1800':1.050}

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
                if doVRunc:
                        if 'templatesV_' in folder or 'templatesHST_' in folder:
                                outputRfiles[iRfile] = TFile(rfile.replace('.root','_rebinned'+str(rebinX)+'_stat'+str(stat).replace('.','p')+'_valUpDn.root'),'RECREATE')
                        elif 'templatesV2_' in folder:
                                outputRfiles[iRfile] = TFile(rfile.replace('.root','_rebinned'+str(rebinX)+'_stat'+str(stat).replace('.','p')+'_valUpDnFromV.root'),'RECREATE')
                                #outputRfiles[iRfile] = TFile(rfile.replace('.root','_rebinned'+str(rebinX)+'_stat'+str(stat).replace('.','p')+'_valUpDn.root'),'RECREATE')
                        elif 'templatesD_' in folder:
                                outputRfiles[iRfile] = TFile(rfile.replace('.root','_rebinned'+str(rebinX)+'_stat'+str(stat).replace('.','p')+'_valUpDnFromVWithD.root'),'RECREATE')
                                #outputRfiles[iRfile] = TFile(rfile.replace('.root','_rebinned'+str(rebinX)+'_stat'+str(stat).replace('.','p')+'_valUpDnWithD.root'),'RECREATE')
                else:
                        outputRfiles[iRfile] = TFile(rfile.replace('.root','_rebinned'+str(rebinX)+'_stat'+str(stat).replace('.','p')+'.root'),'RECREATE')
        else: 
                outputRfiles[iRfile] = TFile(rfile.replace('.root','_chi2_rebinned_stat'+str(stat).replace('.','p')+'.root'),'RECREATE')

        signame = rfile.split('/')[-1].split('_')[1]

        print("PROGRESS:")
        for chn in channels:
                print("         "+chn)
                rebinnedHists = {}
                #Rebinning histograms
                allhistschntemp = allhists[chn].copy() ## remove this when pNet has "Down" originally...
                for hist in allhistschntemp:      ## set back to allhists[chn]                  
                        if 'tagDn' in hist:     ## remove all this, just use the "else"
                                hist = hist.replace('tagDn','tagDown')
                                allhists[chn].remove(hist.replace('tagDown','tagDn'))
                                allhists[chn].append(hist)
                                rebinnedHists[hist] = tfiles[iRfile].Get(hist.replace('tagDown','tagDn')).Clone(hist).Rebin(len(xbins[chn])-1,hist,xbins[chn])
                                print('Hist is now',hist,', and histo name is',rebinnedHists[hist].GetName())
                        elif 'trainDn' in hist:     ## remove all this, just use the "else"
                                hist = hist.replace('trainDn','trainDown')
                                allhists[chn].remove(hist.replace('trainDown','trainDn'))
                                allhists[chn].append(hist)
                                rebinnedHists[hist] = tfiles[iRfile].Get(hist.replace('trainDown','trainDn')).Clone(hist).Rebin(len(xbins[chn])-1,hist,xbins[chn])
                                print('Hist is now',hist,', and histo name is',rebinnedHists[hist].GetName())
                        else:
                                rebinnedHists[hist] = tfiles[iRfile].Get(hist).Rebin(len(xbins[chn])-1,hist,xbins[chn])
                        rebinnedHists[hist].SetDirectory(0)
                        if '__'+sigName in hist:
                                rebinnedHists[hist].Scale(1.0/0.5) # already did lumi*1pb/Ngen, need lumi*1pb/(Ngen*BRsinglet)
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
                                # if 'untagTlep' in majorhist.GetName():
                                #         print('\t\t flipping untagTlep --> untagWlep')
                                #         majorhist.Scale(0.035287068/0.097960876)
                                # if 'untagWlep' in majorhist.GetName():
                                #         print('\t\t flipping untagTlep --> untagWlep')
                                #         majorhist.Scale(0.097960876/0.035287068)

                                majorhist.Write()
                                yieldsAll[majorhist.GetName()] = majorhist.Integral()
                                yieldsErrsAll[majorhist.GetName()] = 0.
                                for ibin in range(1,majorhist.GetXaxis().GetNbins()+1):
                                        yieldsErrsAll[majorhist.GetName()] += majorhist.GetBinError(ibin)**2
                                yieldsErrsAll[majorhist.GetName()] = math.sqrt(yieldsErrsAll[majorhist.GetName()])

                #Construct or apply the validation region uncertainty:
                if doVRunc:
                        if 'ABCDnn' in iPlot:
                                majorname = [k.GetName() for k in tfiles[iRfile].GetListOfKeys() if '__major' in k.GetName() and chn in k.GetName() and upTag not in k.GetName() and downTag not in k.GetName()][0]                                
                                datahist = rebinnedHists[majorname.replace('__major','__data_obs')]
                                majorhist = rebinnedHists[majorname]
                                totbkghist = majorhist.Clone(majorname.replace('__major','__totbkg'))
                                totbkghist.Add(rebinnedHists[majorname.replace('__major','__ewk')])
                                totbkghist.Add(rebinnedHists[majorname.replace('__major','__ttx')])
                                
                                ### CHANGE THIS BACK TO TEMPLATESV_ FOR THE TEST!!!
                                ### USE templatesV for the original method
                                if 'templatesV_' in folder or 'templatesHST' in folder:
                                        #totbkghist = majorhist.Clone(majorname.replace('__major','__totbkg'))
                                        #totbkghist.Add(rebinnedHists[majorname.replace('__major','__ewk')])
                                        #totbkghist.Add(rebinnedHists[majorname.replace('__major','__ttx')])
                                        ## For V we just need to find the difference and SBC an unc (1-sided by definition? symmetrized?)
                                        ## For D we need to know the percentage to apply to major... store as __VRpct
                                        ## Will construct this as an uncertainty on "major"
                                        VRuncUp = majorhist.Clone(majorname.replace('__major','__major__valUp')) # can add Down if desired...
                                        VRuncDown = majorhist.Clone(majorname.replace('__major','__major__valDown')) # can add Down if desired...
                                        VRpct = majorhist.Clone(majorname.replace('__major','__VRpct'))
                                        for ibin in range(1,datahist.GetNbinsX()+1):
                                                if totbkghist.GetBinError(ibin)/totbkghist.GetBinContent(ibin) < 0.1: # bkg stat unc < 10%
                                                        # datahist.GetBinContent(ibin) > 100:  # this is == bins w/ data stat uncert < 10%, seems fine
                                                        # set content of this shifted major to be the expected data - minor
                                                        datMinusMinor = majorhist.GetBinContent(ibin) + datahist.GetBinContent(ibin) - totbkghist.GetBinContent(ibin)
                                                else:
                                                        datMinusMinor = majorhist.GetBinContent(ibin)
                                                VRuncUp.SetBinContent(ibin,datMinusMinor)
                                                VRpct.SetBinContent(ibin,(datMinusMinor - majorhist.GetBinContent(ibin))/majorhist.GetBinContent(ibin))
                                                if doTwoSided:
                                                        VRuncDown.SetBinContent(ibin, majorhist.GetBinContent(ibin)*(1.0 - VRpct.GetBinContent(ibin)))
                                                # percentage should be (shift - nominal)/nominal
                                        VRuncUp.Write()
                                        VRuncDown.Write()
                                        VRpct.Write()
                                        yieldsAll[VRuncUp.GetName()] = VRuncUp.Integral()
                                        yieldsAll[VRuncDown.GetName()] = VRuncDown.Integral()

                                ### UNCOMMENT THIS FOR THE TEST!!!
                                ### COMMENT it for the original method, entire elif block
                                elif 'templatesV2_' in folder:
                                        ## Check if the matching V (or V2, choose!) file exists and open it, extract VRpct
                                        ## Make a VRuncUp and add the right amount
                                        Vfilename = rfile.replace('.root','_rebinned'+str(rebinX)+'_stat'+str(stat).replace('.','p')+'.root').replace('templatesV2','templatesV')
                                        if doTwoSided:
                                                Vfilename = Vfilename.replace('.root','_valUpDn.root')
                                        print('Opening Vfile = ',Vfilename)
                                        if os.path.exists(Vfilename):
                                                Vfile = TFile.Open(Vfilename)
                                        else:
                                                print('You asked for VR uncert on region V2, but the V file is missing!')
                                                exit()
                                        VRpct = Vfile.Get(majorname.replace('_V2','_V').replace('__major','__VRpct'))
                                        VRpct.SetDirectory(0)
                                        Vfile.Close()
                                        outputRfiles[iRfile].cd()
                                        VRuncUp = majorhist.Clone(majorname.replace('__major','__major__valUp'))
                                        VRuncDown = majorhist.Clone(majorname.replace('__major','__major__valDown'))
                                        for ibin in range(1,datahist.GetNbinsX()+1):
                                                Vpct = VRpct.GetBinContent(ibin)
                                                shiftpct = Vpct
                                                # want shift to contain major + major*pct
                                                VRuncUp.SetBinContent(ibin,majorhist.GetBinContent(ibin)*(1.0 + shiftpct))
                                                if doTwoSided:
                                                        VRuncDown.SetBinContent(ibin,majorhist.GetBinContent(ibin)*(1.0 - shiftpct))
                                        VRuncUp.Write()
                                        VRuncDown.Write()

                                        yieldsAll[VRuncUp.GetName()] = VRuncUp.Integral()
                                        yieldsAll[VRuncDown.GetName()] = VRuncDown.Integral()

                                ### CHANGE V2s BACK TO V FOR THE TEST!!!
                                elif 'templatesD' in folder:
                                        ## Check if the matching V (or V2, choose!) file exists and open it, extract VRpct
                                        ## Make a VRuncUp and add the right amount
                                        Vfilename = rfile.replace('.root','_rebinned'+str(rebinX)+'_stat'+str(stat).replace('.','p')+'.root').replace('templatesD','templatesV')
                                        if doTwoSided:
                                                Vfilename = Vfilename.replace('.root','_valUpDn.root')
                                        print('Opening Vfile = ',Vfilename)
                                        if os.path.exists(Vfilename):
                                                Vfile = TFile.Open(Vfilename)
                                        else:
                                                print('You asked for VR uncert on region D, but the V file is missing!')
                                                exit()
                                        VRpct = Vfile.Get(majorname.replace('_D','_V').replace('__major','__VRpct'))
                                        VRpct.SetDirectory(0)
                                        Vfile.Close()
                                        outputRfiles[iRfile].cd()
                                        VRuncUp = majorhist.Clone(majorname.replace('__major','__major__valUp'))
                                        VRuncDown = majorhist.Clone(majorname.replace('__major','__major__valDown'))
                                        for ibin in range(1,datahist.GetNbinsX()+1):
                                                if totbkghist.GetBinError(ibin)/totbkghist.GetBinContent(ibin) < 0.1 and datahist.GetXaxis().GetBinLowEdge(ibin) < 700:
                                                        datMinusMinor = majorhist.GetBinContent(ibin) + datahist.GetBinContent(ibin) - totbkghist.GetBinContent(ibin)
                                                else:
                                                        datMinusMinor = majorhist.GetBinContent(ibin)
                                                Dpct = (datMinusMinor - majorhist.GetBinContent(ibin))/majorhist.GetBinContent(ibin)                                                
                                                Vpct = VRpct.GetBinContent(ibin)
                                                shiftpct = Vpct
                                                if abs(Dpct) > abs(Vpct):
                                                        shiftpct = Dpct
                                                # want shift to contain major + major*pct
                                                VRuncUp.SetBinContent(ibin,majorhist.GetBinContent(ibin)*(1.0 + shiftpct))
                                                if doTwoSided:
                                                        VRuncDown.SetBinContent(ibin,majorhist.GetBinContent(ibin)*(1.0 - shiftpct))
                                        VRuncUp.Write()
                                        VRuncDown.Write()

                                        yieldsAll[VRuncUp.GetName()] = VRuncUp.Integral()
                                        yieldsAll[VRuncDown.GetName()] = VRuncDown.Integral()

                                        
                        else:
                                print('You need to implement the VR uncert for MC background, or set it to false!')
                                exit()
                                        
                #Constructing muRF shapes
                muRUphists = [k.GetName() for k in tfiles[iRfile].GetListOfKeys() if 'muR'+upTag in k.GetName() and chn in k.GetName()]
                for hist in muRUphists:
                        newMuRNameBase = 'muR'
                        if 'qcd__' in hist: newMuRName = newMuRNameBase+'QCD'
                        if 'ewk__' in hist: newMuRName = newMuRNameBase+'EWK'
                        if 'wjets__' in hist: newMuRName = newMuRNameBase+'WJT'
                        if 'ttbar__' in hist: newMuRName = newMuRNameBase+'TT'
                        if 'singletop__' in hist: newMuRName = newMuRNameBase+'ST'
                        if 'ttx__' in hist: newMuRName = newMuRNameBase+'TTX'
                        if '__'+sigName in hist: newMuRName = newMuRNameBase+'SIG'
                        newMuFName = newMuRName.replace('muR','muF')
                        
                        muRUpHist = rebinnedHists[hist].Clone(hist.replace('muR'+upTag,newMuRName+upTag))
                        muRDnHist = rebinnedHists[hist.replace('muR'+upTag,'muR'+downTag)].Clone(hist.replace('muR'+upTag,newMuRName+downTag))
                        muFUpHist = rebinnedHists[hist.replace('muR'+upTag,'muF'+upTag)].Clone(hist.replace('muR'+upTag,newMuFName+upTag))
                        muFDnHist = rebinnedHists[hist.replace('muR'+upTag,'muF'+downTag)].Clone(hist.replace('muR'+upTag,newMuFName+downTag))
                        renormNomHist = rebinnedHists[hist[:hist.find('__mu')]], #nominal
                        if renormNomHist.Integral() < 1e-6: 
                                print("muRF: Empty hist found, skipping: "+hist)
                                continue
                        if ('__'+sigName in hist and '__mu' in hist and normalizeRENORM): #normalize the renorm/fact shapes to nominal
                                signame = hist.split('__')[1]
                                if sigName not in signame: print("DIDNT GET SIGNAME "+signame)
                                #scalefactorUp = muSFsUp[signame]
                                #scalefactorDn = muSFsDn[signame]
                                #muRFcorrdNewUpHist.Scale(scalefactorUp) #drop down .7   ### FIXME, NEED THIS FOR BPRIME
                                #muRFcorrdNewDnHist.Scale(scalefactorDn) #raise up 1.3
                                muRUpHist.Scale(renormNomHist.Integral()/muRUpHist.Integral())
                                muRDnHist.Scale(renormNomHist.Integral()/muRDnHist.Integral())
                                muFUpHist.Scale(renormNomHist.Integral()/muFUpHist.Integral())
                                muFDnHist.Scale(renormNomHist.Integral()/muFDnHist.Integral())
                        # if ('__'+sigName not in hist and normalizeRENORM and not FullMu):
                        #         renormNomHist = histList[0]
                        #         muRFcorrdNewUpHist.Scale(renormNomHist.Integral()/muRFcorrdNewUpHist.Integral())
                        #         muRFcorrdNewDnHist.Scale(renormNomHist.Integral()/muRFcorrdNewDnHist.Integral())
                        muRUpHist.Write()
                        muRDnHist.Write()
                        muFUpHist.Write()
                        muFDnHist.Write()
 
                        yieldsAll[muRUpHist.GetName().replace('_sig','_'+rfile.split('_')[-2])] = muRUpHist.Integral()
                        yieldsAll[muRDnHist.GetName().replace('_sig','_'+rfile.split('_')[-2])] = muRDnHist.Integral()
                        yieldsAll[muFUpHist.GetName().replace('_sig','_'+rfile.split('_')[-2])] = muFUpHist.Integral()
                        yieldsAll[muFDnHist.GetName().replace('_sig','_'+rfile.split('_')[-2])] = muFDnHist.Integral()

                #Constructing PDF shapes -- FIXME LATER FOR BPRIME!
                pdfUphists = [k.GetName() for k in tfiles[iRfile].GetListOfKeys() if 'pdf0' in k.GetName() and chn in k.GetName()]
                newPDFName = 'pdfNew'
                for hist in pdfUphists:
                        pdfNomHist = rebinnedHists[hist.replace('__pdf0','')]
                        pdfNewUpHist = rebinnedHists[hist].Clone(hist.replace('pdf0',newPDFName+upTag))
                        pdfNewDnHist = rebinnedHists[hist].Clone(hist.replace('pdf0',newPDFName+downTag))

                        for ibin in range(1,pdfNewUpHist.GetNbinsX()+1):
                                weightList = [rebinnedHists[hist.replace('pdf0','pdf'+str(pdfInd))].GetBinContent(ibin) for pdfInd in range(101)]

                                errsq = 0
                                for weight in weightList:
                                        ## sum up squares of differences to the central value
                                        errsq += (weight - pdfNomHist.GetBinContent(ibin))**2

                                        
                                ## find the percentage of the shift w.r.t the central value
                                if pdfNomHist.GetBinContent(ibin) != 0: shiftpct = math.sqrt(errsq)/pdfNomHist.GetBinContent(ibin)
                                else:
                                        if errsq > 0.0001:
                                                print('Weird: central is 0 but not PDF unc has errsq',errsq,'in bin',ibin,'of hist',hist)
                                        shiftpct = 0
                
                                #if abs(shiftpct) > 1 and pdfNomHist.GetBinContent(ibin) > 0.008:
                                        #print('WARNING: pdf shift is',shiftpct,', flooring down at 0 in bin',ibin,'of hist',hist,'on bin content of',pdfNomHist.GetBinContent(ibin))
                                ## multiply the central value by 1 +/- the shift
                                pdfNewUpHist.SetBinContent(ibin, max(0,pdfNomHist.GetBinContent(ibin)*(1 + shiftpct)))
                                pdfNewDnHist.SetBinContent(ibin, max(0,pdfNomHist.GetBinContent(ibin)*(1 - shiftpct)))                                

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
                        pdfNewDnHist.Write()

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
taglist = ['tag']
factor = {'tagTjet':0.02,'tagWjet':0.02,'untagTlep':0.02,'untagWlep':0.08}
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
                                modTag = chn[chn.find('is'):].split('_')[1]
                                #print('modTag = ',modTag)
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
                                                if bkg != 'major':
                                                        yielderrtemp += (corrdSys*yieldsAll[histoPrefix+bkg])**2
                                                else:
                                                        yielderrtemp += (factor[modTag]*yieldsAll[histoPrefix+bkg])**2
                                        if proc=='dataOverBkg':
                                                dataTemp = yieldsAll[histoPrefix+dataName]+1e-20
                                                dataTempErr = yieldsErrsAll[histoPrefix+dataName]**2
                                                yielderrtemp = ((dataTemp/yieldtemp)**2)*(dataTempErr/dataTemp**2+yielderrtemp/yieldtemp**2)
                                                yieldtemp = dataTemp/yieldtemp
                                else:
                                        #try:
                                        yieldtemp += yieldsAll[histoPrefix+proc]
                                        yielderrtemp += yieldsErrsAll[histoPrefix+proc]**2
                                        yielderrtemp += (getShapeSystUnc(proc,chn)*yieldsAll[histoPrefix+proc])**2
                                        #except:
                                        #        if proc != 'qcd': print("Missing "+proc+" for channel individual: "+chn)
                                        #        pass
                                        if proc in sigProcList:
                                                signal=proc
                                                if 'left' in signal: signal=proc.replace('left','')+'left'
                                                if 'right' in signal: signal=proc.replace('right','')+'right'
                                                #yieldtemp*=xsec[signal]  ### FIXME using the new dicts if we want non-1pb
                                                #yielderrtemp*=xsec[signal]**2
                                        if proc != 'major':
                                                yielderrtemp += (corrdSys*yieldsAll[histoPrefix+proc])**2
                                        else:
                                                yielderrtemp += (factor[modTag]*yieldsAll[histoPrefix+proc])**2
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
                                        if 'Wtag' in syst and ('Tjet' in chn or 'untag' in chn): row.append(' & \\NA')
                                        elif 'Ttag' in syst and ('Wjet' in chn or 'untag' in chn): row.append(' & \\NA')
                                        elif proc != 'qcd': print("Missing "+proc+" for channel: "+chn+" and systematic: "+syst)
                                        pass
                        row.append('\\\\')
                        table.append(row)
        table.append(['break'])

postFix = ''
if 'templatesV_' in folder:
        postFix = '_valUpDn'
elif 'templatesV2_' in folder:
        postFix = '_valUpDnFromV'
        #postFix = '_valUpDn'
elif 'templatesD_' in folder:
        postFix = '_valUpDnFromVWithD'
        #postFix = '_valUpDnWithD'

out=open(templateDir+'/'+combinefile.replace('templates','yields').replace('.root','_rebinned'+str(rebinX)+'_stat'+str(stat).replace('.','p'))+postFix+'.txt','w')

printTable(table,out)

print("--- %s minutes ---" % (round((time.time() - start_time)/60,2)))



