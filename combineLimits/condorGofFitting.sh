#!/bin/bash

hostname
# Arguments = "%(OUTPUTDIR)s %(WORKSPACE)s %(NTOYS)s %(RINJ)s %(RMIN)s %(RMAX)s %(NAME)s %(SEED)s '%(MASKS)s' %(INDEX)s"

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


if [[ "$INDEX" == 1 ]]; then
    echo '------- Running background-only GOF with data ---------'
    echo 'combine -M GoodnessOfFit workspace.root --algo=saturated --fixedSignalStrength=0'
    combine -M GoodnessOfFit ${WORKSPACE} --algo=saturated --fixedSignalStrength=0
    data=$?
    if [[ $data -ne 0 ]]; then
	rm *.root
	echo "exit code $generated, failure in generating toys"
    fi
fi

echo "---------- 'Running background-only GOF with toys, after frequentist fit -------------"
echo 'Command = combine -M GoodnessOfFit ${WORKSPACE} --algo=saturated -t ${NTOYS} -s ${SEED} --fixedSignalStrength=0'
combine -M GoodnessOfFit ${WORKSPACE} --algo=saturated -t ${NTOYS} -s ${SEED} --fixedSignalStrength=0
fitted=$?
if [[ $fitted -ne 0 ]]; then
    rm *.root
    echo "exit code $fitted, failure in fitting toys"
fi

echo "ROOT Files:"
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







