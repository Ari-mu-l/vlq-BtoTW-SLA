import os,sys
from ROOT import TFile, TH1F, TCanvas, TGraphAsymmErrors, kBlack, kAzure, kOrange, kMagenta, kGray, THStack, gStyle, TPad, TLatex, TLegend, gROOT, kBlue, kRed, TMath, TColor
parent = os.path.dirname(os.getcwd())
sys.path.append(parent)
from samples import xsec
from utils import *

gROOT.SetBatch()
gStyle.SetTitleFont(42)
gStyle.SetTextFont(42)

from tdrStyle import *
setTDRStyle()

limitdir = sys.argv[1]
doprelim = False
if len(sys.argv) > 3: doprelim = bool(eval(sys.argv[3]))
plotOnly = True # set True if not want to run combine commands
normByBin = True
lumi = 138

outDir = os.getcwd()

mass1val = int(sys.argv[2])
mass1 = str(mass1val) #'1000'
mass2 = '800'
mass3 = '1400'
sig1 = 'BpM800' # same as table and other plots
sig2 = 'BpM1400'
#sig3 = 'BpM1300'
sig1leg = 'B (0.8 TeV, 59.35 fb)'
sig2leg = 'B (1.4 TeV, 2.66 fb)'
#sig3leg = 'B ('+'1.3 TeV, 1 fb) x100'

taglabels = {'Case1':'t jet + lept. W','Case2':'W jet + lept. t','Case3':'jet + lept. t','Case4':'jet + lept. W'}

name = limitdir.replace('limits_templatesABCDnn_V2_Oct2024','').replace('limits_templatesABCDnn_DV2_Oct2024','')
path1 = limitdir+'/cmb/'+mass1
path2 = limitdir+'/cmb/'+mass2
path3 = limitdir+'/cmb/'+mass3

isSR = False
partialUnblind = False
if '_D' in limitdir and 'partialBlind' not in limitdir:
    isSR = True
    unblind = True # unblind
else:
    unblind = True
doMorph = False

plotFit = 'fit_b' # fit_s
#plotFit = 'fit_s' # TEMP SWITCH


os.chdir(path1)

shapesfile = ''
if not isSR:
    shapesfile = 'CRPostFitShapes.root'
    if not os.path.exists(shapesfile) and not plotOnly:
        print('Creating pre and post-fit histograms from CR')
        print('Command = PostFitShapesFromWorkspace -d combined.txt.cmb -w initialFitWorkspace.root --output CRPostFitShapes.root -m '+mass1+' -f fitDiagnosticsTest.root:'+plotFit+' --postfit --sampling --print')
        os.system('PostFitShapesFromWorkspace -d combined.txt.cmb -w initialFitWorkspace.root --output CRPostFitShapes.root -m '+mass1+' -f fitDiagnosticsTest.root:'+plotFit+' --postfit --sampling --print')

else:
    if doMorph and not unblind and not partialUnblind:
        shapesfile = 'SRMorphedPrefitShapes.root'
        #for mass in [mass1]:
        for mass in [mass1, mass2, mass3]:
            os.chdir(f'{outDir}/{limitdir}/cmb/{mass}')
            if not os.path.exists(shapesfile) and not plotOnly:
                if 'Boosted' in limitdir:
                    masks = 'mask_Case1_D=0,mask_Case2_D=0,mask_Case1_V2=1,mask_Case2_V2=1'# for boosted cases
                else:
                    masks = 'mask_Case1_D=0,mask_Case2_D=0,mask_Case3_D=0,mask_Case4_D=0,mask_Case1_V2=1,mask_Case2_V2=1,mask_Case3_V2=1,mask_Case4_V2=1' # for all four cases

                print('Creating morphed prefit histograms for SR, after dummy FitDiagnostics command...')
                print('Command = combine -M FitDiagnostics -d morphedWorkspace.root --snapshotName initialFit --saveWorkspace --bypassFrequentistFit -t -1 -n Morphed --setParameters (all masks 0)')
                print(f'Command = PostFitShapesFromWorkspace -d combined.txt.cmb -w higgsCombineMorphed.FitDiagnostics.mH120.root --output SRMorphedPrefitShapes.root -m {mass} --print')

                os.system('combine -M FitDiagnostics -d morphedWorkspace.root --snapshotName initialFit --saveWorkspace --bypassFrequentistFit -t -1 -n Morphed --setParameters '+masks)
                os.system(f'PostFitShapesFromWorkspace -d combined.txt.cmb -w higgsCombineMorphed.FitDiagnostics.mH120.root --output SRMorphedPrefitShapes.root -m {mass} --print')
    else:
        for mass in [mass1, mass2, mass3]:
        #for mass in [mass1]:
            os.chdir(f'{outDir}/{limitdir}/cmb/{mass}')
            shapesfile = f'SRPostFitShapes_{mass}.root'
            #if not os.path.exists(path1+'/'+shapesfile):
            if not plotOnly:
                print('Creating pre and post-fit histograms from SR')
                cmd = f'PostFitShapesFromWorkspace -d combined.txt.cmb -w workspace.root --output {shapesfile} -m {mass} -f fitDiagnosticsTest.root:{plotFit} --postfit' #--setParameters signalScale=0.01' probably don't need signalScale because it is set in dataCardCombine.py
                print(f'Command = {cmd}')
                os.system(cmd)
        shapesfile = f'SRPostFitShapes_{mass1}.root'


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
    histogram.GetYaxis().SetTitleSize(0.06)
    histogram.GetYaxis().SetTitleOffset(1.1) #0.85
    #histogram.GetYaxis().CenterTitle()
    histogram.SetMinimum(0.0101)
    histogram.GetXaxis().SetNdivisions(506)
    if blind and not partialUnblind:
        histogram.GetXaxis().SetLabelSize(0.05)
        histogram.GetXaxis().SetTitleSize(0.055)
        histogram.GetYaxis().SetLabelSize(0.045)
        histogram.GetYaxis().SetTitleSize(0.05)
        histogram.GetYaxis().SetTitleOffset(1.1)
    else:
        histogram.GetXaxis().SetTitleOffset(1)
    #else:
    #    histogram.GetXaxis().SetLabelOffset(1.2) #hide labels behind lower panel


    if not yLog: 
        histogram.SetMinimum(0.0101);
    else:
        uPad.SetLogy()
        histogram.SetMaximum(1000*histogram.GetMaximum())
        histogram.SetMaximum(histogram.GetMaximum())

		
def formatLowerHist(histogram, lpad):
    if lpad=='lpad2':
        print('compare low =',histogram.GetXaxis().GetBinLowEdge(histogram.GetXaxis().GetFirst()),', and high =',histogram.GetXaxis().GetBinUpEdge(histogram.GetXaxis().GetLast()))
        histogram.SetTitle('')
        histogram.GetXaxis().SetLabelSize(0.1)
        histogram.GetXaxis().SetTitleSize(0.1)
        histogram.GetXaxis().SetTitleOffset(0.95)
        histogram.GetXaxis().SetNdivisions(506)
        histogram.GetXaxis().SetTitle("B mass (GeV)")
        histogram.GetYaxis().SetLabelSize(0.1)
        histogram.GetYaxis().SetTitleSize(0.1)
        histogram.GetYaxis().SetTitleOffset(.35)
        histogram.GetYaxis().SetTitle('cont to test stat')
        histogram.GetYaxis().SetNdivisions(7)
        histogram.GetYaxis().SetRangeUser(0,4)
        #histogram.GetYaxis().CenterTitle()
    else:
        print('compare low =',histogram.GetXaxis().GetBinLowEdge(histogram.GetXaxis().GetFirst()),', and high =',histogram.GetXaxis().GetBinUpEdge(histogram.GetXaxis().GetLast()))
        histogram.SetTitle('')
        histogram.SetTitle('')
        histogram.GetXaxis().SetLabelSize(0.13)
        histogram.GetXaxis().SetTitleSize(0.13)
        histogram.GetXaxis().SetTitleOffset(1) #0.95
        histogram.GetXaxis().SetNdivisions(506)
        histogram.GetXaxis().SetTitle("B quark mass [GeV]")
        histogram.GetYaxis().SetLabelOffset(0.01)
        histogram.GetYaxis().SetLabelSize(0.13)
        histogram.GetYaxis().SetTitleSize(0.13)
        histogram.GetYaxis().SetTitleOffset(.35)
        histogram.GetYaxis().SetTitle('#frac{(data-bkg)}{Err}')
        #histogram.GetYaxis().SetTitle('#frac{(data-bkg)}{#sqrt{bkg}}')
        #histogram.GetYaxis().SetTitle('#frac{(data-bkg)}{bkgErr}')
        histogram.GetYaxis().SetNdivisions(7)
        #histogram.GetYaxis().SetRangeUser(-2.99,2.99)
        #histogram.GetYaxis().SetRangeUser(-10,10) # range for large pull def
        histogram.GetYaxis().SetRangeUser(-2.99,2.99) # range for standard pull def
        #histogram.GetYaxis().CenterTitle()

    
os.chdir(outDir)
print('Opening',shapesfile,' -- will plot signals like',sig1.replace(mass1,''))
tFile = TFile.Open(f'{path1}/{shapesfile}')
if isSR:
    tFile2 = TFile.Open(f'{path2}/{shapesfile.replace(mass1,mass2)}')
    tFile3 = TFile.Open(f'{path3}/{shapesfile.replace(mass1,mass3)}')

chns = []
iPlot = ''

iPlot = 'BpMass_ABCDnn'
chns = [k.GetName() for k in tFile.GetListOfKeys() if k.GetName().endswith('_postfit')]
#chns = [k.GetName() for k in tFile.GetListOfKeys()]
bkgProcList = ['ttx','ewk','major']
#bkgHistColors = {'major': kRed-7,'ewk':kMagenta-6,'ttx':kAzure+2}
bkgHistColors = {'major': TColor.GetColor('#5790fc'),'ewk':TColor.GetColor('#964a8b'),'ttx':TColor.GetColor('#9c9ca1')}
bkghists = {}
bkghistsmerged = {}


for chn in chns:

    blind = False #False
    partialUnblind = False
    #if isSR and not unblind and ('Case1' in chn or 'Case2' in chn):
    #    blind = True
    if isSR and not unblind and ('Case1' in chn or 'Case2' in chn):
        blind = True
    if partialUnblind and ('Case3' in chn or 'Case4' in chn):
        partialUnblind = False
    yLog = True # for paper

    perNGeV = 10
    print('------------------ ',chn,' with perNGeV = ',perNGeV,'-----------------------')
    
    for proc in bkgProcList:
        bkghistsmerged[chn+proc] = tFile.Get(chn+'/'+proc).Clone()

    hDatamerged = tFile.Get(chn+'/data_obs').Clone()
    bkgHTgerrmerged = tFile.Get(chn+'/TotalBkg').Clone(chn+'__totbkg')
    hsig1merged = tFile2.Get(chn.replace('postfit','prefit')+'/'+sig1.replace(mass2,'')).Clone(chn+'__sig1merged')
    #hsig1merged_postfit = tFile.Get(chn+'/TotalSig').Clone(chn+'__totsig') # for evaluating 'significance' at 1000 GeV deficit

    if partialUnblind:
        for i in range(hDatamerged.FindBin(700),hDatamerged.GetNbinsX()+1):
            hDatamerged.SetBinContent(i,0)
            bkgHTgerrmerged.SetBinContent(i,0)
            #hsig1merged.SetBinContent(i,0)

            hDatamerged.SetBinError(i,0)
            bkgHTgerrmerged.SetBinError(i,0)
            #hsig1merged.SetBinError(i,0)

    if isSR:
        hsig1merged.Scale(100*xsec[sig1[3:]]*0.5) # 100 is to revert 0.01pb to 1pb. No scaling to make visible
    else:
        hsig1merged.Scale(100*xsec[sig1[3:]]*0.5)
                          
    #if '1000' in sig1: hsig1merged.Scale(0.15) #0.25

    histrange = [hDatamerged.GetBinLowEdge(1),hDatamerged.GetBinLowEdge(hDatamerged.GetNbinsX()+1)]
    gaeDatamerged = TGraphAsymmErrors(hDatamerged.Clone(hDatamerged.GetName().replace("data_obs","gaeDATA")))

    if normByBin and ('Case1' or 'Case2') in chn: # Case1/2 needs normbybin for the tail
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
        hsig2merged = tFile3.Get(chn.replace('postfit','prefit')+'/'+sig2.replace(mass3,'')).Clone(chn+'__sig2merged')
        hsig2merged.Scale(100*xsec[sig2[3:]]*0.5)
        #if ('Case1' in chn or 'Case2' in chn) and '1400' in sig2:
        #    hsig2merged.Scale(5)
        #    sig2leg+=' x 5'
        #else:
        #    sig2leg = 'B (1.4 TeV, 2.66 fb)'
        #if '1000' in sig2: hsig2merged.Scale(0.15)
        normByBinWidth(hsig2merged,perNGeV)
        hsig2merged.SetLineColor(kBlack)
        hsig2merged.SetFillStyle(0)
        hsig2merged.SetLineStyle(2)
        hsig2merged.SetLineWidth(3)

        # hsig3merged = tFile3.Get(chn.replace('postfit','prefit')+'/'+sig3.replace(mass3,'')).Clone(chn+'__sig3merged')
        # hsig3merged.Scale(xsec[sig3[3:]]*10000)
        # if '1000' in sig3: hsig3merged.Scale(0.15)
        # normByBinWidth(hsig3merged,perNGeV)
        # hsig3merged.SetLineColor(kBlack)
        # hsig3merged.SetFillStyle(0)
        # hsig3merged.SetLineStyle(2)
        # hsig3merged.SetLineWidth(3)

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
    yDiv=0.3 #0.4 for the lpad2
    if blind and not partialUnblind: yDiv = 0.01
    uMargin = 0.02
    if blind and not partialUnblind: uMargin = 0.12
    rMargin=.05
    uPad={}

    if yLog and ((not blind) or partialUnblind):
        uPad=TPad("uPad","",0,yDiv-0.009,1,1) #for actual plots
        #uPad=TPad("uPad","",0,yDiv+0.1,1,1) #for actual plots
    else: uPad=TPad("uPad","",0,yDiv,1,1) #for actual plots
    
    uPad.SetTopMargin(0.1) #0.08
    uPad.SetBottomMargin(uMargin)
    uPad.SetRightMargin(rMargin)
    uPad.SetLeftMargin(.12)
    if not yLog: uPad.SetLeftMargin(0.13)
    uPad.Draw()

    if not blind or partialUnblind:
        lPad=TPad("lPad","",0,0,1,yDiv) #lPad=TPad("lPad","",0,yDiv/2,1,yDiv) #for sigma runner #for lpad2
        lPad.SetTopMargin(0)
        lPad.SetBottomMargin(0.4) #0 for lpad2
        lPad.SetRightMargin(rMargin)
        lPad.SetLeftMargin(.12)
        if not yLog: lPad.SetLeftMargin(0.13)
        #lPad.SetGridy()
        lPad.Draw()

        # second panel requested by the conveners
        # remove for paper
        # lPad2=TPad("lPad","",0,0,1,yDiv/2)
        # lPad2.SetTopMargin(0)
        # lPad2.SetBottomMargin(.4)
        # lPad2.SetRightMargin(rMargin)
        # lPad2.SetLeftMargin(.12)
        # if not yLog: lPad2.SetLeftMargin(0.13)
        # ##lPad2.SetGridy()
        # lPad2.Draw()

    hDatamerged.SetMaximum(1.2*max(hDatamerged.GetMaximum(),bkgHTmerged.GetMaximum()))
    hDatamerged.SetMinimum(0.015)    
    #hDatamerged.GetYaxis().SetTitle("#LT Events / "+str(perNGeV)+" GeV #GT")
    if normByBin and ('Case1' or 'Case2') in chn: # Case1/2 needs normbybin for the tail
        hDatamerged.GetYaxis().SetTitle("Events / "+str(perNGeV)+" GeV")
    else:
        hDatamerged.GetYaxis().SetTitle("Events / bin")
    if blind and not partialUnblind: hsig1merged.GetYaxis().SetTitle("#LT Events / "+str(perNGeV)+" GeV #GT")

    formatUpperHist(hDatamerged,hDatamerged)
    uPad.cd()
    hDatamerged.SetTitle("")
    stackbkgHTmerged.SetTitle("")
    if not blind or partialUnblind: 
        gStyle.SetErrorX(0.5)
        hDatamerged.Draw()
    else:
        hsig1merged.SetMinimum(0.015)
        hsig1merged.SetMaximum(1.5*max(hDatamerged.GetMaximum(),bkgHTmerged.GetMaximum()))
        formatUpperHist(hsig1merged,hsig1merged)
        hsig1merged.Draw("HIST")
        
    stackbkgHTmerged.Draw("SAME HIST")
    #stackbkgHTmerged.Draw("SAME PE")
    hsig1merged.Draw("SAME HIST")
    if isSR:
        hsig2merged.Draw("SAME HIST")
        #hsig3merged.Draw("SAME HIST")
    if not blind or partialUnblind: 
        gaeDatamerged.Draw("PZ") #redraw data so its not hidden
    uPad.RedrawAxis()
    bkgHTgerrmerged.Draw("SAME E2")

    chLatexmerged = TLatex()
    chLatexmerged.SetNDC()
    #chLatexmerged.SetTextFont(42)
    chLatexmerged.SetTextSize(0.06)
    if blind and not partialUnblind: chLatexmerged.SetTextSize(0.04)
    #chLatexmerged.SetTextSize(0.08)
    chLatexmerged.SetTextAlign(12) # align left
    flvString = 'e/#mu+jets'
    if not isSR:
        flvString = 'e/#mu (VR)' # unblind
    #tagString = taglabels[chn.split('_')[0]]
    tagString = chn.split('_')[0]
    if yLog:
        chLatexmerged.DrawLatex(0.18, 0.81, flvString) # 0.18, 0.71    
        chLatexmerged.DrawLatex(0.18, 0.71, tagString) # 0.18, 0.61
    else:
        #chLatexmerged.SetTextAlign(32) #right
        #chLatexmerged.DrawLatex(0.89, 0.45, flvString)    
        #chLatexmerged.DrawLatex(0.89, 0.38, tagString)
        
        chLatexmerged.SetTextAlign(22) # center
        chLatexmerged.DrawLatex(0.8, 0.45, flvString)
        chLatexmerged.DrawLatex(0.8, 0.38, tagString)
        
    #if 'postfit' in chn: chLatexmerged.DrawLatex(0.28, 0.72, 'post-fit')

    if yLog:
        legmerged = TLegend(0.4,0.55,0.89,0.87)
    else:
        legmerged = TLegend(0.35,0.55,0.84,0.87)
    legmerged.SetShadowColor(0)
    legmerged.SetFillColor(0)
    legmerged.SetFillStyle(0)
    legmerged.SetLineColor(0)
    legmerged.SetLineStyle(0)
    legmerged.SetBorderSize(0) 
    legmerged.SetNColumns(2)
    #legmerged.SetTextFont(42)
    legmerged.SetColumnSeparation(0.10)
    legmerged.SetTextSize(0.05)
    if not blind or partialUnblind:
        legmerged.AddEntry(gaeDatamerged,"Data","pel")  #left
        #legmerged.AddEntry(bkghistsmerged[chn+'major'],"ABCDnn","f") #right
        legmerged.AddEntry(bkghistsmerged[chn+'major'],"ABCDnn","f") #right
        legmerged.AddEntry(hsig1merged,sig1leg,"l")  #left
        legmerged.AddEntry(bkghistsmerged[chn+'ewk'],"DY+VV","f") #right
        if isSR:
            #print('Not plotting mass2 and 3')
            legmerged.AddEntry(hsig2merged,sig2leg,"l")  #left
            #legmerged.AddEntry(hsig3merged,sig3leg,"l")  #left
        else:
            legmerged.AddEntry(0,"","")  #left
        legmerged.AddEntry(bkghistsmerged[chn+'ttx'],"t#bar{t}+X","f") #right
        legmerged.AddEntry(0,"","")  #left
        legmerged.AddEntry(bkgHTgerrmerged,"Bkg. uncert.","f") #right
    else:
        legmerged.AddEntry(hsig1merged,sig1leg,"l")  #left
        legmerged.AddEntry(bkghistsmerged[chn+'major'],"ABCDnn","f") #right
        if isSR:
            #print('Not plotting mass2 and 3')
            legmerged.AddEntry(hsig2merged,sig2leg,"l")  #left
            #legmerged.AddEntry(hsig3merged,sig3leg,"l")
        else:
            legmerged.AddEntry(0,"","")  #left
        legmerged.AddEntry(bkghistsmerged[chn+'ewk'],"DY+VV","f") #right
        legmerged.AddEntry(bkgHTgerrmerged,"Bkg. uncert.","f") #left
        legmerged.AddEntry(bkghistsmerged[chn+'ttx'],"t#bar{t}+X","f") #right

    legmerged.Draw("same")
 
    prelimTex=TLatex()
    prelimTex.SetNDC()
    prelimTex.SetTextAlign(31) # align right
    #prelimTex.SetTextFont(42)
    prelimTex.SetTextSize(0.06)
    if blind and not partialUnblind: prelimTex.SetTextSize(0.05)
    prelimTex.SetLineWidth(2)
    prelimTex.DrawLatex(0.95,0.92,str(lumi)+" fb^{-1} (13 TeV)")
    
    prelimTex2=TLatex()
    prelimTex2.SetNDC()
    #prelimTex2.SetTextFont(61)
    prelimTex2.SetLineWidth(2)
    prelimTex2.SetTextSize(0.08)
    if blind and not partialUnblind: prelimTex2.SetTextSize(0.08)
    #prelimTex2.SetTextSize(0.1)
    #prelimTex2.DrawLatex(0.12,0.93,"CMS")
    if doprelim: 
        prelimTex2.DrawLatex(0.12,0.93,"#bf{CMS}")
    else:
        prelimTex2.DrawLatex(0.12,0.92,"#bf{CMS}")
        
    prelimTex3=TLatex()
    prelimTex3.SetNDC()
    prelimTex3.SetTextAlign(12)
    #prelimTex3.SetTextFont(52)
    prelimTex3.SetTextSize(0.055)
    prelimTex3.SetLineWidth(2)
    if doprelim: prelimTex3.DrawLatex(0.23,0.945,"Preliminary")
    #if blind: prelimTex3.DrawLatex(0.26,0.945,"Work in progress") #"Preliminary")

    if not blind or partialUnblind:
        #formatUpperHist(hDatamerged,hDatamerged)
        lPad.cd()
        pullmerged=hDatamerged.Clone(chn+"pullmerged")
        # for deficit at 1000
        sum_sig = 0
        N_sig = 0
        for binNo in range(1,hDatamerged.GetNbinsX()+1):
            # case for data < MC:
            dataerror = gaeDatamerged.GetErrorYhigh(binNo-1)
            MCerror = bkgHTgerrmerged.GetBinError(binNo)
            MC = bkgHTgerrmerged.GetBinContent(binNo)
            # case for data > MC:
            if(hDatamerged.GetBinContent(binNo) > bkgHTmerged.GetBinContent(binNo)):
                dataerror = gaeDatamerged.GetErrorYlow(binNo-1)
                MCerror = bkgHTgerrmerged.GetBinError(binNo)
            #pullmerged.SetBinContent(binNo,(hDatamerged.GetBinContent(binNo)-bkgHTmerged.GetBinContent(binNo))/math.sqrt(MCerror**2+dataerror**2))
            #pull = (hDatamerged.GetBinContent(binNo)-bkgHTmerged.GetBinContent(binNo))/math.sqrt(MCerror**2+dataerror**2) # original def of pull
            #pull = (hDatamerged.GetBinContent(binNo)-bkgHTmerged.GetBinContent(binNo))/math.sqrt(bkgHTmerged.GetBinContent(binNo))# requested by the conveners
            if partialUnblind and binNo>=hDatamerged.FindBin(700):
                pull = 0
            else:
                #print(hDatamerged.GetXaxis().GetBinCenter(binNo))
                #pull = (hDatamerged.GetBinContent(binNo)-bkgHTmerged.GetBinContent(binNo))/MCerror # requested by Julie to understand the deficit in 1000 GeV
                #pull = (hDatamerged.GetBinContent(binNo)-bkgHTmerged.GetBinContent(binNo))/math.sqrt(MCerror**2+dataerror**2)
                #pull = 0
                pull = (hDatamerged.GetBinContent(binNo)-bkgHTmerged.GetBinContent(binNo))/math.sqrt(MC-MCerror**2) # STANDARD

            sum_sig += hsig1merged.GetBinContent(binNo)*pull
            N_sig += hsig1merged.GetBinContent(binNo)
            pullmerged.SetBinContent(binNo,pull)
            if pull>=1:
                print(chn, binNo, pull)

        print('sum_sig', sum_sig)
        print('N_sig', N_sig)
        pullmerged.SetMaximum(3)
        pullmerged.SetMinimum(-3)
        pullmerged.SetFillColor(kGray+2)
        pullmerged.SetLineColor(kGray+2)
        formatLowerHist(pullmerged, "lpad")
        pullmerged.Draw("HIST")
        
        # lPad2.cd()
        # binContribution=hDatamerged.Clone(chn+"binContribution") # bin contribution to GoF
        # for binNo in range(1,hDatamerged.GetNbinsX()+1):
        #     if partialUnblind:
        #         if binNo<hDatamerged.FindBin(700):
        #             binContribution.SetBinContent(binNo,-2*math.log(TMath.Poisson(hDatamerged.GetBinContent(binNo), bkgHTmerged.GetBinContent(binNo)) / TMath.Poisson(hDatamerged.GetBinContent(binNo), hDatamerged.GetBinContent(binNo))))
        #         else:
        #             binContribution.SetBinContent(binNo,0)
        #     else:
        #         binContribution.SetBinContent(binNo,-2*math.log(TMath.Poisson(hDatamerged.GetBinContent(binNo), bkgHTmerged.GetBinContent(binNo)) / TMath.Poisson(hDatamerged.GetBinContent(binNo), hDatamerged.GetBinContent(binNo))))
        # binContribution.SetMaximum(4)
        # binContribution.SetMinimum(0)
        # binContribution.SetFillColor(kGray+2)
        # binContribution.SetLineColor(kGray+2)
        # formatLowerHist(binContribution, "lpad2")
        # binContribution.Draw("HIST")

        #lPad2.cd()
        

    savePrefixMerged = f'{path1}/PostFitPlots/'
    if not os.path.exists(savePrefixMerged): os.system('mkdir -p '+savePrefixMerged)
    savePrefixMerged+=iPlot+'_'+str(lumi).replace('.','p')+'fb_'+chn+'_NBBW_pull'
    if blind and partialUnblind: savePrefixMerged+='_blind'
    if yLog: savePrefixMerged+='_logy'
    if doprelim: savePrefixMerged+='_prelim'

    c1merged.SaveAs(f'{savePrefixMerged}.pdf')
    c1merged.SaveAs(f'{savePrefixMerged}.png')
    c1merged.SaveAs(f'{savePrefixMerged}.root')
    #c1merged.SaveAs(savePrefixMerged+".C")

    for proc in bkgProcList:
        try: 
            del bkghistsmerged[chn+proc]
        except: pass
    del c1merged
