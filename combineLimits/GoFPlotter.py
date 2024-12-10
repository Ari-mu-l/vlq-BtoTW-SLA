import os,sys
from ROOT import TFile, TCanvas, TLine, TTree, TChain, gROOT
exec(open("/uscms_data/d3/jmanagan/EOSSafeUtils.py").read())

gROOT.SetBatch(1)
limitdir = sys.argv[1]
mass = sys.argv[2]

name = limitdir.replace('limits_templatesABCDnn_V2_Oct2024_','').replace('limits_templatesABCDnn_DV2_Oct2024_','')
path = limitdir+'/cmb/'+mass

scriptdir = os.getcwd()
os.chdir(path)

datafile = 'higgsCombineTest.GoodnessOfFit.mH120.root'
# RFile=TFile.Open(datafile)
# data = RFile.Get('limit')
# data.GetEntry(0)
# datachi2 = data.limit
os.system('xrdcp root://cmseos.fnal.gov//store/user/xshen/CombineV10_BpGOF/'+limitdir+'_'+mass+'/'+datafile+' .')

toysfile = 'higgsCombineTest.GoodnessOfFit.toys.root'
if not os.path.exists(toysfile):
    rootfiles = EOSlist_root_files('/store/user/xshen/CombineV10_BpGOF/'+limitdir+'_'+mass+'/')
    haddcommand = 'hadd '+toysfile
    for ifile in rootfiles:
        if ifile == 'workspace.root': continue
        haddcommand += ' root://cmseos.fnal.gov//store/user/xshen/CombineV10_BpGOF/'+limitdir+'_'+mass+'/'+ifile
    os.system(haddcommand)

collect = 'combineTool.py -M CollectGoodnessOfFit --input '+datafile+' '+toysfile+' -m 120.0 -o gof.json'
print(collect)
os.system(collect)

plot = scriptdir+'/plotGof.py gof.json --statistic saturated --mass 120.0 -o gof_plot --range 0 600 --title-right="Region V2"'
print(plot)
os.system(plot)



# limit1 = TChain('limit')
# for i in range(0,len(rootfiles)):
#     if 'higgsCombineTest.GoodnessOfFit' not in rootfiles[i]: continue
#     if 'higgsCombineTest.GoodnessOfFit.mH120.root' in rootfiles[i]: continue
#     limit1.Add('root://cmseos.fnal.gov//store/user/jmanagan/CombineV10_BpGOF/'+limitdir+'_'+mass+'/'+rootfiles[i])

# #RFile1=TFile.Open('higgsCombineTest.GoodnessOfFit.mH120.123456.root')
# #limit1=RFile1.Get('limit')
# GoF_can=TCanvas('GoodnessOfFit','GoodnessOfFit',800,600)
# limit1.Draw('limit','','pe')
# line=TLine(datachi2,0,datachi2,25)
# line.SetLineColor(2)
# line.SetLineWidth(2)
# GoF_can.Update()
# line.Draw('Draw')

# GoF_can.SaveAs('GoodnessOfFit.png')
# GoF_can.SaveAs('GoodnessOfFit.pdf')

