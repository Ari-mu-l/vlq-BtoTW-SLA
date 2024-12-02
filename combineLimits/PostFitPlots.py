import os,sys
from ROOT import TFile, TH1F, TCanvas, TGraphAsymmErrors, kBlack, kAzure, kOrange, kMagenta, kGray, THStack, gStyle, TPad, TLatex, TLegend, gROOT, kBlue, kRed
parent = os.path.dirname(os.getcwd())
sys.path.append(parent)
from samples import xsec
from utils import *

gROOT.SetBatch()

from tdrStyle import *
setTDRStyle()

limitdir = sys.argv[1]
doprelim = False
if len(sys.argv) > 2: doprelim = bool(eval(sys.argv[2]))
lumi = 138

outDir = os.getcwd()

sig1 = 'BpM1200'
sig2 = 'BpM1800'
sig1leg = 'B (1.2 TeV)'
sig2leg = 'B (1.8 TeV)'
mass1 = '1200'
mass2 = '1800'

taglabels = {'Case1':'t jet + lept. W','Case2':'W jet + lept. t','Case3':'jet + lept. t','Case4':'jet + lept. W'}

name = limitdir.replace('limits_templatesABCDnn_V2_Oct2024','').replace('limits_templatesABCDnn_DV2_Oct2024','')
path1 = limitdir+'/cmb/'+mass1
path2 = limitdir+'/cmb/'+mass2

isSR = False
if '_D' in limitdir: isSR = True
doMorph = False

os.chdir(path1)

shapesfile = ''
if not isSR:
    shapesfile = 'CRPostFitShapes.root'
    if not os.path.exists(shapesfile):
        print('Creating pre and post-fit histograms from CR')
        print('Command = PostFitShapesFromWorkspace -d combined.txt.cmb -w initialFitWorkspace.root --output CRPostFitShapes.root -m '+mass1+' -f fitDiagnosticsTest.root:fit_b --postfit --sampling --print')
        os.system('PostFitShapesFromWorkspace -d combined.txt.cmb -w initialFitWorkspace.root --output CRPostFitShapes.root -m '+mass1+' -f fitDiagnosticsTest.root:fit_b --postfit --sampling --print')


else:
    if doMorph:
        shapesfile = 'SRMorphedPrefitShapes.root'
        if not os.path.exists(shapesfile):
            masks = 'mask_Case1_D=0,mask_Case2_D=0,mask_Case3_D=0,mask_Case4_D=0,mask_Case1_V2=1,mask_Case2_V2=1,mask_Case3_V2=1,mask_Case4_V2=1'

            print('Creating morphed prefit histograms for SR, after dummy FitDiagnostics command...')
            print('Command = combine -M FitDiagnostics -d morphedWorkspace.root --snapshotName initialFit --saveWorkspace --bypassFrequentistFit -t -1 -n Morphed --setParameters (all masks 0)')
            print('Command = PostFitShapesFromWorkspace -d combined.txt.cmb -w higgsCombineMorphed.FitDiagnostics.mH120.root --output SRMorphedPrefitShapes.root -m '+mass1+' --print')

            os.system('combine -M FitDiagnostics -d morphedWorkspace.root --snapshotName initialFit --saveWorkspace --bypassFrequentistFit -t -1 -n Morphed --setParameters '+masks)
            os.system('PostFitShapesFromWorkspace -d combined.txt.cmb -w higgsCombineMorphed.FitDiagnostics.mH120.root --output SRMorphedPrefitShapes.root -m '+mass1+' --print')
    else:
        shapesfile = 'SRPostFitShapes_'+mass1+'.root'
        if not os.path.exists(outDir+'/'+shapesfile):
            print('Creating pre and post-fit histograms from SR')
            print('Command = PostFitShapesFromWorkspace -d combined.txt -w workspace.root --output '+outDir+'/'+shapesfile+' -m '+str(mass1)+' -f fitDiagnosticsTest.root:fit_b --postfit')
            os.system('PostFitShapesFromWorkspace -d combined.txt -w workspace.root --output '+outDir+'/'+shapesfile+' -m '+str(mass1)+' -f fitDiagnosticsTest.root:fit_b --postfit --skip-proc-errs=1')
        os.chdir(path2)
        if not os.path.exists(outDir+'/'+shapesfile.replace(mass1,mass2)):
            print('Creating pre and post-fit histograms from SR')
            print('Command = PostFitShapesFromWorkspace -d combined.txt -w workspace.root --output '+outDir+'/'+shapesfile.replace(mass1,mass2)+' -m '+str(mass2)+' -f fitDiagnosticsTest.root:fit_b --postfit')
            os.system('PostFitShapesFromWorkspace -d combined.txt -w workspace.root --output '+outDir+'/'+shapesfile.replace(mass1,mass2)+' -m '+str(mass2)+' -f fitDiagnosticsTest.root:fit_b --postfit --skip-proc-errs=1')


def formatUpperHist(histogram,th1hist):
    histogram.SetTitle('')
    histogram.GetXaxis().SetLabelSize(0)
    print('gaeData low = ',histogram.GetXaxis().GetBinLowEdge(0))
    lowside = th1hist.GetBinLowEdge(1)
    highside = th1hist.GetBinLowEdge(th1hist.GetNbinsX()+1)
    if highside > 10: highside = highside-1
    print('Setting range from',lowside,'to',highside)
    histogram.GetXaxis().SetRangeUser(lowside,highside)
    histogram.GetXaxis().SetTitle('')
    histogram.GetYaxis().SetLabelSize(0.06)
    histogram.GetYaxis().SetTitleSize(0.07)
    histogram.GetYaxis().SetTitleOffset(.85)
    histogram.GetYaxis().CenterTitle()
    histogram.SetMinimum(0.0101)
    histogram.GetXaxis().SetNdivisions(506)
    if blind:
        histogram.GetXaxis().SetLabelSize(0.05)
        histogram.GetXaxis().SetTitleSize(0.055)
        histogram.GetYaxis().SetLabelSize(0.045)
        histogram.GetYaxis().SetTitleSize(0.05)
        histogram.GetYaxis().SetTitleOffset(1.1)
    #else:
    #    histogram.GetXaxis().SetLabelOffset(1.2) #hide labels behind lower panel

    if not yLog: 
        histogram.SetMinimum(0.0101);
    else:
        uPad.SetLogy()
        histogram.SetMaximum(1000*histogram.GetMaximum())

		
def formatLowerHist(histogram):
    print('compare low =',histogram.GetXaxis().GetBinLowEdge(histogram.GetXaxis().GetFirst()),', and high =',histogram.GetXaxis().GetBinUpEdge(histogram.GetXaxis().GetLast()))
    histogram.SetTitle('')
    histogram.GetXaxis().SetLabelSize(.18)
    histogram.GetXaxis().SetTitleSize(0.18)
    histogram.GetXaxis().SetTitleOffset(0.95)
    histogram.GetXaxis().SetNdivisions(506)
    histogram.GetXaxis().SetTitle("B mass (GeV)")
    histogram.GetYaxis().SetLabelSize(0.14)
    histogram.GetYaxis().SetTitleSize(0.14)
    histogram.GetYaxis().SetTitleOffset(.35)
    histogram.GetYaxis().SetTitle('#frac{(data-bkg)}{tot. uncert.}')
    histogram.GetYaxis().SetNdivisions(7)
    histogram.GetYaxis().SetRangeUser(-2.99,2.99)
    histogram.GetYaxis().CenterTitle()

if isSR:
    os.chdir(outDir)
print('Opening',shapesfile,' -- will plot signals like',sig1.replace('1200',''))
tFile = TFile.Open(shapesfile)
if isSR:
    tFile2 = TFile.Open(shapesfile.replace(mass1,mass2))

chns = []
iPlot = ''

iPlot = 'BpMass_ABCDnn'
chns = [k.GetName() for k in tFile.GetListOfKeys() if k.GetName().endswith('_postfit')]
bkgProcList = ['ttx','ewk','major']
bkgHistColors = {'major': kRed-7,'ewk':kMagenta-6,'ttx':kAzure+2}
bkghists = {}
bkghistsmerged = {}

for chn in chns:

    blind = False
    if isSR and ('Case1' in chn or 'Case2' in chn): blind = True
    yLog = False

    perNGeV = 50
    print('------------------ ',chn,' with perNGeV = ',perNGeV,'-----------------------')
    
    for proc in bkgProcList:
        bkghistsmerged[chn+proc] = tFile.Get(chn+'/'+proc).Clone()

    hDatamerged = tFile.Get(chn+'/data_obs').Clone()
    bkgHTgerrmerged = tFile.Get(chn+'/TotalBkg').Clone(chn+'__totbkg')
    hsig1merged = tFile.Get(chn.replace('postfit','prefit')+'/'+sig1.replace('1200','')).Clone(chn+'__sig1merged')
    hsig1merged.Scale(xsec[sig1[3:]])
    if isSR: hsig1merged.Scale(1000)

    histrange = [hDatamerged.GetBinLowEdge(1),hDatamerged.GetBinLowEdge(hDatamerged.GetNbinsX()+1)]
    gaeDatamerged = TGraphAsymmErrors(hDatamerged.Clone(hDatamerged.GetName().replace("data_obs","gaeDATA")))

    poissonNormByBinWidth(gaeDatamerged,hDatamerged,perNGeV)
    for proc in bkgProcList:
        try: 
            normByBinWidth(bkghistsmerged[chn+proc],perNGeV)
        except: pass
    normByBinWidth(hsig1merged,perNGeV)
    normByBinWidth(hDatamerged,perNGeV)
    normByBinWidth(bkgHTgerrmerged,perNGeV)
    
    bkgHTmerged = bkghistsmerged[chn+bkgProcList[0]].Clone()
    for proc in bkgProcList:
        if proc==bkgProcList[0]: continue
        try: 
            bkgHTmerged.Add(bkghistsmerged[chn+proc])
        except: pass

    #bkgHTgerrmerged = TGraphAsymmErrors(bkgHTmerged.Clone("bkgHTgerrmerged"))

    stackbkgHTmerged = THStack("stackbkgHTmerged","")
    for proc in bkgProcList:
        print('filling',proc,'into stack')
        bkghistsmerged[chn+proc].SetLineColor(bkgHistColors[proc])
        bkghistsmerged[chn+proc].SetFillColor(bkgHistColors[proc])
        bkghistsmerged[chn+proc].SetLineWidth(2)
        stackbkgHTmerged.Add(bkghistsmerged[chn+proc])

    hsig1merged.SetLineColor(kBlack)
    hsig1merged.SetFillStyle(0)
    hsig1merged.SetLineWidth(3)

    if isSR:
        hsig2merged = tFile2.Get(chn.replace('postfit','prefit')+'/'+sig2.replace('1800','')).Clone(chn+'__sig2merged')
        hsig2merged.Scale(xsec[sig2[3:]]*1000)
        normByBinWidth(hsig2merged,perNGeV)
        hsig2merged.SetLineColor(kBlack)
        hsig2merged.SetFillStyle(0)
        hsig2merged.SetLineStyle(2)
        hsig2merged.SetLineWidth(3)

    gaeDatamerged.SetMarkerStyle(20)
    gaeDatamerged.SetMarkerSize(1.5)
    if hDatamerged.GetNbinsX() > 10:
        gaeDatamerged.SetMarkerSize(1.2) 
    gaeDatamerged.SetLineWidth(2)
    gaeDatamerged.SetMarkerColor(kBlack)
    gaeDatamerged.SetLineColor(kBlack)

    bkgHTgerrmerged.SetFillStyle(3004)
    bkgHTgerrmerged.SetFillColor(kBlack)
    bkgHTgerrmerged.SetLineColor(kBlack)

    gStyle.SetOptStat(0)
    c1merged = TCanvas("c1merged","c1merged",1200,1000)
    gStyle.SetErrorX(0.5)
    yDiv=0.3
    if blind: yDiv = 0.01
    uMargin = 0.02
    if blind: uMargin = 0.12
    rMargin=.05
    uPad={}
    if yLog and not blind: 
        uPad=TPad("uPad","",0,yDiv-0.009,1,1) #for actual plots
        #uPad=TPad("uPad","",0,yDiv+0.1,1,1) #for actual plots
    else: uPad=TPad("uPad","",0,yDiv,1,1) #for actual plots
    uPad.SetTopMargin(0.08)
    uPad.SetBottomMargin(uMargin)
    uPad.SetRightMargin(rMargin)
    uPad.SetLeftMargin(.12)
    if not yLog: uPad.SetLeftMargin(0.13)
    uPad.Draw()

    if not blind:
        lPad=TPad("lPad","",0,0,1,yDiv) #for sigma runner
        lPad.SetTopMargin(0)
        lPad.SetBottomMargin(.4)
        lPad.SetRightMargin(rMargin)
        lPad.SetLeftMargin(.12)
        if not yLog: lPad.SetLeftMargin(0.13)
        #lPad.SetGridy()
        lPad.Draw()

    hDatamerged.SetMaximum(1.2*max(hDatamerged.GetMaximum(),bkgHTmerged.GetMaximum()))
    hDatamerged.SetMinimum(0.015)    
    hDatamerged.GetYaxis().SetTitle("#LT Events / "+str(perNGeV)+" GeV #GT")
    if blind: hsig1merged.GetYaxis().SetTitle("#LT Events / "+str(perNGeV)+" GeV #GT")

    formatUpperHist(hDatamerged,hDatamerged)
    uPad.cd()
    hDatamerged.SetTitle("")
    stackbkgHTmerged.SetTitle("")
    if not blind: 
        gStyle.SetErrorX(0.5)
        hDatamerged.Draw()
    else:
        hsig1merged.SetMinimum(0.015)
        hsig1merged.SetMaximum(1.5*max(hDatamerged.GetMaximum(),bkgHTmerged.GetMaximum()))
        formatUpperHist(hsig1merged,hsig1merged)
        hsig1merged.Draw("HIST")

    stackbkgHTmerged.Draw("SAME HIST")
    hsig1merged.Draw("SAME HIST")
    if isSR:
        hsig2merged.Draw("SAME HIST")
    if not blind: 
        gaeDatamerged.Draw("PZ") #redraw data so its not hidden
    uPad.RedrawAxis()
    bkgHTgerrmerged.Draw("SAME E2")

    chLatexmerged = TLatex()
    chLatexmerged.SetNDC()
    chLatexmerged.SetTextFont(42)
    chLatexmerged.SetTextSize(0.06)
    if blind: chLatexmerged.SetTextSize(0.04)
    chLatexmerged.SetTextSize(0.08)
    chLatexmerged.SetTextAlign(12) # align left
    flvString = 'e/#mu+jets'
    if not isSR:
        flvString = 'e/#mu (VR)'
    tagString = taglabels[chn.split('_')[0]]
    if yLog:
        chLatexmerged.DrawLatex(0.18, 0.71, flvString)    
        chLatexmerged.DrawLatex(0.18, 0.61, tagString)
    else:
        chLatexmerged.SetTextAlign(32) #right
        chLatexmerged.DrawLatex(0.89, 0.45, flvString)    
        chLatexmerged.DrawLatex(0.89, 0.38, tagString)
        
    #if 'postfit' in chn: chLatexmerged.DrawLatex(0.28, 0.72, 'post-fit')

    legmerged = TLegend(0.45,0.55,0.89,0.87)
    legmerged.SetShadowColor(0)
    legmerged.SetFillColor(0)
    legmerged.SetFillStyle(0)
    legmerged.SetLineColor(0)
    legmerged.SetLineStyle(0)
    legmerged.SetBorderSize(0) 
    legmerged.SetNColumns(2)
    legmerged.SetTextFont(42)
    legmerged.SetColumnSeparation(0.10)
    #legmerged.SetTextSize(0.06)
    if not blind:
        legmerged.AddEntry(gaeDatamerged,"Data","pel")  #left
        legmerged.AddEntry(bkghistsmerged[chn+'major'],"ABCDnn","f") #right
        legmerged.AddEntry(hsig1merged,sig1leg,"l")  #left
        legmerged.AddEntry(bkghistsmerged[chn+'ewk'],"DY+VV","f") #right
        if isSR:
            legmerged.AddEntry(hsig2merged,sig2leg,"l")  #left
        else:
            legmerged.AddEntry(0,"","")  #left
        legmerged.AddEntry(bkghistsmerged[chn+'ttx'],"t#bar{t}+X","f") #right
        legmerged.AddEntry(0,"","")  #left
        legmerged.AddEntry(bkgHTgerrmerged,"Bkg. uncert.","f") #right
    else:
        legmerged.AddEntry(hsig1merged,sig1leg,"l")  #left
        legmerged.AddEntry(bkghistsmerged[chn+'major'],"ABCDnn","f") #right
        if isSR:
            legmerged.AddEntry(hsig2merged,sig2leg,"l")  #left
        else:
            legmerged.AddEntry(0,"","")  #left
        legmerged.AddEntry(bkghistsmerged[chn+'ewk'],"DY+VV","f") #right
        legmerged.AddEntry(bkgHTgerrmerged,"Bkg. uncert.","f") #left
        legmerged.AddEntry(bkghistsmerged[chn+'ttx'],"t#bar{t}+X","f") #right

    legmerged.Draw("same")
 
    prelimTex=TLatex()
    prelimTex.SetNDC()
    prelimTex.SetTextAlign(31) # align right
    prelimTex.SetTextFont(42)
    prelimTex.SetTextSize(0.05)
    if blind: prelimTex.SetTextSize(0.05)
    prelimTex.SetLineWidth(2)
    prelimTex.DrawLatex(0.95,0.94,str(lumi)+" fb^{-1} (13 TeV)")
    
    prelimTex2=TLatex()
    prelimTex2.SetNDC()
    prelimTex2.SetTextFont(61)
    prelimTex2.SetLineWidth(2)
    prelimTex2.SetTextSize(0.08)
    if blind: prelimTex2.SetTextSize(0.08)
    prelimTex2.SetTextSize(0.1)
    #prelimTex2.DrawLatex(0.12,0.93,"CMS")
    if doprelim: 
        prelimTex2.DrawLatex(0.12,0.93,"CMS")
    else:
        prelimTex2.DrawLatex(0.18,0.81,"CMS")
        
    prelimTex3=TLatex()
    prelimTex3.SetNDC()
    prelimTex3.SetTextAlign(12)
    prelimTex3.SetTextFont(52)
    prelimTex3.SetTextSize(0.055)
    prelimTex3.SetLineWidth(2)
    if doprelim: prelimTex3.DrawLatex(0.23,0.945,"Preliminary")
    #if blind: prelimTex3.DrawLatex(0.26,0.945,"Work in progress") #"Preliminary")

    if not blind:
        #formatUpperHist(hDatamerged,hDatamerged)
        lPad.cd()
        pullmerged=hDatamerged.Clone(chn+"pullmerged")
        for binNo in range(1,hDatamerged.GetNbinsX()+1):
            # case for data < MC:
            dataerror = gaeDatamerged.GetErrorYhigh(binNo-1)
            MCerror = bkgHTgerrmerged.GetBinError(binNo)
            # case for data > MC:
            if(hDatamerged.GetBinContent(binNo) > bkgHTmerged.GetBinContent(binNo)):
                dataerror = gaeDatamerged.GetErrorYlow(binNo-1)
                MCerror = bkgHTgerrmerged.GetBinError(binNo)
            pullmerged.SetBinContent(binNo,(hDatamerged.GetBinContent(binNo)-bkgHTmerged.GetBinContent(binNo))/math.sqrt(MCerror**2+dataerror**2))
        pullmerged.SetMaximum(3)
        pullmerged.SetMinimum(-3)
        pullmerged.SetFillColor(kGray+2)
        pullmerged.SetLineColor(kGray+2)
        formatLowerHist(pullmerged)
        pullmerged.Draw("HIST")

    savePrefixMerged = 'PostFitPlots/'
    if not os.path.exists(savePrefixMerged): os.system('mkdir -p '+savePrefixMerged)
    savePrefixMerged+=iPlot+'_'+str(lumi).replace('.','p')+'fb_'+chn+'_NBBW_pull'
    if blind: savePrefixMerged+='_blind'
    if yLog: savePrefixMerged+='_logy'
    if doprelim: savePrefixMerged+='_prelim'

    c1merged.SaveAs(savePrefixMerged+".pdf")
    c1merged.SaveAs(savePrefixMerged+".png")
    c1merged.SaveAs(savePrefixMerged+".root")
    #c1merged.SaveAs(savePrefixMerged+".C")

    for proc in bkgProcList:
        try: 
            del bkghistsmerged[chn+proc]
        except: pass
    del c1merged
