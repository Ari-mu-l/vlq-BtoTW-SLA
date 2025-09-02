from ROOT import gROOT, TFile, TH1D, TCanvas, TLegend, TVectorD, TGraphAsymmErrors, TGraph, TLatex, TColor
from array import array
import math
from math import *
import os,sys
import json

gROOT.SetBatch(1)

from tdrStyle import *
setTDRStyle()

limitDir = str(sys.argv[1])
multiplier = 0.02 ## unscale BR put onto signal
# if signalScale = 0.01: r = 7. 7 * 10fb = 70fb
# if signalScale = 0.005: r = 14. 14 * 5fb = 70fb
# if r = 7 when signal is 2x too large, I want r = 0.140
# set multiplier to 0.02
signal = 'B'

blind=False #True # for unblinding
morphed=False # True
saveKey='newTW'
if blind: saveKey+='_blind'
if morphed: saveKey+='_morphed'

lumiPlot = '138'# '97.4'#
lumiStr = '138'

discriminant='BToTW'
histPrefix=discriminant+'_'+str(lumiStr)+'fb'

mass = array('d', [800,1000,1200,1300,1400,1500,1600,1700,1800,2000])
masserr = array('d', [0,0,0,0,0,0,0,0,0,0])
mass_str = ['800','1000','1200','1300','1400','1500','1600','1700','1800','2000']

mass6 = array('d', [800,1000,1200,1400,1600,1800])
mass6err = array('d', [0,0,0])
mass6_str = ['800','1000','1200','1400','1600','1800']

exp   =array('d',[0 for i in range(len(mass))])
experr=array('d',[0 for i in range(len(mass))])
obs   =array('d',[0 for i in range(len(mass))])
obserr=array('d',[0 for i in range(len(mass))]) 
exp68H=array('d',[0 for i in range(len(mass))])
exp68L=array('d',[0 for i in range(len(mass))])
exp95H=array('d',[0 for i in range(len(mass))])
exp95L=array('d',[0 for i in range(len(mass))])

xsec = array('d',[multiplier for i in range(len(mass))])

# https://docs.google.com/spreadsheets/d/1hrvXSGU1lbLPtbK0wvMwwVQTHFAeTzPX_4GVC4hKLHw/edit?gid=0
# Calculation of NWA tW cross section based on TopPartners_SingleProduction github (see links within). 
theory_mass = array('d', [800,900,1000,1100,1200,1300,1400,1500,1600,1700,1800,1900,2000])
# Singlet 1% width
theory_xsecS1 = [0.0593561830,0.0320056423,0.0181489018,0.0107504306,0.0065674164,0.0041314326,0.0026606518,0.0017539205,0.0011414437,0.0007473592,0.0004948968,0.0003259721,0.0002249628]
theoryS1dn    = [0.0471288093,0.0252524517,0.0142105901,0.0083745854,0.0050831803,0.0031812031,0.0020407199,0.0013382413,0.0008663558,0.0005650036,0.0003726573,0.0002444791,0.0001680472]
theoryS1up    = [0.0765101199,0.0416073349,0.0237750614,0.0141905684,0.0087280963,0.0055237254,0.0035759160,0.0023713005,0.0015523635,0.0010208927,0.0006794933,0.0004495155,0.0003117984]
theory_xsecS1_dn = [(a-b) for a,b in zip(theory_xsecS1,theoryS1dn)]
theory_xsecS1_up = [(a-b) for a,b in zip(theoryS1up,theory_xsecS1)]

# Singlet 5% width
theory_xsecS5 = [0.2967809151,0.1600282113,0.0907445091,0.0537521530,0.0328370818,0.0206571632,0.0133032589,0.0087696024,0.0057072186,0.0037367961,0.0024744838,0.0016298605,0.0011248138]
theoryS5dn    = [0.3825505996,0.2080366747,0.1188753070,0.0709528420,0.0436404817,0.0276186272,0.0178795800,0.0118565025,0.0077618173,0.0051044635,0.0033974663,0.0022475777,0.0015589919]
theoryS5up    = [0.2356440466,0.1262622587,0.0710529506,0.0418729272,0.0254159013,0.0159060157,0.0102035996,0.0066912067,0.0043317789,0.0028250178,0.0018632863,0.0012223954,0.0008402359]
theory_xsecS5_dn = [(a-b) for a,b in zip(theory_xsecS5,theoryS5dn)]
theory_xsecS5_up = [(a-b) for a,b in zip(theoryS5up,theory_xsecS5)]

# (T,B) doublet 1% width (100% tW) -- make into a second plot!
theory_xsecD1 = [0.252242,0.134215,0.075402,0.044362,0.026963,0.016895,0.010847,0.007132,0.004632,0.003028,0.002002,0.001317,0.000908]
theoryD1dn = [0.200280,0.105896,0.059040,0.034558,0.020869,0.013009,0.008319,0.005442,0.003516,0.002289,0.001508,0.000988,0.000678]
theoryD1up = [0.325140,0.174480,0.098776,0.058558,0.035833,0.022589,0.014578,0.009643,0.006300,0.004136,0.002749,0.001817,0.001259]
theory_xsecD1_dn = [(a-b) for a,b in zip(theory_xsecD1,theoryD1dn)]
theory_xsecD1_up = [(a-b) for a,b in zip(theoryD1up,theory_xsecD1)]

print('Theory xsec = ',theory_xsecS5)
theory_xsecS1_v    = TVectorD(len(theory_mass),array('d',theory_xsecS1))
theory_xsecS1_up_v = TVectorD(len(theory_mass),array('d',theory_xsecS1_up))
theory_xsecS1_dn_v = TVectorD(len(theory_mass),array('d',theory_xsecS1_dn))      

theory_xsecS1_gr = TGraphAsymmErrors(TVectorD(len(theory_mass),theory_mass),theory_xsecS1_v,TVectorD(len(theory_mass),masserr),TVectorD(len(theory_mass),masserr),theory_xsecS1_dn_v,theory_xsecS1_up_v)
theory_xsecS1_gr.SetFillStyle(3001)
red = TColor.GetColor("#e42536")
theory_xsecS1_gr.SetFillColor(red) #ROOT.kRed
			   
theoryS1 = TGraph(len(theory_mass))
for i in range(len(theory_mass)):
	theoryS1.SetPoint(i, theory_mass[i], theory_xsecS1[i])
        
theory_xsecS5_v    = TVectorD(len(theory_mass),array('d',theory_xsecS5))
theory_xsecS5_up_v = TVectorD(len(theory_mass),array('d',theory_xsecS5_up))
theory_xsecS5_dn_v = TVectorD(len(theory_mass),array('d',theory_xsecS5_dn))      

theory_xsecS5_gr = TGraphAsymmErrors(TVectorD(len(theory_mass),theory_mass),theory_xsecS5_v,TVectorD(len(theory_mass),masserr),TVectorD(len(theory_mass),masserr),theory_xsecS5_dn_v,theory_xsecS5_up_v)
theory_xsecS5_gr.SetFillStyle(3001)
blue = TColor.GetColor("#5790fc")
theory_xsecS5_gr.SetFillColor(blue) # ROOT.kBlue
			   
theoryS5 = TGraph(len(theory_mass))
for i in range(len(theory_mass)):
	theoryS5.SetPoint(i, theory_mass[i], theory_xsecS5[i])

theory_xsecD1_v    = TVectorD(len(theory_mass),array('d',theory_xsecD1))
theory_xsecD1_up_v = TVectorD(len(theory_mass),array('d',theory_xsecD1_up))
theory_xsecD1_dn_v = TVectorD(len(theory_mass),array('d',theory_xsecD1_dn))      

theory_xsecD1_gr = TGraphAsymmErrors(TVectorD(len(theory_mass),theory_mass),theory_xsecD1_v,TVectorD(len(theory_mass),masserr),TVectorD(len(theory_mass),masserr),theory_xsecD1_dn_v,theory_xsecD1_up_v)
theory_xsecD1_gr.SetFillStyle(3001)
violet = TColor.GetColor("#964a8b")
theory_xsecD1_gr.SetFillColor(violet) # ROOT.kViolet
			   
theoryD1 = TGraph(len(theory_mass))
for i in range(len(theory_mass)):
	theoryD1.SetPoint(i, theory_mass[i], theory_xsecD1[i])

def getSensitivity(index, theory, exp):
	a1=mass[index]-mass[index-1]
	b1=mass[index]-mass[index-1]
	c1=0
	a2=exp[index]-exp[index-1]
	b2=theory_xsecS5[theory]-theory_xsecS5[theory-1]
	c2=theory_xsecS5[theory-1]-exp[index-1]
	s = (c1*b2-c2*b1)/(a1*b2-a2*b1)
	t = (a1*c2-a2*c1)/(a1*b2-a2*b1)
	return mass[index-1]+s*(mass[index]-mass[index-1]), exp[index-1]+s*(exp[index]-exp[index-1])

def PlotLimits(limitDir,limitFile,tempKey):
    ljust_i = 10
    print
    print('mass'.ljust(ljust_i), 'observed'.ljust(ljust_i), 'expected'.ljust(ljust_i), '-2 Sigma'.ljust(ljust_i), '-1 Sigma'.ljust(ljust_i), '+1 Sigma'.ljust(ljust_i), '+2 Sigma'.ljust(ljust_i))

    f = open(limitDir+'/'+limitFile)       
    data = json.load(f)

    limExpected = 800
    limObserved = 800
    for i in range(len(mass)):
        key = str(mass[i])
        if '800' in key and '800.0' not in data.keys(): continue
        lims = {}

        if blind:
                lims[-1] = float(data[key]['exp0'])
                obs[i] = float(data[key]['exp0']) * xsec[i]
        else:
                lims[-1] = float(data[key]['obs'])
                obs[i] = float(data[key]['obs']) * xsec[i]
        obserr[i] = 0
        
        lims[.5] = float(data[key]['exp0'])
        exp[i] = float(data[key]['exp0']) * xsec[i]
        experr[i] = 0
        lims[.16] = float(data[key]['exp-1'])
        exp68L[i] = float(data[key]['exp-1']) * xsec[i]
        lims[.84] = float(data[key]['exp+1'])
        exp68H[i] = float(data[key]['exp+1']) * xsec[i]
        lims[.025] = float(data[key]['exp-2'])
        exp95L[i] = float(data[key]['exp-2']) * xsec[i]
        lims[.975] = float(data[key]['exp+2'])
        exp95H[i] = float(data[key]['exp+2']) * xsec[i]

        if i!=0:
                it = theory_mass.index(mass[i])
                itm1 = theory_mass.index(mass[i-1])
                if(exp[i]>theory_xsecS5[it] and exp[i-1]<theory_xsecS5[itm1]) or (exp[i]<theory_xsecS5[it] and exp[i-1]>theory_xsecS5[itm1]):
                        print('Calling getSensitivity. At point',i,'got exp of',exp[i],'and theory of',theory_xsecS5[it],'with previous exp of',exp[i-1],'and theory of',theory_xsecS5[itm1])
                        limExpected,ycross = getSensitivity(i,it,exp)
                if(obs[i]>theory_xsecS5[it] and obs[i-1]<theory_xsecS5[itm1]) or (obs[i]<theory_xsecS5[it] and obs[i-1]>theory_xsecS5[itm1]):
                        limObserved,ycross = getSensitivity(i,it,obs)
        
        exp95L[i]=(exp[i]-exp95L[i])
        exp95H[i]=abs(exp[i]-exp95H[i])
        exp68L[i]=(exp[i]-exp68L[i])
        exp68H[i]=abs(exp[i]-exp68H[i])

        round_i = 5
        print(str(mass[i]).ljust(ljust_i), str(round(lims[-1],round_i)).ljust(ljust_i), str(round(lims[.5],round_i)).ljust(ljust_i), str(round(lims[.025],round_i)).ljust(ljust_i), str(round(lims[.16],round_i)).ljust(ljust_i), str(round(lims[.84],round_i)).ljust(ljust_i), str(round(lims[.975],round_i)).ljust(ljust_i))
    print()

    mass2016 = array('d',[0.36, 0.17, 0.10, 0.07, 0.05, 0.04])
    mass2016v = TVectorD(len(mass6),mass2016)

    mass6v = TVectorD(len(mass6),mass6)
    massv = TVectorD(len(mass),mass)
    expv = TVectorD(len(mass),exp)
    exp68Hv = TVectorD(len(mass),exp68H)
    exp68Lv = TVectorD(len(mass),exp68L)
    exp95Hv = TVectorD(len(mass),exp95H)
    exp95Lv = TVectorD(len(mass),exp95L)

    obsv = TVectorD(len(mass),obs)
    masserrv = TVectorD(len(mass),masserr)
    obserrv = TVectorD(len(mass),obserr)
    experrv = TVectorD(len(mass),experr)       

    mass2016_gr = TGraph(mass6v,mass2016v)
    mass2016_gr.SetLineColor(ROOT.kBlue)
    mass2016_gr.SetLineWidth(2)
    observed = TGraphAsymmErrors(massv,obsv,masserrv,masserrv,obserrv,obserrv)
    observed.SetLineColor(ROOT.kBlack)
    observed.SetLineWidth(2)
    observed.SetMarkerStyle(20)
    expected = TGraphAsymmErrors(massv,expv,masserrv,masserrv,experrv,experrv)
    expected.SetLineColor(ROOT.kBlack)
    expected.SetLineWidth(2)
    expected.SetLineStyle(2)
    expected68 = TGraphAsymmErrors(massv,expv,masserrv,masserrv,exp68Lv,exp68Hv)
    green = TColor.GetColor("#607641")
    expected68.SetFillColor(green) # ROOT.kGreen+1
    expected95 = TGraphAsymmErrors(massv,expv,masserrv,masserrv,exp95Lv,exp95Hv)
    yellow = TColor.GetColor("#F5BB54")
    expected95.SetFillColor(yellow) # ROOT.kOrange
    #'''
    c1 = TCanvas("c1","Limits", 600, 500)
    c1.SetBottomMargin(0.12)
    c1.SetRightMargin(0.04)
    c1.SetLeftMargin(0.14)
    c1.SetTopMargin(0.08)
    c1.SetLogy()

    expected95.Draw("a3")
    expected95.GetYaxis().SetRangeUser(.002,10.1)
    expected95.GetXaxis().SetRangeUser(800,2000)
    expected95.GetXaxis().SetTitle(signal+" mass [GeV]")
    expected95.GetYaxis().SetTitle("#sigma (pp #rightarrow bqB) #font[12]{B}(B #rightarrow tW) [pb]")
    expected95.GetYaxis().SetTitleOffset(1.05)

    expected68.Draw("3same")
    expected.Draw("same")

    #mass2016_gr.Draw("same")

    if not blind: observed.Draw("lpsame")
    theory_xsecS1_gr.SetLineColor(2)
    theory_xsecS1_gr.SetLineStyle(1)
    theory_xsecS1_gr.SetLineWidth(2)
    theory_xsecS1_gr.Draw("3same") 
    theoryS1.SetLineColor(2)
    theoryS1.SetLineStyle(1)
    theoryS1.SetLineWidth(2)
    theoryS1.Draw("same")                                                             
    theory_xsecS5_gr.SetLineColor(ROOT.kBlue)
    theory_xsecS5_gr.SetLineStyle(1)
    theory_xsecS5_gr.SetLineWidth(2)
    theory_xsecS5_gr.Draw("3same") 
    theoryS5.SetLineColor(ROOT.kBlue)
    theoryS5.SetLineStyle(1)
    theoryS5.SetLineWidth(2)
    theoryS5.Draw("same")                                                             

    chLatex = TLatex()
    chLatex.SetNDC()
    chLatex.SetTextSize(0.045)
    chLatex.SetTextAlign(11) # align right
    chString = 'B #rightarrow tW'
    chLatex.DrawLatex(0.18, 0.82, chString)
    chString = 'e/#mu + jets'
    chLatex.DrawLatex(0.18, 0.77, chString)
    #chString = 'MC bkgd.'
    #if 'ABCDnn' in limitDir:
    #        chString = 'ABCDnn'
    #chLatex.DrawLatex(0.18, 0.72, chString)
        
    prelimTex=TLatex()
    prelimTex.SetNDC()
    prelimTex.SetTextAlign(31) # align right
    prelimTex.SetTextFont(42)
    prelimTex.SetTextSize(0.045)
    prelimTex.SetLineWidth(2)
    prelimTex.DrawLatex(0.95,0.93,str(lumiPlot)+" fb^{-1} (13 TeV)")
    
    prelimTex2=TLatex()
    prelimTex2.SetNDC()
    prelimTex2.SetTextFont(61)
    prelimTex2.SetLineWidth(2)
    prelimTex2.SetTextSize(0.06)
    prelimTex2.DrawLatex(0.14,0.93,"CMS")

    prelimTex3 = TLatex()
    prelimTex3.SetNDC()
    prelimTex3.SetTextAlign(12)
    #prelimTex3.SetTextFont(52)
    prelimTex3.SetTextSize(0.045)
    prelimTex3.SetLineWidth(2)
    #prelimTex3.DrawLatex(0.23,0.945,"Simulation work in progress")
    #prelimTex3.DrawLatex(0.15,0.945,"Private Work (CMS Simulation)")

    #legend = TLegend(.55,.5,.89,.89) # good for BR of 1
    legend = TLegend(.43,.45,.97,.88,"95% CL upper limits") # mixes
    if not blind: legend.AddEntry(observed , 'Observed', "lp")
    legend.AddEntry(expected, 'Expected', "l")
    legend.AddEntry(expected68, '68% expected', "f")
    legend.AddEntry(expected95, '95% expected', "f")    
    #legend.AddEntry(mass2016_gr, '2016 expected', 'l')
    legend.AddEntry(theory_xsecS5_gr, 'pp #rightarrow qbtW, #Gamma/M = 5%','f')
    legend.AddEntry(theory_xsecS1_gr, 'pp #rightarrow qbtW, #Gamma/M = 1%','f')
    legend.AddEntry(0,'B singlet','')
    legend.SetShadowColor(0)
    legend.SetFillStyle(0)
    legend.SetBorderSize(0)
    legend.SetFillColor(0)
    legend.SetLineColor(0)
    legend.Draw()
    
    c1.RedrawAxis()
    
    folder = os.getcwd()+'/' #'/uscms_data/d3/jmanagan/CMSSW_10_2_10/src/tptp_2016/combineLimits/'
    outDir=folder+limitDir+'/'
    #outDir = folder
    if not os.path.exists(outDir): os.system('mkdir -p '+outDir)
    c1.SaveAs(outDir+'/LimitPlot_singlet_'+histPrefix+saveKey+'_'+tempKey+'.root')
    c1.SaveAs(outDir+'/LimitPlot_singlet_'+histPrefix+saveKey+'_'+tempKey+'.pdf')
    c1.SaveAs(outDir+'/LimitPlot_singlet_'+histPrefix+saveKey+'_'+tempKey+'.png')
    c1.SaveAs(outDir+'/LimitPlot_singlet_'+histPrefix+saveKey+'_'+tempKey+'.C')

    
    c2 = TCanvas("c2","Limits", 600, 500)
    c2.SetBottomMargin(0.12)
    c2.SetRightMargin(0.04)
    c2.SetLeftMargin(0.14)
    c2.SetTopMargin(0.08)
    c2.SetLogy()

    expected95.Draw("a3")
    expected95.GetYaxis().SetRangeUser(.002,10.1)
    expected95.GetXaxis().SetRangeUser(800,2000)
    expected95.GetXaxis().SetTitle(signal+" mass [GeV]")
    expected95.GetYaxis().SetTitle("#sigma (pp #rightarrow bqB) #font[12]{B}(B #rightarrow tW) [pb]")
    expected95.GetYaxis().SetTitleOffset(1.05)

    expected68.Draw("3same")
    expected.Draw("same")

    #mass2016_gr.Draw("same")

    if not blind: observed.Draw("lpsame")
    theory_xsecD1_gr.SetLineColor(ROOT.kViolet)
    theory_xsecD1_gr.SetLineStyle(1)
    theory_xsecD1_gr.SetLineWidth(2)
    theory_xsecD1_gr.Draw("3same") 
    theoryD1.SetLineColor(ROOT.kViolet)
    theoryD1.SetLineStyle(1)
    theoryD1.SetLineWidth(2)
    theoryD1.Draw("same")                                                             

    chLatex = TLatex()
    chLatex.SetNDC()
    chLatex.SetTextSize(0.045)
    chLatex.SetTextAlign(11) # align right
    chString = 'B #rightarrow tW'
    chLatex.DrawLatex(0.18, 0.82, chString)
    chString = 'e/#mu + jets'
    chLatex.DrawLatex(0.18, 0.77, chString)
    #chString = 'MC bkgd.'
    #if 'ABCDnn' in limitDir:
    #        chString = 'ABCDnn'
    #chLatex.DrawLatex(0.18, 0.72, chString)
        
    prelimTex=TLatex()
    prelimTex.SetNDC()
    prelimTex.SetTextAlign(31) # align right
    prelimTex.SetTextFont(42)
    prelimTex.SetTextSize(0.045)
    prelimTex.SetLineWidth(2)
    prelimTex.DrawLatex(0.95,0.93,str(lumiPlot)+" fb^{-1} (13 TeV)")
    
    prelimTex2=TLatex()
    prelimTex2.SetNDC()
    prelimTex2.SetTextFont(61)
    prelimTex2.SetLineWidth(2)
    prelimTex2.SetTextSize(0.06)
    prelimTex2.DrawLatex(0.14,0.93,"CMS")

    prelimTex3 = TLatex()
    prelimTex3.SetNDC()
    prelimTex3.SetTextAlign(12)
    #prelimTex3.SetTextFont(52)
    prelimTex3.SetTextSize(0.045)
    prelimTex3.SetLineWidth(2)
    #prelimTex3.DrawLatex(0.23,0.945,"Simulation work in progress")
    #prelimTex3.DrawLatex(0.15,0.945,"Private Work (CMS Simulation)")

    #legend = TLegend(.55,.5,.89,.89) # good for BR of 1
    legend = TLegend(.43,.45,.97,.88,"95% CL upper limits") # mixes
    if not blind: legend.AddEntry(observed , 'Observed', "lp")
    legend.AddEntry(expected, 'Expected', "l")
    legend.AddEntry(expected68, '68% expected', "f")
    legend.AddEntry(expected95, '95% expected', "f")    
    #legend.AddEntry(mass2016_gr, '2016 expected', 'l')
    legend.AddEntry(theory_xsecD1_gr, 'pp #rightarrow qbtW, (T,B) #Gamma/M = 1%','f')
    legend.AddEntry(0,'(T,B) doublet','')
    legend.SetShadowColor(0)
    legend.SetFillStyle(0)
    legend.SetBorderSize(0)
    legend.SetFillColor(0)
    legend.SetLineColor(0)
    legend.Draw()
    
    c2.RedrawAxis()
    
    folder = os.getcwd()+'/' #'/uscms_data/d3/jmanagan/CMSSW_10_2_10/src/tptp_2016/combineLimits/'
    outDir=folder+limitDir+'/'
    #outDir = folder
    if not os.path.exists(outDir): os.system('mkdir -p '+outDir)
    c2.SaveAs(outDir+'/LimitPlot_doublet_'+histPrefix+saveKey+'_'+tempKey+'.root')
    c2.SaveAs(outDir+'/LimitPlot_doublet_'+histPrefix+saveKey+'_'+tempKey+'.pdf')
    c2.SaveAs(outDir+'/LimitPlot_doublet_'+histPrefix+saveKey+'_'+tempKey+'.png')
    c2.SaveAs(outDir+'/LimitPlot_doublet_'+histPrefix+saveKey+'_'+tempKey+'.C')

    f.close()

    return int(round(limExpected)), int(round(limObserved))


tempKeys = ['BToTW']

expLims = []
obsLims = []
for tempKey in tempKeys:
        #print(tempKey)
        #exit()
        if blind: 
                if not morphed:
                        expTemp,obsTemp = PlotLimits(limitDir,'limits_cmb_cmb.json',tempKey)
                else:
                        expTemp,obsTemp = PlotLimits(limitDir,'limitsM_cmb_cmb.json',tempKey)
        else:
                expTemp,obsTemp = PlotLimits(limitDir,'limitsUB_cmb_cmb.json',tempKey)
        expLims.append(expTemp)
        obsLims.append(obsTemp)

print("Expected:",expLims)
print("Observed:",obsLims)
