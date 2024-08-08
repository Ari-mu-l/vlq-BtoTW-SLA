#!/bin/bash

hostname 

outDir=$1
iPlot=$2
region=$3
isCategorized=$4
isEM=$5
tag=$6

source /cvmfs/cms.cern.ch/cmsset_default.sh
#scramv1 project CMSSW CMSSW_12_4_8
#cd CMSSW_12_4_8
scramv1 project CMSSW CMSSW_13_3_3
cd CMSSW_13_3_3
eval `scramv1 runtime -sh`
cd -

python3 -u doHists_rdf.py $outDir $iPlot $region $isCategorized $isEM $tag
