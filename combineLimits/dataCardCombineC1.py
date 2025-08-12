#!/usr/bin/env python
#python3 dataCardCombine.py BtargetHoleCorrBTrainTrainCorrUCS1
import os,sys,time,math,datetime,itertools
from ROOT import TFile,TH1F

if 'CMSSW_13_0_18' in os.environ['CMSSW_BASE']:
        print("Go CMSENV inside CMSSW_14_1_0!")
        exit(1)

parent = os.path.dirname(os.getcwd())
thisdir= os.path.dirname(os.getcwd()+'/')
sys.path.append(parent)
from utils import *
import CombineHarvester.CombineTools.ch as ch

#gROOT.SetBatch(1)

#V2, DV2 for ABCDnn
#V2 or ABCV2V2, for MC CRs, DV2, ABCDCV2V2 for MC SRs
region = 'D' #TEMP: change region here
fileDir = '/uscms_data/d3/xshen/alma9/CMSSW_13_3_3/src/vlq-BtoTW-SLA/makeTemplates/'
dirPostFix = 'BtargetHoleCorrBTrain_smooth_rebin' #sys.argv[1]
template = 'templates'+region+'_Jan2025_210bins'+dirPostFix
#postfix = 'rebinned1_stat0p2_smoothed_TVJJ'#_UC'
postfix = 'smoothedJJ_rebinned1_stat0p2_smoothedTV'
saveKey = 'ABCDnn_'+region 
dateKey = '_Jan2025'
outputdir = 'limits_templates'+saveKey+dateKey+'_RB1_2Dcorr'+dirPostFix+'C1'#+'_largeRateUncert' #.replace('UC4','NoUC')  ## Edit last string for unique identifier. IF CHANGING BINNING, GO CHANGE FILE NAME BELOW!
discrim = 'BpMass_ABCDnn'

if '2016' in template:
        outputdir+='2016'
        yearList = []
else:
        yearList = ['2016APV', '2016', '2017', '2018']

if 'ABCDnn' in saveKey:
        regionlist = [region]
        if region == 'DV2':
                regionlist = ['V2','D']
        elif region == 'DV':
                regionlist = ['V','D']
                
if 'MC' in saveKey:
        regionlist = ['V2']
        if region == 'ABCV2V2':
                regionlist = ['A','B','CV2','V2']
        elif region == 'ABCDCV2V2':
                regionlist = ['A','B','C','D','CV2','V2']
        elif region == 'DV2':
                regionlist = ['D','V2']
        discrim = 'BpMass'

print('SETUP:')
print('region = ',region)
print('discrim = ',discrim)
print('templatedir = ',template)
print('output = ',outputdir)

        
massList = [800,1000,1200,1300,1400,1500,1600,1700,1800,2000]
if region == 'V2':
        massList = [1200,1300]

def add_processes_and_observations(cb, prefix='Bp'):
        print('------------------------------------------------------------------------')
        print('>> Creating processes and observations...prefix:',prefix)
        for chn in chns:
                print('>>>> \t Creating proc/obs for channel:',chn)
                cats_chn = cats[chn]
                cb.AddObservations(  ['*'],  [prefix], [era], [chn],                 cats_chn      )
                cb.AddProcesses(     ['*'],  [prefix], [era], [chn], bkg_procs[chn], cats_chn, False  )
                cb.AddProcesses(     masses, [prefix], [era], [chn], sig_procs,      cats_chn, True   )


def add_shapes(cb, prefix='Bp'):
        print('------------------------------------------------------------------------')
        print('>> Extracting histograms from input root files...prefix:',prefix)
        for chn in chns:
                print('>>>> \t Extracting histos for channel:',chn)

                ## Keeping the CR lines just in case...
		#CRbkg_pattern = CRdiscrim+'_'+lumiStr+'_%s$BIN__$PROCESS' % chn
		#CRsig_pattern = CRdiscrim+'_'+lumiStr+'_%s$BIN__$PROCESS$MASS' % chn

                SRbkg_pattern = discrim+'_'+lumiStr+'_%s$BIN__$PROCESS' % chn
                SRsig_pattern = discrim+'_'+lumiStr+'_%s$BIN__$PROCESS$MASS' % chn
                        

		#if 'isCR' in chn: 
		#	cb.cp().channel([chn]).era([era]).backgrounds().ExtractShapes(rfile, CRbkg_pattern, CRbkg_pattern + '__$SYSTEMATIC')
		#	cb.cp().channel([chn]).era([era]).signals().ExtractShapes(rfile, CRsig_pattern, CRsig_pattern + '__$SYSTEMATIC')
                #else:
                cb.cp().channel([chn]).era([era]).backgrounds().ExtractShapes(rfile, SRbkg_pattern, SRbkg_pattern + '__$SYSTEMATIC')
                cb.cp().channel([chn]).era([era]).signals().ExtractShapes(rfile, SRsig_pattern, SRsig_pattern + '__$SYSTEMATIC')
		        

def rename_and_write(cb):
        print('------------------------------------------------------------------------')
        print('>> Setting standardised bin names...')
        ch.SetStandardBinNames(cb)
	
        writer = ch.CardWriter(outputdir+'/$TAG/$MASS/$ANALYSIS_$CHANNEL_$BINID_Combine.txt',
                               outputdir+'/$TAG/common/$ANALYSIS_$CHANNEL.input.root')
        writer.SetVerbosity(1)
        writer.WriteCards('cmb', cb)
        for chn in chns:
                print('>>>> \t WriteCards for channel:',chn)
                writer.WriteCards(chn, cb.cp().channel([chn]))
        print('>> Done writing cards!')


def print_cb(cb):
	for s in ['Obs', 'Procs', 'Systs', 'Params']:
		print('* %s *' % s)
		getattr(cb, 'Print%s' % s)()
		print()


def add_systematics(cb):
        print('------------------------------------------------------------------------')
        print('>> Adding systematic uncertainties...')
        print('>> Using ABCDnn? '+str(isABCDnn))

        signal = cb.cp().signals().process_set()
        
	#### Use these rateParams to make a comparison to 2016-only
        #cb.cp().process(signal).channel(chns).AddSyst(cb, 'signalScale', 'rateParam', ch.SystMap()(1.0)) ##35.9/138.0)) # scale down to 2016
        cb.cp().process(signal).channel(chns).AddSyst(cb, 'signalScale', 'rateParam', ch.SystMap()(0.01)) # scale to 0.01 for SR fit
        cb.GetParameter("signalScale").set_frozen(True)
        print (cb.GetParameter("signalScale").frozen())

        #cb.cp().process(signal+allbkgs).channel(chns).AddSyst(cb, 'scale36fb', 'rateParam', ch.SystMap()(35.9/138.0)) # scale down to 2016
        #cb.GetParameter("scale36fb").set_frozen(True)
        #print (cb.GetParameter("scale36fb").frozen())
	
        if isABCDnn:
                # cb.cp().process([allbkgs[0]]).channel(chns).AddSyst(cb, 'param0', 'shape', ch.SystMap()(1.0))
                # cb.cp().process([allbkgs[0]]).channel(chns).AddSyst(cb, 'param1', 'shape', ch.SystMap()(1.0))
                # cb.cp().process([allbkgs[0]]).channel(chns).AddSyst(cb, 'param2', 'shape', ch.SystMap()(1.0))
                # cb.cp().process([allbkgs[0]]).channel(chns).AddSyst(cb, 'param3', 'shape', ch.SystMap()(1.0))
                # cb.cp().process([allbkgs[0]]).channel(chns).AddSyst(cb, 'param4', 'shape', ch.SystMap()(1.0))
                # cb.cp().process([allbkgs[0]]).channel(chns).AddSyst(cb, 'param5', 'shape', ch.SystMap()(1.0))
                # cb.cp().process([allbkgs[0]]).channel(chns).AddSyst(cb, 'param6', 'shape', ch.SystMap()(1.0))
                # cb.cp().process([allbkgs[0]]).channel(chns).AddSyst(cb, 'param7', 'shape', ch.SystMap()(1.0))
                # cb.cp().process([allbkgs[0]]).channel(chns).AddSyst(cb, 'lastbin', 'shape', ch.SystMap()(1.0))
                cb.cp().process([allbkgs[0]]).channel(chns).AddSyst(cb, 'train', 'shape', ch.SystMap()(1.0))
                cb.cp().process([allbkgs[0]]).channel(chns).AddSyst(cb, 'correct', 'shape', ch.SystMap()(1.0))

                # cb.cp().process([allbkgs[0]]).channel(chns).AddSyst(cb, 'trainMassRange1', 'shape', ch.SystMap()(1.0))
                # cb.cp().process([allbkgs[0]]).channel(chns1).AddSyst(cb, 'trainMassRange2', 'shape', ch.SystMap()(1.0))
                # cb.cp().process([allbkgs[0]]).channel(chns2).AddSyst(cb, 'trainMassRange2', 'shape', ch.SystMap()(1.0))
                # cb.cp().process([allbkgs[0]]).channel(chns3).AddSyst(cb, 'trainMassRange2', 'shape', ch.SystMap()(1.0))
                # cb.cp().process([allbkgs[0]]).channel(chns3).AddSyst(cb, 'trainMassRange3', 'shape', ch.SystMap()(1.0))
                # #cb.cp().process([allbkgs[0]]).channel(chns4).AddSyst(cb, 'trainMassRange3', 'shape', ch.SystMap()(1.0))
                # #cb.cp().process([allbkgs[0]]).channel(chns4).AddSyst(cb, 'trainMassRange2', 'shape', ch.SystMap()(1.0))
                
                # cb.cp().process([allbkgs[0]]).channel(chns).AddSyst(cb, 'correctMassRange1', 'shape', ch.SystMap()(1.0))
                
                # cb.cp().process([allbkgs[0]]).channel(chns1).AddSyst(cb, 'correctMassRange2', 'shape', ch.SystMap()(1.0))
                # cb.cp().process([allbkgs[0]]).channel(chns1).AddSyst(cb, 'correctMassRange3', 'shape', ch.SystMap()(1.0))
                
                # cb.cp().process([allbkgs[0]]).channel(chns2).AddSyst(cb, 'correctMassRange2', 'shape', ch.SystMap()(1.0))
                # cb.cp().process([allbkgs[0]]).channel(chns2).AddSyst(cb, 'correctMassRange3', 'shape', ch.SystMap()(1.0))
                
                # cb.cp().process([allbkgs[0]]).channel(chns3).AddSyst(cb, 'correctMassRange2', 'shape', ch.SystMap()(1.0))
                # cb.cp().process([allbkgs[0]]).channel(chns3).AddSyst(cb, 'correctMassRange3', 'shape', ch.SystMap()(1.0))
                # cb.cp().process([allbkgs[0]]).channel(chns3).AddSyst(cb, 'correctMassRange4', 'shape', ch.SystMap()(1.0))
                
                # cb.cp().process([allbkgs[0]]).channel(chns4).AddSyst(cb, 'correctMassRange2', 'shape', ch.SystMap()(1.0))
                # cb.cp().process([allbkgs[0]]).channel(chns4).AddSyst(cb, 'correctMassRange3', 'shape', ch.SystMap()(1.0))
                
                cb.cp().process([allbkgs[0]]).channel(chns1).AddSyst(cb, 'abcdRateC1', 'lnN', ch.SystMap()(1.02)) #1.02 #1.15

                # large rate uncerts
                #cb.cp().process([allbkgs[0]]).channel(chns1).AddSyst(cb, 'abcdRateC1', 'lnN', ch.SystMap()(1.15))
                #cb.cp().process([allbkgs[0]]).channel(chns2).AddSyst(cb, 'abcdRateC2', 'lnN', ch.SystMap()(1.05))
                #cb.cp().process([allbkgs[0]]).channel(chns3).AddSyst(cb, 'abcdRateC3', 'lnN', ch.SystMap()(1.15))
                #cb.cp().process([allbkgs[0]]).channel(chns4).AddSyst(cb, 'abcdRateC4', 'lnN', ch.SystMap()(1.10))

        allmcgrps = signal + allbkgs
        if isABCDnn:
                allmcgrps = signal + [allbkgs[1]] + [allbkgs[2]]

        cb.cp().process(allmcgrps).channel(chns).AddSyst(cb, 'lumi', 'lnN', ch.SystMap()(1.018))
        cb.cp().process(allmcgrps).channel(chns).AddSyst(cb, 'elRecoSF', 'shape', ch.SystMap()(1.0))
        cb.cp().process(allmcgrps).channel(chns).AddSyst(cb, 'elIdSF', 'shape', ch.SystMap()(1.0))
        cb.cp().process(allmcgrps).channel(chns).AddSyst(cb, 'elIsoSF', 'shape', ch.SystMap()(1.0))
        cb.cp().process(allmcgrps).channel(chns).AddSyst(cb, 'muRecoSF', 'shape', ch.SystMap()(1.0))
        cb.cp().process(allmcgrps).channel(chns).AddSyst(cb, 'muIdSF', 'shape', ch.SystMap()(1.0))
        cb.cp().process(allmcgrps).channel(chns).AddSyst(cb, 'muIsoSF', 'shape', ch.SystMap()(1.0))
        cb.cp().process(allmcgrps).channel(chns).AddSyst(cb, 'btagHFCO', 'shape', ch.SystMap()(1.0))
        cb.cp().process(allmcgrps).channel(chns).AddSyst(cb, 'btagLFCO', 'shape', ch.SystMap()(1.0))
        cb.cp().process(allmcgrps).channel(chns).AddSyst(cb, 'Prefire', 'shape', ch.SystMap()(1.0))
        cb.cp().process(allmcgrps).channel(chns).AddSyst(cb, 'Pileup', 'shape', ch.SystMap()(1.0))
        cb.cp().process(allmcgrps).channel(chns).AddSyst(cb, 'PuJetSF', 'shape', ch.SystMap()(1.0)) 
        cb.cp().process(allmcgrps).channel(chns).AddSyst(cb, 'pdfNew', 'shape', ch.SystMap()(1.0))

        cb.cp().process(allmcgrps+[allbkgs[0]]).channel(chns1).AddSyst(cb, 'pNetTtag', 'shape', ch.SystMap()(1.0))
        cb.cp().process(allmcgrps+[allbkgs[0]]).channel(chns2).AddSyst(cb, 'pNetWtag', 'shape', ch.SystMap()(1.0))

        for syst in ['jec','jer','TrigEffEl','TrigEffMu','btagHFUC','btagLFUC']: #
                for year in yearList:
                        cb.cp().process(allmcgrps).channel(chns).AddSyst(cb, syst+year, 'shape', ch.SystMap()(1.0))
                        
        if not isABCDnn:
                ## HT weighting only on WJet background, same in all years
                cb.cp().process([allbkgs[1]]).channel(chns).AddSyst(cb, 'jsf', 'shape', ch.SystMap()(1.0))

                ## HTCorr on top background only, same in all years
                cb.cp().process([allbkgs[0]]).channel(chns).AddSyst(cb, 'toppt', 'shape', ch.SystMap()(1.0))

                ## Taking as correlated across years, but not processes -- no changes to this setting in MC
                cb.cp().process([allbkgs[0]]).channel(chns).AddSyst(cb, 'muRFcorrdNewTT', 'shape', ch.SystMap()(1.0))
                cb.cp().process([allbkgs[1]]).channel(chns).AddSyst(cb, 'muRFcorrdNewWJT', 'shape', ch.SystMap()(1.0))
                cb.cp().process([allbkgs[2]]).channel(chns).AddSyst(cb, 'muRFcorrdNewST', 'lnN', ch.SystMap()(1.05)) #'shape', ch.SystMap()(1.0))
                cb.cp().process([allbkgs[5]]).channel(chns).AddSyst(cb, 'muRFcorrdNewQCD', 'lnN', ch.SystMap()(1.05)) #'shape', ch.SystMap()(1.0))

        if isABCDnn:
                ttxgrp = [allbkgs[1]]
                ewkgrp = [allbkgs[2]]
        else:
                ttxgrp = [allbkgs[3]]
                ewkgrp = [allbkgs[4]]
        
        cb.cp().process(ttxgrp).channel(chns).AddSyst(cb, 'muRFcorrdNewTTX', 'lnN', ch.SystMap()(1.05)) #'shape', ch.SystMap()(1.0))
        cb.cp().process(ewkgrp).channel(chns).AddSyst(cb, 'muRFcorrdNewEWK', 'lnN', ch.SystMap()(1.05)) #'shape', ch.SystMap()(1.0))
        cb.cp().process(signal).channel(chns).AddSyst(cb, 'muRFcorrdNewSIG', 'shape', ch.SystMap()(1.0))



def add_autoMCstat(cb):
        print('------------------------------------------------------------------------')
        print('>> Adding autoMCstats...')
	
        thisDir = os.getcwd()        
        xsec = {'800':0.1187124, '900':0.0640113, '1000':0.0362987, '1100':0.0215009, '1200':0.0131348, '1300':0.0082629, '1400':0.0053213, '1500':0.0035078, '1600':0.0022829, '1700':0.0014947, '1800':0.0009898, '1900':0.0006519, '2000':0.0004499}

        for chn in ['cmb']:
                print('>>>> \t Adding autoMCstats for channel:',chn)
                for mass in massList:
                        chnDir = os.getcwd()+'/'+outputdir+'/'+chn+'/'+str(mass)+'/'
                        print('chnDir: ',chnDir)
                        os.chdir(chnDir)
                        files = [x for x in os.listdir(chnDir) if '.txt' in x]
                        for ifile in files:
                                with open(chnDir+ifile, 'a') as chnfile:
                                        chnfile.write('* autoMCStats 1.\n')
                                        ## IN CASE SIGNALS GET SCALED TO THEIR CROSS SECTION IN THE FILES
                                        #chnfile.write('noXsec     rateParam  *          BpM        '+str(round(1.0/xsec[str(mass)],5))+'\n')
                                        #chnfile.write('nuisance edit freeze noXsec')

                        os.chdir(thisDir)

                        
def create_workspace(cb):
        print('------------------------------------------------------------------------')
        print('>> Creating workspace...')

        thisDir = os.getcwd()
        for chn in ['cmb']:
                print('>>>> \t Creating workspace for channel:',chn)
                for mass in massList:
                        chnDir = os.getcwd()+'/'+outputdir+'/'+chn+'/'+str(mass)+'/'
                        os.chdir(chnDir)
                        cmd = 'combineCards.py '
                        for reg in regionlist:
                                cmd += 'Case1_'+reg+'=Bp_isL_tagTjet_'+reg+'_0_Combine.txt '
                        cmd += '&> combined.txt.cmb'
                        print('Running: ',cmd)
                        os.system(cmd)

                        if 'MC' in saveKey:
                                with open('combined.txt.cmb', 'a') as chnfile:
                                        chnfile.write('nuisance edit rename ttbar * toppt Toppt \n')
                                        chnfile.write('nuisance edit rename ewk * muRFcorrdNewEWK muRFewk\n')
                                        chnfile.write('nuisance edit rename ttx * muRFcorrdNewTTX muRFttx\n')
                                        chnfile.write('nuisance edit rename BpM * muRFcorrdNewSIG muRFsig\n')
                                        chnfile.write('nuisance edit rename ttbar * muRFcorrdNewTT muRFtt\n')
                                        chnfile.write('nuisance edit rename singletop * muRFcorrdNewST muRFtt\n')
                                        chnfile.write('nuisance edit rename wjets * muRFcorrdNewWJT muRFwjt\n')
                                        chnfile.write('nuisance edit rename qcd * muRFcorrdNewQCD muRFqcd\n')                                                
                                     
                        if 'ABCDnn' in saveKey:
                                with open('combined.txt.cmb', 'a') as chnfile:
                                        for reg in regionlist:
                                                chnfile.write('nuisance edit rename major Case1_'+reg+' train abcdTrainC1\n')
                                                chnfile.write('nuisance edit rename major Case1_'+reg+' correct abcdCorrC1\n')
                                                
                                                
                                        chnfile.write('nuisance edit rename ewk * muRFcorrdNewEWK muRFewk\n')
                                        chnfile.write('nuisance edit rename ttx * muRFcorrdNewTTX muRFttx\n')
                                        chnfile.write('nuisance edit rename BpM * muRFcorrdNewSIG muRFsig\n')
                                        chnfile.write('nuisance edit rename (ttx|ewk|BpM) * TrigEffEl2016APV TrigEl16APV\n')
                                        chnfile.write('nuisance edit rename (ttx|ewk|BpM) * TrigEffEl2016 TrigEl16\n')
                                        chnfile.write('nuisance edit rename (ttx|ewk|BpM) * TrigEffEl2017 TrigEl17\n')
                                        chnfile.write('nuisance edit rename (ttx|ewk|BpM) * TrigEffEl2018 TrigEl18\n')
                                        chnfile.write('nuisance edit rename (ttx|ewk|BpM) * TrigEffMu2016APV TrigMu16APV\n')
                                        chnfile.write('nuisance edit rename (ttx|ewk|BpM) * TrigEffMu2016 TrigMu16\n')
                                        chnfile.write('nuisance edit rename (ttx|ewk|BpM) * TrigEffMu2017 TrigMu17\n')
                                        chnfile.write('nuisance edit rename (ttx|ewk|BpM) * TrigEffMu2018 TrigMu18\n')
                                        chnfile.write('nuisance edit rename (ttx|ewk|BpM) * jec2016APV jec16APV\n')
                                        chnfile.write('nuisance edit rename (ttx|ewk|BpM) * jec2016 jec16\n')
                                        chnfile.write('nuisance edit rename (ttx|ewk|BpM) * jec2017 jec17\n')
                                        chnfile.write('nuisance edit rename (ttx|ewk|BpM) * jec2018 jec18\n')
                                        chnfile.write('nuisance edit rename (ttx|ewk|BpM) * jer2016APV jer16APV\n')
                                        chnfile.write('nuisance edit rename (ttx|ewk|BpM) * jer2016 jer16\n')
                                        chnfile.write('nuisance edit rename (ttx|ewk|BpM) * jer2017 jer17\n')
                                        chnfile.write('nuisance edit rename (ttx|ewk|BpM) * jer2018 jer18\n')
                                        chnfile.write('nuisance edit rename (ttx|ewk|BpM) * btagHFUC2016APV bHFUC16APV\n')
                                        chnfile.write('nuisance edit rename (ttx|ewk|BpM) * btagHFUC2016 bHFUC16\n')
                                        chnfile.write('nuisance edit rename (ttx|ewk|BpM) * btagHFUC2017 bHFUC17\n')
                                        chnfile.write('nuisance edit rename (ttx|ewk|BpM) * btagHFUC2018 bHFUC18\n')
                                        chnfile.write('nuisance edit rename (ttx|ewk|BpM) * btagLFUC2016APV bLFUC16APV\n')
                                        chnfile.write('nuisance edit rename (ttx|ewk|BpM) * btagLFUC2016 bLFUC16\n')
                                        chnfile.write('nuisance edit rename (ttx|ewk|BpM) * btagLFUC2017 bLFUC17\n')
                                        chnfile.write('nuisance edit rename (ttx|ewk|BpM) * btagLFUC2018 bLFUC18\n')
                                        chnfile.write('nuisance edit rename (ttx|ewk|BpM) * btagHFCO bHFCO\n')
                                        chnfile.write('nuisance edit rename (ttx|ewk|BpM) * btagLFCO bLFCO\n')
                
                        cmd = 'text2workspace.py -o workspace.root --channel-masks -m '+str(mass)+' combined.txt.cmb'
                        print('Running: ',cmd)
                        os.system(cmd)
                        os.chdir(thisDir)

                #cmd = 'combineTool.py -M T2W -i '+chnDir+' -o workspace.root --parallel 4 --channel-masks'
                #os.system(cmd)


def go(cb):
	add_processes_and_observations(cb)
	add_systematics(cb)
	add_shapes(cb)
	rename_and_write(cb)
	add_autoMCstat(cb)
	create_workspace(cb)


if __name__ == '__main__':
        cb = ch.CombineHarvester()
        era = 'Run2'
        lumiStrDir = '138'
        lumiStr = lumiStrDir+'fbfb'

        if not os.path.exists('./'+outputdir): os.system('mkdir -p ./'+outputdir+'/')

        isABCDnn = False
        if 'ABCDnn' in discrim:
                isABCDnn = True

        ### CHANGE THE rebinnedX HERE IF YOU CHANGE X
        rfile = fileDir+template+'/templates_'+discrim+'_138fbfb_'+postfix+'.root'
        if 'D' not in region:
                rfile = rfile.replace('WithD','')
        if 'TW100' in outputdir:
                rfile = fileDir+template+'/templates_'+discrim+'_138fbfb_rebinned_TW100_stat0p2.root'
        os.system('cp '+rfile+' ./'+outputdir+'/')

        print('File: ',rfile)
        allbkgs = ['ttbar','wjets','singletop','ttx','ewk','qcd']
        if isABCDnn:
                allbkgs = ['major','ttx','ewk']

        print('Allbkgs = ',allbkgs)

        dataName = 'data_obs'
        tfile = TFile(rfile)
        allHistNames = [k.GetName() for k in tfile.GetListOfKeys() if not 'allTlep' in k.GetName() and not 'allWlep' in k.GetName() and not (k.GetName().endswith('Up') or k.GetName().endswith('Down'))]
        upSystNames = [k.GetName() for k in tfile.GetListOfKeys() if (k.GetName().endswith('Up') and not 'allTlep' in k.GetName() and not 'allWlep' in k.GetName())]
        qcdsysts = [(k.GetName().split('__')[-1]).replace('Up','') for k in tfile.GetListOfKeys() if '__ttbar__' in k.GetName() and k.GetName().endswith('Up') and '_untagWlep_' in k.GetName()]
        tfile.Close()

        chns = [hist[hist.find('fb_')+3:hist.find('__')] for hist in allHistNames if '__'+dataName in hist and 'all' not in hist and 'tagTjet' in hist]

        chns1 = [chn for chn in chns if '_tagTjet_' in chn]
        chns2 = [chn for chn in chns if '_tagWjet_' in chn]
        chns3 = [chn for chn in chns if '_untagTlep_' in chn]
        chns4 = [chn for chn in chns if '_untagWlep_' in chn]
        
        bkg_procs = {chn:[hist.split('__')[-1] for hist in allHistNames if '_'+chn+'_' in hist and not (hist.endswith('Up') or hist.endswith('Down') or hist.endswith(dataName) or '_BpM' in hist or 'VRpct' in hist)] for chn in chns}

        systchannels = {chn:[(hist.split('__')[-1]).replace('Up','') for hist in upSystNames if '__qcd__' in hist and '_'+chn+'_' in hist] for chn in chns}

        print('bkg_procs: ',bkg_procs)

        sig_procs = ['BpM']

        cats = {}
        for chn in chns: cats[chn] = [(0, '')]

        masses = ch.ValsFromRange('800:2000|200')
        masses.push_back("1300")
        masses.push_back("1500")
        masses.push_back("1700")
        if region == 'V2':
                #masses = ch.ValsFromRange('1200:1300|200') # original setting
                masses = ch.ValsFromRange('1200:1400|100')# added for testing the 1300 kink
        
        print('Found this mass list: ',masses)

        go(cb)
