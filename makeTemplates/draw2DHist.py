import ROOT

nForwardFile = ROOT.TFile('templates_NJetsForward_138fbfb.root')
nBFile = ROOT.TFile('templates_NBJets_138fbfb.root')

bkgList = ['ewk','qcd','ttbar','ttx','wjets','singletop']

for hist in bkgList:
    hist = f'NBJets_138fbfb_isL_all__{}'

