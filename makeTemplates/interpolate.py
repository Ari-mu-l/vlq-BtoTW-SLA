import ROOT, os
ROOT.TH1.SetDefaultSumw2(True)
ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(1)

indir = "templatesD_Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST"
fileName = "templates_BpMass_ABCDnn_138fbfb_smoothedJJ_rebinned1_stat0p2_smoothedTV_smooth2DUncert_smoothedCorr.root"

os.makedirs(f"{indir}/plots_interpolate", exist_ok=True)

inFile = ROOT.TFile(f"{indir}/{fileName}","READ")
outFile =  ROOT.TFile(f"{indir}/{fileName.replace('.root','_interpolate.root')}","RECREATE")
nomHists = []
systHists = []

for key in inFile.GetListOfKeys():
    histName = key.GetName()
    outFile.cd()
    hist = inFile.Get(histName)
    hist.Write()
    
    if 'BpM800' in histName:
        if len(histName.split('__'))==2:
            nomHists.append(histName)
        else:
            systHists.append(histName)
            
for histName in nomHists+systHists:
    hist800 = inFile.Get(histName)
    hist1000 = inFile.Get(histName.replace('800','1000'))
    hist1200 = inFile.Get(histName.replace('800','1200'))

    hist900 = hist800.Clone(histName.replace('800','900'))
    hist900.Add(hist1000)
    hist900.Scale(0.5)

    hist1100 = hist1000.Clone(histName.replace('800','1100'))
    hist1100.Add(hist1200)
    hist1100.Scale(0.5)
    
    outFile.cd()
    hist900.Write()
    hist1100.Write()

print(f"Created {outFile.GetName()}")

tagList = ["tagTjet","tagWjet","untagTlep","untagWlep"]
for tag in tagList:
    c1 = ROOT.TCanvas(f"c1_{tag}",f"c1_{tag}",1200,1000)

    #BpMass_ABCDnn_138fbfb_isL_tagTjet_D__BpM1100
    hist800 = outFile.Get(nomHists[0].replace('tagTjet',tag))
    hist900 = outFile.Get(nomHists[0].replace('tagTjet',tag).replace('800','900'))
    hist1000 = outFile.Get(nomHists[0].replace('tagTjet',tag).replace('800','1000'))
    hist1100 = outFile.Get(nomHists[0].replace('tagTjet',tag).replace('800','1100'))
    hist1200 = outFile.Get(nomHists[0].replace('tagTjet',tag).replace('800','1200'))

    hist800.Scale(1/hist800.Integral())
    hist900.Scale(1/hist900.Integral())
    hist1000.Scale(1/hist1000.Integral())
    hist1100.Scale(1/hist1100.Integral())
    hist1200.Scale(1/hist1200.Integral())
    
    hist800.SetLineColor(2)
    hist900.SetLineColor(3)
    hist1000.SetLineColor(4)
    hist1100.SetLineColor(6)
    hist1200.SetLineColor(43)
    
    hist800.Draw("HIST")
    hist900.Draw("HIST SAME")
    hist1000.Draw("HIST SAME")
    hist1100.Draw("HIST SAME")
    hist1200.Draw("HIST SAME")

    legend = ROOT.TLegend(0.47,0.62,0.92,0.89)
    legend.AddEntry(hist800, "BpM800", "l")
    legend.AddEntry(hist900, "BpM900", "l")
    legend.AddEntry(hist1000, "BpM1000", "l")
    legend.AddEntry(hist1100, "BpM1100", "l")
    legend.AddEntry(hist1200, "BpM1200", "l")
    legend.Draw()

    c1.SaveAs(f"{indir}/plots_interpolate/interploate_{tag}.png")

inFile.Close()
outFile.Close()
