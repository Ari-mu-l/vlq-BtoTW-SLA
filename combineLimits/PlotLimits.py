from ROOT import gROOT, TFile, TH1D, TCanvas, TLegend, TVectorD, TGraphAsymmErrors, TGraph, TLatex
from array import array
import math
from math import *
import os,sys
import json

gROOT.SetBatch(1)

from tdrStyle import *
setTDRStyle()

limitDir = str(sys.argv[1])
# stat='0.3'
# if len(sys.argv) > 2: stat = str(sys.argv[2])
multiplier = 0.01 ## should match signalScale in the fits
# if len(sys.argv) > 3: multiplier = float(sys.argv[3])
signal = 'B'
# if len(sys.argv) > 4: signal = str(sys.argv[4])
# combination=False
# if len(sys.argv) > 5: combination = bool(eval(sys.argv[5]))

blind=True
morphed=False
ACLS = False
saveKey=''
if ACLS: saveKey+='_ACLS'
if blind: saveKey+='_blind'
if morphed: saveKey+='_morphed'

lumiPlot = '138'# '97.4'#
lumiStr = '138'

discriminant='BToTW'
histPrefix=discriminant+'_'+str(lumiStr)+'fb'

mass3 = array('d', [800,1400,2000])
mass3err = array('d', [0,0,0])
mass3_str = ['800','1400','2000']

mass = array('d', [800,1000,1200,1300,1400,1500,1600,1700,1800,2000])
masserr = array('d', [0,0,0,0,0,0,0,0,0,0])
mass_str = ['800','1000','1200','1300','1400','1500','1600','1700','1800','2000']

exp   =array('d',[0 for i in range(len(mass))])
experr=array('d',[0 for i in range(len(mass))])
obs   =array('d',[0 for i in range(len(mass))])
obserr=array('d',[0 for i in range(len(mass))]) 
exp68H=array('d',[0 for i in range(len(mass))])
exp68L=array('d',[0 for i in range(len(mass))])
exp95H=array('d',[0 for i in range(len(mass))])
exp95L=array('d',[0 for i in range(len(mass))])

xsec = array('d',[multiplier for i in range(len(mass))])
# https://github.com/CrossSectionsLHC/TopPartners_SingleProduction/blob/master/interpreted_tables/sigma_B_Bbj.csv
theory_mass = array('d', [800,900,1000,1100,1200,1300,1400,1500,1600,1700,1800,1900,2000])

# From Xanda, for "singlet" B prod with a b quark, for 1% width, for 50% tW
theory_xsec = [0.1187124, 0.0640113, 0.0362987, 0.0215009, 0.0131348, 0.0082629, 0.0053213, 0.0035078, 0.0022829, 0.0014947, 0.0009898, 0.0006519, 0.0004499]
theoryDn = [0.0942576, 0.0505049, 0.0284212, 0.0167492, 0.0101664, 0.0063624, 0.0040814, 0.0026765, 0.0017327, 0.0011300, 0.0007453, 0.0004890, 0.0003361]
theoryUp = [0.1530202, 0.0832147, 0.0475501, 0.0283811, 0.0174562, 0.0110475, 0.0071518, 0.0047426, 0.0031047, 0.0020418, 0.0013590, 0.0008990, 0.0006236]
theory_xsec_dn = [(a-b) for a,b in zip(theory_xsec,theoryDn)]
theory_xsec_up = [(a-b) for a,b in zip(theoryUp,theory_xsec)]

# From Xanda, for "singlet" B prod with a b quark, for 5% width, for 50% tW
theory_xsec5 = [0.5935618293464724,0.3200564222002925,0.18148901798364311,0.10750430583938862,0.06567416344453472,0.04131432636617531,0.02660651777788213,0.01753920486457393,0.011414437132957303,0.007473592170418943,0.004948967609898932,0.0032597210500001765,0.002249627608203919]
theoryDn5 = [0.4712880925010991, 0.25252451711603074, 0.14210590108119256, 0.08374585424888374, 0.050831802506069876, 0.03181203130195499, 0.020407199135635594, 0.013382413311669908, 0.008663557783914594, 0.005650035680836721, 0.0037265726102538956, 0.0024447907875001324, 0.0016804718233283274]
theoryUp5 = [0.7651011980276029, 0.4160733488603803, 0.2377506135585725, 0.141905683707993, 0.08728096321778664, 0.05523725435157639, 0.03575915989347358, 0.023713004976903953, 0.01552363450082193, 0.010208926904792278, 0.006794932528391234, 0.004495155327950243, 0.0031179838649706315]
theory_xsec5_dn = [(a-b) for a,b in zip(theory_xsec5,theoryDn5)]
theory_xsec5_up = [(a-b) for a,b in zip(theoryUp5,theory_xsec5)]

## Not needed as of Oct2024 samples -- we have now divided the BR in the signal histograms
# theory_xsec_dn = [2*(a-b) for a,b in zip(theory_xsec,theoryDn)]
# theory_xsec_up = [2*(a-b) for a,b in zip(theoryUp,theory_xsec)]
# theory_xsec = [2*a for a in theory_xsec] # multiplying 50% tW by 2 to become 100% tW
# theory_xsec5_dn = [2*(a-b) for a,b in zip(theory_xsec5,theoryDn5)]
# theory_xsec5_up = [2*(a-b) for a,b in zip(theoryUp5,theory_xsec5)]
# theory_xsec5 = [2*a for a in theory_xsec5] # multiplying 50% tW by 2 to become 100% tW

print('Theory xsec = ',theory_xsec)
#theory_xsec_up = [item/1000 for item in xsecErrUp]
#theory_xsec_dn = [item/1000 for item in xsecErrDn]

theory_xsec_v    = TVectorD(len(theory_mass),array('d',theory_xsec))
theory_xsec_up_v = TVectorD(len(theory_mass),array('d',theory_xsec_up))
theory_xsec_dn_v = TVectorD(len(theory_mass),array('d',theory_xsec_dn))      

theory_xsec_gr = TGraphAsymmErrors(TVectorD(len(theory_mass),theory_mass),theory_xsec_v,TVectorD(len(theory_mass),masserr),TVectorD(len(theory_mass),masserr),theory_xsec_dn_v,theory_xsec_up_v)
theory_xsec_gr.SetFillStyle(3001)
theory_xsec_gr.SetFillColor(ROOT.kRed)
			   
theory = TGraph(len(theory_mass))
for i in range(len(theory_mass)):
	theory.SetPoint(i, theory_mass[i], theory_xsec[i])
        
theory_xsec5_v    = TVectorD(len(theory_mass),array('d',theory_xsec5))
theory_xsec5_up_v = TVectorD(len(theory_mass),array('d',theory_xsec5_up))
theory_xsec5_dn_v = TVectorD(len(theory_mass),array('d',theory_xsec5_dn))      

theory_xsec5_gr = TGraphAsymmErrors(TVectorD(len(theory_mass),theory_mass),theory_xsec5_v,TVectorD(len(theory_mass),masserr),TVectorD(len(theory_mass),masserr),theory_xsec5_dn_v,theory_xsec5_up_v)
theory_xsec5_gr.SetFillStyle(3001)
theory_xsec5_gr.SetFillColor(ROOT.kBlue)
			   
theory5 = TGraph(len(theory_mass))
for i in range(len(theory_mass)):
	theory5.SetPoint(i, theory_mass[i], theory_xsec5[i])

def getSensitivity(index, theory, exp):
	a1=mass[index]-mass[index-1]
	b1=mass[index]-mass[index-1]
	c1=0
	a2=exp[index]-exp[index-1]
	b2=theory_xsec[theory]-theory_xsec[theory-1]
	c2=theory_xsec[theory-1]-exp[index-1]
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
                if(exp[i]>theory_xsec[it] and exp[i-1]<theory_xsec[itm1]) or (exp[i]<theory_xsec[it] and exp[i-1]>theory_xsec[itm1]):
                        print('Calling getSensitivity. At point',i,'got exp of',exp[i],'and theory of',theory_xsec[it],'with previous exp of',exp[i-1],'and theory of',theory_xsec[itm1])
                        limExpected,ycross = getSensitivity(i,it,exp)
                if(obs[i]>theory_xsec[it] and obs[i-1]<theory_xsec[itm1]) or (obs[i]<theory_xsec[it] and obs[i-1]>theory_xsec[itm1]):
                        limObserved,ycross = getSensitivity(i,it,obs)
        
        exp95L[i]=(exp[i]-exp95L[i])
        exp95H[i]=abs(exp[i]-exp95H[i])
        exp68L[i]=(exp[i]-exp68L[i])
        exp68H[i]=abs(exp[i]-exp68H[i])

        round_i = 5
        print(str(mass[i]).ljust(ljust_i), str(round(lims[-1],round_i)).ljust(ljust_i), str(round(lims[.5],round_i)).ljust(ljust_i), str(round(lims[.025],round_i)).ljust(ljust_i), str(round(lims[.16],round_i)).ljust(ljust_i), str(round(lims[.84],round_i)).ljust(ljust_i), str(round(lims[.975],round_i)).ljust(ljust_i))
    print()
    # signExp = "="
    # signObs = "="
    # if limExpected==800: signExp = "<"
    # if limObserved==800: signObs = "<"
    # print "Expected lower limit "+signExp,int(round(limExpected)),"GeV"
    # print "Observed lower limit "+signObs,int(round(limObserved)),"GeV"
    # print

    may2022mass = array('d',[0.2451171875,0.0380859375,0.01123046875]) #May 2022
    dec2022mass = array('d',[0.11279296875,0.01416015625,0.00537109375]) #Dec 2022
    mar2023mass = array('d',[0.0990625,0.0137109375,0.00513671875]) #Mar 2023
    may2022massv = TVectorD(len(mass3),may2022mass)
    dec2022massv = TVectorD(len(mass3),dec2022mass)
    mar2023massv = TVectorD(len(mass3),mar2023mass)

    mass3v = TVectorD(len(mass3),mass3)
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

    may2022mass_gr = TGraph(mass3v,may2022massv)
    may2022mass_gr.SetLineColor(ROOT.kRed)
    may2022mass_gr.SetLineWidth(2)
    dec2022mass_gr = TGraph(mass3v,dec2022massv)
    dec2022mass_gr.SetLineColor(ROOT.kMagenta)
    dec2022mass_gr.SetLineWidth(2)
    mar2023mass_gr = TGraph(mass3v,mar2023massv)
    mar2023mass_gr.SetLineColor(ROOT.kBlue)
    mar2023mass_gr.SetLineWidth(2)
    observed = TGraphAsymmErrors(massv,obsv,masserrv,masserrv,obserrv,obserrv)
    observed.SetLineColor(ROOT.kBlack)
    observed.SetLineWidth(2)
    observed.SetMarkerStyle(20)
    expected = TGraphAsymmErrors(massv,expv,masserrv,masserrv,experrv,experrv)
    expected.SetLineColor(ROOT.kBlack)
    expected.SetLineWidth(2)
    expected.SetLineStyle(2)
    expected68 = TGraphAsymmErrors(massv,expv,masserrv,masserrv,exp68Lv,exp68Hv)
    expected68.SetFillColor(ROOT.kGreen+1)
    expected95 = TGraphAsymmErrors(massv,expv,masserrv,masserrv,exp95Lv,exp95Hv)
    expected95.SetFillColor(ROOT.kOrange)
    #'''
    c4 = TCanvas("c4","Limits", 600, 500)
    c4.SetBottomMargin(0.12)
    c4.SetRightMargin(0.04)
    c4.SetLeftMargin(0.14)
    c4.SetTopMargin(0.08)
    c4.SetLogy()

    expected95.Draw("a3")
    if signal == 'T': expected95.GetYaxis().SetRangeUser(.00005+.00001,2.01)
    else: expected95.GetYaxis().SetRangeUser(.0005+.00001,20.1)
    expected95.GetXaxis().SetRangeUser(800,2000)
    expected95.GetXaxis().SetTitle(signal+" mass [GeV]")
    expected95.GetYaxis().SetTitle("#sigma (Bbj #rightarrow tWbj) [pb]")
    expected95.GetYaxis().SetTitleOffset(1.05)

    expected68.Draw("3same")
    expected.Draw("same")

    #may2022mass_gr.Draw("same")
    #dec2022mass_gr.Draw("same")
    #mar2023mass_gr.Draw("same")

    if not blind: observed.Draw("cpsame")
    theory_xsec_gr.SetLineColor(2)
    theory_xsec_gr.SetLineStyle(1)
    theory_xsec_gr.SetLineWidth(2)
    theory_xsec_gr.Draw("3same") 
    theory.SetLineColor(2)
    theory.SetLineStyle(1)
    theory.SetLineWidth(2)
    theory.Draw("same")                                                             
    theory_xsec5_gr.SetLineColor(ROOT.kBlue)
    theory_xsec5_gr.SetLineStyle(1)
    theory_xsec5_gr.SetLineWidth(2)
    theory_xsec5_gr.Draw("3same") 
    theory5.SetLineColor(ROOT.kBlue)
    theory5.SetLineStyle(1)
    theory5.SetLineWidth(2)
    theory5.Draw("same")                                                             

    chLatex = TLatex()
    chLatex.SetNDC()
    chLatex.SetTextSize(0.045)
    chLatex.SetTextAlign(11) # align right
    chString = 'B #rightarrow tW'
    chLatex.DrawLatex(0.18, 0.82, chString)
    chString = '1-lep'
    chLatex.DrawLatex(0.18, 0.77, chString)
    chString = 'MC bkgd.'
    if 'ABCDnn' in limitDir:
            chString = 'ABCDnn'
    chLatex.DrawLatex(0.18, 0.72, chString)
        
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
    #prelimTex2.DrawLatex(0.12,0.93,"CMS")

    prelimTex3 = TLatex()
    prelimTex3.SetNDC()
    prelimTex3.SetTextAlign(12)
    #prelimTex3.SetTextFont(52)
    prelimTex3.SetTextSize(0.045)
    prelimTex3.SetLineWidth(2)
    #prelimTex3.DrawLatex(0.23,0.945,"Simulation work in progress")
    prelimTex3.DrawLatex(0.15,0.945,"Private Work (CMS Simulation)")

    #legend = TLegend(.55,.5,.89,.89) # good for BR of 1
    legend = TLegend(.55,.5,.89,.88,"95% CL upper limits") # mixes
    if not blind: legend.AddEntry(observed , 'Observed', "lp")
    legend.AddEntry(expected, 'Expected', "l")
    legend.AddEntry(expected68, '68% expected', "f")
    legend.AddEntry(expected95, '95% expected', "f")    
    #legend.AddEntry(mar2023mass_gr, 'M(B), ParticleNet', 'l')
    #legend.AddEntry(dec2022mass_gr, 'M(B), Dec 2022', 'l')
    #legend.AddEntry(may2022mass_gr, '', 'l')
    legend.AddEntry(theory_xsec_gr, 'Theory: Bbj 1%','f')
    legend.AddEntry(theory_xsec5_gr, 'Theory: Bbj 5%','f')
    legend.AddEntry(0,'Singlet: tW 50%','')
    legend.SetShadowColor(0)
    legend.SetFillStyle(0)
    legend.SetBorderSize(0)
    legend.SetFillColor(0)
    legend.SetLineColor(0)
    legend.Draw()
    
    c4.RedrawAxis()
    
    folder = os.getcwd()+'/' #'/uscms_data/d3/jmanagan/CMSSW_10_2_10/src/tptp_2016/combineLimits/'
    outDir=folder+limitDir+'/'
    #outDir = folder
    if not os.path.exists(outDir): os.system('mkdir -p '+outDir)
    c4.SaveAs(outDir+'/LimitPlot_'+histPrefix+saveKey+'_'+tempKey+'.root')
    c4.SaveAs(outDir+'/LimitPlot_'+histPrefix+saveKey+'_'+tempKey+'.pdf')
    c4.SaveAs(outDir+'/LimitPlot_'+histPrefix+saveKey+'_'+tempKey+'.png')
    c4.SaveAs(outDir+'/LimitPlot_'+histPrefix+saveKey+'_'+tempKey+'.C')

    f.close()

    return int(round(limExpected)), int(round(limObserved))


tempKeys = ['BToTW']

expLims = []
obsLims = []
for tempKey in tempKeys:
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
