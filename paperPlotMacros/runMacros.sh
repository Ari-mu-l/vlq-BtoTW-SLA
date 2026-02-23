mkdir -p plots

# kinematic plots
root -l -q BpMass_138fbfb_isL_alltotBand_paper.C
root -l -q BpDecay_138fbfb_isL_alltotBand_paper.C
root -l -q NBJets_138fbfb_isL_alltotBand_paper.C
root -l -q NJetsForward_138fbfb_isL_alltotBand_paper.C

# Bbq VR prefit before correction
root -l -q -b BpMass_ABCDnn_138fbfb_isL_untagTlep_V2_smoothedJJ_rebinned1_stat0p2_NBBW_logytotBand_paper.C

# Bbq SR postfit
root -l -q -b BpMass_ABCDnn_138fb_Case1_D_postfit_NBBW_pull_logy.C
root -l -q -b BpMass_ABCDnn_138fb_Case2_D_postfit_NBBW_pull_logy.C
root -l -q -b BpMass_ABCDnn_138fb_Case3_D_postfit_NBBW_pull_logy.C
root -l -q -b BpMass_ABCDnn_138fb_Case4_D_postfit_NBBW_pull_logy.C

# xsec limits
python3 PlotLimits_paper.py limitsUB_cmb_cmb_Bbq.json
python3 PlotLimits_paper.py limitsUB_cmb_cmb_Btq.json

# coupling limits
root -l -q -b combiLimits_VLQ_Bb_coupling_singlet_.C
root -l -q -b combiLimits_VLQ_Bt_coupling_singlet_.C
root -l -q -b combiLimits_VLQ_Bt_coupling_doublet_.C

ABCDnn training plots
python3 plot_training_paper.py -m logBpMlogST_mmd1_case14_random22
python3 plot_training_paper.py -m logBpMlogST_mmd1_case23_random33
