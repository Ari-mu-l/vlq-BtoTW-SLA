import sys, subprocess, ROOT
exec(open("/uscms_data/d3/jmanagan/EOSSafeUtils.py").read())

ROOT.gROOT.SetBatch(1)
limitdir = sys.argv[1]
mass = sys.argv[2]
rInj = float(sys.argv[3])

name = limitdir.replace('limits_templatesABCDnn_V2_Jan2025_','').replace('limits_templatesABCDnn_DV2_Jan2025_','')+'InjR'+str(rInj).replace('.','p')+'CDMS0'
path = limitdir+'/cmb/'+mass

rootfiles = EOSlist_root_files('/store/user/xshen/CombineV10_BpInjection/'+limitdir+'_'+mass+'/')	

tree_fit_sb = ROOT.TChain('tree_fit_sb')
for i in range(0,len(rootfiles)):
    if 'fitDiagnostics'+name+'_' not in rootfiles[i]: continue
    tree_fit_sb.Add('root://cmseos.fnal.gov//store/user/xshen/CombineV10_BpInjection/'+limitdir+'_'+mass+'/'+rootfiles[i])

#post_file = ROOT.TFile.Open('root://cmseos.fnal.gov/fitDiagnostics'+name+'_hadd.root')
#tree_fit_sb = post_file.Get('tree_fit_sb')

# Final plotting
result_can = ROOT.TCanvas('sigpull_can','sigpull_can',800,700)

#fit_status>=0 just ensures you aren't including fits that failed
tree_fit_sb.Draw("(r-"+str(rInj)+")/(rHiErr*(r<"+str(rInj)+")+rLoErr*(r>"+str(rInj)+"))>>sigpull(20,-5,5)","fit_status==0")# && abs(rLoErr) < 10 && abs(rHiErr) < 10")
#tree_fit_sb.Draw("(r-"+str(rInj)+")/(rHiErr*(r<"+str(rInj)+")+rLoErr*(abs(rLoErr)<=5 && r>"+str(rInj)+")+rHiErr*(abs(rLoErr)>5 && r>"+str(rInj)+"))>>sigpull(20,-5,5)","fit_status==0")# && abs(rLoErr) < 10 && abs(rHiErr) < 10")
min = 0 - rInj*5
max = 0 + rInj*5
if rInj == 0:
    min = -1
    max = 1
tree_fit_sb.Draw("(r-"+str(rInj)+")>>sigstrength(20,"+str(min)+','+str(max)+")","fit_status==0")

hsigpull = ROOT.gDirectory.Get('sigpull')
hsignstrength = ROOT.gDirectory.Get('sigstrength')

ROOT.gStyle.SetOptFit(1)
hsigpull.Fit("gaus","L")
hsigpull.SetTitle(name)
hsigpull.GetXaxis().SetTitle('(r-'+str(rInj)+')/rErr')
result_can.cd()
hsigpull.Draw('pe')
result_can.Print(path+'/'+name+'_sigpull.png','png')

hsignstrength.Fit("gaus","L")
hsignstrength.SetTitle(name)
hsignstrength.GetXaxis().SetTitle('r-'+str(rInj))
result_can.cd()
hsignstrength.Draw('pe')
result_can.Print(path+'/'+name+'_sigstrength.png','png')

## "Grass" plot suggested by Lucas for checks if needed

# g = ROOT.TGraphAsymmErrors(tree_fit_sb.GetEntries())
# for i in range(1,tree_fit_sb.GetEntries()+1):
#     if i%20 == 0: print 'Event',i,'...'
#     tree_fit_sb.GetEntry(i)
#     g.SetPoint(i,i,tree_fit_sb.r-rInj)
#     g.SetPointError(i,0.5,0.5,tree_fit_sb.rLoErr,tree_fit_sb.rHiErr)

# c = ROOT.TCanvas('c','',800,700)
# c.cd()
# g.Draw('AP')
# l = ROOT.TLine(0,0,tree_fit_sb.GetEntries()+1,0)
# l.SetLineColor(ROOT.kBlue)
# l.Draw()
# c.Print(path+'/'+name+'_toy_r_'+str(rInj).replace('.','p')+'.png','png')

# if rInj == 0:
#     min = -10
#     max = 10
# g.GetYaxis().SetRangeUser(min,max)
# c.Print(path+'/'+name+'_toy_r_'+str(rInj).replace('.','p')+'_zoom.png','png')
