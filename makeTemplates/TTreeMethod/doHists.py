#!/usr/bin/python

# python3 -u doHists.py . BpMass_ABCDnn all 1 L
# optional arguments:
#    argv1: outDir (default cwd)
#    argv2: iPlot (discriminant from plotList. default 'HT')
#    argv3: region (divide into ABCDnn regions. takes 'A', 'B', ..., 'all'. default 'all')
#    argv4: isCategorized (divide into decay modes. takes integer values 0 or 1 (True). default '0' (False))
#    argv5: isEMlist (default 'E')
#    argv6: taglist (default 'all')

# Outputs .p files containing a dictionary of histograms

import os,sys,time,math,datetime,pickle,itertools,getopt
from ROOT import TH1D,gROOT,TFile,TTree
parent = os.path.dirname(os.getcwd())
sys.path.append(parent)
from numpy import linspace

from analyze import *
from samples import samples_electroweak, samples_wjets, samples_singletop, samples_ttbarx, samples_qcd, samples_data, samples_signal
from utils import *

gROOT.SetBatch(1)
start_time = time.time()

# ------------- File location and total lumi ---------------

#step1Dir = 'root://cmseos.fnal.gov//store/user/jmanagan/BtoTW_Apr2024_fullRun2/'
step1Dir = 'root://cmseos.fnal.gov//store/user/xshen/BtoTW_Apr2024_fullRun2_ABCDnnMar2024/'

# ------------- Arguments and default values ------------
iPlot = 'HT' #choose a discriminant from plotList below!
if len(sys.argv)>2: iPlot=sys.argv[2]
region = 'all'
if len(sys.argv)>3: region=sys.argv[3]
isCategorized = False
if len(sys.argv)>4: isCategorized=int(sys.argv[4])

doABCDnn = False
if 'ABCDnn' in iPlot:
        doABCDnn = True
        import samples_ttbar_abcdnn
else:
        import samples_ttbar

doJetRwt= 1
doAllSys= False
cTime=datetime.datetime.now()
datestr='%i_%i_%i'%(cTime.year,cTime.month,cTime.day)
timestr='%i_%i_%i'%(cTime.hour,cTime.minute,cTime.second)
pfix='templatesTest'+region
if not isCategorized: pfix='kinematicsTEST'+region
print('Set pfix to '+pfix)

# -------------- Groups of background samples to use --------------

# this is a list of group dictionaries. "wjets" has entries like "WJetsHT2002018":WJetsHT2002018, where the 2nd is the class
bkgList = [samples_electroweak,samples_wjets,samples_ttbar,samples_singletop,samples_ttbarx,samples_qcd]

### TO-DO: in samples.py, make up an entry for each year for ABCDnn with dummy information where needed.
### When iPlot == a transform variable, bkgList = [samples_electroweak,samples_ttbarx,samples_abcdnn] (singletop?)

# use "samples_data" and "samples_signal" below for the dictionaries of data and signals

# ------------- Parameters to divide up the histograms --------------

if len(sys.argv)>5: isEMlist=[str(sys.argv[5])]
else: isEMlist = ['E']
if len(sys.argv)>6: taglist=[str(sys.argv[6])]
else: 
	taglist = ['all']
	if isCategorized: taglist=['tagTjet','tagWjet','untagTlep','untagWlep','allWlep','allTlep']

# ------------- Definition of plots to make ------------------
### TO-DO: add ABCDnn branches
plotList = {#discriminantName:(discriminantLJMETName, binning, xAxisLabel)
         'lepPt' :('lepton_pt',linspace(0, 1000, 51).tolist(),';lepton p_{T} [GeV]'),
         'lepEta':('lepton_eta',linspace(-2.5, 2.5, 51).tolist(),';lepton #eta'),
         'lepPhi':('lepton_phi',linspace(-3.2,3.2,65).tolist(),';lepton #phi'),
         'lepIso':('lepton_miniIso',linspace(0,0.2,51).tolist(),';lepton mini-isolation'),
         'MET'   :('corrMET_pt',linspace(0, 1000, 51).tolist(),';#slash{E}_{T} [GeV]'),
         'METphi':('corrMET_phi',linspace(-3.2,3.2, 65).tolist(),';#slash{E}_{T} phi'),
         'HT':('gcJet_HT',linspace(0, 5000, 51).tolist(),';H_{T} (GeV)'),
         'ST':('gcJet_ST',linspace(0, 5000, 51).tolist(),';S_{T} (GeV)'),
         'JetEta':('gcJet_eta',linspace(-3, 3, 41).tolist(),';central AK4 jet #eta'),
         'JetPt' :('gcJet_pt',linspace(0, 1500, 51).tolist(),';central AK4 jet p_{T} [GeV]'),
         'JetPhi':('gcJet_phi',linspace(-3.2,3.2, 65).tolist(),';central AK4 jet phi'),
         'JetBtag':('gcJet_DeepFlav',linspace(0,1,51).tolist(),';central AK4 jet DeepJet disc'),
         'ForwJetEta':('gcforwJet_eta',linspace(-3, 3, 41).tolist(),';forward AK4 jet #eta'),
         'ForwJetPt' :('gcforwJet_pt',linspace(0, 1500, 51).tolist(),';forward AK4 jet p_{T} [GeV]'),
         'ForwJetPhi':('gcforwJet_phi',linspace(-3.2,3.2, 65).tolist(),';forward AK4 jet phi'),
         'FatJetEta':('gcFatJet_eta',linspace(-3, 3, 41).tolist(),';AK8 jet #eta'),
         'FatJetPt' :('gcFatJet_pt',linspace(0, 1500, 51).tolist(),';AK8 jet p_{T} [GeV]'),
         'FatJetPhi':('gcFatJet_phi',linspace(-3.2,3.2, 65).tolist(),';AK8 jet phi'),
         'FatJetSD' :('gcFatJet_sdmass',linspace(0, 500, 51).tolist(),';AK8 soft drop mass [GeV]'),
         'FatJetMatch':('gcFatJet_genmatch',linspace(-24,24,49).tolist(),';AK8 gen match ID'),
         'OS1FatJetEta':('gcOSFatJet_eta[0]',linspace(-3, 3, 41).tolist(),';B decay AK8 #eta'),
         'OS1FatJetPt' :('gcOSFatJet_pt[0]',linspace(0, 1500, 51).tolist(),';B decay AK8 p_{T} [GeV]'),
         'OS1FatJetPhi':('gcOSFatJet_phi[0]',linspace(-3.2,3.2, 65).tolist(),';B decay AK8 phi'),
         'OS1FatJetSD' :('gcOSFatJet_sdmass[0]',linspace(0, 500, 51).tolist(),';B decay AK8 soft drop mass [GeV]'),
         'NJetsCentral' :('NJets_central',linspace(0, 10, 11).tolist(),';central AK4 jet multiplicity'),
         'NJetsForward' :('NJets_forward',linspace(0, 10, 11).tolist(),';forward AK4 jet multiplicity'),
         'NBJets':('NJets_DeepFlavL',linspace(0, 10, 11).tolist(),';DeepJet loose multiplicity'),
         'NOSJets':('NOS_gcJets_central',linspace(0, 5, 6).tolist(),';central AK4 opp-side jets'),
         'NSSJets':('NSS_gcJets_central',linspace(0, 5, 6).tolist(),';central AK4 same-side jets'),
         'NOSBJets':('NOS_gcJets_DeepFlavL',linspace(0, 5, 6).tolist(),';central AK4 opp-side b jets'),
         'NSSBJets':('NSS_gcJets_DeepFlavL',linspace(0, 5, 6).tolist(),';central AK4 same-side b jets'),
         'NFatJets':('NFatJets',linspace(0, 10, 11).tolist(),';AK8 jet multiplicity'),
         'NOSFatJets':('NOS_gcFatJets',linspace(0, 5, 6).tolist(),';AK8 opp-side jets'),
         'NSSFatJets':('NSS_gcFatJets',linspace(0, 5, 6).tolist(),';AK8 same-side jets'),
         'minDR_twoAK8s':('minDR_leadAK8otherAK8',linspace(0,5,51).tolist(),';min #Delta R(leading AK8 jet, other AK8 jet) [GeV]'),
         'minDR_twoAK4s':('minDR_leadAK4otherAK4',linspace(0,5,51).tolist(),';min #Delta R(leading AK4 jet, other AK4 jet) [GeV]'),
         'PtRel':('ptRel_atMinDR_lepJets',linspace(0,500,51).tolist(),';p_{T,rel}(l, closest jet) [GeV]'),
         'PtRelAK8':('ptRel_atMinDR_lepFatJets',linspace(0,500,51).tolist(),';p_{T,rel}(l, closest AK8 jet) [GeV]'),
         'minDR':('minDR_lepJets',linspace(0,5,51).tolist(),';#Delta R(l, closest jet) [GeV]'),
         'minDRAK8':('minDR_lepFatJets',linspace(0,5,51).tolist(),';#Delta R(l, closest AK8 jet) [GeV]'),
         'FatJetTau21'  :('gcFatJet_tau21',linspace(0, 1, 51).tolist(),';AK8 Jet #tau_{2}/#tau_{1}'),
         'FatJetTau32'  :('gcFatJet_tau32',linspace(0, 1, 51).tolist(),';AK8 Jet #tau_{3}/#tau_{2}'),
         'OS1FatJetTau21'  :('gcOSFatJet_tau21[0]',linspace(0, 1, 51).tolist(),';B decay AK8 #tau_{2}/#tau_{1}'),
         'OS1FatJetTau32'  :('gcOSFatJet_tau32[0]',linspace(0, 1, 51).tolist(),';B decay AK8 #tau_{3}/#tau_{2}'),
         'FatJetProbJ':('gcFatJet_pNetJ',linspace(0,1.2,51).tolist(),';pNet J score'),
         'FatJetProbT':('gcFatJet_pNetT',linspace(0,1.2,51).tolist(),';pNet t score'),
         'FatJetProbW':('gcFatJet_pNetW',linspace(0,1.2,51).tolist(),';pNet W score'),
         'FatJetProbTvJ':('gcFatJet_pNetTvsQCD',linspace(0,1.2,51).tolist(),';pNet t-v-QCD score'),
         'FatJetProbWvJ':('gcFatJet_pNetWvsQCD',linspace(0,1.2,51).tolist(),';pNet W-v-QCD score'),
         'FatJetTag':('gcFatJet_pNetTag',linspace(0,3,4).tolist(),';pNet tag (0 = J, 1 = t, 2 = W)'),
         'OS1FatJetProbJ':('gcOSFatJet_pNetJ[0]',linspace(0,1.2,51).tolist(),';B decay AK8 pNet J score'),
         'OS1FatJetProbT':('gcOSFatJet_pNetT[0]',linspace(0,1.2,51).tolist(),';B decay AK8 pNet t score'),
         'OS1FatJetProbW':('gcOSFatJet_pNetW[0]',linspace(0,1.2,51).tolist(),';B decay AK8 pNet W score'),
         'OS1FatJetProbTvJ':('gcOSFatJet_pNetTvsQCD[0]',linspace(0,1.2,51).tolist(),';B decay AK8 pNet t-v-QCD score'),
         'OS1FatJetProbWvJ':('gcOSFatJet_pNetWvsQCD[0]',linspace(0,1.2,51).tolist(),';B decay AK8 pNet W-v-QCD score'),
         'OS1FatJetTag':('gcOSFatJet_pNetTag[0]',linspace(0,3,4).tolist(),';B decay AK8 pNet tag (0 = J, 1 = t, 2 = W)'),
         'nT':('gcFatJet_nT',linspace(0,5,6).tolist(),';N pNet t-tagged jets'),
         'nW':('gcFatJet_nW',linspace(0,5,6).tolist(),';N pNet W-tagged jets'),
         'Wmass':('W_mass',linspace(0,500,51).tolist(),';reco W mass [GeV]'),
         'Wpt':('W_pt',linspace(0,1500,51).tolist(),';reco W pt [GeV]'),
         'Weta':('W_eta',linspace(-4,4,41).tolist(),';reco W eta'),
         'Wphi':('W_phi',linspace(-3.2,3.2, 65).tolist(),';reco W phi'),
         'WMt':('W_MT',linspace(0,500,51).tolist(),';reco W M_{T} [GeV]'),
         'Wdrlep':('DR_W_lep',linspace(0,5,51).tolist(),';reco W #DeltaR(W,lepton)'),        
         'minMlj':('minM_lep_Jet',linspace(0,1000,51).tolist(),';min[M(l,jet)] [GeV]'),
         'tmassMLJ':('t_mass_minMlj',linspace(0,500,51).tolist(),';reco t mass (minMlj method) [GeV]'),
         'tptMLJ':('t_pt_minMlj',linspace(0,1000,51).tolist(),';reco t pt (minMlj method) [GeV]'),
         'tetaMLJ':('t_eta_minMlj',linspace(-4,4,41).tolist(),';reco t eta (minMlj method)'),
         'tphiMLJ':('t_phi_minMlj',linspace(-3.2,3.2, 65).tolist(),';reco t phi (minMlj method)'),
         'tmassSSB':('t_mass_SSb',linspace(0,500,51).tolist(),';reco t mass (SSb method) [GeV]'),
         'tptSSB':('t_pt_SSb',linspace(0,1000,51).tolist(),';reco t pt (SSb method) [GeV]'),
         'tetaSSB':('t_eta_SSb',linspace(-4,4,41).tolist(),';reco t eta (SSb method)'),
         'tphiSSB':('t_phi_SSb',linspace(-3.2,3.2, 65).tolist(),';reco t phi (SSb method)'),
         'tdrWbMLJ':('DR_W_b_minMlj',linspace(0,6.3,51).tolist(),';reco t, #DeltaR(W,b) (minMlj method)'),
         'tdrWbSSB':('DR_W_b_SSb',linspace(0,6.3,51).tolist(),';reco t, #DeltaR(W,b) (SSb method)'),
         'BpMass':('Bprime_mass',linspace(0,4000,51).tolist(),';B quark mass [GeV]'),
         'BpPt':('Bprime_pt',linspace(0,3000,51).tolist(),';B quark p_{T} [GeV]'),
         'BpEta':('Bprime_eta',linspace(-5,5,51).tolist(),';B quark #eta'),
         'BpPhi':('Bprime_phi',linspace(-3.14,3.14,51).tolist(),';B quark #phi'),
         'BpDeltaR':('Bprime_DR',linspace(0,5,51).tolist(),';#DeltaR(B quark products)'),
         'BpPtBal':('Bprime_ptbal',linspace(0,3,51).tolist(),';B quark t/W p_{T} ratio'),
         'BpChi2':('Bprime_chi2',linspace(0,1000,51).tolist(),';B quark reconstruction #chi^{2}'), # CHECK ME, what range?
         'BpDecay':('Bdecay_obs',linspace(0,5,6).tolist(),';B quark mode (1: Tjet+lepW, 2: Wjet+lepT, 3: AK8+lepW, 4: AK8+lepT'),
         'BpMass_ABCDnn':('Bprime_mass_ABCDnn',linspace(0,5000,51).tolist(),';B quark mass [GeV]'),
         'ST_ABCDnn':('gcJet_ST_ABCDnn',linspace(0, 5000, 51).tolist(),';S_{T} (GeV)'),
}

print( "PLOTTING: "+iPlot)
print( "         LJMET Variable: "+plotList[iPlot][0])
print( "         X-AXIS TITLE  : "+plotList[iPlot][2])
print( "         BINNING USED  : "+str(plotList[iPlot][1]))

shapesFiles = ['jec','jer']
tTreeData = {}
tTreeSig = {}
tTreeBkg = {}

catList = list(itertools.product(isEMlist,taglist))
print('Cat list: '+str(catList))
nCats  = len(catList)
catInd = 1
for cat in catList:
        print('==================== Category: '+str(cat)+' ======================')
        catDir = cat[0]+'_'+cat[1]

        if len(sys.argv)>1:
                outDir=sys.argv[1]
                sys.path.append(outDir)
        else: 
                outDir = os.getcwd()+'/'+pfix+'/'+catDir
                if not os.path.exists(outDir): os.system('mkdir -p '+outDir)                
        category = {'isEM':cat[0],'tag':cat[1]} # THINK: is this necessary?

        print('Running analyze! Storing in outDir = '+outDir)
        datahists = {}
        for data in samples_data.keys(): # "data" is the class 
                print('------------ '+data+' -------------')
                fileprefix = (samples_data[data].samplename).split('/')[1]+((samples_data[data].samplename).split('/')[2])[7]
                tTreeData[data]=readTreeNominal(fileprefix,samples_data[data].year,step1Dir) ## located in utils.py

                ### For analyze_RDF make the switch here (and similar regions below)
                ### Could "datahists" now be "updated" with more histptrs instead of hists? 
                datahists.update(analyze(tTreeData,samples_data[data],False,iPlot,plotList[iPlot],category,region,isCategorized))
                if catInd==nCats: 
                        print('deleting '+data)
                        del tTreeData[data]

        ### this function puts overflow into the last column -- in utils? Works on histptrs? If not, do this later?
        for data in datahists.keys(): overflow(datahists[data]) 

        ### store the dictionary of hists in a pickle file. Change this to open output ROOT, loop and .Write histptrs?
        pickle.dump(datahists,open(outDir+'/datahists_'+iPlot+'.p','wb'))
        del datahists

        ### Now we begin the same general process but for simulated backgrounds
        igrp = 0
        for bkgGrp in bkgList:
                bkghists  = {}
                for bkg in bkgGrp.keys():
                        print('------------ '+bkg+' -------------')
                        fileprefix = (bkgGrp[bkg].samplename).split('/')[1]
                        tTreeBkg[bkg]=readTreeNominal(fileprefix,bkgGrp[bkg].year,step1Dir)
                        if doAllSys: # TODO: consider ABCDnn
                                for syst in shapesFiles:
                                        for ud in ['Up','Dn']:
                                                print("        "+syst+ud)
                                                tTreeBkg[bkg+syst+ud]=readTreeShift(fileprefix,bkgGrp[bkg].year,syst.upper()+ud.lower(),step1Dir) ## located in utils.py
                        bkghists.update(analyze(tTreeBkg,bkgGrp[bkg],doAllSys,iPlot,plotList[iPlot],category,region,isCategorized))
                        if catInd==nCats:
                                print('deleting '+bkg)
                                del tTreeBkg[bkg]
                                if doAllSys:
                                        for syst in shapesFiles:
                                                for ud in ['Up','Dn']: del tTreeBkg[bkg+syst+ud]

                for bkg in bkghists.keys(): negBinCorrection(bkghists[bkg])
                for bkg in bkghists.keys():   overflow(bkghists[bkg])
                pickle.dump(bkghists,open(outDir+'/bkghists'+str(igrp)+'_'+iPlot+'.p','wb'))
                igrp += 1
        del bkghists

        sighists  = {}
        for sig in samples_signal.keys(): 
                print('------------- '+sig+' ------------')
                fileprefix = (samples_signal[sig].samplename).split('/')[1]
                tTreeSig[sig]=readTreeNominal(fileprefix,samples_signal[sig].year,step1Dir)
                if doAllSys:
                        for syst in shapesFiles:
                                for ud in ['Up','Dn']:
                                        print("        "+syst+ud)
                                        tTreeSig[sig+syst+ud]=readTreeShift(fileprefix,samples_signal[sig].year,syst.upper()+ud.lower(),step1Dir)
                sighists.update(analyze(tTreeSig,samples_signal[sig],doAllSys,iPlot,plotList[iPlot],category,region,isCategorized))
                if catInd==nCats: 
                        print('deleting '+sig)
                        del tTreeSig[sig]
                        if doAllSys:
                                for syst in shapesFiles:
                                        for ud in ['Up','Dn']: del tTreeSig[sig+syst+ud]

        for sig in sighists.keys(): negBinCorrection(sighists[sig])
        for sig in sighists.keys(): overflow(sighists[sig])	
        pickle.dump(sighists,open(outDir+'/sighists_'+iPlot+'.p','wb'))
        del sighists

        catInd+=1

print("--- %s minutes ---" % (round((time.time() - start_time)/60,2)))
