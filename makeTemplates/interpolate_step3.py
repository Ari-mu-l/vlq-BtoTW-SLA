# make plots for sanity checks
import ROOT

ROOT.TH1.SetDefaultSumw2(True)
ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(1)

indir = "templatesD_Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST"
fileName = "templates_BpMass_ABCDnn_138fbfb_smoothedJJ_interpolate.root"
tFile = ROOT.TFile(f"{indir}/{fileName}", "READ")

#BpMass_ABCDnn_138fbfb_isL_untagWlep_D__BpM1100__jer2016Up
# plot nominal for various mass points
for tag in ['tagTjet', 'tagWjet', 'untagTlep', 'untagWlep']:

    c1 = ROOT.TCanvas(f'c1_{tag}',f'c1_{tag}',1200,1000)
    
    hist800 = tFile.Get(f'BpMass_ABCDnn_138fbfb_isL_{tag}_D__BpM800')
    hist900 = tFile.Get(f'BpMass_ABCDnn_138fbfb_isL_{tag}_D__BpM900')
    hist1000 = tFile.Get(f'BpMass_ABCDnn_138fbfb_isL_{tag}_D__BpM1000')
    hist1100 = tFile.Get(f'BpMass_ABCDnn_138fbfb_isL_{tag}_D__BpM1100')
    hist1200 = tFile.Get(f'BpMass_ABCDnn_138fbfb_isL_{tag}_D__BpM1200')

    hist800.Scale(1/hist800.Integral())
    hist900.Scale(1/hist900.Integral())
    hist1000.Scale(1/hist1000.Integral())
    hist1100.Scale(1/hist1100.Integral())
    hist1200.Scale(1/hist1200.Integral())

    hist800.SetLineColor(1)
    hist900.SetLineColor(2)
    hist1000.SetLineColor(3)
    hist1100.SetLineColor(4)
    hist1200.SetLineColor(6)
    
    hist800.Draw("HIST")
    hist900.Draw("HIST SAME")
    hist1000.Draw("HIST SAME")
    hist1100.Draw("HIST SAME")
    hist1200.Draw("HIST SAME")

    legend = ROOT.TLegend(0.6, 0.7, 0.89, 0.89)
    legend.AddEntry(hist800, "BpM800")
    legend.AddEntry(hist900, "BpM900")
    legend.AddEntry(hist1000, "BpM1000")
    legend.AddEntry(hist1100, "BpM1100")
    legend.AddEntry(hist1200, "BpM1200")
    legend.Draw()

    hist800.GetXaxis().SetTitle('B quark mass [GeV]')

    c1.SaveAs(f'{indir}/plots_interpolate/interpolate_{tag}.png')
