import os,sys,datetime,itertools,math

thisDir = os.getcwd()
if thisDir[-13:] == 'makeTemplates': runDir = thisDir[:-13]
else: runDir = thisDir
if os.getcwd()[-17:] == 'singleLepAnalyzer': os.chdir(os.getcwd()+'/makeTemplates/')
outputDir = thisDir+'/'

region='Y' #all, BAX, DCY, individuals

categorize=1 #1==categorize into 6 tags

cTime=datetime.datetime.now()
date='%i_%i_%i'%(cTime.year,cTime.month,cTime.day)
time='%i_%i_%i'%(cTime.hour,cTime.minute,cTime.second)
pfix = 'templates'+region
if not categorize: pfix='kinematics'+region

pfix+='_Oct2023statsonly_Extended'

plotList = [#distribution name as defined in "doHists.py"
        #'ST', #:('gcJet_ST',linspace(0, 5000, 51).tolist(),';S_{T} (GeV)'),
        #'BpMass', #:('Bprime_mass',linspace(0,4000,51).tolist(),';B quark mass [GeV]'),
        # 'HT', #:('gcJet_HT',linspace(0, 5000, 51).tolist(),';H_{T} (GeV)'), 
        # 'lepPt' , #:('lepton_pt',linspace(0, 1000, 51).tolist(),';lepton p_{T} [GeV]'),
        # 'lepEta', #:('lepton_eta',linspace(-2.5, 2.5, 51).tolist(),';lepton #eta'),
        # 'lepPhi', #:('lepton_phi',linspace(-3.2,3.2,65).tolist(),';lepton #phi'),
        # 'lepIso', #:('lepton_miniIso',linspace(0,0.2,51).tolist(),';lepton mini-isolation'),
        # 'MET'   , #:('corrMET_pt',linspace(0, 1000, 51).tolist(),';#slash{E}_{T} [GeV]'),
        # 'METphi', #:('corrMET_phi',linspace(-3.2,3.2, 65).tolist(),';#slash{E}_{T} phi'),
        # 'JetEta', #:('gcJet_eta',linspace(-3, 3, 41).tolist(),';central AK4 jet #eta'),
        # 'JetPt' , #:('gcJet_pt',linspace(0, 1500, 51).tolist(),';central AK4 jet p_{T} [GeV]'),
        # 'JetPhi', #:('gcJet_phi',linspace(-3.2,3.2, 65).tolist(),';central AK4 jet phi'),
        # 'JetBtag', #:('gcJet_DeepFlav',linspace(0,1,51).tolist(),';central AK4 jet DeepJet disc'),
        # 'ForwJetEta', #:('gcforwJet_eta',linspace(-3, 3, 41).tolist(),';forward AK4 jet #eta'),
        # 'ForwJetPt' , #:('gcforwJet_pt',linspace(0, 1500, 51).tolist(),';forward AK4 jet p_{T} [GeV]'),
        # 'ForwJetPhi', #:('gcforwJet_phi',linspace(-3.2,3.2, 65).tolist(),';forward AK4 jet phi'),
        # 'FatJetEta', #:('gcFatJet_eta',linspace(-3, 3, 41).tolist(),';AK8 jet #eta'),
        # 'FatJetPt' , #:('gcFatJet_pt',linspace(0, 1500, 51).tolist(),';AK8 jet p_{T} [GeV]'),
        # 'FatJetPhi', #:('gcFatJet_phi',linspace(-3.2,3.2, 65).tolist(),';AK8 jet phi'),
        # 'FatJetSD' , #:('gcFatJet_sdmass',linspace(0, 500, 51).tolist(),';AK8 soft drop mass [GeV]'),
        # 'FatJetMatch', #:('gcFatJet_genmatch',linspace(-24,24,49).tolist(),';AK8 gen match ID'),
        # 'OS1FatJetEta', #:('gcOSFatJet_eta[0]',linspace(-3, 3, 41).tolist(),';B decay AK8 #eta'),
        # 'OS1FatJetPt' , #:('gcOSFatJet_pt[0]',linspace(0, 1500, 51).tolist(),';B decay AK8 p_{T} [GeV]'),
        # 'OS1FatJetPhi', #:('gcOSFatJet_phi[0]',linspace(-3.2,3.2, 65).tolist(),';B decay AK8 phi'),
        # 'OS1FatJetSD' , #:('gcOSFatJet_sdmass[0]',linspace(0, 500, 51).tolist(),';B decay AK8 soft drop mass [GeV]'),
        # 'NJetsCentral' , #:('NJets_central',linspace(0, 10, 11).tolist(),';central AK4 jet multiplicity'),
        # 'NJetsForward' , #:('NJets_forward',linspace(0, 10, 11).tolist(),';forward AK4 jet multiplicity'),
        # 'NBJets', #:('NJets_DeepFlavL',linspace(0, 10, 11).tolist(),';DeepJet loose multiplicity'),
        # 'NOSJets', #:('NOS_gcJets_central',linspace(0, 5, 6).tolist(),';central AK4 opp-side jets'),
        # 'NSSJets', #:('NSS_gcJets_central',linspace(0, 5, 6).tolist(),';central AK4 same-side jets'),
        # 'NOSBJets', #:('NOS_gcJets_DeepFlavL',linspace(0, 5, 6).tolist(),';central AK4 opp-side b jets'),
        # 'NSSBJets', #:('NSS_gcJets_DeepFlavL',linspace(0, 5, 6).tolist(),';central AK4 same-side b jets'),
        # 'NFatJets', #:('NFatJets',linspace(0, 10, 11).tolist(),';AK8 jet multiplicity'),
        # 'NOSFatJets', #:('NOS_gcFatJets',linspace(0, 5, 6).tolist(),';AK8 opp-side jets'),
        # 'NSSFatJets', #:('NSS_gcFatJets',linspace(0, 5, 6).tolist(),';AK8 same-side jets'),
        # 'minDR_twoAK8s', #:('minDR_leadAK8otherAK8',linspace(0,5,51).tolist(),';min #Delta R(leading AK8 jet, other AK8 jet) [GeV]'),
        # 'minDR_twoAK4s', #:('minDR_leadAK4otherAK4',linspace(0,5,51).tolist(),';min #Delta R(leading AK4 jet, other AK4 jet) [GeV]'),
        # 'PtRel', #:('ptRel_atMinDR_lepJets',linspace(0,500,51).tolist(),';p_{T,rel}(l, closest jet) [GeV]'),
        # 'PtRelAK8', #:('ptRel_atMinDR_lepFatJets',linspace(0,500,51).tolist(),';p_{T,rel}(l, closest AK8 jet) [GeV]'),
        # 'minDR', #:('minDR_lepJets',linspace(0,5,51).tolist(),';#Delta R(l, closest jet) [GeV]'),
        # 'minDRAK8', #:('minDR_lepFatJets',linspace(0,5,51).tolist(),';#Delta R(l, closest AK8 jet) [GeV]'),
        # 'FatJetTau21'  , #:('gcFatJet_tau21',linspace(0, 1, 51).tolist(),';AK8 Jet #tau_{2}/#tau_{1}'),
        # 'FatJetTau32'  , #:('gcFatJet_tau32',linspace(0, 1, 51).tolist(),';AK8 Jet #tau_{3}/#tau_{2}'),
        # 'OS1FatJetTau21'  , #:('gcOSFatJet_tau21[0]',linspace(0, 1, 51).tolist(),';B decay AK8 #tau_{2}/#tau_{1}'),
        # 'OS1FatJetTau32'  , #:('gcOSFatJet_tau32[0]',linspace(0, 1, 51).tolist(),';B decay AK8 #tau_{3}/#tau_{2}'),
        # 'FatJetProbJ', #:('gcFatJet_pNetJ',linspace(0,1.2,51).tolist(),';pNet J score'),
        # 'FatJetProbT', #:('gcFatJet_pNetT',linspace(0,1.2,51).tolist(),';pNet t score'),
        # 'FatJetProbW', #:('gcFatJet_pNetW',linspace(0,1.2,51).tolist(),';pNet W score'),
        # 'FatJetProbTvJ', #:('gcFatJet_pNetTvsQCD',linspace(0,1.2,51).tolist(),';pNet t-v-QCD score'),
        # 'FatJetProbWvJ', #:('gcFatJet_pNetWvsQCD',linspace(0,1.2,51).tolist(),';pNet W-v-QCD score'),
        # 'FatJetTag', #:('gcFatJet_pNetTag',linspace(0,3,4).tolist(),';pNet tag (0 = J, 1 = t, 2 = W)'),
        # 'OS1FatJetProbJ', #:('gcOSFatJet_pNetJ[0]',linspace(0,1.2,51).tolist(),';B decay AK8 pNet J score'),
        # 'OS1FatJetProbT', #:('gcOSFatJet_pNetT[0]',linspace(0,1.2,51).tolist(),';B decay AK8 pNet t score'),
        # 'OS1FatJetProbW', #:('gcOSFatJet_pNetW[0]',linspace(0,1.2,51).tolist(),';B decay AK8 pNet W score'),
        # 'OS1FatJetProbTvJ', #:('gcOSFatJet_pNetTvsQCD[0]',linspace(0,1.2,51).tolist(),';B decay AK8 pNet t-v-QCD score'),
        # 'OS1FatJetProbWvJ', #:('gcOSFatJet_pNetWvsQCD[0]',linspace(0,1.2,51).tolist(),';B decay AK8 pNet W-v-QCD score'),
        # 'OS1FatJetTag', #:('gcOSFatJet_pNetTag[0]',linspace(0,3,4).tolist(),';B decay AK8 pNet tag (0 = J, 1 = t, 2 = W)'),
        # 'nT', #:('gcFatJet_nT',linspace(0,5,6).tolist(),';N pNet t-tagged jets'),
        # 'nW', #:('gcFatJet_nW',linspace(0,5,6).tolist(),';N pNet W-tagged jets'),
        # 'Wmass', #:('W_mass',linspace(0,500,51).tolist(),';reco W mass [GeV]'),
        # 'Wpt', #:('W_pt',linspace(0,1500,51).tolist(),';reco W pt [GeV]'),
        # 'Weta', #:('W_eta',linspace(-4,4,41).tolist(),';reco W eta'),
        # 'Wphi', #:('W_phi',linspace(-3.2,3.2, 65).tolist(),';reco W phi'),
        # 'WMt', #:('W_MT',linspace(0,500,51).tolist(),';reco W M_{T} [GeV]'),
        # 'Wdrlep', #:('DR_W_lep',linspace(0,5,51).tolist(),';reco W #DeltaR(W,lepton)'),        
        # 'minMlj', #:('minM_lep_Jet',linspace(0,1000,51).tolist(),';min[M(l,jet)] [GeV]'),
        # 'tmassMLJ', #:('t_mass_minMlj',linspace(0,500,51).tolist(),';reco t mass (minMlj method) [GeV]'),
        # 'tptMLJ', #:('t_pt_minMlj',linspace(0,1000,51).tolist(),';reco t pt (minMlj method) [GeV]'),
        # 'tetaMLJ', #:('t_eta_minMlj',linspace(-4,4,41).tolist(),';reco t eta (minMlj method)'),
        # 'tphiMLJ', #:('t_phi_minMlj',linspace(-3.2,3.2, 65).tolist(),';reco t phi (minMlj method)'),
        # 'tmassSSB', #:('t_mass_SSb',linspace(0,500,51).tolist(),';reco t mass (SSb method) [GeV]'),
        # 'tptSSB', #:('t_pt_SSb',linspace(0,1000,51).tolist(),';reco t pt (SSb method) [GeV]'),
        # 'tetaSSB', #:('t_eta_SSb',linspace(-4,4,41).tolist(),';reco t eta (SSb method)'),
        # 'tphiSSB', #:('t_phi_SSb',linspace(-3.2,3.2, 65).tolist(),';reco t phi (SSb method)'),
        # 'tdrWbMLJ', #:('DR_W_b_minMlj',linspace(0,6.3,51).tolist(),';reco t, #DeltaR(W,b) (minMlj method)'),
        # 'tdrWbSSB', #:('DR_W_b_SSb',linspace(0,6.3,51).tolist(),';reco t, #DeltaR(W,b) (SSb method)'),
        # 'BpPt', #:('Bprime_pt',linspace(0,3000,51).tolist(),';B quark p_{T} [GeV]'),
        # 'BpEta', #:('Bprime_eta',linspace(-5,5,51).tolist(),';B quark #eta'),
        # 'BpPhi', #:('Bprime_phi',linspace(-3.14,3.14,51).tolist(),';B quark #phi'),
        # 'BpDeltaR', #:('Bprime_DR',linspace(0,5,51).tolist(),';#DeltaR(B quark products)'),
        # 'BpPtBal', #:('Bprime_ptbal',linspace(0,3,51).tolist(),';B quark t/W p_{T} ratio'),
        # 'BpChi2', #:('Bprime_chi2',linspace(0,1000,51).tolist(),';B quark reconstruction #chi^{2}'), # CHECK ME, what range?
        # 'BpDecay', #:('Bdecay_obs',linspace(0,5,6).tolist(),';B quark mode (1: Tjet+lepW, 2: Wjet+lepT, 3: AK8+lepW, 4: AK8+lepT')
        'BpMass_ABCDnn', #:('Bprime_mass_ABCDnn',linspace(0,5000,51).tolist(),';B quark mass [GeV]')
        #'ST_ABCDnn', #:('gcJet_ST_ABCDnn',linspace(0, 5000, 51).tolist(),';S_{T} (GeV)')
	]

isEMlist = ['L'] #['E','M']
if '2D' in pfix: isEMlist = ['L']

taglist = ['all']
if categorize:
        #taglist=['tagTjet','tagWjet','untagTlep','untagWlep', 'allWlep','allTlep']#,'allWlep','allTlep']
        taglist=['allWlep','allTlep']
        ## later, can determine tag lists for different regions

outDir = outputDir+pfix+'/'
print(outDir)
if not os.path.exists(outDir): os.system('mkdir '+outDir)
if '2D' in outDir:
        os.system('cp ../analyze2D.py doHists2D.py ../utils.py ../samples.py doCondorTemplates.py doCondorTemplates2D.sh '+outDir+'/')
else:
        os.system('cp ../analyze.py doHists.py ../utils.py ../samples.py doCondorTemplates.py doCondorTemplates.sh '+outDir+'/')
os.chdir(outDir)

catlist = list(itertools.product(isEMlist,taglist))

iPlotList = []
dimstr = ''
if '2D' in outDir: ## outdated, not used yet in BtoTW
        dimstr = '2D'
        templist = list(itertools.combinations(plotList,2))
        for item in templist:
                if 'NJetsAK8' not in item[0] and 'NJetsAK8' not in item[1]: continue
                iPlotList.append('X'+item[0]+'Y'+item[1])
else:
        iPlotList = plotList
        
print('Dimensions:',dimstr)
print('iPlotList:',iPlotList)

count=0
for iplot in iPlotList:
	for cat in list(itertools.product(isEMlist,taglist)):
		catDir = cat[0]+'_'+cat[1]	
		outDir = outputDir+pfix+'/'+catDir
		if not os.path.exists(outDir): os.system('mkdir '+outDir)
		os.chdir(outDir)			

		dict={'rundir':runDir, 'dir':'.','iPlot':iplot,'region':region,'isCategorized':categorize,
			  'isEM':cat[0],'tag':cat[1],'2D':dimstr}
		print(dict)
		jdf=open('condor.job','w')
		jdf.write(
			"""use_x509userproxy = true
universe = vanilla
Executable = %(rundir)s/makeTemplates/doCondorTemplates%(2D)s.sh
Should_Transfer_Files = YES
WhenToTransferOutput = ON_EXIT
Transfer_Input_Files = ../analyze%(2D)s.py, ../samples.py, ../utils.py, ../doHists%(2D)s.py
Output = condor_%(iPlot)s.out
Error = condor_%(iPlot)s.err
Log = condor_%(iPlot)s.log
Notification = Never
Arguments = %(dir)s %(iPlot)s %(region)s %(isCategorized)s %(isEM)s %(tag)s

Queue 1"""%dict)
		jdf.close()

		os.system('condor_submit condor.job')
		os.chdir('..')
		count+=1

print("Total jobs submitted:", count)
                  
