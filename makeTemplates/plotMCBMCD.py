import ROOT, os

ROOT.gROOT.SetBatch(True)

#fileB = ROOT.TFile.Open(f'templatesB_Jan2025_210bins/templates_BpMass_138fbfb_rebinned1_stat0p2.root','READ')
#fileD = ROOT.TFile.Open(f'templatesD_Jan2025_210bins/templates_BpMass_138fbfb_rebinned1_stat0p2.root','READ')
fileB = ROOT.TFile.Open(f'templatesB_Jan2025_210bins/templates_BpMass_138fbfb.root','READ')
fileD = ROOT.TFile.Open(f'templatesD_Jan2025_210bins/templates_BpMass_138fbfb.root','READ')

outDir = 'MCB_MCD_comparsion_plots'
if not os.path.isdir(outDir):
    os.mkdir(outDir)

tagList = ['tagTjet', 'tagWjet', 'untagTlep', 'untagWlep']
majorList = ['ttbar', 'wjets', 'qcd', 'singletop']
for tag in tagList:
    histMajorB = ROOT.TH1D(f'hist_major_B_{tag}','',210,400,2500)
    histMajorD = ROOT.TH1D(f'hist_major_D_{tag}','',210,400,2500)
    for bkg in majorList:
        histB = fileB.Get(f'BpMass_138fbfb_isL_{tag}_B__{bkg}').Clone()
        histD = fileD.Get(f'BpMass_138fbfb_isL_{tag}_D__{bkg}').Clone()
        
        histMajorB.Add(histB)
        histMajorD.Add(histD)

    histMajorB.Scale(1/histMajorB.Integral())
    histMajorD.Scale(1/histMajorD.Integral())

    c1 = ROOT.TCanvas(f'c1_{tag}','')
    histMajorB.Draw()
    c1.SaveAs(f'{outDir}/histMajorMC_{tag}_B.png')

    c2 = ROOT.TCanvas(f'c2_{tag}','')
    histMajorD.Draw()
    c2.SaveAs(f'{outDir}/histMajorMC_{tag}_D.png')

    c3 = ROOT.TCanvas(f'c3_{tag}','')
    histMajorB.Divide(histMajorD)
    histMajorB.Draw()
    c3.SaveAs(f'{outDir}/histMajorMCRatio_{tag}_BvsD.png')
