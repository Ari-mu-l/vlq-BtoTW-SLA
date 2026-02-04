import ROOT, os, sys, json
import numpy as np
ROOT.TH1.SetDefaultSumw2(True)
ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(1)

# b-associated
indir = "templatesD_Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST"
# t-associated
#indir = "templatesD_Jan2025BprimeT"

os.makedirs(f"{indir}/plots_interpolate", exist_ok=True)

tagList = ['tagTjet', 'tagWjet', 'untagTlep', 'untagWlep']
for tag in tagList:
   os.makedirs(f"{indir}/plots_interpolate/{tag}", exist_ok=True)
   #os.makedirs(f"{indir}/plots_interpolate/{tag}/shifts", exist_ok=True)

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
   inFile.Close()
   print(f"Created {outFile.GetName()}")

def interpolateFitFunc(tag, systName, mass):
   subdir = f"{indir}/plots_fit/{tag}/{systName}"
   with open(f"{subdir}/fit_params.json", "r") as infile:
      fitParams = json.load(infile)
   with open(f"{subdir}/hist_params.json", "r") as infile:
      histParams = json.load(infile)
      
   cb = ROOT.TF1(f'cb_{tag}_{systName}',ROOT.DoubleSidedCB,400,2490,npar=7)
   
   #print(f'Interpolating {mass} GeV using {mass-100} GeV and {mass+100} GeV')
   histParams_lowM = np.array(histParams[f'{mass-100}'])
   histParams_highM = np.array(histParams[f'{mass+100}'])
   histParams_new = (histParams_lowM + histParams_highM)/2
                 
   cb.SetParameters(histParams_new[:7])

   return cb, histParams_new

def getBinCenters(tag): # for varied binnings. Not used in this current implementation
   inFile = ROOT.TFile(f"{indir}/{fileName}","READ")
   hist = inFile.Get(f'BpMass_ABCDnn_138fbfb_isL_{tag}_D__BpM800')
   binCenterList = [0]*210
   for i in range(210):
      binCenterList[i] = hist.GetBinCenter(i+1)
   inFile.Close()
   return binCenterList
   
def getSystShifts(tag, systName, mass, cb_nom):
   # Defining ratio=sys/nom didn't work as epected
   # Get sys/nom for each bin center from 2 dscb's
   cb_sys,_ = interpolateFitFunc(tag, systName, mass)
   #cb_nom,_ = interpolateFitFunc(tag, 'nom', mass)

   hist_shift = ROOT.TH1D(f'{systName}_shift_{mass}', '', 210, 400, 2500)
   for i in range(1,211):
      value_sys = cb_sys.Eval(hist_shift.GetBinCenter(i))
      value_nom = cb_nom.Eval(hist_shift.GetBinCenter(i))
      if value_nom==0:
         hist_shift.SetBinContent(i,value_sys/1e-10)
      else:
         hist_shift.SetBinContent(i,value_sys/value_nom)
      hist_shift.SetBinError(i,0)

   return hist_shift

#binCenterLists = getBinCenters('tagTjet')
def interpolate(tag, mass):
    cb_nom, histParams_nom = interpolateFitFunc(tag, 'nom', mass)
   
    histName = f'BpMass_ABCDnn_138fbfb_isL_{tag}_D__BpM{mass}'
    histOutNom = ROOT.TH1D(histName, '', 210, 400, 2500)
    histOutNom.FillRandom(f'cb_{tag}_nom',100000)
    histOutNom.SetBinContent(210, histParams_nom[7]*100000/(1-histParams_nom[7]))
   
    yields = histParams_nom[8] # interpolate yields with adjacent points
    Nselect = yields/histParams_nom[9] # param9 is the approximate weight factor
    factor = histParams_nom[9]

    histOutNom_nom1 = histOutNom.Clone(f'{histName}_norm1')
    histOutNom_nom1.Scale(1/histOutNom_nom1.Integral())
    for i in range(1,211):
       if histOutNom_nom1.GetBinContent(i)==0:
          histOutNom_nom1.SetBinContent(i,1e-10)
          
    histOutNom.Scale(yields/histOutNom.Integral())
    histStatNom = histOutNom.Clone(f'{histName}_stat')
    histStatNom.Scale(Nselect/histStatNom.Integral())

    for ibin in range(1,211): # loop over bins
        histOutNom.SetBinError(ibin, np.sqrt(histStatNom.GetBinContent(ibin))*factor)

    outFile.cd()
    histOutNom.Write()

    c_nom = ROOT.TCanvas(f"c1_{histName}",f"c1_{histName}",1200,1000)
    histOutNom.Draw("HIST E")
    c_nom.SaveAs(f"{indir}/plots_interpolate/{tag}/{histName}.png")

    # Get list of systematics
    systList = []
    pdfList = []
    for entry in os.scandir(f"{indir}/plots_fit/{tag}"):
        if (entry.name!="nom") and (entry.is_dir()):
            if "Up" in entry.name:
               systList.append(entry.name[:-2])
            elif "pdf" in entry.name:
               pdfList.append(entry.name) # no Up/Down for pdf

    for pdf in pdfList:
       histShift = getSystShifts(tag, pdf, mass, cb_nom)
       histOutSys = histOutNom_nom1.Clone(f'{histName}__{pdf}')
       
       histOutSys.Multiply(histShift)

       for i in range(1,211):
           if histOutSys.GetBinContent(i)<0:
              histOutSys.SetBinContent(i,0)

       subdir = f"{indir}/plots_fit/{tag}/{pdf}"
       with open(f"{subdir}/hist_params.json", "r") as infile:
           histParams = json.load(infile)
           yields = (histParams[f'{mass-100}'][8]+histParams[f'{mass+100}'][8])/2

       histOutSys.Scale(yields/histOutSys.Integral())

       outFile.cd()
       histOutSys.Write()
       
    for systName in systList:
        histShiftUp = getSystShifts(tag, f'{systName}Up', mass, cb_nom)
        histShiftDown = getSystShifts(tag, f'{systName}Down', mass, cb_nom)
        mirror = ''
        for i in range(1,211): # if the difference between up and down too big, might be artificial
           if (histShiftDown.GetBinContent(i)-1)!=0:
              ratio = (histShiftUp.GetBinContent(i)-1)/(histShiftDown.GetBinContent(i)-1)
              if abs(ratio)>10: # mirror the smaller one
                 mirror = 'Down'
                 break
              elif abs(1/ratio)>10:
                 mirror = 'Up'
                 break
              elif ratio>0: # avoid same-sided up and down
                 mirror = 'Up'
                 break
        print(f'Processing {systName}')
        histShiftDownApply = histShiftDown.Clone(f'{systName}DownApply')
        histShiftUpApply = histShiftUp.Clone(f'{systName}UpApply')
        if mirror=='Down':
           for i in range(1,211):
              percentageShift = 1-histShiftDown.GetBinContent(i)
              factorShift = 1+percentageShift
              histShiftUpApply.SetBinContent(i,factorShift)
        elif mirror=='Up':
           for i in range(1,211):
              percentageShift = histShiftUp.GetBinContent(i)-1
              factorShift = 1-percentageShift
              histShiftDownApply.SetBinContent(i,factorShift)
      
        histOutSysUp = histOutNom_nom1.Clone(f'{histName}__{systName}Up')
        histOutSysDown = histOutNom_nom1.Clone(f'{histName}__{systName}Down')
     
        histOutSysUp.Multiply(histShiftUpApply)
        histOutSysDown.Multiply(histShiftDownApply)

        for i in range(1,211):
           if histOutSysUp.GetBinContent(i)<0:
              histOutSysUp.SetBinContent(i,0)
           if histOutSysDown.GetBinContent(i)<0:
              histOutSysDown.SetBinContent(i,0)

        subdir = f"{indir}/plots_fit/{tag}/{systName}"
        with open(f"{subdir}Up/hist_params.json", "r") as infile:
            histParamsUp = json.load(infile)
            yieldsUp = (histParamsUp[f'{mass-100}'][8]+histParamsUp[f'{mass+100}'][8])/2
        with open(f"{subdir}Down/hist_params.json", "r") as infile:
            histParamsDown = json.load(infile)
            yieldsDown = (histParamsDown[f'{mass-100}'][8]+histParamsDown[f'{mass+100}'][8])/2 # systematics might become a problem. Check

        
        histOutSysUp.Scale(yieldsUp/histOutSysUp.Integral()) # TEST: adjust syst yields
        histOutSysDown.Scale(yieldsDown/histOutSysDown.Integral())
     
        outFile.cd()
        histOutSysUp.Write()
        histOutSysDown.Write()

saveOriginalHists()
interpolate('tagTjet', 900)
interpolate('tagWjet', 900)
interpolate('untagTlep', 900)
interpolate('untagWlep', 900)

interpolate('tagTjet', 1100)
interpolate('tagWjet', 1100)
interpolate('untagTlep', 1100)
interpolate('untagWlep', 1100)

outFile.Close()
#################################################################################
# Deprecated method: Sample histograms from fit functions for both nom and syst #
#################################################################################
# def createHistogramFromFit(tag, systName, mass):
#         subdir = f"{indir}/plots_fit/{tag}/{systName}"
#         with open(f"{subdir}/fit_params.json", "r") as infile:
#             fitParams = json.load(infile)
#         with open(f"{subdir}/hist_params.json", "r") as infile:
#             histParams = json.load(infile)

#         cb = ROOT.TF1("cb",ROOT.DoubleSidedCB,400,2490,npar=7)
#         # linear interpolation for height, peak location, width
#         #cb.SetParameter(0,fitParams['p0'][0]*(mass/1000)+fitParams['p0'][1])
#         #cb.SetParameter(1,fitParams['p1'][0]*(mass/1000)+fitParams['p1'][1])
#         #cb.SetParameter(2,fitParams['p2'][0]*(mass/1000)+fitParams['p2'][1])

#         # print(fitParams['p0'][0]*(mass/1000)+fitParams['p0'][1])
#         # print(fitParams['p1'][0]*(mass/1000)+fitParams['p1'][1])
#         # print(fitParams['p2'][0]*(mass/1000)+fitParams['p2'][1])
#         # print(fitParams['p2'])
#         # print(histParams['800'][2], histParams['1000'][2])

#         # param 3-6: tail shape
#         # param 7: last bin
#         # interpolate with average between two adjacent points

#         print(f'Interpolating {mass} GeV using {mass-100} GeV and {mass+100} GeV')
#         histParams_lowM = np.array(histParams[f'{mass-100}'])
#         histParams_highM = np.array(histParams[f'{mass+100}'])
#         histParams_new = (histParams_lowM + histParams_highM)/2
#         for iparam in range(7): # 7 params for dscb
#             cb.SetParameter(iparam,histParams_new[iparam])

#         # Generate histogram from the function
#         # BpMass_ABCDnn_138fbfb_isL_untagWlep_D__BpM1800__jer2018Up
#         if systName=='nom':
#            histName = f'BpMass_ABCDnn_138fbfb_isL_{tag}_D__BpM{mass}'
#         else:
#            histName = f'BpMass_ABCDnn_138fbfb_isL_{tag}_D__BpM{mass}__{systName}'
#         histOut = ROOT.TH1D(f'{histName}_interpolate', histName, 210, 400, 2500)
#         histOut.FillRandom("cb", 50000)

#         # add last bin
#         # bulk yield: x, last bin yield: y
#         # y/(x+y) = p7 (p7 is the percentage of events in the last bin)
#         # y' = (p7/(1-p7)) * x'
#         # here x' = 10000, because generated 10000 from the function
#         histOut.SetBinContent(210, histParams_new[7]*50000/(1-histParams_new[7]))

#         # normalize to 1
#         histOut.Scale(1/histOut.Integral())

#         return histOut

     
# def interpolate(tag, mass):
#     paramDir = f"{indir}/plots_fit/{tag}"
#     systList = []
#     for entry in os.scandir(paramDir):
#         if (entry.name!="nom") and (entry.is_dir()):
#             systList.append(entry.name)

#     hist_nom = createHistogramFromFit(tag,"nom",mass)

#     # normalize nom to the correct yield
#     subdir = f"{indir}/plots_fit/{tag}/nom"
#     with open(f"{subdir}/hist_params.json", "r") as infile:
#         histParams = json.load(infile)
        
#     yields = (histParams[f'{mass-100}'][8] + histParams[f'{mass+100}'][8])/2 # interpolate yields with adjacent points
#     Ngen = yields/((histParams[f'{mass-100}'][9] + histParams[f'{mass+100}'][9])/2) # param9 is N_selected / N_gen. Interpolate this ratio to get interpolated Ngen to set stat err
#     factor = (histParams[f'{mass-100}'][10] + histParams[f'{mass+100}'][10])/2
    
#     histOutName = hist_nom.GetName().replace('_interpolate','')
#     hist_nom_out = hist_nom.Clone(histOutName)
#     #hist_nom_out.SetTitle(histOutName)
#     hist_nom_out.SetTitle('')
#     hist_nom_stat = hist_nom.Clone(f'{histOutName}_stat') # used to get statistical error
#     hist_nom_out.Scale(yields)
#     hist_nom_stat.Scale(Ngen)

#     for ibin in range(1,211): # loop over bins
#         hist_nom_out.SetBinError(ibin, np.sqrt(hist_nom_stat.GetBinContent(ibin))*factor)

#     outFile.cd()
#     hist_nom_out.Write()

#     # TEMP: comment out for debug
#     #c_nom = ROOT.TCanvas(f"c1_{histOutName}",f"c1_{histOutName}",1200,1000)
#     #hist_nom_out.Draw("HIST E")
#     #c_nom.SaveAs(f"{indir}/plots_interpolate/{tag}/{histOutName}.png")
            
#     for systName in systList:
#         hist_sys = createHistogramFromFit(tag,systName,mass)
#         hist_shift = hist_sys.Clone(f'{systName}_shift')
        
#         hist_shift.Add(hist_nom, -1)
#         hist_shift.Divide(hist_nom)

#         for ibin in range(1,211):
#            hist_shift.SetBinContent(ibin, 1+hist_shift.GetBinContent(ibin)) # make it into a SF
#            hist_shift.SetBinError(ibin, 0)

#         systOutName = f"{histOutName}__{systName}"
#         hist_syst_out = hist_nom_out.Clone(systOutName)
#         hist_syst_out.SetTitle('')
#         #hist_syst_out.SetTitle(systOutName)
        
#         hist_syst_out.Multiply(hist_shift)

#         outFile.cd()
#         hist_syst_out.Write()
        
#         c_syst = ROOT.TCanvas(f"c1_{systOutName}",f"c1_{systOutName}",1200,1000)
#         hist_syst_out.Draw()
#         c_syst.SaveAs(f"{indir}/plots_interpolate/{tag}/{systOutName}.png")
        
#         #histOut.Scale(1/histOut.Integral())
#         #histOut.Draw()
#         #cb.Draw("SAME")
#         #c_syst.SaveAs(f"{indir}/plots_interpolate/{tag}/{histName}.png")
            

# saveOriginalHists()
# interpolate('tagTjet', 900)
# interpolate('tagWjet', 900)
# interpolate('untagTlep', 900)
# interpolate('untagWlep', 900)

# interpolate('tagTjet', 1100)
# interpolate('tagWjet', 1100)
# interpolate('untagTlep', 1100)
# interpolate('untagWlep', 1100)

