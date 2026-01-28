import ROOT, os, sys, json
import numpy as np
import matplotlib.pyplot as plt
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

tagList = ['tagTjet', 'tagWjet', 'untagTlep', 'untagWlep']
for tag in tagList:
   os.makedirs(f"{indir}/plots_fit/{tag}", exist_ok=True)

inFile = ROOT.TFile(f"{indir}/{fileName}","READ")
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

def getFit(tag, massList):
    
    #nomHists = []
    #systHists = []
    histLists = []
    for key in inFile.GetListOfKeys():
        histName = key.GetName()
        outFile.cd()
        hist = inFile.Get(histName)
        hist.Write()

        if ('BpM800' in histName) and (tag in histName):
            histLists.append(histName)
            #if len(histName.split('__'))==2:
            #    nomHists.append(histName)
            #else:
            #    systHists.append(histName)

    #print(nomHists[0].split('_')[4]) # tag
    #print(systHists[0].split('__')[-1]) # syst

    nomParams = {}
    systParams = {}
    #massList = [800,1000,1200,1300,1400]
    #for histName in nomHists:
    for histName in histLists:

        if len(histName.split('__'))==2: # nom
            syst = "nom"
        else:
            syst = histName.split('__')[-1]

        subdir = f"{indir}/plots_fit/{histName.split('_')[4]}/{syst}"
        os.makedirs(subdir, exist_ok=True)

        interpolateParams = {}

        for mass in massList:
            nomParams[f'{mass}'] = [0,0,0,0,0,0,0]

            hist = inFile.Get(histName.replace('800',str(mass)))
            hist.Scale(1/hist.Integral())

            #peak = hist.GetBinCenter(hist.GetMaximumBin())

            if "jet" in tag:
                cb = ROOT.TF1("cb",ROOT.DoubleSidedCB,400,2490,npar=7)
                cb.SetParameters(0.05,mass,100,1,1,1,1)
            elif tag=="untagTlep": # TEMP: decision not finalized
                if mass==1000:
                    cb = ROOT.TF1("cb",ROOT.DoubleSidedCB,450,2490,npar=7)
                else:
                    cb = ROOT.TF1("cb",ROOT.DoubleSidedCB,400,2490,npar=7)
                cb.SetParameters(0.05,mass,100,2,2,5,2)
            elif tag=="untagWlep":
                if mass==800:
                    cb = ROOT.TF1("cb",ROOT.DoubleSidedCB,400,2490,npar=7)
                else:
                    cb = ROOT.TF1("cb",ROOT.DoubleSidedCB,500,2490,npar=7)
                cb.SetParameters(hist.GetMaximum(),mass,100,1,100,1,1)


            #cb.SetParameters(0.05,peak,100,1,1,1,1)
            #cb.SetParameters(0.05,mass,100,1,1,1,1) 
            #cb.SetParameters(0.05,mass,100,2,2,5,2) # untagTlep
            #cb.SetParameters(hist.GetMaximum(),mass,100,2,2,5,2)
            #cb.SetParameters(hist.GetMaximum(),mass,100,1,100,1,1) # untagWlep
            #cb.SetParameters(hist.GetMaximum(),peak,100,1,100,1,1)
            #cb.SetParLimits(0,hist.GetMaximum()*0.95,hist.GetMaximum()*1.05)
            #cb.SetParLimits(1,peak*0.9,peak*1.1)

            # if mass==1800:
            #     cb.SetParameters(0.05,mass,100,1,1,5,2)
            # else:
            #     cb.SetParameters(0.05,mass,100,1,1,1,1)

            #cb = ROOT.TF1("cb","crystalball",400,2400)
            #cb.SetParameters(0.05,mass,100,0.5,1)
            #cb = ROOT.TF1("cb","gaus",400,2500)
            #cb.SetParameters(0.05,mass,100)
            #cb.FixParameter(0,peak[mass])

            fit = hist.Fit("cb","RS")

            for i in range(7): # save fit parameters
                nomParams[f'{mass}'][i] = fit.Parameter(i)        

            c1 = ROOT.TCanvas(f"c1_{histName}",f"c1_{histName}",1200,1000)
            hist.Draw()

            c1.SaveAs(f"{subdir}/{histName.replace('800',str(mass))}_fit.png")

        for i in range(7): # plot param vs mass
            masses = np.array(massList)/1000
            param_i = np.zeros(len(massList))
            for j_mass in range(len(massList)):
                param_i[j_mass] = nomParams[f'{massList[j_mass]}'][i]

            fit = np.polyfit(masses,param_i,1) # tried order 3
            if ("jet" in tag) and (i==5):
                interpolateParams[f'p{i}'] = [0, np.average(param_i)] # take avg and fit as a const
            else:
                interpolateParams[f'p{i}'] = [fit[0],fit[1]]
            #print(f'p{i}: {fit}')

            plt.figure()
            plt.plot(masses, param_i, 'o', label=f'best fit $p_{i}$')
            plt.plot(masses, masses*fit[0] + fit[1], label= f'{fit[0]:.3f}' +' * $m_{B}$ + '+ f'{fit[1]:.3f}')
            plt.legend()
            plt.xlabel("$m_{B}$ [TeV]")
            plt.ylabel(f"$p_{i}$")
            plt.savefig(f"{subdir}/p{i}.png")
            plt.close()


        print(f"Plot saved to {indir}/plots_fit/")

        json_obj = json.dumps(interpolateParams, indent=4)
        with open(f"{subdir}/interpolate_params.json","w") as outjson:
            outjson.write(json_obj)

getFit("tagTjet", [800,1000,1200,1300,1400])
getFit("tagWjet", [800,1000,1200,1300,1400,1500])
getFit("untagTlep", [800,1000,1200,1400])
getFit("untagWlep", [800,1000,1200,1300,1400])
inFile.Close()
outFile.Close()

