#!/usr/bin/python

import os,sys,time,math,fnmatch
from array import array
from numpy import linspace
parent = os.path.dirname(os.getcwd())
sys.path.append(parent)
from ROOT import *
start_time = time.time()

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Run as:
# > python modifyBinning.py
# 
# Optional arguments:
# -- statistical uncertainty threshold
#
# Notes:
# -- Finds certain root files in a given directory and rebins all histograms in each file
# -- A selection of subset of files in the input directory can be done below under "#Setup the selection ..."
# -- A custom binning choice can also be given below and this choice can be activated by giving a stat unc 
#    threshold larger than 100% (>1.) in the argument
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

#cutString = 'splitLess/'#BB_templates/'
templateV = os.getcwd()+'/templatesV_Jan2025_corr/templates_BpMass_ABCDnn_138fbfb.root'
templateD = os.getcwd()+'/templatesD_Jan2025_corr/templates_BpMass_ABCDnn_138fbfb.root'

Vfile = TFile(templateV)
Dfile = TFile(templateD)
allhists = [hist.GetName() for hist in Vfile.GetListOfKeys()]

outputfile = TFile(os.getcwd()+'/templatesV2_Jan2025_corr/templates_BpMass_ABCDnn_138fbfb.root','RECREATE')

for hist in allhists:

    if 'untagWlep' in hist or 'untagTlep' in hist:
        tmphist=Dfile.Get(hist.replace('_V_','_D_')).Clone(hist.replace('_V_','_V2_'))
        #print('Writing',tmphist.GetName())
        tmphist.SetDirectory(0)
        tmphist.Write()
    else:
        tmphist=Vfile.Get(hist).Clone(hist.replace('_V_','_V2_'))
        tmphist.SetDirectory(0)
        tmphist.Write()
        
Vfile.Close()
Dfile.Close()
outputfile.Close()

print("--- %s minutes ---" % (round((time.time() - start_time)/60,2)))



