import os, sys
from ROOT import TFile, TH2D, TAxis, TCanvas, TPaletteAxis, gPad, gStyle, gROOT

gROOT.SetBatch(1)
limitdir = sys.argv[1]
mass = sys.argv[2]

path = limitdir+'/cmb/'+mass
name = limitdir.replace('limits_templatesABCDnn_V2_Jan2025_','').replace('limits_templatesABCDnn_DV2_Jan2025_','').replace('limits_templatesABCDnn_ABCV2V2_Jan2025_','')

os.chdir(path)

#if not os.path.exists('covariance_fit_b.png'):
if not os.path.exists('initialFitWorkspace.root') and not os.path.exists('morphedWorkspace.root'):
    print("Running FitDiagnostics with plots")
    os.system('combine -M FitDiagnostics -d workspace.root --saveWorkspace --plots --saveShapes')

fd = TFile.Open("fitDiagnosticsTest.root")
covar = fd.Get("covariance_fit_s");

covar.GetXaxis().SetRange(1,54) ## check me! 82
covar.LabelsOption("v","X")
covar.GetYaxis().SetRange(covar.GetNbinsY()-53,covar.GetNbinsY()) ## check me! 81
covar.SetMarkerSize(0.5)
covar.GetYaxis().SetLabelSize(0.03)
covar.GetZaxis().SetLabelSize(0.03)

c1 = TCanvas("c1","c1",1900,1000)
gStyle.SetOptStat(0)
gStyle.SetPaintTextFormat("%1.2f")
gStyle.SetPaintTextFormat("1.2f")
gPad.SetBottomMargin(0.22)
gPad.SetRightMargin(0.07)
gPad.SetLeftMargin(0.10)
palette = covar.GetListOfFunctions().FindObject("palette")
palette.SetX1NDC(0.94)
palette.SetX2NDC(0.96)
palette.SetY1NDC(0.22)
palette.SetY2NDC(0.9)

covar.Draw("colz text")

c1.SaveAs(name+'_covariance_s.png')
c1.SaveAs(name+'_covariance_s.pdf')

covar = fd.Get("covariance_fit_b")
covar.GetXaxis().SetRange(1,54) ## check me! 82
covar.LabelsOption("v","X")
covar.GetYaxis().SetRange(covar.GetNbinsY()-53,covar.GetNbinsY()); ## check me! 81
covar.SetMarkerSize(0.5)
covar.GetYaxis().SetLabelSize(0.03);
covar.GetZaxis().SetLabelSize(0.03);

palette = covar.GetListOfFunctions().FindObject("palette");
palette.SetX1NDC(0.94);
palette.SetX2NDC(0.96);
palette.SetY1NDC(0.22);
palette.SetY2NDC(0.9);

covar.Draw("colz text");

c1.SaveAs(name+'_covariance_b.png');
c1.SaveAs(name+'_covariance_b.pdf');

