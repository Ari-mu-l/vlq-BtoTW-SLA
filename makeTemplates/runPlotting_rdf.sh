# run with ./runPlotting_rdf.sh (chmod +x runPlotting_rdf.sh first if no permission)
# python3 groupHists.py $iPlot $region $isCategorized $pfix
# python3 plotHists.py $iPlot $region $isCategorized $pfix $blind $yLog $isRebinned
#pfix = "_Apr2024SysAll"
#isRebinned = "_rebinned_stat0p2"
# control plots

plotList='ForwJetEta'

plotListFull='BpMass ST HT lepPt lepEta lepPhi lepIso MET METphi JetEta JetPt JetPhi JetBtag ForwJetEta ForwJetPt ForwJetPhi FatJetEta FatJetPt FatJetPhi FatJetSD OS1FatJetEta OS1FatJetPt OS1FatJetPhi OS1FatJetSD NJetsCentral NJetsForward NBJets NOSJets NSSJets NOSBJets NSSBJets NFatJets NOSFatJets NSSFatJets PtRel PtRelAK8 minDR minDRAK8 FatJetProbJ FatJetProbTvJ FatJetProbWvJ FatJetTag OS1FatJetProbJ OS1FatJetProbTvJ OS1FatJetProbWvJ OS1FatJetTag nT nW Wmass Wpt Weta Wphi WMt Wdrlep minMlj tmassSSB tptSSB tetaSSB tphiSSB tdrWbMLJ tdrWbSSB BpPt BpEta BpPhi BpDeltaR BpPtBal BpChi2 BpDecay'

plotListTags='FatJetTag OS1FatJetTag BpDecay'

plotListPU='NPV'

# for iPlot in $plotListPU; do
#    echo $iPlot
#    python3 groupHists.py $iPlot all False _Oct2024
#    python3 plotHists.py $iPlot all False _Oct2024 False False
#    python3 groupHists.py $iPlot all False _Oct2024_noPUwgt
#    python3 plotHists.py $iPlot all False _Oct2024_noPUwgt False False
# done
#_rebinned_stat0p2

# signal region plots
plotList='BpMass_ABCDnn'
for iPlot in $plotList; do
    echo $iPlot
    # python3 groupHists.py $iPlot D True _Oct2024_420bins
    # python3 groupHists.py $iPlot C True _Oct2024_420bins
    # python3 groupHists.py $iPlot V2 True _Oct2024_420bins
    # python3 groupHists.py $iPlot B True _Oct2024_420bins
    # python3 groupHists.py $iPlot A True _Oct2024_420bins
    # python3 groupHists.py $iPlot CV2 True _Oct2024_420bins
    # python3 groupHists.py $iPlot V True _Oct2024_420bins

    #python3 modifyBinning.py $iPlot templatesD_Oct2024_420bins 0.2 2
    #python3 modifyBinning.py $iPlot templatesD_Oct2024_420bins 0.2 5
    #python3 modifyBinning.py $iPlot templatesD_Oct2024_420bins 0.2 10
    # python3 modifyBinning.py $iPlot templatesC_Oct2024_420bins 0.1
    # python3 modifyBinning.py $iPlot templatesB_Oct2024_420bins 0.1
    # python3 modifyBinning.py $iPlot templatesA_Oct2024_420bins 0.1
    #python3 modifyBinning.py $iPlot templatesV2_Oct2024_420bins 0.2 10
    # python3 modifyBinning.py $iPlot templatesV_Oct2024_420bins 0.2
    # python3 modifyBinning.py $iPlot templatesCV2_Oct2024_420bins 0.1
    
    #python3 modifyBinning.py $iPlot templatesV2_Oct2024_420binsTU 0.2 4 True
    #python3 modifyBinning.py $iPlot templatesV2_Oct2024_420binsTU 0.2 3 True
    #python3 modifyBinning.py $iPlot templatesD_Oct2024_420binsTU 0.2 4 True
    #python3 modifyBinning.py $iPlot templatesD_Oct2024_420binsTU 0.2 3 True

    #python3 plotHists.py $iPlot V2 True _Oct2024_420binsTU False True _rebinned5_stat0p2
    python3 plotHists.py $iPlot V2 True _Oct2024_420binsTU False True _rebinned3_stat0p2_smoothed

    
    #python3 plotHists.py $iPlot D True _Oct2024_420bins False True _rebinned2_stat0p2
    # python3 plotHists.py $iPlot C True _Oct2024_420bins False True _rebinned_stat0p1
    # python3 plotHists.py $iPlot B True _Oct2024_420bins False True _rebinned_stat0p1
    # python3 plotHists.py $iPlot A True _Oct2024_420bins False True _rebinned_stat0p1
    #python3 plotHists.py $iPlot V2 True _Oct2024_420bins False True _rebinned2_stat0p2
    #python3 plotHists.py $iPlot V True _Oct2024_420binsTU False True _rebinned5_stat0p2
    #python3 plotHists.py $iPlot V True _Oct2024_420binsTU False True _rebinned10_stat0p2
    #python3 plotHists.py $iPlot V2 True _Oct2024_420binsTU False True _rebinned5_stat0p2
    #python3 plotHists.py $iPlot V2 True _Oct2024_420binsTU False True _rebinned10_stat0p2
    # python3 plotHists.py $iPlot V True _Oct2024_420bins False True _rebinned5_stat0p2
    # python3 plotHists.py $iPlot CV2 True _Oct2024_420bins False True _rebinned_stat0p1
    # python3 plotHists.py $iPlot D True _Oct2024_420bins False False _rebinned5_stat0p2
    # python3 plotHists.py $iPlot C True _Oct2024_420bins False False _rebinned_stat0p1
    # python3 plotHists.py $iPlot B True _Oct2024_420bins False False _rebinned_stat0p1
    # python3 plotHists.py $iPlot A True _Oct2024_420bins False False _rebinned_stat0p1
    # python3 plotHists.py $iPlot V2 True _Oct2024_420bins False False _rebinned5_stat0p2
    # python3 plotHists.py $iPlot V True _Oct2024_420bins False False _rebinned5_stat0p2
    # python3 plotHists.py $iPlot CV2 True _Oct2024_420bins False False _rebinned_stat0p1
    
done

#Python3 groupHists.py BpMass_ABCDnn D True _Aug2024
#python3 modifyBinning.py BpMass_ABCDnn templatesD_Aug2024 0.2
#python3 plotHists.py BpMass_ABCDnn D True _Aug2024SysAll False False _rebinned_stat0p2

#python3 groupHists.py BpMass_ABCDnn D True _Aug2024SysAll_validation
#python3 modifyBinning.py BpMass_ABCDnn templatesD_Aug2024SysAll_validation 0.2
#python3 plotHists.py BpMass_ABCDnn D True _Aug2024SysAll_validation False False _rebinned_stat0p2
