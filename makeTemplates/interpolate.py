import ROOT, os, sys
ROOT.TH1.SetDefaultSumw2(True)
ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(1)

parent = os.path.dirname(os.getcwd())
sys.path.append(parent)
from samples import systListFull

indir = "templatesD_Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST"
fileName = "templates_BpMass_ABCDnn_138fbfb_smoothedJJ.root"
#fileName = "templates_BpMass_ABCDnn_138fbfb_smoothedJJ_rebinned1_stat0p2_smoothedTV_smooth2DUncert_smoothedCorr.root"

os.makedirs(f"{indir}/plots_interpolate", exist_ok=True)
os.makedirs(f"{indir}/plots_fit", exist_ok=True)

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


ROOT.gInterpreter.Declare("""
Double_t DoubleSidedCB2(double x, double mu, double width, double a1, double p1, double a2, double p2)
{
  double u   = (x-mu)/width;
  double A1  = TMath::Power(p1/TMath::Abs(a1),p1)*TMath::Exp(-a1*a1/2);
  double A2  = TMath::Power(p2/TMath::Abs(a2),p2)*TMath::Exp(-a2*a2/2);
  double B1  = p1/TMath::Abs(a1) - TMath::Abs(a1);
  double B2  = p2/TMath::Abs(a2) - TMath::Abs(a2);

  double result(1);
  if      (u<-a1) result *= A1*TMath::Power(B1-u,-p1);
  else if (u<a2)  result *= TMath::Exp(-u*u/2);
  else            result *= A2*TMath::Power(B2+u,-p2);
  return result;
}


double DoubleSidedCB(double* x, double *par)
{
  return(par[0] * DoubleSidedCB2(x[0], par[1],par[2],par[3],par[4],par[5],par[6]));
}
""")

peak = {800:0.045, 1000:0.04, 1200:0.035}
#BpMass_ABCDnn_138fbfb_isL_tagTjet_D__BpM800__elRecoSFUp
#for hsitName in nomHists:
# tagList = ["tagTjet"]
# for tag in tagList:
#     for mass in [800]:
#         for syst in systListFull:
#             hist = hist.inFile.Get(f'BpMass_ABCDnn_138fbfb_isL_{tag}_D__BpM{mass}')
#             histUp = inFile.Get(f'BpMass_ABCDnn_138fbfb_isL_{tag}_D__BpM{mass}__{syst}Up')
#             histDn = inFile.Get(f'BpMass_ABCDnn_138fbfb_isL_{tag}_D__BpM{mass}__{syst}Down')

#             #hist.Scale(1/hist.Integral())
#             #histUp.Scale(1/histUp.Integral())
#             #histDn.Scale(1/histDn.Integral())

            
#             exit()

#for histName in nomHists:
for histName in systHists:
    for mass in [800]:
    #for mass in [800,1000,1200,1800]:
        if 'tagTjet' not in histName: continue
        hist = inFile.Get(histName.replace('800',str(mass)))
        hist.Scale(1/hist.Integral())

        cb = ROOT.TF1("cb",ROOT.DoubleSidedCB,400,2490,npar=7) # TEMP: change fit range if necessary
        #cb.SetParLimits(3,-500,500)
        #cb.SetParLimits(4,0,10)
        #cb.SetParLimits(5,-500,500)
        #cb.SetParLimits(6,0,10)
        if mass==1800:
            cb.SetParameters(0.05,mass,100,1,1,5,2)
        else:
            cb.SetParameters(0.05,mass,100,1,1,1,1)
        #cb.SetParameters(0.05,mass,100,1,1,1,1)
        #cb.FixParameter(0,0.044)
        #cb.SetParameters(0.05,mass,100,100,1,100,1)
        
        #cb = ROOT.TF1("cb","crystalball",400,2400)
        #cb.SetParameters(0.05,mass,100,100,2)
        #cb = ROOT.TF1("cb","gaus",400,2500)
        #cb.SetParameters(0.05,mass,100)
        #cb.FixParameter(0,peak[mass])
        hist.Fit("cb","R")

        c1 = ROOT.TCanvas(f"c1_{histName}",f"c1_{histName}",1200,1000)
        hist.Draw()
        #cb.Draw("SAME")

        c1.SaveAs(f"{indir}/plots_fit/{histName.replace('800',str(mass))}_fit.png")
        
print(f"Plot saved to {indir}/plots_fit/")

exit()
            
for histName in nomHists+systHists:
    hist800 = inFile.Get(histName)
    hist1000 = inFile.Get(histName.replace('800','1000'))
    hist1200 = inFile.Get(histName.replace('800','1200'))
    hist1300 = inFile.Get(histName.replace('800','1300'))

    hist800.Scale(1/hist800.Integral())
    hist1000.Scale(1/hist1000.Integral())
    hist1200.Scale(1/hist1200.Integral())
    hist1300.Scale(1/hist1300.Integral())

    #cb = ROOT.TF1("cb","crystalball",400,2400)
    #cb.SetParameters(0.045,800,100,100,2)
    #cb.FixParameter(0,0.045)
    cb = ROOT.TF1("cb","gaus",400,2500)
    cb.SetParameters(0.045,800,100)
    cb.FixParameter(0,0.045)
    
    hist800.Fit("cb","B")

    hist800.Draw()
    exit()

    # print('BpM1000')
    # cb = ROOT.TF1("cb","crystalball",400,2500)
    # cb.SetParameters(1,1,100,1000)
    # hist1000.Fit("cb","R")
    
    print('BpM1200')
    cb = ROOT.TF1("cb","crystalball",400,2500)
    cb.SetParameters(1,1,150,1200)
    hist1200.Fit("cb","R")

    print('BpM1300')
    cb = ROOT.TF1("cb","crystalball",400,2500)
    cb.SetParameters(1,1,150,1300)
    hist1300.Fit("cb","R")

    exit()

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
