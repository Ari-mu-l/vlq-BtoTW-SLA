import ROOT, os, sys, json
import numpy as np
import matplotlib.pyplot as plt
ROOT.TH1.SetDefaultSumw2(True)
ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(1)

parent = os.path.dirname(os.getcwd())
sys.path.append(parent)
from samples import samples_signal # TEMP: for Bbj only. samples_signalT for Btj

indir = "templatesD_Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST"
fileName = "templates_BpMass_ABCDnn_138fbfb_smoothedJJ.root"
#fileName = "templates_BpMass_ABCDnn_138fbfb_smoothedJJ_rebinned1_stat0p2_smoothedTV_smooth2DUncert_smoothedCorr.root"

#os.makedirs(f"{indir}/plots_interpolate", exist_ok=True)
os.makedirs(f"{indir}/plots_fit", exist_ok=True)

tagList = ['tagTjet', 'tagWjet', 'untagTlep', 'untagWlep']
for tag in tagList:
   os.makedirs(f"{indir}/plots_fit/{tag}", exist_ok=True)

inFile = ROOT.TFile(f"{indir}/{fileName}","READ")
#outFile =  ROOT.TFile(f"{indir}/{fileName.replace('.root','_interpolate.root')}","RECREATE")

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
    
    nomHists = []
    systHists = []
    for key in inFile.GetListOfKeys():
        histName = key.GetName()
        #outFile.cd()
        hist = inFile.Get(histName)
        #hist.Write()

        if ('BpM800' in histName) and (tag in histName):
            if len(histName.split('__'))==2:
                nomHists.append(histName)
            else:
                systHists.append(histName)

    #print(nomHists[0].split('_')[4]) # tag
    #print(systHists[0].split('__')[-1]) # syst

    histParams = {}
    #for histName in nomHists:
    for histName in nomHists+systHists:

        if len(histName.split('__'))==2: # nom
            syst = "nom"
        else:
            syst = histName.split('__')[-1]

        subdir = f"{indir}/plots_fit/{histName.split('_')[4]}/{syst}"
        os.makedirs(subdir, exist_ok=True)

        interpolateParams = {}

        for mass in massList:
            histParams[f'{mass}'] = [0,0,0,0,0,0,0,0,0,0,0] # 7 parameters + last bin + yields + N_select/N_gen

            hist = inFile.Get(histName.replace('800',str(mass)))
            if syst == "nom":
               histParams[f'{mass}'][8] = hist.Integral()
               nrun = samples_signal[f'Bprime_M{mass}_2016APV'].nrun + samples_signal[f'Bprime_M{mass}_2016'].nrun + samples_signal[f'Bprime_M{mass}_2017'].nrun + samples_signal[f'Bprime_M{mass}_2018'].nrun
               histParams[f'{mass}'][9] = hist.GetEntries()/nrun
               histParams[f'{mass}'][10] = hist.Integral()/hist.GetEntries()

               # two different ways of estimating the overall scaling.
               # bin-by-bin scaling for two bins
               # all these values are close to each other

               # nEntries = 0
               # for i in range(1,211):
               #     nEntries+=hist.GetBinError(i)**2
               # print(np.sqrt(nEntries/hist.GetEntries()))
               # print(hist.Integral()/hist.GetEntries())
               # print(hist.GetBinContent(50), hist.GetBinError(50)**2, (hist.GetBinError(50)**2)/hist.GetBinContent(50)) #(hist.GetBinError(50)**2)*(nEntries/hist.GetEntries()))
               # print(hist.GetBinContent(10), hist.GetBinError(10)**2, (hist.GetBinError(10)**2)/hist.GetBinContent(10))
               
            hist.Scale(1/hist.Integral())

            #cb = ROOT.TF1("cb",ROOT.DoubleSidedCB,npar=7)
            #cb.SetParameters(0.05,mass,100,1,1,1,1)
            #fit = hist.Fit("cb",400,2490,"RS")

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
                cb.SetParameters(hist.GetMaximum(),mass,100,1,1,1,1)
                #cb.SetParameters(hist.GetMaximum(),mass,100,1,100,1,1) # not good for some systematics
                #cb.SetParLimits(0,hist.GetMaximum()*0.95,hist.GetMaximum()*1.05)

            #cb.SetParLimits(4,100,200)
            cb.SetParLimits(0,0,1)
            cb.SetParLimits(1,0,2000)
            cb.SetParLimits(2,0,400)
            cb.SetParLimits(3,0,5)
            cb.SetParLimits(4,0,200)
            cb.SetParLimits(5,0,5)
            cb.SetParLimits(6,0,20)
            

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
                histParams[f'{mass}'][i] = fit.Parameter(i)
            histParams[f'{mass}'][7] = hist.GetBinContent(210) # last bin content

            c1 = ROOT.TCanvas(f"c1_{histName}",f"c1_{histName}",1200,1000)
            hist.Draw()

            c1.SaveAs(f"{subdir}/{histName.replace('800',str(mass))}_fit.png")


        if syst=="nom":
           numPlots = 11 # get yield interpretation only for nom
        else:
           numPlots = 8
           
        for i in range(numPlots): # plot param vs mass + last bin
            masses = np.array(massList)/1000
            param_i = np.zeros(len(massList))
            for j_mass in range(len(massList)):
                param_i[j_mass] = histParams[f'{massList[j_mass]}'][i]

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

        json_obj_int = json.dumps(interpolateParams, indent=4)
        with open(f"{subdir}/fit_params.json","w") as outjson: # probably need to change a file name
            outjson.write(json_obj_int)

        json_obj_par = json.dumps(histParams, indent=4)
        with open(f"{subdir}/hist_params.json","w") as outjson:
            outjson.write(json_obj_par)

getFit("tagTjet", [800,1000,1200,1300,1400])
getFit("tagWjet", [800,1000,1200,1300,1400,1500])
getFit("untagTlep", [800,1000,1300,1400])
getFit("untagWlep", [800,1000,1200,1300,1400])

###############################################
# Study the effect of parameters on the shape #
###############################################
# idea: choose one histogram and vary the tail parameter
# overlay the fit lines with the histogram
# Check Case3: untagTlep
#BpMass_ABCDnn_138fbfb_isL_untagTlep_D__BpM800

# subdir = f"{indir}/plots_fit/untagTlep/nom"
# histName = 'BpMass_ABCDnn_138fbfb_isL_untagTlep_D__BpM1300'

# with open(f"{subdir}/fit_params.json", "r") as infile:
#    fitParams = json.load(infile)

# hist = inFile.Get(histName)
# hist.Scale(1/hist.Integral())

# cb0 = ROOT.TF1("cb0",ROOT.DoubleSidedCB,400,2490,npar=7)
# cb1 = ROOT.TF1("cb1",ROOT.DoubleSidedCB,400,2490,npar=7)
# #cb2 = ROOT.TF1("cb2",ROOT.DoubleSidedCB,400,2490,npar=7)
# for i in range(7):
#    cb0.SetParameter(i,fitParams['1300'][i])

#    # check tail params
#    #if i==4:
#    #   cb1.SetParameter(i,110)
#    #elif i==5:
#    #   cb1.SetParameter(i,0.76)
#    #else:
#    #   cb1.SetParameter(i,fitParams['1300'][i]) # from the linear fit

#    # check width
#    if i==2:
#       cb1.SetParameter(i,115)
#    else:
#       cb1.SetParameter(i,fitParams['1300'][i])

# cb1.SetLineColor(ROOT.kBlue)

# c1 = ROOT.TCanvas(f"c1_{histName}",f"c1_{histName}",1200,1000)
# hist.Draw()
# cb0.Draw("SAME")
# cb1.Draw("SAME")

# c1.SaveAs(f"{subdir}/{histName}_fitComparison.png")


inFile.Close()
#outFile.Close()
