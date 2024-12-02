#!/bin/bash

hostname
# Arguments = %(WORKSPACE)s %(NTOYS)s %(RINJ)s %(RMIN)s %(RMAX)s %(NAME)s %(SEED)s %(MASKS)s %(OUTPUTDIR)s

OUTPUTDIR=${1}
WORKSPACE=${2}
NTOYS=${3}
RINJ=${4}
RMIN=${5}
RMAX=${6}
NAME=${7}
SEED=${8}
MASKS=${9}
INDEX=${10}

scratch=${PWD}
source /cvmfs/cms.cern.ch/cmsset_default.sh
scramv1 project CMSSW CMSSW_14_1_0_pre4
cd CMSSW_14_1_0_pre4

echo "unpacking tar"
tar -xf ${scratch}/combineV10.tar
rm ${scratch}/combineV10.tar

eval `scramv1 runtime -sh`
cd -

echo "---------- Generating toys -----------"
echo "combine -M GenerateOnly -d ${WORKSPACE} --snapshotName initialFit --toysFrequentist --bypassFrequentistFit -t ${NTOYS} --saveToys --expectSignal ${RINJ} -n ${NAME} -s ${SEED} ${MASKS}"
combine -M GenerateOnly -d ${WORKSPACE} --snapshotName initialFit --toysFrequentist --bypassFrequentistFit -t ${NTOYS} --saveToys --expectSignal ${RINJ} -n ${NAME} -s ${SEED} ${MASKS}
generated=$?
if [[ $generated -ne 0 ]]; then
    rm *.root
    echo "exit code $generated, failure in generating toys"
fi

echo "---------- Fitting toys -------------"
echo "combine -M FitDiagnostics -d ${WORKSPACE} --snapshotName initialFit --skipBOnlyFit --toysFrequentist --bypassFrequentistFit -t ${NTOYS} --toysFile higgsCombine${NAME}.GenerateOnly.mH120.${SEED}.root --cminDefaultMinimizerStrategy 0 --rMin ${RMIN} --rMax ${RMAX} -n ${NAME}_${INDEX} -s ${SEED} ${MASKS}" #--robustFit=1 
combine -M FitDiagnostics -d ${WORKSPACE} --snapshotName initialFit --skipBOnlyFit --toysFrequentist --bypassFrequentistFit -t ${NTOYS} --toysFile higgsCombine${NAME}.GenerateOnly.mH120.${SEED}.root --cminDefaultMinimizerStrategy 0 --rMin ${RMIN} --rMax ${RMAX} -n ${NAME}_${INDEX} -s ${SEED} ${MASKS}  # --robustFit=1 
fitted=$?
if [[ $fitted -ne 0 ]]; then
    rm *.root
    echo "exit code $fitted, failure in fitting toys"
fi

echo "ROOT Files:"
rm higgsCombine${NAME}_${INDEX}.FitDiagnostics.mH120.${SEED}.root
rm higgsCombine${NAME}.GenerateOnly.mH120.${SEED}.root
ls -l *.root

echo "xrdcp output for condor"
for FILE in *.root
do
  echo "xrdcp -f ${FILE} root://cmseos.fnal.gov/${OUTPUTDIR}/${FILE}"
  xrdcp -f ${FILE} root://cmseos.fnal.gov/${OUTPUTDIR}/${FILE} 2>&1
  XRDEXIT=$?
  if [[ $XRDEXIT -ne 0 ]]; then
    rm *.root
    echo "exit code $XRDEXIT, failure in xrdcp"
    exit $XRDEXIT
  fi
  rm ${FILE}
done

echo "done"







