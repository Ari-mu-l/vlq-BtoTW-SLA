#!/usr/bin/env python

import os,sys,time,math,datetime,itertools
from ROOT import gROOT,TFile,TH1F,TH1D

if 'CMSSW_12_4_8' in os.environ['CMSSW_BASE']:
        print "Go CMSENV inside CMSSW_10_2_13!"
        exit(1)

parent = os.path.dirname(os.getcwd())
thisdir= os.path.dirname(os.getcwd()+'/')
sys.path.append(parent)
#from utils import *
import CombineHarvester.CombineTools.ch as ch

gROOT.SetBatch(1)

#BRconfStr=str(sys.argv[1])

#whichsignal = 'TT'
#if 'tW' in BRconfStr: whichsignal = 'BB'

fileDir = '/uscms_data/d3/jmanagan/BtoTW/CMSSW_12_4_8/src/vlq-BtoTW-SLA/makeTemplates/templatesDCY_Oct2023statonly/' ## Use Evan's Mar2021 folder here for SRCR ROOT files

#print '**** CAUTION: tag is about to be set to Mar2021 -- do you still want to use these old templates?'
tag = 'Oct2023_138fb' ##Tag and saveKey are used for output directory names
saveKey = ''#tag+'_'+str(sys.argv[3])
discrim = 'BpMass' #sys.argv[4]

print'Tag = ',tag

def add_processes_and_observations(cb):
        print '------------------------------------------------------------------------'
	print '>> Creating processes and observations...'
	for chn in chns:
                print '>>>> \t Creating proc/obs for channel:',chn
		cats_chn = cats[chn]
		cb.AddObservations(  ['*'],  ['BtoTW'], [era], [chn],                 cats_chn      )
		cb.AddProcesses(     ['*'],  ['BtoTW'], [era], [chn], bkg_procs[chn], cats_chn, False  )
		cb.AddProcesses(     masses, ['BtoTW'], [era], [chn], sig_procs,      cats_chn, True   )


def add_shapes(cb):
        print '------------------------------------------------------------------------'
	print '>> Extracting histograms from input root files...'
	for chn in chns:
                print '>>>> \t Extracting histos for channel:',chn
		SRbkg_pattern = discrim+'_'+lumiStr+'_%s$BIN__$PROCESS' % chn
		SRbkg_pattern = discrim+'_'+lumiStr+'_%s$BIN__$PROCESS$MASS' % chn
                cb.cp().channel([chn]).era([era]).backgrounds().ExtractShapes(rfile, SRbkg_pattern, SRbkg_pattern + '__$SYSTEMATIC')
                cb.cp().channel([chn]).era([era]).signals().ExtractShapes(rfile, SRsig_pattern, SRsig_pattern + '__$SYSTEMATIC')

        

def add_bbb(cb):
        ## This function is not used! autoMCstats in the card instead
	print '>> Merging bin errors and generating bbb uncertainties...'
	bbb = ch.BinByBinFactory()
	bbb.SetAddThreshold(0.1).SetMergeThreshold(0.5).SetFixNorm(False)
	
	for chn in chns:
		cb_chn = cb.cp().channel([chn])
		if 'CR' in chn:
			bbb.MergeAndAdd(cb_chn.cp().era([era]).bin_id([0,1,2,3]).process(bkg_procs[chn]), cb)
			bbb.MergeAndAdd(cb_chn.cp().era([era]).bin_id([0,1,2,3]).process(sig_procs), cb)
		else:
			bbb.MergeAndAdd(cb_chn.cp().era([era]).bin_id([0]).process(bkg_procs[chn]), cb)
			bbb.MergeAndAdd(cb_chn.cp().era([era]).bin_id([0]).process(sig_procs), cb)


def rename_and_write(cb):
        print '------------------------------------------------------------------------'
	print '>> Setting standardised bin names...'
	ch.SetStandardBinNames(cb)
	
	writer = ch.CardWriter('limits_'+tag+'/$TAG/$MASS/$ANALYSIS_$CHANNEL_$BINID_Combine.txt',
						   'limits_'+tag+'/$TAG/common/$ANALYSIS_$CHANNEL.input.root')
	writer.SetVerbosity(1)
	writer.WriteCards('cmb', cb)
	for chn in chns:
                print '>>>> \t WriteCards for channel:',chn
		writer.WriteCards(chn, cb.cp().channel([chn]))
	print '>> Done writing cards!'


def print_cb(cb):
	for s in ['Obs', 'Procs', 'Systs', 'Params']:
		print '* %s *' % s
		getattr(cb, 'Print%s' % s)()
		print


def add_systematics(cb):
        print '------------------------------------------------------------------------'
	print '>> Adding systematic uncertainties...'

	signal = cb.cp().signals().process_set()
	
        #cb.cp().process(signal+allbkgs).channel(chns).AddSyst(cb, 'lumiScale', 'rateParam', ch.SystMap()(36./138.)) # 137fb --> 36fb
        #cb.GetParameter("lumiScale").set_frozen(True)
	
        cb.cp().process([allbkgs[0]]).channel(chns).AddSyst(cb, 'TTBscale', 'lnN', ch.SystMap()(1.20))
        cb.cp().process([allbkgs[1]]).channel(chns).AddSyst(cb, 'SITscale', 'lnN', ch.SystMap()(1.20))
        cb.cp().process([allbkgs[2]]).channel(chns).AddSyst(cb, 'TTXscale', 'lnN', ch.SystMap()(1.20))
        cb.cp().process([allbkgs[3]]).channel(chns).AddSyst(cb, 'WJTscale', 'lnN', ch.SystMap()(1.20))
        cb.cp().process([allbkgs[4]]).channel(chns).AddSyst(cb, 'EWKscale', 'lnN', ch.SystMap()(1.20))
        cb.cp().process([allbkgs[5]]).channel(chns).AddSyst(cb, 'QCDscale', 'lnN', ch.SystMap()(1.20))
        cb.cp().process(signal).channel(chns).AddSyst(cb, 'SIGscale', 'lnN', ch.SystMap()(1.10))




def add_autoMCstat(cb):
        print '------------------------------------------------------------------------'
	print '>> Adding autoMCstats...'
	
	thisDir = os.getcwd()
	mass=0
	massList = [800,1400,2000]

	for chn in chns+['cmb']:
                print '>>>> \t Adding autoMCstats for channel:',chn
		for mass in massList:
			chnDir = os.getcwd()+'/limits_'+tag+'/'+chn+'/'+str(mass)+'/'
			print 'chnDir: ',chnDir
			os.chdir(chnDir)
			files = [x for x in os.listdir(chnDir) if '.txt' in x]
			for ifile in files:
				with open(chnDir+ifile, 'a') as chnfile: chnfile.write('* autoMCStats 1.')
			os.chdir(thisDir)

def create_workspace(cb):
        print '------------------------------------------------------------------------'
	print '>> Creating workspace...'

	#for chn in ['cmb']+chns:  ## do I really need individual workspaces? Not sure...
	for chn in ['cmb']:
                print '>>>> \t Creating workspace for channel:',chn
		chnDir = os.getcwd()+'/limits_'+tag+'/'+chn+'/*'
		cmd = 'combineTool.py -M T2W -i '+chnDir+' -o workspace.root --channel-masks'
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

        if not os.path.exists('./limits_'+tag+'/'): os.system('mkdir -p ./limits_'+tag+'/')

        rfile = fileDir+'/templates_'+discrim+'_'+lumiStr+'.root'

	print'File: ',rfile
	allbkgs = ['ttbar','singletop','ttx','wjets','ewk','qcd']

	dataName = 'data_obs'
	tfile = TFile(rfile)
	tfile.Close()

        chns = ['tagTjet','tagWjet','untagTlep','untagWlep']
        chns = ['isL_'+chn for chn in chns]
        bkg_procs = {}
        for chn in chns:
                bkg_procs[chn] = allbkgs
	
	print 'bkg_procs: ',bkg_procs
	for cat in sorted(bkg_procs.keys()):
		print cat,bkg_procs[cat]
	
        sig_procs = ['BpM']

	cats = {}
	for chn in chns: cats[chn] = [(0, '')]
	
	masses = ch.ValsFromRange('800:2200|200')
        #masses.push_back("1300") # these worked in newer combine
        #masses.push_back("1500")
        #masses.push_back("1700")
        masses.append('1300')
        masses.append('1500')
        masses.append('1700')
        
	print 'Found this mass list: ',masses

	go(cb)

