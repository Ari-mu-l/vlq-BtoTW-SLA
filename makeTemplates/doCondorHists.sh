#!/bin/bash

hostname 

outDir=$1
iPlot=$2
region=$3
isCategorized=$4
isEM=$5
tag=$6
procs=$7

source /cvmfs/cms.cern.ch/cmsset_default.sh
scramv1 project CMSSW CMSSW_13_0_18
cd CMSSW_13_0_18
eval `scramv1 runtime -sh`
cd -

python3 -u doHists_rdf_${procs}.py $outDir $iPlot $region $isCategorized $isEM $tag
