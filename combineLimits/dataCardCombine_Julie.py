#!/usr/bin/env python

import os,sys,time,math,datetime,itertools
from ROOT import TFile,TH1F

if 'CMSSW_12_4_8' in os.environ['CMSSW_BASE']:
        print("Go CMSENV inside CMSSW_11_3_4!")
        exit(1)

parent = os.path.dirname(os.getcwd())
thisdir= os.path.dirname(os.getcwd()+'/')
sys.path.append(parent)
from utils import *
import CombineHarvester.CombineTools.ch as ch

#gROOT.SetBatch(1)

fileDir = '/uscms_data/d3/jmanagan/BtoTW/CMSSW_12_4_8/src/vlq-BtoTW-SLA/makeTemplates/'
template = 'templatesD_Oct2023Xiaohe'

tag = 'Apr2024' ##Tag and saveKey are used for output directory names
saveKey = '138fb'#tag+'_'+str(sys.argv[3])

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
	
        writer = ch.CardWriter('limits_'+template+saveKey+'/$TAG/$MASS/$ANALYSIS_$CHANNEL_$BINID_Combine.txt',
                               'limits_'+template+saveKey+'/$TAG/common/$ANALYSIS_$CHANNEL.input.root')
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
        #cb.cp().process(signal).channel(chns).AddSyst(cb, 'signalScale', 'rateParam', ch.SystMap()(35.9/138.0)) # scale down to 2016
        #cb.cp().process(allbkgs).channel(chns).AddSyst(cb, 'bkgScale', 'rateParam', ch.SystMap()(35.9/138.0)) # scale down to 2016
        #cb.GetParameter("signalScale").set_frozen(True)
        #cb.GetParameter("bkgScale").set_frozen(True)
        #print (cb.GetParameter("signalScale").frozen())
        #print (cb.GetParameter("bkgScale").frozen())
	
        if isABCDnn:
                cb.cp().process([allbkgs[0]]).channel(chns).AddSyst(cb, 'peak', 'shape', ch.SystMap()(1.0))
                cb.cp().process([allbkgs[0]]).channel(chns).AddSyst(cb, 'tail', 'shape', ch.SystMap()(1.0))
                cb.cp().process([allbkgs[0]]).channel(chns).AddSyst(cb, 'closure', 'shape', ch.SystMap()(1.0))
                cb.cp().process([allbkgs[0]]).channel(chns1).AddSyst(cb, 'abdcyield1', 'lnN', ch.SystMap()(1.079))
                cb.cp().process([allbkgs[0]]).channel(chns2).AddSyst(cb, 'abdcyield2', 'lnN', ch.SystMap()(1.062))
                cb.cp().process([allbkgs[0]]).channel(chns3).AddSyst(cb, 'abdcyield3', 'lnN', ch.SystMap()(1.081))
                cb.cp().process([allbkgs[0]]).channel(chns4).AddSyst(cb, 'abdcyield4', 'lnN', ch.SystMap()(1.018))

        allmcgrps = signal + allbkgs
        if isABCDnn:
                allmcgrps = signal + [allbkgs[1]] + [allbkgs[2]]

        ## https://twiki.cern.ch/twiki/bin/view/CMS/TWikiLUM#CurRec
        cb.cp().process(allmcgrps).channel(chns).AddSyst(cb, 'lumi', 'lnN', ch.SystMap()(1.018))

        ## FIXME -- need to implement year-to-year uncorrelations...
        cb.cp().process(allmcgrps).channel(chns).AddSyst(cb, 'jec', 'shape', ch.SystMap()(1.0))
        cb.cp().process(allmcgrps).channel(chns).AddSyst(cb, 'jer', 'shape', ch.SystMap()(1.0))
        cb.cp().process(allmcgrps).channel(chns).AddSyst(cb, 'elRecoSF', 'shape', ch.SystMap()(1.0))
        cb.cp().process(allmcgrps).channel(chns).AddSyst(cb, 'elIdSF', 'shape', ch.SystMap()(1.0))
        cb.cp().process(allmcgrps).channel(chns).AddSyst(cb, 'elIsoSF', 'shape', ch.SystMap()(1.0))
        cb.cp().process(allmcgrps).channel(chns).AddSyst(cb, 'muRecoSF', 'shape', ch.SystMap()(1.0))
        cb.cp().process(allmcgrps).channel(chns).AddSyst(cb, 'muIdSF', 'shape', ch.SystMap()(1.0))
        cb.cp().process(allmcgrps).channel(chns).AddSyst(cb, 'muIsoSF', 'shape', ch.SystMap()(1.0))
        cb.cp().process(allmcgrps).channel(chns).AddSyst(cb, 'TrigEffEl', 'shape', ch.SystMap()(1.0))
        cb.cp().process(allmcgrps).channel(chns).AddSyst(cb, 'TrigEffMu', 'shape', ch.SystMap()(1.0))
        cb.cp().process(allmcgrps).channel(chns).AddSyst(cb, 'btagHFCO', 'shape', ch.SystMap()(1.0))
        cb.cp().process(allmcgrps).channel(chns).AddSyst(cb, 'btagLFCO', 'shape', ch.SystMap()(1.0))
        cb.cp().process(allmcgrps).channel(chns).AddSyst(cb, 'btagHFUC', 'shape', ch.SystMap()(1.0)) ## FIXME FOR SURE!
        cb.cp().process(allmcgrps).channel(chns).AddSyst(cb, 'btagLFUC', 'shape', ch.SystMap()(1.0)) ## FIXME FOR SURE!

        ## Taking lepton SFs as uncorrelated, new calculations each year.
        # new el = 1.80 per year -- 3.1% combo . Mu w/o track = 2.5 per year -- 4.3 combo
	#cb.cp().process(allmcgrps).channel(chnsE).AddSyst(cb, 'elRecoIsoSys', 'lnN', ch.SystMap()(1.031))
	#cb.cp().process(allmcgrps).channel(chnsM).AddSyst(cb, 'muIdIsoSys', 'lnN', ch.SystMap()(1.043))

        #for year in ['2016','2017','2018']:

        #        cb.cp().process(signal + [allbkgs[0]] + [allbkgs[1]]).channel(chnsE).AddSyst(cb, 'elTrig'+year, 'shape', ch.SystMap()(1.0))
        #        cb.cp().process([allbkgs[2]]).channel(qcdchnsE['elTrig'+year]).AddSyst(cb, 'elTrig'+year, 'shape', ch.SystMap()(1.0))                
        #        cb.cp().process(signal + [allbkgs[0]] + [allbkgs[1]]).channel(chnsE).AddSyst(cb, 'elIdSF'+year, 'shape', ch.SystMap()(1.0))
        #        cb.cp().process([allbkgs[2]]).channel(qcdchnsE['elIdSF'+year]).AddSyst(cb, 'elIdSF'+year, 'shape', ch.SystMap()(1.0))
        #        cb.cp().process(signal + [allbkgs[0]] + [allbkgs[1]]).channel(chnsM).AddSyst(cb, 'muTrig'+year, 'shape', ch.SystMap()(1.0))
        #        cb.cp().process([allbkgs[2]]).channel(qcdchnsM['muTrig'+year]).AddSyst(cb, 'muTrig'+year, 'shape', ch.SystMap()(1.0))

        #        for syst in ['jec','jer','Wmis','Tmis']:
                        ## JEC/JER uncorrelated -- example of B2G-19-001. Jec uncorrelated is more conservative than the various 0/50/100 scenarios that require source splitting
                        ## DeepAK8 tags uncorrelated for mistags
        #                cb.cp().process(signal + [allbkgs[0]] + [allbkgs[1]]).channel(chns).AddSyst(cb, syst+year, 'shape', ch.SystMap()(1.0))
        #                cb.cp().process([allbkgs[2]]).channel(qcdchns[syst+year]).AddSyst(cb, syst+year, 'shape', ch.SystMap()(1.0))
                        
        ## Correlated in 2016 and 2017, doesn't exist in 2018 
        cb.cp().process(allmcgrps).channel(chns).AddSyst(cb, 'Prefire', 'shape', ch.SystMap()(1.0))

        ## Taking these as correlated since the training was unchanged
        #cb.cp().process(allmcgrps).channel(chns).AddSyst(cb, 'Teff', 'shape', ch.SystMap()(1.0)) 
        #cb.cp().process(allmcgrps).channel(chns).AddSyst(cb, 'Weff', 'shape', ch.SystMap()(1.0))

        ## PDF was separate in 16 from 17/18 -- FIXME, check in NanoAOD what was used....observe no more neg weights....
        #cb.cp().process(signal + [allbkgs[0]] + [allbkgs[1]]).channel(chns).AddSyst(cb, 'pdfNew2016', 'shape', ch.SystMap()(1.0))
        #cb.cp().process([allbkgs[2]]).channel(qcdchns['pdfNew2016']).AddSyst(cb, 'pdfNew2016', 'shape', ch.SystMap()(1.0))
        #cb.cp().process(signal + [allbkgs[0]] + [allbkgs[1]]).channel(chns).AddSyst(cb, 'pdfNew20172018', 'shape', ch.SystMap()(1.0))
        #cb.cp().process([allbkgs[2]]).channel(qcdchns['pdfNew20172018']).AddSyst(cb, 'pdfNew20172018', 'shape', ch.SystMap()(1.0))
        ## FIX ME: need nuisance edit rename TTM * pdfNew20172018 pdfSig20172018 at the bottom of the datacards...
        ## OR need to rename it properly when created and add a separate AddSyst here for pdfSig20172018

        ## Correlated: https://hypernews.cern.ch/HyperNews/CMS/get/b2g/1381.html
        cb.cp().process(allmcgrps).channel(chns).AddSyst(cb, 'Pileup', 'shape', ch.SystMap()(1.0)) 

        if not isABCDnn:
                ## HT weighting only on WJet background, same in all years
                cb.cp().process([allbkgs[1]]).channel(chns).AddSyst(cb, 'jsf', 'shape', ch.SystMap()(1.0))

                ## HTCorr on top background only, same in all years
                cb.cp().process([allbkgs[0]]).channel(chns).AddSyst(cb, 'toppt', 'shape', ch.SystMap()(1.0))

                ## DeepAK8 J-score shape correction, combining them for 2017 and 2018 (no 16, so sometimes qcd fails...)
                #cb.cp().process(signal + [allbkgs[0]] + [allbkgs[1]]).channel(chns).AddSyst(cb, 'dnnJ', 'shape', ch.SystMap()(1.0)) 
                #cb.cp().process([allbkgs[2]]).channel(qcdchns['dnnJ']).AddSyst(cb, 'dnnJ', 'shape', ch.SystMap()(1.0)) 

                ## Taking as correlated across years, but not processes -- no changes to this setting in MC
                cb.cp().process([allbkgs[0]]).channel(chns).AddSyst(cb, 'muRFcorrdNewTT', 'shape', ch.SystMap()(1.0))
                cb.cp().process([allbkgs[1]]).channel(chns).AddSyst(cb, 'muRFcorrdNewWJT', 'shape', ch.SystMap()(1.0))
                cb.cp().process([allbkgs[2]]).channel(chns).AddSyst(cb, 'muRFcorrdNewST', 'shape', ch.SystMap()(1.0))
                cb.cp().process([allbkgs[5]]).channel(chns).AddSyst(cb, 'muRFcorrdNewQCD', 'shape', ch.SystMap()(1.0))

        if isABCDnn:
                ttxgrp = [allbkgs[1]]
                ewkgrp = [allbkgs[2]]
        else:
                ttxgrp = [allbkgs[3]]
                ewkgrp = [allbkgs[4]]
        
        cb.cp().process(ttxgrp).channel(chns).AddSyst(cb, 'muRFcorrdNewTTX', 'shape', ch.SystMap()(1.0))
        cb.cp().process(ewkgrp).channel(chns).AddSyst(cb, 'muRFcorrdNewEWK', 'shape', ch.SystMap()(1.0))
        cb.cp().process(signal).channel(chns).AddSyst(cb, 'muRFcorrdNewSIG', 'shape', ch.SystMap()(1.0))



def add_autoMCstat(cb):
        print('------------------------------------------------------------------------')
        print('>> Adding autoMCstats...')
	
        thisDir = os.getcwd()
        mass=0
        massList = [800,1000,1200,1300,1400,1500,1600,1700,1800,2000,2200]

        for chn in chns+['cmb']:
                print('>>>> \t Adding autoMCstats for channel:',chn)
                for mass in massList:
                        chnDir = os.getcwd()+'/limits_'+template+saveKey+'/'+chn+'/'+str(mass)+'/'
                        print('chnDir: ',chnDir)
                        os.chdir(chnDir)
                        files = [x for x in os.listdir(chnDir) if '.txt' in x]
                        for ifile in files:
                                with open(chnDir+ifile, 'a') as chnfile: chnfile.write('* autoMCStats 1.')
                        os.chdir(thisDir)

def create_workspace(cb):
        print('------------------------------------------------------------------------')
        print('>> Creating workspace...')

        for chn in ['cmb']:
                print('>>>> \t Creating workspace for channel:',chn)
                chnDir = os.getcwd()+'/limits_'+template+saveKey+'/'+chn+'/*'
                cmd = 'combineTool.py -M T2W -i '+chnDir+' -o workspace.root --parallel 4 --channel-masks'
                os.system(cmd)


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

        if not os.path.exists('./limits_'+template+saveKey): os.system('mkdir -p ./limits_'+template+saveKey+'/')

        discrim = 'BpMass_ABCDnn'
        isABCDnn = False
        if 'ABCDnn' in discrim:
                isABCDnn = True

        rfile = fileDir+template+'/templates_'+discrim+'_138fbfb_rebinned_stat0p2.root'
        os.system('cp '+rfile+' ./limits_'+template+saveKey+'/')

        print('File: ',rfile)
        allbkgs = ['ttbar','wjets','singletop','ttx','ewk','qcd']
        if isABCDnn:
                allbkgs = ['major','ttx','ewk']

        dataName = 'data_obs'
        tfile = TFile(rfile)
        allHistNames = [k.GetName() for k in tfile.GetListOfKeys() if not 'allTlep' in k.GetName() and not 'allWlep' in k.GetName() and not (k.GetName().endswith('Up') or k.GetName().endswith('Down'))]
        upSystNames = [k.GetName() for k in tfile.GetListOfKeys() if (k.GetName().endswith('Up') and not 'allTlep' in k.GetName() and not 'allWlep' in k.GetName())]
        #qcdsysts = [(k.GetName().split('__')[-1]).replace('Up','') for k in tfile.GetListOfKeys() if '__ttbar__' in k.GetName() and k.GetName().endswith('Up') and '_untagWlep_' in k.GetName()]
        tfile.Close()

        chns = [hist[hist.find('fb_')+3:hist.find('__')] for hist in allHistNames if '__'+dataName in hist and 'all' not in hist]

        chns1 = [chn for chn in chns if '_tagTjet_' in chn]
        chns2 = [chn for chn in chns if '_tagWjet_' in chn]
        chns3 = [chn for chn in chns if '_untagTlep_' in chn]
        chns4 = [chn for chn in chns if '_untagWlep_' in chn]
        bkg_procs = {chn:[hist.split('__')[-1] for hist in allHistNames if '_'+chn+'_' in hist and not (hist.endswith('Up') or hist.endswith('Down') or hist.endswith(dataName) or '_BpM' in hist)] for chn in chns}

        #systchannels = {chn:[(hist.split('__')[-1]).replace('Up','') for hist in upSystNames if '__qcd__' in hist and '_'+chn+'_' in hist] for chn in chns}
        #qcdchns = {syst:[chn for chn in chns if syst in systchannels[chn]] for syst in qcdsysts}
        #qcdchnsE = {syst:[chn for chn in chns if 'isE' in chn and syst in systchannels[chn]] for syst in qcdsysts}
        #qcdchnsM = {syst:[chn for chn in chns if 'isM' in chn and syst in systchannels[chn]] for syst in qcdsysts}

        print('bkg_procs: ',bkg_procs)
        # for cat in sorted(bkg_procs.keys()):
        #         print(cat,bkg_procs[cat])
        #         if 'qcd' in bkg_procs[cat]:
        #                 print('		Removing qcd ...')
        #                 bkg_procs[cat]=bkg_procs[cat][:-1]

        sig_procs = ['BpM']

        cats = {}
        for chn in chns: cats[chn] = [(0, '')]

        masses = ch.ValsFromRange('800:2200|200')	
        masses.push_back("1300") # these worked in newer combine
        masses.push_back("1500")
        masses.push_back("1700")
        
        print('Found this mass list: ',masses)

        go(cb)
