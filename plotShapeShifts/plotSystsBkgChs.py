import ROOT as R
import os,sys,math
parent = os.path.dirname(os.getcwd())
sys.path.append(parent)
from utils import *
from array import array

from tdrStyle import *
setTDRStyle()
R.gROOT.SetBatch(1)

discriminant = 'BpMass'
rfilePostFix = '_rebinned_stat0p2'

lumi = 138
lumiStr = '_138fbfb'
outDir = os.getcwd()+'/templatesD_Aug2024/'
templateFile = '/uscms_data/d3/jmanagan/BtoTW/CMSSW_13_0_18/src/vlq-BtoTW-SLA/makeTemplates/templatesD_Aug2024/templates_'+discriminant+lumiStr+rfilePostFix+'.root'

if not os.path.exists(outDir): os.system('mkdir '+outDir)
if not os.path.exists(outDir+'/bkgs'): os.system('mkdir '+outDir+'/bkgs')
if not os.path.exists(outDir+'/sigs'): os.system('mkdir '+outDir+'/sigs')

saveKey = ''#
channels = ['isL']
tags = ['tagTjet','tagWjet','untagTlep','untagWlep']

systnames = {
        'elRecoSF':'El reco SF',
        'elIdSF':'El ID SF',
        'elIsoSF':'El iso SF',
        'muRecoSF':'Mu reco SF',
        'muIdSF':'Mu ID SF',
        'muIsoSF':'Mu iso SF',        
        'Pileup':'Pileup',
        'Prefire':'Prefiring',
        'jec2016APV':'JEC 16APV',
        'jec2016':'JEC 16',
        'jec2017':'JEC 17',
        'jec2018':'JEC 18',
        'jer2016APV':'JER 16APV',
        'jer2016':'JER 16',
        'jer2017':'JER 17',
        'jer2018':'JER 18',
        'jsf':'HT weight W+jets',
        'toppt':'HT weight t#bar{t}',
        'muRFcorrdNewSIG':'Ren./Fact. Sig',
        'muRFcorrdNewTT':'Ren./Fact. t#bar{t}',
        'muRFcorrdNewST':'Ren./Fact. single t',
        'muRFcorrdNewTTX':'Ren./Fact. t#bar{t}+X',
        'muRFcorrdNewWJT':'Ren./Fact. W+jets',
        'muRFcorrdNewEWK':'Ren./Fact. DY+VV',
        'muRFcorrdNewQCD':'Ren./Fact. QCD',
        'pdfNew':'PDF',
        'TrigEffEl2016APV':'El trigger 16APV',
        'TrigEffEl2016':'El trigger 16',
        'TrigEffEl2017':'El trigger 17',
        'TrigEffEl2018':'El trigger 18',
        'TrigEffMu2016APV':'Mu trigger 16APV',
        'TrigEffMu2016':'Mu trigger 16',
        'TrigEffMu2017':'Mu trigger 17',
        'TrigEffMu2018':'Mu trigger 18',
        'btagHFCO':'DeepJet HF correlated',
        'btagHFUC2016APV':'DeepJet HF uncorrelated 16APV',
        'btagHFUC2016':'DeepJet HF uncorrelated 16',
        'btagHFUC2017':'DeepJet HF uncorrelated 17',
        'btagHFUC2018':'DeepJet HF uncorrelated 18',
        'btagLFCO':'DeepJet LF correlated',
        'btagLFUC2016APV':'DeepJet HF uncorrelated 16APV',
        'btagLFUC2016':'DeepJet LF uncorrelated 16',
        'btagLFUC2017':'DeepJet LF uncorrelated 17',
        'btagLFUC2018':'DeepJet LF uncorrelated 18',
        'pNetTtag':'ParticleNet t SF',
        'pNetWtag':'PartlcleNet W SF',
        }
systematics = systnames.keys()

RFile = R.TFile(templateFile)

if not lumiStr[-2:] == 'fb': lumiStr += 'fb'
for syst in systematics:
        if syst == 'muRFcorrdNewSIG': continue
        # for systs where the histogram exists for only one process, adjust the list so they are process 0
        if 'EWK' in syst:
                bkgList = ['ewk','ttbar','singletop','wjets','ttx','qcd']
        elif 'TTX' in syst:
                bkgList = ['ttx','ttbar','singletop','wjets','ewk','qcd']
        elif 'WJT' in syst:
                bkgList = ['wjets','ttbar','singletop','ewk','ttx','qcd']
        elif 'ST' in syst:
                bkgList = ['singletop','ttbar','wjets','ewk','ttx','qcd']
        elif 'QCD' in syst:
                bkgList = ['qcd','ttbar','singletop','wjets','ewk','ttx']
        else:
                bkgList = ['ttbar','singletop','wjets','ewk','ttx','qcd']
        for ch in channels:
                for tag in tags:
                        if ('Ttag' in syst and 'Tjet' not in tag and 'Wlep' not in tag) or ('Wtag' in syst and 'Wjet' not in tag and 'Tlep' not in tag):
                                continue
                        print('-----------------------------'+syst+', '+ch+', '+tag+'--------------------------------')
                        histname = discriminant
                        region = 'D'
                        #BpMass_138fbfb_isL_tagTjet_D__BpM800__pNetTtagUp
                        Prefix = histname+lumiStr+'_'+channels[0]+'_'+tag+'_'+region+'__'+bkgList[0]
                        try:
                                hNm = RFile.Get(Prefix.replace(channels[0],ch)).Clone()
                        except:
                                print('No histogram for ',bkgList[0],' in this channel!')
                                continue

                        hNm = RFile.Get(Prefix.replace(channels[0],ch)).Clone()
                        hUp = RFile.Get(Prefix.replace(channels[0],ch)+'__'+syst+'Up').Clone()
                        hDn = RFile.Get(Prefix.replace(channels[0],ch)+'__'+syst+'Down').Clone()

                        for bkg in bkgList:
                                if ch==channels[0] and bkg==bkgList[0]:
                                        print(Prefix)
                                        continue
                                try:
                                        print(Prefix.replace(channels[0],ch).replace(bkgList[0],bkg))
                                        htemp = RFile.Get(Prefix.replace(channels[0],ch).replace(bkgList[0],bkg)).Clone()
                                        hNm.Add(htemp)
                                except: pass
                                try:
                                        if ('EWK' in syst and bkg!='ewk') or ('TT' in syst and bkg!='ttbar') or ('ST' in syst and bkg!='singletop') or ('QCD' in syst and bkg!='qcd') or ('TTX' in syst and bkg!='ttx') or ('WJT' in syst and bkg!='wjets'):
                                                htempUp = RFile.Get(Prefix.replace(channels[0],ch).replace(bkgList[0],bkg)).Clone()
                                                hUp.Add(htempUp)
                                                htempDown = RFile.Get(Prefix.replace(channels[0],ch).replace(bkgList[0],bkg)).Clone()
                                                hDn.Add(htempDown)
                                        else:
                                                htempUp = RFile.Get(Prefix.replace(channels[0],ch).replace(bkgList[0],bkg)+'__'+syst+'Up').Clone()
                                                hUp.Add(htempUp)
                                                htempDown = RFile.Get(Prefix.replace(channels[0],ch).replace(bkgList[0],bkg)+'__'+syst+'Down').Clone()
                                                hDn.Add(htempDown)
                                except:pass

                        normByBinWidth(hNm)
                        normByBinWidth(hUp)
                        normByBinWidth(hDn)

                        canv = R.TCanvas(Prefix+'__'+syst,Prefix+'__'+syst,1000,700)
                        yDiv = 0.35
                        uPad=R.TPad('uPad','',0,yDiv,1,1)
                        uPad.SetTopMargin(0.07)
                        uPad.SetBottomMargin(0)
                        uPad.SetRightMargin(.05)
                        uPad.SetLeftMargin(.18)
                        #uPad.SetLogy()
                        uPad.Draw()

                        lPad=R.TPad("lPad","",0,0,1,yDiv) #for sigma runner
                        lPad.SetTopMargin(0)
                        lPad.SetBottomMargin(.4)
                        lPad.SetRightMargin(.05)
                        lPad.SetLeftMargin(.18)
                        lPad.SetGridy()
                        lPad.Draw()

                        uPad.cd()

                        R.gStyle.SetOptTitle(0)

                        #canv.SetLogy()
                        hNm.SetFillColor(R.kWhite)
                        hUp.SetFillColor(R.kWhite)
                        hDn.SetFillColor(R.kWhite)
                        hNm.SetMarkerColor(R.kBlack)
                        hUp.SetMarkerColor(R.kRed)
                        hDn.SetMarkerColor(R.kBlue)
                        hNm.SetLineColor(R.kBlack)
                        hUp.SetLineColor(R.kRed)
                        hDn.SetLineColor(R.kBlue)
                        hNm.SetLineWidth(2)
                        hNm.SetLineStyle(1)
                        hUp.SetLineWidth(2)
                        hUp.SetLineStyle(1)
                        hDn.SetLineWidth(2)
                        hDn.SetLineStyle(1)
                        hNm.SetMarkerSize(.05)
                        hUp.SetMarkerSize(.05)
                        hDn.SetMarkerSize(.05)

                        hUp.GetYaxis().SetTitle("< Events / GeV >")

                        hUp.GetYaxis().SetLabelSize(0.10)
                        hUp.GetYaxis().SetTitleSize(0.1)
                        hUp.GetYaxis().SetTitleOffset(.6)

                        #hUp.SetMaximum(1.1*max(hUp.GetMaximum(),hNm.GetMaximum(),hDn.GetMaximum()))
                        hUp.GetYaxis().SetRangeUser(0.0001,1.4*max(hUp.GetMaximum(),hNm.GetMaximum(),hDn.GetMaximum()))

                        hUp.Draw('hist')
                        hNm.Draw('same hist')
                        hDn.Draw('same hist')
                        #uPad.RedrawAxis()

                        lPad.cd()
                        R.gStyle.SetOptTitle(0)
                        pullUp = hUp.Clone()
                        for iBin in range(0,pullUp.GetXaxis().GetNbins()+2):
                                pullUp.SetBinContent(iBin,pullUp.GetBinContent(iBin)-hNm.GetBinContent(iBin))
                                pullUp.SetBinError(iBin,math.sqrt(pullUp.GetBinError(iBin)**2+hNm.GetBinError(iBin)**2))
                        pullUp.Divide(hNm)
                        pullUp.SetTitle('')
                        pullUp.SetFillColor(2)
                        pullUp.SetLineColor(2)

                        #pullUp.GetXaxis().SetTitle(histName)
                        pullUp.GetXaxis().SetLabelSize(.15)
                        pullUp.GetXaxis().SetTitleSize(0.18)
                        pullUp.GetXaxis().SetTitleOffset(0.95)

                        pullUp.GetYaxis().SetTitle('#frac{Up/Down-Nom}{Nom}')#'Python-C++'
                        pullUp.GetYaxis().CenterTitle(1)
                        pullUp.GetYaxis().SetLabelSize(0.125)
                        pullUp.GetYaxis().SetTitleSize(0.1)
                        pullUp.GetYaxis().SetTitleOffset(.55)
                        pullUp.GetYaxis().SetNdivisions(506)
                        #pullUp.SetMinimum(pullDown.GetMinimum())
                        #pullUp.SetMaximum(pullUp.GetMaximum())

                        pullDown = hDn.Clone()
                        for iBin in range(0,pullDown.GetXaxis().GetNbins()+2):
                                pullDown.SetBinContent(iBin,pullDown.GetBinContent(iBin)-hNm.GetBinContent(iBin))
                                pullDown.SetBinError(iBin,math.sqrt(pullDown.GetBinError(iBin)**2+hNm.GetBinError(iBin)**2))
                        pullDown.Divide(hNm)
                        pullDown.SetTitle('')
                        pullDown.SetFillColor(4)
                        pullDown.SetLineColor(4)

                        #pullDown.GetXaxis().SetTitle(histName)
                        pullDown.GetXaxis().SetLabelSize(.15)
                        pullDown.GetXaxis().SetTitleSize(0.18)
                        pullDown.GetXaxis().SetTitleOffset(0.95)

                        pullDown.GetYaxis().SetTitle('#frac{Up/Down-Nom}{Nom}')#'Python-C++'
                        pullDown.GetYaxis().CenterTitle(1)
                        pullDown.GetYaxis().SetLabelSize(0.125)
                        pullDown.GetYaxis().SetTitleSize(0.1)
                        pullDown.GetYaxis().SetTitleOffset(.55)
                        pullDown.GetYaxis().SetNdivisions(506)
                        if 'muRF' in syst:
                                pullUp.SetMinimum(-0.5)
                                pullUp.SetMaximum(0.5)
                        else:
                                pullUp.SetMinimum(-0.20)
                                pullUp.SetMaximum(0.20)
                        pullUp.Draw("hist")
                        pullDown.Draw('same hist')
                        lPad.RedrawAxis()

                        uPad.cd()

                        legend = R.TLegend(0.4,0.65,0.7,0.90)
                        legend.SetShadowColor(0);
                        legend.SetFillColor(0);
                        legend.SetLineColor(0);
                        legend.AddEntry(hNm,'Nominal','l')
                        legend.AddEntry(hUp,systnames[syst]+' Up','l')
                        legend.AddEntry(hDn,systnames[syst]+' Down','l')
                        legend.Draw('same')

                        prelimTex=R.TLatex()
                        prelimTex.SetNDC()
                        prelimTex.SetTextAlign(31) # align right
                        prelimTex.SetTextFont(42)
                        prelimTex.SetTextSize(0.05)
                        prelimTex.SetLineWidth(2)
                        #lumi=round(lumi,2)
                        prelimTex.DrawLatex(0.90,0.943,str(lumi)+" fb^{-1} (13 TeV)")
                        #prelimTex.DrawLatex(0.88, 0.95, "CMS Preliminary, "+str(lumi)+" fb^{-1} at #sqrt{s} = 8 TeV");

                        prelimTex2=R.TLatex()
                        prelimTex2.SetNDC()
                        prelimTex2.SetTextFont(61)
                        prelimTex2.SetLineWidth(2)
                        prelimTex2.SetTextSize(0.07)
                        prelimTex2.DrawLatex(0.18,0.9364,"CMS")

                        prelimTex3=R.TLatex()
                        prelimTex3.SetNDC()
                        prelimTex3.SetTextAlign(13)
                        prelimTex3.SetTextFont(52)
                        prelimTex3.SetTextSize(0.040)
                        prelimTex3.SetLineWidth(2)
                        prelimTex3.DrawLatex(0.25175,0.9664,"Preliminary")
                        #if blind: prelimTex3.DrawLatex(0.29175,0.9664,"Preliminary")

                        Tex1=R.TLatex()
                        Tex1.SetNDC()
                        Tex1.SetTextSize(0.05)
                        Tex1.SetTextAlign(31) # align right
                        #if i == 0: textx = 0.89
                        #else: textx = 0.85
                        textx = 0.3
                        #Tex1.DrawLatex(textx, 0.86, 'test')

                        Tex2 = R.TLatex()
                        Tex2.SetNDC()
                        Tex2.SetTextSize(0.05)
                        Tex2.SetTextAlign(21)
                        if ch=='isE': channelTxt = 'e+jets'
                        if ch=='isM': channelTxt = '#mu+jets'
                        if ch=='isL': channelTxt = 'e/#mu+jets'
                        tagTxt = tag
                        sigbkgTxt = 'Total Bkg'
                        Tex2.DrawLatex(textx, 0.85, channelTxt)
                        Tex2.DrawLatex(textx, 0.80, tagTxt)
                        Tex2.DrawLatex(textx, 0.75, sigbkgTxt)
                        #Tex2.DrawLatex(textx, 0.70, ttagTxt)

                        canv.SaveAs(outDir+'/bkgs/'+syst+'_'+ch+'_'+tag+'.pdf')
                        canv.SaveAs(outDir+'/bkgs/'+syst+'_'+ch+'_'+tag+'.png')
                        canv.SaveAs(outDir+'/bkgs/'+syst+'_'+ch+'_'+tag+'.root')

                        print('-----------------------------'+syst+', '+ch+', '+tag+' SIGNAL --------------------------------')
                        if syst=='muRFcorrdNewTT': systtemp = 'muRFcorrdNewSIG'
                        elif 'muRFcorrd' in syst: continue
                        else: systtemp = syst

                        hNm.Reset()
                        hUp.Reset()
                        hDn.Reset()

                        Prefix = histname+lumiStr+'_'+channels[0]+'_'+tag+'_'+region+'__BpM1600'
                        try: 
                                hNm = RFile.Get(Prefix.replace(channels[0],ch)).Clone()
                        except:
                                print('No histogram for sig in this channel!')
                                continue

                        hNm = RFile.Get(Prefix.replace(channels[0],ch)).Clone()
                        hUp = RFile.Get(Prefix.replace(channels[0],ch)+'__'+systtemp+'Up').Clone()
                        hDn = RFile.Get(Prefix.replace(channels[0],ch)+'__'+systtemp+'Down').Clone()

                        normByBinWidth(hNm)
                        normByBinWidth(hUp)
                        normByBinWidth(hDn)

                        canv = R.TCanvas(Prefix+'__'+systtemp,Prefix+'__'+systtemp,1000,700)
                        yDiv = 0.35
                        uPad=R.TPad('uPad','',0,yDiv,1,1)
                        uPad.SetTopMargin(0.07)
                        uPad.SetBottomMargin(0)
                        uPad.SetRightMargin(.05)
                        uPad.SetLeftMargin(.18)
                        #uPad.SetLogy()
                        uPad.Draw()

                        lPad=R.TPad("lPad","",0,0,1,yDiv) #for sigma runner
                        lPad.SetTopMargin(0)
                        lPad.SetBottomMargin(.4)
                        lPad.SetRightMargin(.05)
                        lPad.SetLeftMargin(.18)
                        lPad.SetGridy()
                        lPad.Draw()

                        uPad.cd()
                        R.gStyle.SetOptTitle(0)

                        #canv.SetLogy()
                        hNm.SetFillColor(R.kWhite)
                        hUp.SetFillColor(R.kWhite)
                        hDn.SetFillColor(R.kWhite)
                        hNm.SetMarkerColor(R.kBlack)
                        hUp.SetMarkerColor(R.kRed)
                        hDn.SetMarkerColor(R.kBlue)
                        hNm.SetLineColor(R.kBlack)
                        hUp.SetLineColor(R.kRed)
                        hDn.SetLineColor(R.kBlue)
                        hNm.SetLineWidth(2)
                        hNm.SetLineStyle(1)
                        hUp.SetLineWidth(2)
                        hUp.SetLineStyle(1)
                        hDn.SetLineWidth(2)
                        hDn.SetLineStyle(1)
                        hNm.SetMarkerSize(.05)
                        hUp.SetMarkerSize(.05)
                        hDn.SetMarkerSize(.05)

                        hUp.GetYaxis().SetTitle("< Events / 1 GeV >")
                        hUp.GetYaxis().SetLabelSize(0.10)
                        hUp.GetYaxis().SetTitleSize(0.1)
                        hUp.GetYaxis().SetTitleOffset(.6)

                        #hUp.SetMaximum(1.1*max(hUp.GetMaximum(),hNm.GetMaximum(),hDn.GetMaximum()))
                        hUp.GetYaxis().SetRangeUser(0.0001,1.2*max(hUp.GetMaximum(),hNm.GetMaximum(),hDn.GetMaximum()))

                        hUp.Draw()
                        hNm.Draw('same')
                        hDn.Draw('same')
			#uPad.RedrawAxis()

                        pullUp.Reset()
                        pullDown.Reset()

                        lPad.cd()
                        R.gStyle.SetOptTitle(0)
                        pullUp = hUp.Clone()
                        for iBin in range(0,pullUp.GetXaxis().GetNbins()+2):
                                pullUp.SetBinContent(iBin,pullUp.GetBinContent(iBin)-hNm.GetBinContent(iBin))
                                pullUp.SetBinError(iBin,math.sqrt(pullUp.GetBinError(iBin)**2+hNm.GetBinError(iBin)**2))
                        pullUp.Divide(hNm)
                        pullUp.SetTitle('')
                        pullUp.SetFillColor(2)
                        pullUp.SetLineColor(2)

                        #pullUp.GetXaxis().SetTitle(histName)
                        pullUp.GetXaxis().SetLabelSize(.15)
                        pullUp.GetXaxis().SetTitleSize(0.18)
                        pullUp.GetXaxis().SetTitleOffset(0.95)

                        pullUp.GetYaxis().SetTitle('#frac{Up/Down-Nom}{Nom}')#'Python-C++'
                        pullUp.GetYaxis().CenterTitle(1)
                        pullUp.GetYaxis().SetLabelSize(0.125)
                        pullUp.GetYaxis().SetTitleSize(0.1)
                        pullUp.GetYaxis().SetTitleOffset(.55)
                        pullUp.GetYaxis().SetNdivisions(506)
                        #pullUp.SetMinimum(pullDown.GetMinimum())
                        #pullUp.SetMaximum(pullUp.GetMaximum())

                        pullDown = hDn.Clone()
                        for iBin in range(0,pullDown.GetXaxis().GetNbins()+2):
                                pullDown.SetBinContent(iBin,pullDown.GetBinContent(iBin)-hNm.GetBinContent(iBin))
                                pullDown.SetBinError(iBin,math.sqrt(pullDown.GetBinError(iBin)**2+hNm.GetBinError(iBin)**2))
                        pullDown.Divide(hNm)
                        pullDown.SetTitle('')
                        pullDown.SetFillColor(4)
                        pullDown.SetLineColor(4)

                        #pullDown.GetXaxis().SetTitle(histName)
                        pullDown.GetXaxis().SetLabelSize(.15)
                        pullDown.GetXaxis().SetTitleSize(0.18)
                        pullDown.GetXaxis().SetTitleOffset(0.95)

                        pullDown.GetYaxis().SetTitle('#frac{Up/Down-Nom}{Nom}')#'Python-C++'
                        pullDown.GetYaxis().CenterTitle(1)
                        pullDown.GetYaxis().SetLabelSize(0.125)
                        pullDown.GetYaxis().SetTitleSize(0.1)
                        pullDown.GetYaxis().SetTitleOffset(.55)
                        pullDown.GetYaxis().SetNdivisions(506)
                        if 'muRF' in systtemp or 'jec' in systtemp:
                                pullUp.SetMinimum(-0.5)#min(pullDown.GetMinimum(),pullUp.GetMinimum()))
                                pullUp.SetMaximum(0.5)#max(pullDown.GetMaximum(),pullUp.GetMaximum()))
                        else:
                                pullUp.SetMinimum(-0.20)
                                pullUp.SetMaximum(0.20)
                        pullUp.Draw('hist')
                        pullDown.Draw('same hist')
                        lPad.RedrawAxis()

                        uPad.cd()

                        legendS = R.TLegend(0.4,0.65,0.7,0.90)
                        legendS.SetShadowColor(0);
                        legendS.SetFillColor(0);
                        legendS.SetLineColor(0);
                        legendS.AddEntry(hNm,'Nominal','l')
                        legendS.AddEntry(hUp,systnames[systtemp]+' Up','l')
                        legendS.AddEntry(hDn,systnames[systtemp]+' Down','l')
                        legendS.Draw('same')

                        #prelimTex=R.TLatex()
                        prelimTex.SetNDC()
                        prelimTex.SetTextAlign(31) # align right
                        prelimTex.SetTextFont(42)
                        prelimTex.SetTextSize(0.05)
                        prelimTex.SetLineWidth(2)
                        #lumi=round(lumi,2)
                        prelimTex.DrawLatex(0.90,0.943,str(lumi)+" fb^{-1} (13 TeV)")
                        #prelimTex.DrawLatex(0.88, 0.95, "CMS Preliminary, "+str(lumi)+" fb^{-1} at #sqrt{s} = 8 TeV");

                        #prelimTex2=R.TLatex()
                        prelimTex2.SetNDC()
                        prelimTex2.SetTextFont(61)
                        prelimTex2.SetLineWidth(2)
                        prelimTex2.SetTextSize(0.07)
                        prelimTex2.DrawLatex(0.18,0.9364,"CMS")

                        #prelimTex3=R.TLatex()
                        prelimTex3.SetNDC()
                        prelimTex3.SetTextAlign(13)
                        prelimTex3.SetTextFont(52)
                        prelimTex3.SetTextSize(0.040)
                        prelimTex3.SetLineWidth(2)
                        prelimTex3.DrawLatex(0.25175,0.9664,"Preliminary")
                        #if blind: prelimTex3.DrawLatex(0.29175,0.9664,"Preliminary")

                        #Tex1=R.TLatex()
                        Tex1.SetNDC()
                        Tex1.SetTextSize(0.05)
                        Tex1.SetTextAlign(31) # align right
                        #if i == 0: textx = 0.89
                        #else: textx = 0.85
                        textx = 0.3
                        #Tex1.DrawLatex(textx, 0.86, 'test')

                        #Tex2 = R.TLatex()
                        Tex2.SetNDC()
                        Tex2.SetTextSize(0.05)
                        Tex2.SetTextAlign(21)
                        if ch=='isE': channelTxt = 'e+jets'
                        if ch=='isM': channelTxt = '#mu+jets'
                        if ch=='isL': channelTxt = 'e/#mu+jets'
                        tagTxt = tag
                        sigbkgTxt = 'B 1.6 TeV'
                        Tex2.DrawLatex(textx, 0.85, channelTxt)
                        Tex2.DrawLatex(textx, 0.80, tagTxt)
                        Tex2.DrawLatex(textx, 0.75, sigbkgTxt)
                        #Tex2.DrawLatex(textx, 0.70, ttagTxt)

                        canv.SaveAs(outDir+'/sigs/'+systtemp+'_'+ch+'_'+tag+'.pdf')
                        canv.SaveAs(outDir+'/sigs/'+systtemp+'_'+ch+'_'+tag+'.png')
                        canv.SaveAs(outDir+'/sigs/'+systtemp+'_'+ch+'_'+tag+'.root')

RFile.Close()

