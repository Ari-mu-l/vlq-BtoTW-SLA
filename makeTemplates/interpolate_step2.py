import ROOT, os, sys, json
import numpy as np
ROOT.TH1.SetDefaultSumw2(True)
ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(1)

indir = "templatesD_Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST"

os.makedirs(f"{indir}/plots_interpolate", exist_ok=True)

tagList = ['tagTjet', 'tagWjet', 'untagTlep', 'untagWlep']
for tag in tagList:
   os.makedirs(f"{indir}/plots_interpolate/{tag}", exist_ok=True)

fileName = "templates_BpMass_ABCDnn_138fbfb_smoothedJJ.root"
outFile =  ROOT.TFile(f"{indir}/{fileName.replace('.root','_interpolate.root')}","RECREATE")

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

def saveOriginalHists():
   inFile = ROOT.TFile(f"{indir}/{fileName}","READ")
   for key in inFile.GetListOfKeys():
        histName = key.GetName()
        outFile.cd()
        hist = inFile.Get(histName)
        hist.Write()
   print(f"Created {outFile.GetName()}")



def interpolate(tag, mass):
    paramDir = f"{indir}/plots_fit/{tag}"
    systList = []
    for entry in os.scandir(paramDir):
        if entry.is_dir():
            systList.append(entry.name) # include nom

    for systName in systList:
        subdir = f"{indir}/plots_fit/{tag}/{systName}"
        with open(f"{subdir}/fit_params.json", "r") as infile:
            fitParams = json.load(infile)
        with open(f"{subdir}/hist_params.json", "r") as infile:
            histParams = json.load(infile)

        cb = ROOT.TF1("cb",ROOT.DoubleSidedCB,400,2490,npar=7)
        # linear interpolation for height, peak location, width
        #cb.SetParameter(0,fitParams['p0'][0]*(mass/1000)+fitParams['p0'][1])
        #cb.SetParameter(1,fitParams['p1'][0]*(mass/1000)+fitParams['p1'][1])
        #cb.SetParameter(2,fitParams['p2'][0]*(mass/1000)+fitParams['p2'][1])

        # print(fitParams['p0'][0]*(mass/1000)+fitParams['p0'][1])
        # print(fitParams['p1'][0]*(mass/1000)+fitParams['p1'][1])
        # print(fitParams['p2'][0]*(mass/1000)+fitParams['p2'][1])
        # print(fitParams['p2'])
        # print(histParams['800'][2], histParams['1000'][2])

        # param 3-6: tail shape
        # param 7: last bin
        # interpolate with average between two adjacent points

        print(f'Interpolating {mass} GeV using {mass-100} GeV and {mass+100} GeV')
        histParams_lowM = np.array(histParams[f'{mass-100}'])
        histParams_highM = np.array(histParams[f'{mass+100}'])
        histParams_new = (histParams_lowM + histParams_highM)/2
        for iparam in range(7): # 7 params for dscb
        cb.SetParameter(i,histParams_new[i])

        # Generate histogram from the function
        # BpMass_ABCDnn_138fbfb_isL_untagWlep_D__BpM1800__jer2018Up
        if systName=='nom':
           histName = f'BpMass_ABCDnn_138fbfb_isL_{tag}_D__BpM{mass}'
        else:
           histName = f'BpMass_ABCDnn_138fbfb_isL_{tag}_D__BpM{mass}__{systName}'
        histOut = ROOT.TH1D(histName, histName, 210, 400, 2500)
        histOut.FillRandom("cb", 10000)

        # add last bin
        # bulk yield: x, last bin yield: y
        # y/(x+y) = p7 (p7 is the percentage of events in the last bin)
        # y' = (p7/(1-p7)) * x'
        # here x' = 10000, because generated 10000 from the function
        histOut.SetBinContent(210, histParams_new[7]*10000/(1-histParams_new[7]))

        # Bin error: sqrt(N)
        for i in range(1,211):
           histOut.SetBinError(i, np.sqrt(histOut.GetBinContent(i)))

        # Scale to lumi*1pb/Ngen to be consistent with the MC signals
        # 1.0/0.5 is done in the next step (modifyBinning) along with MC signals
        histOut.Scale(138/histOut.Integral())
        
        c1 = ROOT.TCanvas(f"c1_{histName}",f"c1_{histName}",1200,1000)
        histOut.Scale(1/histOut.Integral())
        histOut.Draw()
        cb.Draw("SAME")
        c1.SaveAs(f"{indir}/plots_interpolate/{tag}/{histName}.png")
            

#saveOriginalHists()
interpolate('tagTjet', 900)


