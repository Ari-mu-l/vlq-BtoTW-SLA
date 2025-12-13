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

# 2016 line starts with 700 but ours start with 800
# data extraction: https://plotdigitizer.com/app
mass2016 = array('d', [800,900,1000,1100,1200,1300,1400,1500,1600,1700,1800]) #700
# 2016 single production: 1%
if 'BprimeT' in limitDir:
        exp_xsec2016 = [0.19391,0.153400,0.11771,0.09311,0.07992,0.06453,0.05538,0.048511,0.04293,0.03760,0.03227]
else:
        exp_xsec2016 = [0.36178,0.24041,0.17130,0.12452,0.09803,0.08031,0.06847,0.05666,0.04977,0.04118,0.03728]
# SS pi/2
exp_xsecTpi2 = [14.90625,6.53125,2.90625,2.1796875,1.7421875,1.4296875,1.25390625,1.04296875,0.80859375,0.51953125]

# https://docs.google.com/spreadsheets/d/1hrvXSGU1lbLPtbK0wvMwwVQTHFAeTzPX_4GVC4hKLHw/edit?gid=0
# Calculation of NWA tW cross section based on TopPartners_SingleProduction github (see links within).
if 'BprimeT' in limitDir:
        theory_mass = array('d', [800,900,1000,1100,1200,1300,1400,1500,1600,1700,1800,1900,2000])
        # Singlet 1% width
        theory_xsecS1 = [0.0359978441,0.0207371919,0.0123926795,0.0076438080,0.0048422945,0.0031387045,0.0020719745,0.0013860395,0.0009611403,0.0006701036,0.0004713479,0.0003344701,0.0002398678]
        theoryS1dn    = [0.0286542839,0.0164238560,0.0097530388,0.0059851016,0.0037769897,0.0024356347,0.0016016363,0.0010672504,0.0007371946,0.0005139695,0.0003601098,0.0002545317,0.0001820597]
        theoryS1up    = [0.0462932276,0.0268339264,0.0161476614,0.0100210322,0.0063821441,0.0041556448,0.0027577980,0.0018531348,0.0012908114,0.0009006192,0.0006358483,0.0004528725,0.0003262202]
else:
        theory_mass = array('d', [800,900,1000,1100,1200,1300,1400,1500,1600,1700,1800,1900,2000])
        # Singlet 1% width
        theory_xsecS1 = [0.0593561830,0.0320056423,0.0181489018,0.0107504306,0.0065674164,0.0041314326,0.0026606518,0.0017539205,0.0011414437,0.0007473592,0.0004948968,0.0003259721,0.0002249628]
        theoryS1dn    = [0.0471288093,0.0252524517,0.0142105901,0.0083745854,0.0050831803,0.0031812031,0.0020407199,0.0013382413,0.0008663558,0.0005650036,0.0003726573,0.0002444791,0.0001680472]
        theoryS1up    = [0.0765101199,0.0416073349,0.0237750614,0.0141905684,0.0087280963,0.0055237254,0.0035759160,0.0023713005,0.0015523635,0.0010208927,0.0006794933,0.0004495155,0.0003117984]

theory_xsecS1_dn = [(a-b) for a,b in zip(theory_xsecS1,theoryS1dn)]
theory_xsecS1_up = [(a-b) for a,b in zip(theoryS1up,theory_xsecS1)]

# Singlet 5% width
if 'BprimeT' in	limitDir:
        theory_xsecS5 = [0.1799892207,0.1036859596,0.0619633975,0.0382190398,0.0242114724,0.0156935226,0.0103598723,0.0069301975,0.0048057013,0.0033505180,0.0023567396,0.0016723504,0.0011993390]
        theoryS5dn    = [0.1432714197,0.0821192800,0.0487651938,0.0299255082,0.0188849485,0.0121781735,0.0080081813,0.0053362521,0.0036859729,0.0025698473,0.0018005490,0.0012726587,0.0009102983]
        theoryS5up    = [0.2314661378,0.1341696318,0.0807383069,0.0501051612,0.0319107207,0.0207782239,0.0137889900,0.0092656741,0.0064540569,0.0045030961,0.0031792417,0.0022643624,0.0016311010]
else:
        theory_xsecS5 = [0.2967809151,0.1600282113,0.0907445091,0.0537521530,0.0328370818,0.0206571632,0.0133032589,0.0087696024,0.0057072186,0.0037367961,0.0024744838,0.0016298605,0.0011248138]
        theoryS5dn    = [0.2356440466,0.1262622587,0.0710529506,0.0418729272,0.0254159013,0.0159060157,0.0102035996,0.0066912067,0.0043317789,0.0028250178,0.0018632863,0.0012223954,0.0008402359]
        theoryS5up    = [0.3825505996,0.2080366747,0.1188753070,0.0709528420,0.0436404817,0.0276186272,0.0178795800,0.0118565025,0.0077618173,0.0051044635,0.0033974663,0.0022475777,0.0015589919]
        
theory_xsecS5_dn = [(a-b) for a,b in zip(theory_xsecS5,theoryS5dn)]
theory_xsecS5_up = [(a-b) for a,b in zip(theoryS5up,theory_xsecS5)]

# (T,B) doublet 1% width (100% tW) -- make into a second plot!
if 'BprimeT' in limitDir:
        theory_xsecD1 = [0.152977,0.086961,0.051487,0.031542,0.019880,0.012835,0.008447,0.005636,0.003901,0.002715,0.001907,0.001352,0.000968]
        theoryD1dn = [0.121770,0.068873,0.040520,0.024698,0.015507,0.009960,0.006529,0.004340,0.002992,0.002082,0.001457,0.001029,0.000735]
        theoryD1up = [0.196729,0.112528,0.067087,0.041352,0.026202,0.016994,0.011243,0.007536,0.005239,0.003649,0.002573,0.001830,0.001317]
else:
        theory_xsecD1 = [0.252242,0.134215,0.075402,0.044362,0.026963,0.016895,0.010847,0.007132,0.004632,0.003028,0.002002,0.001317,0.000908]
        theoryD1dn = [0.200280,0.105896,0.059040,0.034558,0.020869,0.013009,0.008319,0.005442,0.003516,0.002289,0.001508,0.000988,0.000678]
        theoryD1up = [0.325140,0.174480,0.098776,0.058558,0.035833,0.022589,0.014578,0.009643,0.006300,0.004136,0.002749,0.001817,0.001259]
        
theory_xsecD1_dn = [(a-b) for a,b in zip(theory_xsecD1,theoryD1dn)]
theory_xsecD1_up = [(a-b) for a,b in zip(theoryD1up,theory_xsecD1)]

#print('Theory xsec = ',theory_xsecS5)
print('Theory xsec = ',theory_xsecD1) 
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

exp_xsecTpi2_gr = TGraph(len(mass))
for i in range(len(mass)):
        exp_xsecTpi2_gr.SetPoint(i, mass[i], exp_xsecTpi2[i] * multiplier)
exp_xsecTpi2_gr.SetLineColor(ROOT.kBlack)

exp_xsec2016_gr = TGraph(len(mass2016))
for i in range(len(mass2016)):
	exp_xsec2016_gr.SetPoint(i, mass2016[i], exp_xsec2016[i])
purple = TColor.GetColor("#7a21dd")
exp_xsec2016_gr.SetLineColor(purple)


        
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
#violet = TColor.GetColor("#964a8b")
theory_xsecD1_gr.SetFillColor(red) # ROOT.kViolet
			   
theoryD1 = TGraph(len(theory_mass))
for i in range(len(theory_mass)):
	theoryD1.SetPoint(i, theory_mass[i], theory_xsecD1[i])

def getSensitivity(index, theory, exp, theory_xsecList):
    #print(mass[index],mass[index-1])
    a1=mass[index]-mass[index-1]
    b1=mass[index]-mass[index-1]
    c1=0
    a2=exp[index]-exp[index-1]
    b2=theory_xsecList[theory]-theory_xsecList[theory-1]
    c2=theory_xsecList[theory-1]-exp[index-1]
    s = (c1*b2-c2*b1)/(a1*b2-a2*b1)
    t = (a1*c2-a2*c1)/(a1*b2-a2*b1)
    return mass[index-1]+s*(mass[index]-mass[index-1]), exp[index-1]+s*(exp[index]-exp[index-1])

def PlotLimits(limitDir,limitFile,tempKey):
    ljust_i = 10
    print
    print('mass'.ljust(ljust_i), 'observed'.ljust(ljust_i), 'expected'.ljust(ljust_i), '-2 Sigma'.ljust(ljust_i), '-1 Sigma'.ljust(ljust_i), '+1 Sigma'.ljust(ljust_i), '+2 Sigma'.ljust(ljust_i))

    f = open(limitDir+'/'+limitFile)       
    data = json.load(f)

    limExpectedS = 800
    limObservedS = 800
    limExpectedD = 800
    limObservedD = 800
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

        #print(exp[i])

        if i!=0:
                it = theory_mass.index(mass[i])
                itm1 = theory_mass.index(mass[i-1])
                if(exp[i]>theory_xsecS5[it] and exp[i-1]<theory_xsecS5[itm1]) or (exp[i]<theory_xsecS5[it] and exp[i-1]>theory_xsecS5[itm1]):
                        print('Calling getSensitivity. At point',i,'got exp of',exp[i],'and theory of',theory_xsecS5[it],'with previous exp of',exp[i-1],'and theory of',theory_xsecS5[itm1])
                        limExpectedS,ycrossS = getSensitivity(i,it,exp,theory_xsecS5)
                if(obs[i]>theory_xsecS5[it] and obs[i-1]<theory_xsecS5[itm1]) or (obs[i]<theory_xsecS5[it] and obs[i-1]>theory_xsecS5[itm1]):
                        limObservedS,ycrossS = getSensitivity(i,it,obs,theory_xsecS5)

                if(exp[i]>theory_xsecD1[it] and exp[i-1]<theory_xsecD1[itm1]) or (exp[i]<theory_xsecD1[it] and exp[i-1]>theory_xsecD1[itm1]):
                        print('Calling getSensitivity. At point',i,'got exp of',exp[i],'and theory of',theory_xsecD1[it],'with previous exp of',exp[i-1],'and theory of',theory_xsecD1[itm1])
                        limExpectedD,ycrossD = getSensitivity(i,it,exp,theory_xsecD1)
                if(obs[i]>theory_xsecD1[it] and obs[i-1]<theory_xsecD1[itm1]) or (obs[i]<theory_xsecD1[it] and obs[i-1]>theory_xsecD1[itm1]):
                        limObservedD,ycrossD = getSensitivity(i,it,obs,theory_xsecD1)
        
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

    # mass2016_gr = TGraph(mass6v,mass2016v)
    # mass2016_gr.SetLineColor(ROOT.kBlue)
    # mass2016_gr.SetLineWidth(2)
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
    expected95.GetXaxis().SetTitle("m_{B} [GeV]")
    #expected95.GetXaxis().SetTitle(signal+" mass [GeV]")

    if 'BprimeT' in limitDir:
            expected95.GetYaxis().SetTitle("\\sigma\\mbox{(pp}\\rightarrow\\mbox{tqB)}\\mathscr{B}\mbox{(B}\\rightarrow\mbox{tW) [pb]}")
            #expected95.GetYaxis().SetTitle("#sigma (pp #rightarrow tqB) #font[12]{B}(B #rightarrow tW) [pb]")
    else:
            expected95.GetYaxis().SetTitle("\\sigma\\mbox{(pp}\\rightarrow\\mbox{bqB)}\\mathscr{B}\mbox{(B}\\rightarrow\mbox{tW) [pb]}")
            #expected95.GetYaxis().SetTitle("#sigma (pp #rightarrow bqB) #font[12]{B}(B #rightarrow tW) [pb]")
    expected95.GetYaxis().SetTitleOffset(1.05)

    expected68.Draw("3same")
    #expected.Draw("same")

    #mass2016_gr.Draw("same")

    #if not blind: observed.Draw("lpsame")
    theory_xsecS1_gr.SetLineColor(red)
    theory_xsecS1_gr.SetLineStyle(1)
    theory_xsecS1_gr.SetLineWidth(2)
    theory_xsecS1_gr.Draw("3same") 
    theoryS1.SetLineColor(red)
    theoryS1.SetLineStyle(1)
    theoryS1.SetLineWidth(2)
    theoryS1.Draw("same")                                                             
    theory_xsecS5_gr.SetLineColor(blue)
    theory_xsecS5_gr.SetLineStyle(1)
    theory_xsecS5_gr.SetLineWidth(2)
    theory_xsecS5_gr.Draw("3same") 
    theoryS5.SetLineColor(blue)
    theoryS5.SetLineStyle(1)
    theoryS5.SetLineWidth(2)
    theoryS5.Draw("same")

    # if 'BprimeT' in limitDir:
    #         exp_xsecTpi2_gr.SetLineWidth(2)
    #         exp_xsecTpi2_gr.Draw("same")

    exp_xsec2016_gr.SetLineWidth(2)
    exp_xsec2016_gr.Draw("same")
    
    expected.Draw("same")
    if not blind: observed.Draw("lpsame")

    chLatex = TLatex()
    chLatex.SetNDC()
    chLatex.SetTextSize(0.045)
    chLatex.SetTextAlign(11) # align right
    chString = 'B #rightarrow tW'
    chLatex.DrawLatex(0.18, 0.82, chString)
    #chString = 'e/#mu + jets'
    #chLatex.DrawLatex(0.18, 0.77, chString)
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
    #legend = TLegend(.43,.45,.97,.88,"95% CL upper limits") # mixes
    legend = TLegend(.45,.45,.99,.88,"95% CL upper limits") # mixes
    if not blind: legend.AddEntry(observed , 'Observed', "lp")
    legend.AddEntry(expected, 'Expected', "l")
    legend.AddEntry(expected68, '68% expected', "f")
    legend.AddEntry(expected95, '95% expected', "f")    
    #legend.AddEntry(mass2016_gr, '2016 expected', 'l')
    if 'BprimeT' in limitDir:
            legend.AddEntry(theory_xsecS5_gr, 'pp #rightarrow tqtW, #Gamma/M = 5%','f')
            legend.AddEntry(theory_xsecS1_gr, 'pp #rightarrow tqtW, #Gamma/M = 1%','f')
    else:
            legend.AddEntry(theory_xsecS5_gr, 'pp #rightarrow bqtW, #Gamma/M = 5%','f')
            legend.AddEntry(theory_xsecS1_gr, 'pp #rightarrow bqtW, #Gamma/M = 1%','f')
            
    if 'BprimeT' in limitDir:
            legend.AddEntry(exp_xsec2016_gr, '2016 t-associated', 'l')
            #legend.AddEntry(exp_xsecTpi2_gr, 'SS pi/2','l')
    else:
            legend.AddEntry(exp_xsec2016_gr, '2016 b-associated', 'l')
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
    expected95.GetXaxis().SetTitle("m_{B} [GeV]")
    #expected95.GetXaxis().SetTitle(signal+" mass [GeV]")
    if 'BprimeT' in limitDir:
            expected95.GetYaxis().SetTitle("\\sigma\\mbox{(pp}\\rightarrow\\mbox{tqB)}\\mathscr{B}\mbox{(B}\\rightarrow\mbox{tW) [pb]}")
            #expected95.GetYaxis().SetTitle("#sigma (pp #rightarrow tqB) #font[12]{B}(B #rightarrow tW) [pb]")
    else:
            expected95.GetYaxis().SetTitle("\\sigma\\mbox{(pp}\\rightarrow\\mbox{bqB)}\\mathscr{B}\mbox{(B}\\rightarrow\mbox{tW) [pb]}")
            #expected95.GetYaxis().SetTitle("#sigma (pp #rightarrow bqB) #font[12]{B}(B #rightarrow tW) [pb]")
    expected95.GetYaxis().SetTitleOffset(1.05)

    expected68.Draw("3same")
    #expected.Draw("same")

    #mass2016_gr.Draw("same")

    #if not blind: observed.Draw("lpsame")
    theory_xsecD1_gr.SetLineColor(red)
    theory_xsecD1_gr.SetLineStyle(1)
    theory_xsecD1_gr.SetLineWidth(2)
    theory_xsecD1_gr.Draw("3same") 
    theoryD1.SetLineColor(red)
    theoryD1.SetLineStyle(1)
    theoryD1.SetLineWidth(2)
    theoryD1.Draw("same")

    expected.Draw("same")
    if not blind: observed.Draw("lpsame")

    chLatex = TLatex()
    chLatex.SetNDC()
    chLatex.SetTextSize(0.045)
    chLatex.SetTextAlign(11) # align right
    chString = 'B #rightarrow tW'
    chLatex.DrawLatex(0.18, 0.82, chString)
    #chString = 'e/#mu + jets'
    #chLatex.DrawLatex(0.18, 0.77, chString)
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
    #legend = TLegend(.43,.45,.97,.88,"95% CL upper limits") # mixes
    legend = TLegend(.45,.5,.99,.88,"95% CL upper limits")
    if not blind: legend.AddEntry(observed , 'Observed', "lp")
    legend.AddEntry(expected, 'Expected', "l")
    legend.AddEntry(expected68, '68% expected', "f")
    legend.AddEntry(expected95, '95% expected', "f")    
    #legend.AddEntry(mass2016_gr, '2016 expected', 'l')
    if 'BprimeT' in limitDir:
            legend.AddEntry(theory_xsecD1_gr, 'pp #rightarrow tqtW, #Gamma/M = 1%','f')
    else:
            legend.AddEntry(theory_xsecD1_gr, 'pp #rightarrow bqtW, #Gamma/M = 1%','f')
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

    return int(round(limExpectedS)), int(round(limObservedS)), int(round(limExpectedD)), int(round(limObservedD))


tempKeys = ['BToTW']

expLims = []
obsLims = []
for tempKey in tempKeys:
        #print(tempKey)
        #exit()
        if blind: 
                if not morphed:
                        expTempS,obsTempS,expTempD,obsTempD = PlotLimits(limitDir,'limitsUB_cmb_cmb.json',tempKey) # TEMP: for t-associated SS1p2 test
                else:
                        expTempS,obsTempS,expTempD,obsTempD = PlotLimits(limitDir,'limitsM_cmb_cmb.json',tempKey)
        else:
                expTempS,obsTempS,expTempD,obsTempD = PlotLimits(limitDir,'limitsUB_cmb_cmb.json',tempKey)
        expLims.append([expTempS,expTempD])
        obsLims.append([obsTempS,obsTempD])

print("Singlet Expected:",expLims[0][0])
print("Singlet Observed:",obsLims[0][0])
print("Doublet Expected:",expLims[0][1])
print("Doublet Observed:",obsLims[0][1])
