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
#plotList='BpMass'
for iPlot in $plotList; do
    echo $iPlot

    ### plot for paper ###
    #python3 plotHists_paper.py BpMass all False _Jan2025 False False
    #python3 plotHists_paper.py BpDecay all False _Jan2025 False False
    #python3 plotHists_paper.py NBJets all False _Jan2025 False False
    #python3 plotHists_paper.py NJetsForward all False _Jan2025 False False
    
    #python3 groupHists.py $iPlot A True _Jan2025
    #python3 groupHists.py $iPlot B True _Jan2025
    #python3 groupHists.py $iPlot C True _Jan2025
    #python3 groupHists.py $iPlot D True _Jan2025
    #python3 groupHists.py $iPlot X True _Jan2025
    #python3 groupHists.py $iPlot Y True _Jan2025

    #python3 modifyBinning.py $iPlot templatesA_Jan2025 0.2 1 
    #python3 modifyBinning.py $iPlot templatesB_Jan2025 0.2 1
    #python3 modifyBinning.py $iPlot templatesC_Jan2025 0.2 1
    #python3 modifyBinning.py $iPlot templatesD_Jan2025 0.2 1
    #python3 modifyBinning.py $iPlot templatesX_Jan2025 0.2 1
    #python3 modifyBinning.py $iPlot templatesY_Jan2025 0.2 1
    
    #python3 modifyBinning.py $iPlot templatesV2_Oct2024_420binsTU 0.2 4 True
    #python3 modifyBinning.py $iPlot templatesV2_Oct2024_420binsTU 0.2 3 True
    #python3 modifyBinning.py $iPlot templatesD_Oct2024_420binsTU 0.2 4 True
    #python3 modifyBinning.py $iPlot templatesD_Oct2024_420binsTU 0.2 3 True
    #python3 modifyBinning.py $iPlot templatesD_Oct2024_420bins 0.2 5 True
    #python3 modifyBinning.py $iPlot templatesV_Oct2024_420bins 0.2 5 True
    #python3 modifyBinning.py $iPlot templatesV2_Oct2024_420bins 0.2 5 True

    #python3 modifyBinning_smoothJEC.py D
    #python3 modifyBinning_smoothJEC.py V
    #python3 modifyBinning_smoothJEC.py V2

    #python3 modifyBinning.py BpMass templatesD_Jan2025_210bins 0.2 1
    #python3 modifyBinning.py BpMass templatesV2_Jan2025_210bins 0.2 1
    #python3 modifyBinning.py BpMass templatesB_Jan2025_210bins 0.2 1

    #python3 plotHists.py $iPlot V2 True _Jan2025_42bins False True
    #python3 plotHists.py BpMass D True _Jan2025_210bins False False _rebinned1_stat0p2
    #python3 plotHists.py BpMass V2 True _Jan2025_210bins False False _rebinned1_stat0p2
    #python3 plotHists.py BpMass B True _Jan2025_210bins False False _rebinned1_stat0p2
    #python3 plotHists.py $iPlot V True _Oct2024_420bins_model6 False True _rebinned5_stat0p2_valUpDn
    #python3 plotHists.py $iPlot V2 True _Oct2024_420bins_model6 False True _rebinned5_stat0p2_valUpDnFromV_smoothed_TVJJ
    #python3 plotHists.py $iPlot D True _Oct2024_420bins_model6 False True _rebinned5_stat0p2_valUpDnFromVWithD_smoothed_TVJJ
    #python3 plotHists.py $iPlot D True _Jan2025_210binsCorr2016 False True
    #python3 modifyBinning.py BpMass_ABCDnn templatesD_Jan2025_105binsCorr 0.2 1 
    #python3 modifyBinning_smooth2Dcorr.py D Jan2025_105binsCorr
    #python3 uncorrUncert.py D False
    #python3 plotHists.py $iPlot D True _Jan2025_105binsCorr False True _rebinned1_stat0p2_smoothed_TVJJ_UC
    
    # python3 modifyBinning.py BpMass_ABCDnn templatesD_Jan2025_105binsCorr2016AvgCorrUC4 0.2 1
    # python3 modifyBinning_smooth2Dcorr.py D Jan2025_105binsCorr2016AvgCorrUC4
    #python3 uncorrUncert.py D False Jan2025_105binsCorr2016AvgCorrUC4 _2016
    # python3 plotHists.py $iPlot D True _Jan2025_105binsCorr2016AvgCorrUC4 False True _rebinned1_stat0p2_smoothed_TVJJ_UC 2016

    # python3 modifyBinning.py BpMass_ABCDnn templatesD_Jan2025_105binsCorr2016AvgTrainCorrUC4 0.2 1
    # python3 modifyBinning_smooth2Dcorr.py D Jan2025_105binsCorr2016AvgTrainCorrUC4
    # python3 uncorrUncert.py D False Jan2025_105binsCorr2016AvgTrainCorrUC4 _2016
    # python3 plotHists.py $iPlot D True _Jan2025_105binsCorr2016AvgTrainCorrUC4 False True _rebinned1_stat0p2_smoothed_TVJJ_UC 2016

    # python3 modifyBinning.py BpMass_ABCDnn templatesD_Jan2025_105binsCorr2016WeightCorrUC4 0.2 1
    # python3 modifyBinning_smooth2Dcorr.py D Jan2025_105binsCorr2016WeightCorrUC4
    # python3 uncorrUncert.py D False Jan2025_105binsCorr2016WeightCorrUC4 _2016
    # python3 plotHists.py $iPlot D True _Jan2025_105binsCorr2016WeightCorrUC4 False True _rebinned1_stat0p2_smoothed_TVJJ_UC 2016

    #python3 modifyBinning.py BpMass_ABCDnn templatesD_Jan2025_105binsCorr2016WeightTrainCorrUC4 0.2 1
    #python3 modifyBinning_smooth2Dcorr.py D Jan2025_105binsCorr2016WeightTrainCorrUC4
    #python3 uncorrUncert.py D False Jan2025_105binsCorr2016WeightTrainCorrUC4 _2016
    #python3 plotHists.py $iPlot D True _Jan2025_105binsCorr2016WeightTrainCorrUC4 False True _rebinned1_stat0p2_smoothed_TVJJ_UC 2016

    #python3 uncorrUncert.py D False Jan2025_105binsCorr2016BTrainCorrUC3S2NoTrain1Train2No1080 _2016

    #python3 modifyBinning.py BpMass_ABCDnn templatesD_Jan2025_105binsBtargetHoleCorrBTrain2016 0.2 1
    #python3 modifyBinning_smooth2Dcorr.py D Jan2025_105binsBtargetHoleCorrBTrain2016
    #python3 plotHists.py $iPlot D True _Jan2025_105binsBtargetHoleCorrBTrain2016 False True _rebinned1_stat0p2_smoothed_TVJJ 2016

    #python3 modifyBinning.py BpMass_ABCDnn templatesD_Jan2025_105binsBtargetHoleCorrACTrain2016 0.2 1
    #python3 modifyBinning_smooth2Dcorr.py D Jan2025_105binsBtargetHoleCorrACTrain2016
    #python3 plotHists.py $iPlot D True _Jan2025_105binsBtargetHoleCorrACTrain2016 False True _rebinned1_stat0p2_smoothed_TVJJ 2016

    # # smooth jecjer
    # python3 modifyBinning_smooth2Dcorr_jecjer.py D Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST
    # # rebin
    # python3 modifyBinning.py BpMass_ABCDnn templatesD_Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST 0.2 1
    # # smooth traincorr
    # python3 modifyBinning_smooth2Dcorr_traincorr.py D Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST

    # python3 plotHists.py $iPlot D True _Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST False False _smoothedJJ_rebinned1_stat0p2_smoothedTV

    #python3 modifyBinning_smooth2Dcorr_jecjer.py V2 Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST
    #python3 modifyBinning.py BpMass_ABCDnn templatesV2_Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST 0.2 1
    #python3 modifyBinning_smooth2Dcorr_traincorr.py V2 Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST
    #python3 plotHists.py $iPlot V2 True _Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST False False _smoothedJJ_rebinned1_stat0p2_smoothedTV

    #####################################################
    # ARC review save point 1: dynamic ST + 1D smoothig #
    #####################################################
    #python3 modifyBinning.py BpMass_ABCDnn templatesV2_Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST 0.2 1
    #python3 modifyBinning_smooth2Dcorr_traincorr.py V2 Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST
    #python3 plotHists.py $iPlot V2 True _Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST False False _smoothedJJ_rebinned1_stat0p2_smoothedTV
    
    #python3 modifyBinning.py BpMass_ABCDnn templatesD_Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST 0.2 1
    #python3 modifyBinning_smooth2Dcorr_traincorr.py D Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST
    #python3 plotHists.py $iPlot D True _Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST False False _smoothedJJ_rebinned1_stat0p2_smoothedTV
    #####################################################

    ###################################################
    # Tune 2D smoothing fraction for smoothing uncert #
    ###################################################
    #python3 modifyBinning.py BpMass_ABCDnn templatesV2_Jan2025_210binsBtargetHoleCorrABCpABCTrain_2Dsmooth_rebin 0.2 1
    #python3 plotHists.py $iPlot V2 True _Jan2025_210binsBtargetHoleCorrABCpABCTrain_2Dsmooth_rebin False False _rebinned1_stat0p2

    #python3 modifyBinning.py BpMass_ABCDnn templatesD_Jan2025_210binsBtargetHoleCorrABCpABCTrain_2Dsmooth_rebin 0.2 1
    #python3 plotHists.py $iPlot D True _Jan2025_210binsBtargetHoleCorrABCpABCTrain_2Dsmooth_rebin False False _rebinned1_stat0p2
    ###################################################
    # try different smoothing fractions
    #python3 modifyBinning_smooth2Dcorr_traincorr.py V2 Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_0p045
    #python3 modifyBinning_smooth2Dcorr_traincorr.py V2 Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_0p18
    #python3 modifyBinning_smooth2Dcorr_traincorr.py V2 Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_0p035
    #python3 modifyBinning_smooth2Dcorr_traincorr.py V2 Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_0p12
    #python3 modifyBinning_smooth2Dcorr_traincorr.py D Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_0p005
    #python3 modifyBinning_smooth2Dcorr_traincorr.py D Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_0p005
    #python3 modifyBinning_smooth2Dcorr_traincorr.py D Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_0p12
    
    # Add smoothing uncertainty
    #python3 modifyBinning_smooth2Dcorr_jecjer.py V2 Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST
    #python3 modifyBinning.py BpMass_ABCDnn templatesV2_Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST 0.2 1
    #python3 modifyBinning_smooth2Dcorr_traincorr.py V2 Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST
    #python3 modifyBinning_smooth2Dcorr_smoothfrac.py V2 Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST

    #python3 modifyBinning_smooth2Dcorr_jecjer.py D Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST
    #python3 modifyBinning.py BpMass_ABCDnn templatesD_Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST 0.2 1
    #python3 modifyBinning_smooth2Dcorr_traincorr.py D Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST
    #python3 modifyBinning_smooth2Dcorr_smoothfrac.py D Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST

    #python3 combineDV2.py Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST _smoothedJJ_rebinned1_stat0p2_smoothedTV_smoothUncert

    #python3 plotHists.py $iPlot V2 True _Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST False False _smoothedJJ_rebinned1_stat0p2_smoothedTV_smoothUncert
    
    #python3 plotHists.py $iPlot D True _Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST False False _smoothedJJ_rebinned1_stat0p2_smoothedTV_smoothUncert

    #python3 plotHists.py $iPlot V2 True _Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST False False _rebinned1_stat0p2

    #python3 plotHists.py $iPlot D True _Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST False False _rebinned1_stat0p2_smoothedTV_smoothUncert
    
    ###################################################################
    # ARC response -- smoothUncert study with two alternative methods #
    ###################################################################
    ###### smoothUncert from 2D ######
    #python3 modifyBinning_smooth2Dcorr_jecjer.py V2 Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_2DsmoothUncert
    #python3 modifyBinning.py BpMass_ABCDnn templatesV2_Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_2DsmoothUncert 0.2 1
    #python3 modifyBinning_smooth2Dcorr_traincorr.py V2 Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_2DsmoothUncert
    #python3 modifyBinning_smooth2Dcorr_smooth2D.py V2 Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_2DsmoothUncert

    #python3 modifyBinning_smooth2Dcorr_jecjer.py D Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_2DsmoothUncert
    #python3 modifyBinning.py BpMass_ABCDnn templatesD_Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_2DsmoothUncert 0.2 1
    #python3 modifyBinning_smooth2Dcorr_traincorr.py D Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_2DsmoothUncert
    #python3 modifyBinning_smooth2Dcorr_smooth2D.py D Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_2DsmoothUncert

    #python3 combineDV2.py Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_2DsmoothUncert _smoothedJJ_rebinned1_stat0p2_smoothedTV_smoothUncert 

    # python3 modifyBinning_smooth2Dcorr_jecjer.py D Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_clipped
    # python3 modifyBinning.py BpMass_ABCDnn templatesD_Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_clipped 0.2 1
    # python3 modifyBinning_smooth2Dcorr_traincorr.py D Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_clipped
    # python3 modifyBinning_smooth2Dcorr_smooth.py D Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_clipped

    # python3 plotHists.py $iPlot D True _Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_clipped False False _smoothedJJ_rebinned1_stat0p2_smoothedTV_smoothUncert

    ###### smoothUncert from 1D ######
    #python3 modifyBinning_smooth2Dcorr_jecjer.py D Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST
    #python3 modifyBinning.py BpMass_ABCDnn templatesD_Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST 0.2 1
    #python3 modifyBinning_smooth2Dcorr_traincorr.py D Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST
    #python3 modifyBinning_smooth2Dcorr_smooth2D.py D Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST
    #python3 plotHists.py $iPlot D True _Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST False False _smoothedJJ_rebinned1_stat0p2_smoothedTV_smooth2DUncert

    # cp -r templatesD_Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST/templates_BpMass_ABCDnn_138fbfb_smoothedJJ_rebinned1_stat0p2.root templatesD_Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_0p005
    # cp -r templatesD_Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST/templates_BpMass_ABCDnn_138fbfb_smoothedJJ_rebinned1_stat0p2.root templatesD_Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_0p02
    # cp -r templatesD_Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST/templates_BpMass_ABCDnn_138fbfb_smoothedJJ_rebinned1_stat0p2.root templatesD_Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_0p035
    # cp -r templatesD_Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST/templates_BpMass_ABCDnn_138fbfb_smoothedJJ_rebinned1_stat0p2.root templatesD_Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_0p14

    # then do it one by one: change smoothFrac in modifyBinning_smooth2Dcorr_traincorr.py
    #python3 modifyBinning_smooth2Dcorr_traincorr.py D Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_0p005
    #python3 modifyBinning_smooth2Dcorr_traincorr.py D Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_0p02
    #python3 modifyBinning_smooth2Dcorr_traincorr.py D Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_0p035
    #python3 modifyBinning_smooth2Dcorr_traincorr.py D Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_0p14
    
    #python3 modifyBinning_smooth2Dcorr_smoothfrac.py D Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST


    # try smoothB for case 1 and 2 as smoothing uncert
    #python3 modifyBinning_smooth2Dcorr_smoothB.py D Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_smoothBUncert
    # all the script after this: act on root file with _smoothBUncert tag
    #python3 modifyBinning_smooth2Dcorr_jecjer.py D Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_smoothBUncert
    #python3 modifyBinning.py BpMass_ABCDnn templatesD_Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_smoothBUncert 0.2 1
    #python3 modifyBinning_smooth2Dcorr_traincorr.py D Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_smoothBUncert
    #python3 modifyBinning_smooth2Dcorr_smoothB_smooth.py D Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_smoothBUncert
    #python3 plotHists.py $iPlot D True _Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_smoothBUncert False False _smoothBUncert_smoothedJJ_rebinned1_stat0p2_smoothedTV

    ##############################
    # ANv8: smooth2D uncert only #
    ##############################
    #python3 modifyBinning_smooth2Dcorr_jecjer.py D Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST
    #python3 modifyBinning.py BpMass_ABCDnn templatesD_Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST 0.2 1
    #python3 modifyBinning_smooth2Dcorr_traincorr.py D Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST
    #python3 modifyBinning_smooth2Dcorr_smooth2D.py D Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST
    #python3 plotHists.py $iPlot D True _Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST False False _smoothedJJ_rebinned1_stat0p2_smoothedTV_smooth2DUncert
    #python3 plotHists.py $iPlot D True _Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST False False _smoothedJJ_rebinned1_stat0p2_smoothedTV_smooth2DUncert
    
    #####################################
    # ANv8: V2 plots without correction #
    #####################################
    #python3 modifyBinning_smooth2Dcorr_jecjer.py V2 Jan2025_210bins_noCorrection
    #python3 modifyBinning.py BpMass_ABCDnn templatesV2_Jan2025_210bins_noCorrection
    #python3 plotHists.py $iPlot V2 True _Jan2025_210bins_noCorrection False True _smoothedJJ_rebinned1_stat0p2
    #python3 plotHists.py $iPlot V2 True _Jan2025_210bins_noCorrection False True _smoothedJJ_rebinned3_stat0p2

    ### Plot for paper ###
    python3 plotHists_paper.py $iPlot V2 True _Jan2025_210bins_noCorrection False True _smoothedJJ_rebinned1_stat0p07
    
    #####################################################################
    # ARC request: compare smoothB for case 1 and 2 as smoothing uncert #
    #####################################################################
    # '0p005','0p02','0p035','0p14'
    #python3 modifyBinning_smooth2Dcorr_jecjer.py D Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_smoothBUncert
    #python3 modifyBinning_smooth2Dcorr_jecjer.py D Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_2DsmoothUncert
    # python3 modifyBinning_smooth2Dcorr_jecjer.py D Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST
    # cp -r templatesD_Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST/templates_BpMass_ABCDnn_138fbfb_smoothedJJ.root templatesD_Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_0p005
    # cp -r templatesD_Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST/templates_BpMass_ABCDnn_138fbfb_smoothedJJ.root templatesD_Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_0p02
    # cp -r templatesD_Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST/templates_BpMass_ABCDnn_138fbfb_smoothedJJ.root templatesD_Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_0p035
    # cp -r templatesD_Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST/templates_BpMass_ABCDnn_138fbfb_smoothedJJ.root templatesD_Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_0p14

    # then do it one by one: change smoothFrac in modifyBinning_smooth2Dcorr_traincorr.py
    # python3 modifyBinning_smooth2Dcorr_traincorr.py D Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_0p005
    # python3 modifyBinning_smooth2Dcorr_traincorr.py D Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_0p02
    # python3 modifyBinning_smooth2Dcorr_traincorr.py D Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_0p035
    # python3 modifyBinning_smooth2Dcorr_traincorr.py D Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_0p14
    
    # ##python3 modifyBinning.py BpMass_ABCDnn templatesD_Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_smoothBUncert 0.2 1
    # #python3 modifyBinning_smooth2Dcorr_traincorr.py D Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_smoothBUncert
    #python3 modifyBinning_smooth2Dcorr_traincorr.py D Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_2DsmoothUncert
    #python3 modifyBinning_smooth2Dcorr_traincorr.py D Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST
    #python3 modifyBinning_smooth2Dcorr_smoothfrac.py D Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST
    #python3 modifyBinning_smooth2Dcorr_smooth2D.py D Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_2DsmoothUncert
    
    # # nom->smoothUncert nom_from_diff_dir->new_nom
    #python3 modifyBinning_smooth2Dcorr_smoothB.py D Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_smoothBUncert

    # Add smoothing uncertainty + clip the turn on region
    # python3 clipHistogram.py V2
    # python3 modifyBinning_smooth2Dcorr_jecjer.py V2 Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_clipped
    # python3 modifyBinning.py BpMass_ABCDnn templatesV2_Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_clipped 0.2 1
    # python3 modifyBinning_smooth2Dcorr_traincorr.py V2 Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_clipped
    # python3 modifyBinning_smooth2Dcorr_smooth.py V2 Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_clipped
    # ##python3 plotHists.py $iPlot V2 True _Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST False False _rebinned1_stat0p2_smoothedTV_smoothUncert
    # python3 plotHists.py $iPlot V2 True _Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_clipped False False _smoothedJJ_rebinned1_stat0p2_smoothedTV_smoothUncert

    # python3 clipHistogram.py D
    # python3 modifyBinning_smooth2Dcorr_jecjer.py D Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_clipped
    # python3 modifyBinning.py BpMass_ABCDnn templatesD_Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_clipped 0.2 1
    # python3 modifyBinning_smooth2Dcorr_traincorr.py D Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_clipped
    # python3 modifyBinning_smooth2Dcorr_smooth.py D Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_clipped
    ##python3 plotHists.py $iPlot D True _Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST False False _rebinned1_stat0p2_smoothedTV_smoothUncert
    #python3 plotHists.py $iPlot D True _Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST False False _smoothedJJ_rebinned1_stat0p2_smoothedTV_smoothUncert
    #python3 plotHists.py $iPlot D True _Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_clipped False False _smoothedJJ_rebinned1_stat0p2_smoothedTV_smoothUncert

    #python3 clipHistogram.py V2 _smoothedJJ_rebinned1_stat0p2_smoothedTV_smoothUncert
    #python3 plotHists.py $iPlot V2 True _Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_clipped False False _smoothedJJ_rebinned1_stat0p2_smoothedTV_smoothUncert

    #python3 clipHistogram.py D _smoothedJJ_rebinned1_stat0p2_smoothedTV_smoothUncert
    #python3 plotHists.py $iPlot D True _Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_clipped False False _smoothedJJ_rebinned1_stat0p2_smoothedTV_smoothUncert
    
    #python3 combineDV2.py Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_clipped _smoothedJJ_rebinned1_stat0p2_smoothedTV_smoothUncert

    #python3 combineDV2.py Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST _smoothedJJ_rebinned1_stat0p2_smoothedTV_smoothUncert

    #python3 combineDV2.py Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST _smoothedJJ_rebinned1_stat0p2_smoothedTV
    
    #python3 modifyBinning_smooth2Dcorr_jecjer.py D Jan2025_210binsBtargetHoleCorrBTrain_smooth2D_rebin
    #python3 modifyBinning.py BpMass_ABCDnn templatesD_Jan2025_210binsBtargetHoleCorrBTrain_smooth2D_rebin 0.2 1
    #python3 plotHists.py $iPlot D True _Jan2025_210binsBtargetHoleCorrBTrain_smooth2D_rebin False False _smoothedJJ_rebinned1_stat0p2

    # python3 modifyBinning_smooth2Dcorr_jecjer.py V2 Jan2025_210binsBtargetHoleCorrBTrain_smooth2D_rebin
    # python3 modifyBinning.py BpMass_ABCDnn templatesV2_Jan2025_210binsBtargetHoleCorrBTrain_smooth2D_rebin 0.2 1
    # python3 plotHists.py $iPlot V2 True _Jan2025_210binsBtargetHoleCorrBTrain_smooth2D_rebin False False _smoothedJJ_rebinned1_stat0p2

    #python3 modifyBinning_smooth2Dcorr_jecjer.py D Jan2025_210binsBtargetHoleCorrBTrain_2Dsmooth_rebin
    #python3 modifyBinning.py BpMass_ABCDnn templatesD_Jan2025_210binsBtargetHoleCorrBTrain_2Dsmooth_rebin 0.2 1
    #python3 plotHists.py $iPlot D True _Jan2025_210binsBtargetHoleCorrBTrain_2Dsmooth_rebin False False _smoothedJJ_rebinned1_stat0p2

    #################################################
    # L3 suggestion: use two smoothUncerts together #
    #################################################
    # python3 modifyBinning_smooth2Dcorr_jecjer.py V2 Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST
    # python3 modifyBinning.py BpMass_ABCDnn templatesV2_Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST 0.2 1
    #python3 modifyBinning_smooth2Dcorr_traincorr.py V2 Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST
    #python3 modifyBinning_smooth2Dcorr_smooth2D.py V2 Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST
    #python3 modifyBinning_smooth2Dcorr_smoothfrac.py V2 Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST
    #python3 modifyBinning_smooth2Dcorr_smooth2Dfrac.py V2 Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST

    #python3 modifyBinning_smooth2Dcorr_jecjer.py D Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST
    #python3 modifyBinning.py BpMass_ABCDnn templatesD_Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST 0.2 1
    #python3 modifyBinning_smooth2Dcorr_traincorr.py D Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST
    #python3 modifyBinning_smooth2Dcorr_smooth2D.py D Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST
    #python3 modifyBinning_smooth2Dcorr_smoothfrac.py D Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST
    #python3 modifyBinning_smooth2Dcorr_smooth2Dfrac.py D Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST 

    #python3 combineDV2.py Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST_2DsmoothUncert _smoothedJJ_rebinned1_stat0p2_smoothedTV_smoothUncert

    #python3 plotHists.py $iPlot D True _Jan2025_210binsBtargetHoleCorrBTrain_smooth_rebin_dynamicST False False _smoothedJJ_rebinned1_stat0p2

    # ##### UNBLINDING ####
    # ANv7 2D smooth
    #python3 modifyBinning_smooth2Dcorr_jecjer.py D Jan2025_105binsBtargetHoleCorrABCpABCTrain_2Dsmooth_rebin
    #python3 modifyBinning.py BpMass_ABCDnn templatesD_Jan2025_105binsBtargetHoleCorrABCpABCTrain_2Dsmooth_rebin 0.2 1
    #python3 plotHists.py $iPlot D True _Jan2025_105binsBtargetHoleCorrABCpABCTrain_2Dsmooth_rebin False False _smoothedJJ_rebinned1_stat0p2

    #python3 modifyBinning_smooth2Dcorr_jecjer.py V2 Jan2025_105binsBtargetHoleCorrABCpABCTrain_2Dsmooth_rebin
    #python3 modifyBinning.py BpMass_ABCDnn templatesV2_Jan2025_105binsBtargetHoleCorrABCpABCTrain_2Dsmooth_rebin 0.2 1
    #python3 plotHists.py $iPlot V2 True _Jan2025_105binsBtargetHoleCorrABCpABCTrain_2Dsmooth_rebin False False _rebinned1_stat0p2

    #python3 modifyBinning_smooth2Dcorr_jecjer.py D Jan2025_105binsBtargetHoleCorrABCpABCTrain_2Dsmooth_rebin
    #python3 modifyBinning.py BpMass_ABCDnn templatesD_Jan2025_105binsBtargetHoleCorrABCpABCTrain_2Dsmooth_rebin 0.2 1
    #python3 plotHists.py $iPlot D True _Jan2025_105binsBtargetHoleCorrABCpABCTrain_2Dsmooth_rebin False False _rebinned1_stat0p2

    # python3 combineDV2.py Jan2025_105binsBtargetHoleCorrABCpABCTrain_2Dsmooth_rebin _smoothedJJ_rebinned1_stat0p2

    #####################
    
    # ANv7: VR before correction
    #python3 modifyBinning.py BpMass_ABCDnn templatesD_Jan2025_105bins 0.2 1
    #python3 plotHists.py $iPlot D True _Jan2025_105bins False False _rebinned1_stat0p2
    
    #python3 modifyBinning.py BpMass_ABCDnn templatesV2_Jan2025_105bins 0.2 1
    #python3 plotHists.py $iPlot V2 True _Jan2025_105bins False False _rebinned1_stat0p2

    ####################
    # without 2D smoothing JECJER smoothing
    #python3 modifyBinning.py BpMass_ABCDnn templatesV2_Jan2025_210binsBtargetHoleCorrABCpABCTrain_2Dsmooth_rebin 0.2 1
    #python3 plotHists.py $iPlot V2 True _Jan2025_210binsBtargetHoleCorrABCpABCTrain_2Dsmooth_rebin False False _rebinned1_stat0p2 

    #python3 modifyBinning.py BpMass_ABCDnn templatesD_Jan2025_105binsBtargetHoleCorrABCpABCTrain_2Dsmooth_rebin 0.2 1
    #python3 plotHists.py $iPlot D True _Jan2025_105binsBtargetHoleCorrABCpABCTrain_2Dsmooth_rebin False False _rebinned1_stat0p2

    #########
    # with JECJER smoothing for 2D smoothing
    #python3 modifyBinning_smooth2Dcorr_jecjer.py D Jan2025_210binsBtargetHoleCorrABCpABCTrain_2Dsmooth_rebin
    #python3 modifyBinning.py BpMass_ABCDnn templatesD_Jan2025_210binsBtargetHoleCorrABCpABCTrain_2Dsmooth_rebin 0.2 1
    #python3 plotHists.py $iPlot D True _Jan2025_210binsBtargetHoleCorrABCpABCTrain_2Dsmooth_rebin False False _smoothedJJ_rebinned1_stat0p2

    #python3 modifyBinning_smooth2Dcorr_jecjer.py V2 Jan2025_210binsBtargetHoleCorrABCpABCTrain_2Dsmooth_rebin
    #python3 modifyBinning.py BpMass_ABCDnn templatesV2_Jan2025_210binsBtargetHoleCorrABCpABCTrain_2Dsmooth_rebin 0.2 1
    #python3 plotHists.py $iPlot V2 True _Jan2025_210binsBtargetHoleCorrABCpABCTrain_2Dsmooth_rebin False False _smoothedJJ_rebinned1_stat0p2
    
    #python3 modifyBinning_smooth2Dcorr_jecjer.py V2 Jan2025_210binsBtargetHoleCorrABCpACHoleTrain_2Dsmooth_rebin
    #python3 modifyBinning.py BpMass_ABCDnn templatesV2_Jan2025_210binsBtargetHoleCorrABCpACHoleTrain_2Dsmooth_rebin 0.2 1
    #python3 plotHists.py $iPlot V2 True _Jan2025_210binsBtargetHoleCorrABCpACHoleTrain_2Dsmooth_rebin False False _smoothedJJ_rebinned1_stat0p2

    #python3 modifyBinning_smooth2Dcorr_jecjer.py D Jan2025_105binsBtargetHoleCorrBTrain_smooth_rebin_2018
    #python3 modifyBinning.py BpMass_ABCDnn templatesD_Jan2025_105binsBtargetHoleCorrBTrain_smooth_rebin_2018 0.2 1
    #python3 modifyBinning_smooth2Dcorr_traincorr.py D Jan2025_105binsBtargetHoleCorrBTrain_smooth_rebin_2018
    #python3 plotHists.py $iPlot D True _Jan2025_105binsBtargetHoleCorrBTrain_smooth_rebin_2018 False False _2018_smoothedJJ_rebinned1_stat0p2_smoothedTV

    # ANv7: V2 without correction
    #python3 modifyBinning.py BpMass_ABCDnn templatesV2_Jan2025_210bins_noCorrection 0.2 1
    #python3 plotHists.py $iPlot V2 True _Jan2025_210bins_noCorrection False False _rebinned1_stat0p2

    # ARC: ABCDnn by category (no correction)
    #python3 modifyBinning.py BpMass_ABCDnn templatesV2_Jan2025_210binsNoCorrectionByCategory 0.2 1
    #python3 plotHists.py $iPlot V2 True _Jan2025_210binsNoCorrectionByCategory False False #_rebinned1_stat0p2

    # Unblind Step 2 check: year-by-year gof
    #python3 modifyBinning_smooth2Dcorr_jecjer.py D Jan2025_105binsBtargetHoleCorrBTrain_smooth_rebin_2016
    #python3 modifyBinning.py BpMass_ABCDnn templatesD_Jan2025_105binsBtargetHoleCorrBTrain_smooth_rebin_2016APV 0.2 1
    #python3 modifyBinning_smooth2Dcorr_traincorr.py D Jan2025_105binsBtargetHoleCorrBTrain_smooth_rebin_2018
    #python3 plotHists.py $iPlot D True _Jan2025_105binsBtargetHoleCorrBTrain_smooth_rebin_2018 False False _2018_smoothedJJ_rebinned1_stat0p2_smoothed

    #python3 modifyBinning.py BpMass_ABCDnn templatesD_Jan2025_210binsBtargetHoleCorrBTrain 0.2 1
    #python3 modifyBinning_smooth2Dcorr.py D Jan2025_210binsBtargetHoleCorrBTrain
    #python3 plotHists.py $iPlot D True _Jan2025_210binsBtargetHoleCorrBTrain True True _rebinned1_stat0p2_smoothed_TVJJ

    #python3 modifyBinning.py BpMass_ABCDnn templatesV2_Jan2025_210binsBtargetHoleCorrBTrain 0.2 1
    #python3 modifyBinning_smooth2Dcorr.py V2 Jan2025_210binsBtargetHoleCorrBTrain
    #python3 plotHists.py $iPlot V2 True _Jan2025_210binsBtargetHoleCorrBTrain False True _rebinned1_stat0p2_smoothed_TVJJ

    #python3 combineDV2.py Jan2025_210binsBtargetHoleCorrBTrain _rebinned1_stat0p2_smoothed_TVJJ


    #cp -r templatesD_Jan2025_210binsBtargetHoleCorrBTrainTrainCorrUCS1 templatesD_Jan2025_210binsBtargetHoleCorrBTrainTrainUCC3
    #cp -r templatesV2_Jan2025_210binsBtargetHoleCorrBTrainTrainCorrUCS1 templatesV2_Jan2025_210binsBtargetHoleCorrBTrainTrainUCC3
    #python3 uncorrUncert.py D False Jan2025_210binsBtargetHoleCorrBTrainCorrUCAll
    #python3 uncorrUncert.py V2 False Jan2025_210binsBtargetHoleCorrBTrainCorrUCAll
    #python3 combineDV2.py Jan2025_210binsBtargetHoleCorrBTrainCorrUCAll _rebinned1_stat0p2_smoothed_TVJJ_UC

    # python3 modifyBinning.py BpMass_ABCDnn templatesD_Jan2025_210binsBtargetHoleCorrACTrainHole 0.2 1
    # python3 modifyBinning_smooth2Dcorr.py D Jan2025_210binsBtargetHoleCorrACTrainHole
    # python3 plotHists.py $iPlot D True _Jan2025_210binsBtargetHoleCorrACTrainHole False True _rebinned1_stat0p2_smoothed_TVJJ

    #python3 modifyBinning.py BpMass_ABCDnn templatesV2_Jan2025_210binsBtargetHoleCorrACTrainHole 0.2 1
    #python3 modifyBinning_smooth2Dcorr.py V2 Jan2025_210binsBtargetHoleCorrACTrainHole
    #python3 plotHists.py $iPlot V2 True _Jan2025_210binsBtargetHoleCorrACTrainHole False True _rebinned1_stat0p2_smoothed_TVJJ

    #python3 combineDV2.py Jan2025_210binsBtargetHoleCorrACTrainHole _rebinned1_stat0p2_smoothed_TVJJ
    
    # python3 modifyBinning.py BpMass_ABCDnn templatesD_Jan2025_210binsBtargetHoleCorrACTrain 0.2 1
    # python3 modifyBinning_smooth2Dcorr.py D Jan2025_210binsBtargetHoleCorrACTrain
    # python3 plotHists.py $iPlot D True _Jan2025_210binsBtargetHoleCorrACTrain False True _rebinned1_stat0p2_smoothed_TVJJ

    # python3 modifyBinning.py BpMass_ABCDnn templatesV2_Jan2025_210binsBtargetHoleCorrACTrain 0.2 1
    # python3 modifyBinning_smooth2Dcorr.py V2 Jan2025_210binsBtargetHoleCorrACTrain
    # python3 plotHists.py $iPlot V2 True _Jan2025_210binsBtargetHoleCorrACTrain False True _rebinned1_stat0p2_smoothed_TVJJ

    # python3 combineDV2.py Jan2025_210binsBtargetHoleCorrACTrain _rebinned1_stat0p2_smoothed_TVJJ
    
    
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
