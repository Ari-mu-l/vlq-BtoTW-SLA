import os,sys
from ROOT import TFile, TH1
from samples import sample, mclist_2016APV, mclist_2016, mclist_2017, mclist_2018
from utils import *
from math import sqrt

## something about samples goes here

for sample in mclist_2016APV:
    #print('-------------------------------------------------------')
    
    samplename = sample.samplename.split('/')[1]

    step1dir = 'root://cmseos.fnal.gov//store/user/lpchtop/BtoTW_Aug2024_fullRun2/'
    tree = readTreeNominal(samplename,"2016APV",step1dir,"Runs")

    integral = 0
    adjusted = 0
    for irun in range(tree.GetEntries()):
        tree.GetEntry(irun)
        integral += tree.genEventCount
        adjusted += tree.genEventSumw/sqrt(tree.genEventSumw2/tree.genEventCount)

    print(sample.prefix+'.nrun = '+str(adjusted)+' # from integral '+str(integral)+', file '+sample.prefix)

    #if 'Bp' in sample:
        # use the LHEScaleWeight and LHEPDFWeight to extract the SFs

for sample in mclist_2016:
    #print('-------------------------------------------------------')
    
    samplename = sample.samplename.split('/')[1]

    step1dir = 'root://cmseos.fnal.gov//store/user/lpchtop/BtoTW_Aug2024_fullRun2/'
    tree = readTreeNominal(samplename,"2016",step1dir,"Runs")

    integral = 0
    adjusted = 0
    for irun in range(tree.GetEntries()):
        tree.GetEntry(irun)
        integral += tree.genEventCount
        adjusted += tree.genEventSumw/sqrt(tree.genEventSumw2/tree.genEventCount)

    print(sample.prefix+'.nrun = '+str(adjusted)+' # from integral '+str(integral)+', file '+sample.prefix)

    #if 'Bp' in sample:
        # use the LHEScaleWeight and LHEPDFWeight to extract the SFs

for sample in mclist_2017:
    #print('-------------------------------------------------------')
    
    samplename = sample.samplename.split('/')[1]

    step1dir = 'root://cmseos.fnal.gov//store/user/lpchtop/BtoTW_Aug2024_fullRun2/'
    tree = readTreeNominal(samplename,"2017",step1dir,"Runs")

    integral = 0
    adjusted = 0
    for irun in range(tree.GetEntries()):
        tree.GetEntry(irun)
        integral += tree.genEventCount
        adjusted += tree.genEventSumw/sqrt(tree.genEventSumw2/tree.genEventCount)

    print(sample.prefix+'.nrun = '+str(adjusted)+' # from integral '+str(integral)+', file '+sample.prefix)

    #if 'Bp' in sample:
        # use the LHEScaleWeight and LHEPDFWeight to extract the SFs

for sample in mclist_2018:
    #print('-------------------------------------------------------')
    
    samplename = sample.samplename.split('/')[1]

    step1dir = 'root://cmseos.fnal.gov//store/user/lpchtop/BtoTW_Aug2024_fullRun2/'
    tree = readTreeNominal(samplename,"2018",step1dir,"Runs")

    integral = 0
    adjusted = 0
    for irun in range(tree.GetEntries()):
        tree.GetEntry(irun)
        integral += tree.genEventCount
        adjusted += tree.genEventSumw/sqrt(tree.genEventSumw2/tree.genEventCount)

    print(sample.prefix+'.nrun = '+str(adjusted)+' # from integral '+str(integral)+', file '+sample.prefix)

    #if 'Bp' in sample:
        # use the LHEScaleWeight and LHEPDFWeight to extract the SFs

