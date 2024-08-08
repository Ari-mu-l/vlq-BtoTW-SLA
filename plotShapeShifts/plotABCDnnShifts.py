from ROOT import *
import os,sys,math, itertools
parent = os.path.dirname(os.getcwd())
sys.path.append(parent)
from utils import *
from array import array
from samples import targetlumi, lumiStr, systListFull, systListABCDnn, samples_data, samples_signal, samples_electroweak, samples_wjets, samples_ttbar, samples_singletop, samples_ttbarx, samples_qcd

from tdrStyle import *
setTDRStyle()
#gROOT.SetBatch(1)

if len(sys.argv) > 1: year = str(sys.argv[1])
else: year = 'combo'

region = 'D'
discriminant = 'BpMass_ABCDnn' # not plotting uncertainty shifts for minor backgrounds
inDirPostFix = 'Apr2024SysAll'
rfilePostFix = 'rebinned_stat0p2'
isCategorized = True

lumi = 138
outDir = os.getcwd()+'/templatesSRCR_Jul2024/'
templateFile = f'/uscms_data/d3/xshen/alma9/CMSSW_13_3_3/src/vlq-BtoTW-SLA/makeTemplates/templates{region}_{inDirPostFix}/templates_{discriminant}_{lumiStr}_{rfilePostFix}.root'
if year == '2018': # UPDATE if needed (with targetlumi perhaps)
	lumi = 59.7
	lumiStr = '_59p69fb'

if not os.path.exists(outDir): os.system('mkdir '+outDir)
if not os.path.exists(outDir+'/bkgs'): os.system('mkdir '+outDir+'/bkgs')
if not os.path.exists(outDir+'/sigs'): os.system('mkdir '+outDir+'/sigs')

saveKey = ''#
isEMlist = ['L'] # ['isE','isM'] # old var name: channels
if isCategorized:
        taglist = ['allTlep','allWlep'] #TEMP: test only
        #taglist = ['tagTjet','tagWjet','untagTlep','untagWlep','allWlep','allTlep'] # old var name: tags
else:
        taglist = ['all']
catList = ['is'+item[0]+'_'+item[1] for item in list(itertools.product(isEMlist,taglist))]

bkgList = ['major'] # not doing for minor backgrounds for now. but the script can be adapted to include minors

# TODO: add abcdnn in a separate dict or script
# Old: systnames dictionary removed. systematics list now replaced with list in samples

#if year == '2018': systematics.remove('prefire') #TODO: Check how we only applied prefiring to 2016-2017
#systematics = {'jec2016','jec2017','jec2018','jer2016','jer2017','jer2018'}

RFile = TFile(templateFile)

#if not lumiStr[-2:] == 'fb': lumiStr += 'fb'
#for syst in systListABCDnn: # now only implementing ABCDnn
for syst in ["tail"]: # TEMP
        print(syst)
        for ch in isEMlist:
                for tag in taglist:
                        catStr = f'is{ch}_{tag}'
                        histPrefix = f'{discriminant}_{lumiStr}_{catStr}'
                        histname = f'{histPrefix}_{region}__{bkgList[0]}'
                        print(f'-----------------------------{syst}, {catStr}--------------------------------')
                        print(histname)
                        hNm = RFile.Get(histname).Clone() # ABCDnn only cares about isL. modify the code for minor
                        hUp = RFile.Get(f'{histname}__{syst}Up').Clone()
                        hDn = RFile.Get(f'{histname}__{syst}Down').Clone()

			#hNm.Rebin(2);
			#hUp.Rebin(2);
			#hDn.Rebin(2);
			#hNm.Draw()
			#hUp.Draw()
			#hDn.Draw()

                        c = TCanvas(f'{histname}__{syst}',f'{histname}__{syst}',1000,700) # old var name: canv
                        yDiv = 0.35
                        uPad = TPad('uPad','',0,yDiv,1,1)
                        uPad.SetTopMargin(0.07)
                        uPad.SetBottomMargin(0)
                        uPad.SetRightMargin(0.05)
                        uPad.SetLeftMargin(0.18)
                        #uPad.SetLogy()
                        uPad.Draw()

                        lPad=TPad("lPad","",0,0,1,yDiv) #for sigma runner
                        lPad.SetTopMargin(0)
                        lPad.SetBottomMargin(0.4)
                        lPad.SetRightMargin(0.05)
                        lPad.SetLeftMargin(0.18)
                        lPad.SetGridy()
                        lPad.SetGridx()
                        lPad.Draw()

                        uPad.cd()
                        gStyle.SetOptTitle(0)
			#c.SetLogy()
                        #hNm.SetFillColor(kWhite)
                        #hUp.SetFillColor(kWhite)
                        #hDn.SetFillColor(kWhite)
                        #hNm.SetMarkerColor(kBlack)
                        #hUp.SetMarkerColor(kRed)
                        #hDn.SetMarkerColor(kBlue)
                        hNm.SetLineColor(kBlack)
                        hUp.SetLineColor(kRed)
                        hDn.SetLineColor(kBlue)
                        hNm.SetLineWidth(2)
                        hNm.SetLineStyle(1)
                        hUp.SetLineWidth(2)
                        hUp.SetLineStyle(2)
                        hDn.SetLineWidth(2)
                        hDn.SetLineStyle(2)
                        #hNm.SetMarkerSize(0.05)
                        #hUp.SetMarkerSize(0.05)
                        #hDn.SetMarkerSize(0.05)

                        hUp.GetYaxis().SetTitle("Events/bin") #TEMP: should not have 0.1
                        hUp.GetYaxis().SetLabelSize(0.06)
                        hUp.GetYaxis().SetTitleSize(0.06)
                        hUp.GetYaxis().SetTitleOffset(0.85)

			#hUp.SetMaximum(1.1*max(hUp.GetMaximum(),hNm.GetMaximum(),hDn.GetMaximum()))
                        hUp.GetYaxis().SetRangeUser(0.0001,1.4*max(hUp.GetMaximum(),hNm.GetMaximum(),hDn.GetMaximum()))

                        hUp.Draw('hist')
                        hNm.Draw('same hist')
                        hDn.Draw('same hist')
			#uPad.RedrawAxis()

                        lPad.cd()
                        gStyle.SetOptTitle(0)
                        pullUp = hUp.Clone()
                        for iBin in range(0,pullUp.GetXaxis().GetNbins()+2):
                                pullUp.SetBinContent(iBin,pullUp.GetBinContent(iBin)-hNm.GetBinContent(iBin))
                                pullUp.SetBinError(iBin,math.sqrt(pullUp.GetBinError(iBin)**2+hNm.GetBinError(iBin)**2))
                        pullUp.Divide(hNm)
                        pullUp.SetLineWidth(2)
                        #pullUp.SetTitle('')
                        #pullUp.SetFillColor(2)
                        #pullUp.SetLineColor(2)

                        #pullUp.GetXaxis().SetTitle(histName)
                        pullUp.GetXaxis().SetLabelSize(0.1)
                        pullUp.GetXaxis().SetTitleSize(0.1)
                        #pullUp.GetXaxis().SetTitleOffset(0.95)

                        pullUp.GetYaxis().SetTitle('')
                        #pullUp.GetYaxis().SetTitle('#frac{Up/Down-Nom}{Nom}')#'Python-C++'
                        #pullUp.GetYaxis().CenterTitle(1)
                        pullUp.GetYaxis().SetLabelSize(0.1)
                        #pullUp.GetYaxis().SetTitleSize(0.1)
                        #pullUp.GetYaxis().SetTitleOffset(.55)
                        pullUp.GetYaxis().SetNdivisions(506)

                        pullDown = hDn.Clone()
                        for iBin in range(0,pullDown.GetXaxis().GetNbins()+2):
                                pullDown.SetBinContent(iBin,pullDown.GetBinContent(iBin)-hNm.GetBinContent(iBin))
                                pullDown.SetBinError(iBin,math.sqrt(pullDown.GetBinError(iBin)**2+hNm.GetBinError(iBin)**2))
                        pullDown.Divide(hNm)
                        pullDown.SetLineWidth(2)
                        pullDown.SetTitle('')
                        #pullDown.SetFillColor(4)
                        #pullDown.SetLineColor(4)

                        if syst=="tail":
                                pullUp.SetMinimum(-0.5)
                                pullUp.SetMaximum(0.5)
                        else:
                                pullUp.SetMinimum(-0.199) #pullUp.SetMinimum(pullDown.GetMinimum())
                                pullUp.SetMaximum(0.199) #pullUp.SetMaximum(pullUp.GetMaximum())

                        #pullDown.GetXaxis().SetTitle(histName)
                        #pullDown.GetXaxis().SetLabelSize(0.18)
                        #pullDown.GetXaxis().SetTitleSize(0.18)
                        #pullDown.GetXaxis().SetTitleOffset(0.95)

                        pullDown.GetYaxis().SetTitle('')#'Python-C++'
                        #pullDown.GetYaxis().CenterTitle(1)
                        pullDown.GetYaxis().SetLabelSize(0.1)
                        pullDown.GetYaxis().SetTitleSize(0.1)
                        #pullDown.GetYaxis().SetTitleOffset(.55)
                        pullDown.GetYaxis().SetNdivisions(506)
                        
                        pullUp.Draw("hist")
                        pullDown.Draw('same hist')
                        lPad.RedrawAxis()

                        uPad.cd()

                        legend = TLegend(0.4,0.65,0.7,0.90)
                        legend.SetShadowColor(0);
                        legend.SetFillColor(0);
                        legend.SetLineColor(0);
                        legend.AddEntry(hNm,'ABCDnn Nominal','l')
                        legend.AddEntry(hUp,f'ABCDnn {syst} Up','l')
                        legend.AddEntry(hDn,f'ABCDnn {syst} Down','l')
                        legend.Draw('same')

                        prelimTex=TLatex()
                        prelimTex.SetNDC()
                        prelimTex.SetTextAlign(31) # align right
                        prelimTex.SetTextFont(42)
                        prelimTex.SetTextSize(0.05)
                        prelimTex.SetLineWidth(2)
                        #lumi=round(lumi,2)
                        prelimTex.DrawLatex(0.90,0.943,str(lumi)+" fb^{-1} (13 TeV)")
                        #prelimTex.DrawLatex(0.88, 0.95, "CMS Preliminary, "+str(lumi)+" fb^{-1} at #sqrt{s} = 8 TeV");

                        prelimTex2=TLatex()
                        prelimTex2.SetNDC()
                        prelimTex2.SetTextFont(61)
                        prelimTex2.SetLineWidth(2)
                        prelimTex2.SetTextSize(0.07)
                        prelimTex2.DrawLatex(0.18,0.9364,"CMS")

                        prelimTex3=TLatex()
                        prelimTex3.SetNDC()
                        prelimTex3.SetTextAlign(13)
                        prelimTex3.SetTextFont(52)
                        prelimTex3.SetTextSize(0.040)
                        prelimTex3.SetLineWidth(2)
                        prelimTex3.DrawLatex(0.25175,0.9664,"Preliminary")
                        #if blind: prelimTex3.DrawLatex(0.29175,0.9664,"Preliminary")

                        Tex1=TLatex()
                        Tex1.SetNDC()
                        Tex1.SetTextSize(0.05)
                        Tex1.SetTextAlign(31) # align right
                        #if i == 0: textx = 0.89
                        #else: textx = 0.85
                        textx = 0.3
                        #Tex1.DrawLatex(textx, 0.86, 'test')

                        Tex2 = TLatex()
                        Tex2.SetNDC()
                        Tex2.SetTextSize(0.05)
                        Tex2.SetTextAlign(21)
                        if ch=='isE': channelTxt = 'e+jets'
                        elif ch=='isM': channelTxt = '#mu+jets'
                        else: channelTxt = 'l+jets'
                        tagTxt = tag
                        sigbkgTxt = 'Major Bkg'
                        Tex2.DrawLatex(textx, 0.85, channelTxt)
                        Tex2.DrawLatex(textx, 0.80, tagTxt)
                        Tex2.DrawLatex(textx, 0.75, sigbkgTxt)
                        #Tex2.DrawLatex(textx, 0.70, ttagTxt)

                        c.SaveAs(outDir+'/bkgs/'+syst+'_'+ch+'_'+tag+'.pdf')
                        c.SaveAs(outDir+'/bkgs/'+syst+'_'+ch+'_'+tag+'.png')
                        c.SaveAs(outDir+'/bkgs/'+syst+'_'+ch+'_'+tag+'.root')

                        
                        # print('-----------------------------'+syst+', '+ch+', '+tag+' SIGNAL --------------------------------')
                        # if syst=='muRFcorrdNewTop': systtemp = 'muRFcorrdNewSig'
                        # elif syst=='muRFcorrdNewEwk': continue
                        # else: systtemp = syst

                        # hNm.Reset()
                        # hUp.Reset()
                        # hDn.Reset()

                        # Prefix = histname+lumiStr+'_'+region+'_'+channels[0]+'_'+tag+'_DeepAK8__TTM1400'
                        # try: 
                        #         if ch != 'isL': hNm = RFile.Get(Prefix.replace(channels[0],ch)).Clone()
                        #         else: 
                        #                 hNm = RFile.Get(Prefix).Clone()
                        #                 hNm = RFile.Get(Prefix.replace(channels[0],channels[1]))
                        # except:
                        #         print('No histogram for sig in this channel!')
                        #         continue

                        # if ch != 'isL':
                        #         hNm = RFile.Get(Prefix.replace(channels[0],ch)).Clone()
                        #         hUp = RFile.Get(Prefix.replace(channels[0],ch)+'__'+systtemp+'Up').Clone()
                        #         hDn = RFile.Get(Prefix.replace(channels[0],ch)+'__'+systtemp+'Down').Clone()
                        # else:
                        #         hNm = RFile.Get(Prefix).Clone()
                        #         hUp = RFile.Get(Prefix+'__'+systtemp+'Up').Clone()
                        #         hDn = RFile.Get(Prefix+'__'+systtemp+'Down').Clone()
                        #         hNm.Add(RFile.Get(Prefix.replace(channels[0],channels[1])))
                        #         hUp.Add(RFile.Get(Prefix.replace(channels[0],channels[1])+'__'+systtemp+'Up'))
                        #         hDn.Add(RFile.Get(Prefix.replace(channels[0],channels[1])+'__'+systtemp+'Down'))


                        # #hNm.Rebin(2);
                        # #hUp.Rebin(2);
                        # #hDn.Rebin(2);
                        # #hNm.Draw()
                        # #hUp.Draw()
                        # #hDn.Draw()
                        # if histname != 'HTNtag' or 'dnnLargeJ' in tag:
                        #         normByBinWidth(hNm)
                        #         normByBinWidth(hUp)
                        #         normByBinWidth(hDn)

                        # c = TCanvas(Prefix+'__'+systtemp,Prefix+'__'+systtemp,1000,700)
                        # yDiv = 0.35
                        # uPad=R.TPad('uPad','',0,yDiv,1,1)
                        # uPad.SetTopMargin(0.07)
                        # uPad.SetBottomMargin(0)
                        # uPad.SetRightMargin(.05)
                        # uPad.SetLeftMargin(.18)
                        # #uPad.SetLogy()
                        # uPad.Draw()

                        # lPad=TPad("lPad","",0,0,1,yDiv) #for sigma runner
                        # lPad.SetTopMargin(0)
                        # lPad.SetBottomMargin(.4)
                        # lPad.SetRightMargin(.05)
                        # lPad.SetLeftMargin(.18)
                        # lPad.SetGridy()
                        # lPad.Draw()

                        # uPad.cd()

                        # gStyle.SetOptTitle(0)

                        # #canv.SetLogy()
                        # hNm.SetFillColor(kWhite)
                        # hUp.SetFillColor(kWhite)
                        # hDn.SetFillColor(kWhite)
                        # hNm.SetMarkerColor(kBlack)
                        # hUp.SetMarkerColor(kRed)
                        # hDn.SetMarkerColor(kBlue)
                        # hNm.SetLineColor(kBlack)
                        # hUp.SetLineColor(kRed)
                        # hDn.SetLineColor(kBlue)
                        # hNm.SetLineWidth(2)
                        # hNm.SetLineStyle(1)
                        # hUp.SetLineWidth(2)
                        # hUp.SetLineStyle(1)
                        # hDn.SetLineWidth(2)
                        # hDn.SetLineStyle(1)
                        # hNm.SetMarkerSize(.05)
                        # hUp.SetMarkerSize(.05)
                        # hDn.SetMarkerSize(.05)

                        # if histname == 'HTNtag':
                        #         if 'dnnLargeJ' in tag: hUp.GetYaxis().SetTitle("< Events / 1 GeV >")
                        #         elif 'dnnLarge' in tag: hUp.GetYaxis().SetTitle("Events")
                        # else: hUp.GetYaxis().SetTitle("< Events / 0.1 >")
                        # hUp.GetYaxis().SetLabelSize(0.10)
                        # hUp.GetYaxis().SetTitleSize(0.1)
                        # hUp.GetYaxis().SetTitleOffset(.6)

                        # #hUp.SetMaximum(1.1*max(hUp.GetMaximum(),hNm.GetMaximum(),hDn.GetMaximum()))
                        # hUp.GetYaxis().SetRangeUser(0.0001,1.2*max(hUp.GetMaximum(),hNm.GetMaximum(),hDn.GetMaximum()))

                        # hUp.Draw()
                        # hNm.Draw('same')
                        # hDn.Draw('same')
                        # #uPad.RedrawAxis()

                        # pullUp.Reset()
                        # pullDown.Reset()

                        # lPad.cd()
                        # gStyle.SetOptTitle(0)
                        # pullUp = hUp.Clone()
                        # for iBin in range(0,pullUp.GetXaxis().GetNbins()+2):
                        #         pullUp.SetBinContent(iBin,pullUp.GetBinContent(iBin)-hNm.GetBinContent(iBin))
                        #         pullUp.SetBinError(iBin,math.sqrt(pullUp.GetBinError(iBin)**2+hNm.GetBinError(iBin)**2))
                        # pullUp.Divide(hNm)
                        # pullUp.SetTitle('')
                        # pullUp.SetFillColor(2)
                        # pullUp.SetLineColor(2)

                        # #pullUp.GetXaxis().SetTitle(histName)
                        # pullUp.GetXaxis().SetLabelSize(.15)
                        # pullUp.GetXaxis().SetTitleSize(0.18)
                        # pullUp.GetXaxis().SetTitleOffset(0.95)

                        # pullUp.GetYaxis().SetTitle('#frac{Up/Down-Nom}{Nom}')#'Python-C++'
                        # pullUp.GetYaxis().CenterTitle(1)
                        # pullUp.GetYaxis().SetLabelSize(0.125)
                        # pullUp.GetYaxis().SetTitleSize(0.1)
                        # pullUp.GetYaxis().SetTitleOffset(.55)
                        # pullUp.GetYaxis().SetNdivisions(506)
                        # #pullUp.SetMinimum(pullDown.GetMinimum())
                        # #pullUp.SetMaximum(pullUp.GetMaximum())

                        # pullDown = hDn.Clone()
                        # for iBin in range(0,pullDown.GetXaxis().GetNbins()+2):
                        #         pullDown.SetBinContent(iBin,pullDown.GetBinContent(iBin)-hNm.GetBinContent(iBin))
                        #         pullDown.SetBinError(iBin,math.sqrt(pullDown.GetBinError(iBin)**2+hNm.GetBinError(iBin)**2))
                        # pullDown.Divide(hNm)
                        # pullDown.SetTitle('')
                        # pullDown.SetFillColor(4)
                        # pullDown.SetLineColor(4)

                        # #pullDown.GetXaxis().SetTitle(histName)
                        # pullDown.GetXaxis().SetLabelSize(.15)
                        # pullDown.GetXaxis().SetTitleSize(0.18)
                        # pullDown.GetXaxis().SetTitleOffset(0.95)

                        # pullDown.GetYaxis().SetTitle('#frac{Up/Down-Nom}{Nom}')#'Python-C++'
                        # pullDown.GetYaxis().CenterTitle(1)
                        # pullDown.GetYaxis().SetLabelSize(0.125)
                        # pullDown.GetYaxis().SetTitleSize(0.1)
                        # pullDown.GetYaxis().SetTitleOffset(.55)
                        # pullDown.GetYaxis().SetNdivisions(506)
                        # if 'muRF' in systtemp or 'jec' in systtemp:
                        #         pullUp.SetMinimum(-0.5)#min(pullDown.GetMinimum(),pullUp.GetMinimum()))
                        #         pullUp.SetMaximum(0.5)#max(pullDown.GetMaximum(),pullUp.GetMaximum()))
                        # else:
                        #         pullUp.SetMinimum(-0.20)
                        #         pullUp.SetMaximum(0.20)
                        # pullUp.Draw('hist')
                        # pullDown.Draw('same hist')
                        # lPad.RedrawAxis()

                        # uPad.cd()

                        # legendS = TLegend(0.4,0.65,0.7,0.90)
                        # legendS.SetShadowColor(0);
                        # legendS.SetFillColor(0);
                        # legendS.SetLineColor(0);
                        # legendS.AddEntry(hNm,'Nominal','l')
                        # legendS.AddEntry(hUp,systnames[systtemp]+' Up','l')
                        # legendS.AddEntry(hDn,systnames[systtemp]+' Down','l')
                        # legendS.Draw('same')

                        # #prelimTex=TLatex()
                        # prelimTex.SetNDC()
                        # prelimTex.SetTextAlign(31) # align right
                        # prelimTex.SetTextFont(42)
                        # prelimTex.SetTextSize(0.05)
                        # prelimTex.SetLineWidth(2)
                        # #lumi=round(lumi,2)
                        # prelimTex.DrawLatex(0.90,0.943,str(lumi)+" fb^{-1} (13 TeV)")
                        # #prelimTex.DrawLatex(0.88, 0.95, "CMS Preliminary, "+str(lumi)+" fb^{-1} at #sqrt{s} = 8 TeV");

                        # #prelimTex2=TLatex()
                        # prelimTex2.SetNDC()
                        # prelimTex2.SetTextFont(61)
                        # prelimTex2.SetLineWidth(2)
                        # prelimTex2.SetTextSize(0.07)
                        # prelimTex2.DrawLatex(0.18,0.9364,"CMS")

                        # #prelimTex3=TLatex()
                        # prelimTex3.SetNDC()
                        # prelimTex3.SetTextAlign(13)
                        # prelimTex3.SetTextFont(52)
                        # prelimTex3.SetTextSize(0.040)
                        # prelimTex3.SetLineWidth(2)
                        # prelimTex3.DrawLatex(0.25175,0.9664,"Preliminary")
                        # #if blind: prelimTex3.DrawLatex(0.29175,0.9664,"Preliminary")

                        # #Tex1=TLatex()
                        # Tex1.SetNDC()
                        # Tex1.SetTextSize(0.05)
                        # Tex1.SetTextAlign(31) # align right
                        # #if i == 0: textx = 0.89
                        # #else: textx = 0.85
                        # textx = 0.3
                        # #Tex1.DrawLatex(textx, 0.86, 'test')

                        # #Tex2 = TLatex()
                        # Tex2.SetNDC()
                        # Tex2.SetTextSize(0.05)
                        # Tex2.SetTextAlign(21)
                        # if ch=='isE': channelTxt = 'e+jets'
                        # if ch=='isM': channelTxt = '#mu+jets'
                        # tagTxt = tag
                        # sigbkgTxt = 'TT 1.4 TeV (50/25/25)'
                        # Tex2.DrawLatex(textx, 0.85, channelTxt)
                        # Tex2.DrawLatex(textx, 0.80, tagTxt)
                        # Tex2.DrawLatex(textx, 0.75, sigbkgTxt)
                        # #Tex2.DrawLatex(textx, 0.70, ttagTxt)

                        # canv.SaveAs(outDir+'/sigs/'+systtemp+'_'+ch+'_'+tag+'.pdf')
                        # canv.SaveAs(outDir+'/sigs/'+systtemp+'_'+ch+'_'+tag+'.png')
                        # canv.SaveAs(outDir+'/sigs/'+systtemp+'_'+ch+'_'+tag+'.root')

RFile.Close()

