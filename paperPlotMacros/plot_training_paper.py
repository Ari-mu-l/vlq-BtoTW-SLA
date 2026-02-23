# python3 plot_training_paper.py -m logBpMlogST_mmd1_case14_random22

import numpy as np
import os
from argparse import ArgumentParser
from json import load
from array import array
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
#plt.rcParams['font.sans-serif'] = ['Helvetica']
#plt.rcParams['font.family'] = 'sans-serif'
import mplhep as hep # cms style
hep.style.use("CMS")

#import matplotlib.font_manager as fm
#fm._rebuild()

parser = ArgumentParser()
parser.add_argument( "-m", "--tag", required = True )
args = parser.parse_args()

variable = "Bprime_mass"

region_key = { # the row and column of ABCDXY
  0: {
    0: "X", 1: "Y"
  },
  1: {
    0: "A", 1: "C" 
  },
  2:{
    0: "B", 1: "D"
  }
}

with open(f'hists_{args.tag}_{variable}.json', 'r') as jsonfile:
  hists_dict = load(jsonfile)
  
bins = np.array(hists_dict["bins"], dtype=int)

def plot_hist( ax, x, y ):
  region = region_key[x][y]
  
  data_mod     = np.array(hists_dict[region]["data_mod"])
  mc_true_hist = np.array(hists_dict[region]["mc_true_hist"])
  mc_pred_hist = np.array(hists_dict[region]["mc_pred_hist"])
  
  data_mod_scale = float( np.sum(data_mod) )
  mc_true_scale  = float( np.sum(mc_true_hist) )
  mc_pred_scale  = float( np.sum(mc_pred_hist) )

  # plot the data first
  if region!="D":
    ax.errorbar(
      0.5 * ( bins[1:] + bins[:-1] ),
      data_mod / data_mod_scale, yerr = np.sqrt( data_mod ) / data_mod_scale,
      label = "Data",
      marker = "o", markersize = 3, markerfacecolor = "black", markeredgecolor = "black",
      elinewidth = 1, ecolor = "black" , capsize = 2, lw = 0, zorder=3
    )
    
  # plot the mc
  ax.errorbar(
    0.5 * ( bins[1:] + bins[:-1] ),
    mc_true_hist / mc_true_scale, yerr = np.sqrt( mc_true_hist ) / mc_true_scale,
    label = "Source",
    marker = ",", drawstyle = "steps-mid", lw = 2, color = "#f89c20" #, alpha = 0.7
  )

  # plot the predicted    
  ax.fill_between(
    0.5 * ( bins[1:] + bins[:-1] ),
    y2 = np.zeros( len( mc_pred_hist ) ),
    y1 = mc_pred_hist / mc_pred_scale, step = "mid",
    label = "ABCDnn",
    color = "#5790fc", alpha = 0.8,
  )

  # plot ABCDnn stats uncert
  ax.fill_between(
    0.5 * ( bins[1:] + bins[:-1] ),
    y1 = ( mc_pred_hist + np.sqrt( mc_pred_hist ) ) / mc_pred_scale,
    y2 = ( mc_pred_hist - np.sqrt( mc_pred_hist ) ) / mc_pred_scale,
    interpolate = False, step = "mid",
    label = "ABCDnn Uncert.",
    facecolor = "none", edgecolor="gray", linewidth=0, hatch='\\\\\\\\'
  )

  ax.set_xlim( 0, 2500 )
  ax.set_ylim( 0, 0.15 )
  ax.set_yticks( [0.02, 0.04, 0.06, 0.08, 0.10] )
  if y==0:
    ax.set_ylabel(r"$N_{bin}/N_{tot}$", y=0.8, fontsize=18)
    ax.tick_params(axis='y', labelsize=15)
  else:
    ax.tick_params(axis='y', labelsize=0)
  ax.tick_params(axis='x', which='both', labelbottom=False, labelsize=15)

  ax.text(
    0.06, 0.9, f'Region {region}',
    ha = "left", va = "top", transform = ax.transAxes, fontsize = 16 #, fontweight='bold' # guideline suggest to not use bold
  )
  if 'case23' in args.tag:
    ax.text(
      0.06, 0.8, f'LepT',
      ha = "left", va = "top", transform = ax.transAxes, fontsize = 16
    )
  elif 'case14' in args.tag:
    ax.text(
      0.06, 0.8, f'LepW',
      ha = "left", va = "top", transform = ax.transAxes, fontsize = 16
    )
  else:
    os.exit('Unexpected tag category')
    
  handles, labels = ax.get_legend_handles_labels()
  if len(handles)>3:
    ax.legend([handles[2], handles[3], handles[0], handles[1]], ["Data", "MC", "ABCDnn", "ABCDnn Uncert."], loc = "upper right", ncol = 1, fontsize = 16 )
  else:
    ax.legend([handles[2], handles[0], handles[1]], ["MC", "ABCDnn", "ABCDnn Uncert."], loc = "upper right", ncol = 1, fontsize = 16 )

def plot_ratio( ax, x, y ):
  region = region_key[x][y]

  data_mod     = np.array(hists_dict[region]["data_mod"])
  mc_true_hist = np.array(hists_dict[region]["mc_true_hist"])
  mc_pred_hist = np.array(hists_dict[region]["mc_pred_hist"])

  data_mod_scale = float( np.sum(data_mod) )
  mc_true_scale  = float( np.sum(mc_true_hist) )
  mc_pred_scale  = float( np.sum(mc_pred_hist) )
    
  ratio = []
  ratio_std = []
  data_uncert = []
  for i in range( len( data_mod ) ):
    if data_mod[i] == 0 or mc_pred_hist[i] == 0: 
      ratio.append(0)
      ratio_std.append(0)
      data_uncert.append(0)
    else:
      ratio.append( ( data_mod[i] / float( data_mod_scale ) ) /  ( mc_pred_hist[i] / float( mc_pred_scale ) ) )
      if mc_pred_hist[i]==0:
        ratio_std.append(0)
      else:
        ratio_std.append( np.sqrt(2/mc_pred_hist[i]))
      data_uncert.append((np.sqrt( data_mod[i] ) / data_mod_scale) / ( mc_pred_hist[i] / float( mc_pred_scale ) ))

  if region!="D":
    # plot data uncert in ratio panel
    ax.errorbar(
      0.5 * ( bins[1:] + bins[:-1] ),
      ratio, yerr = data_uncert,
      marker = "o", markersize = 3, markerfacecolor = "black", markeredgecolor = "black",
      elinewidth = 1, ecolor = "black" , capsize = 2, lw = 0,
      zorder = 3
    )

  ax.fill_between(
    0.5 * ( bins[1:] + bins[:-1] ),
    y1 = 1 + np.array( ratio_std ), #np.array( ratio ) + np.array( ratio_std ),
    y2 = 1 - np.array( ratio_std ), #np.array( ratio ) - np.array( ratio_std ),
    interpolate = False, step = "mid",
    facecolor = "none", edgecolor="gray", linewidth=0, hatch='\\\\\\\\'
    #label="Stat. Uncert."
  )

  ax.grid(axis='y', color='black', linestyle='--')

  if y==1:
    ax.set_xlabel( "${\mathrm{\mathit{m}}_{tW}\,[GeV]}$", ha = "right", x = 1.0, fontsize = 20 )
    #ax.set_xlabel( r"{}".format( config.variables[ variable ][ "LATEX" ] ), ha = "right", x = 1.0, fontsize = 20, fontname='Times New Roman' )
    ax.set_xlim( 0, 2500 )
  else:
    ax.set_ylabel( "Data/ABCDnn", loc = "bottom", fontsize = 14 )
    ax.set_xlim( 0, 2500 )
    xticks = ax.xaxis.get_major_ticks()
    xticks[-1].label1.set_visible(False)
  ax.set_yticks( [ 0.60, 0.80, 1.0, 1.20, 1.40 ] )
  ax.set_ylim( 0.5, 1.49 )
  if y==1:
    ax.tick_params( axis = "y", labelsize = 0 )
  else:
    ax.tick_params( axis = "both", labelsize = 15 )
  ax.tick_params( axis = "x", which = "both", top = False, labelsize = 15 )
  if x != 2: ax.axes.xaxis.set_visible(False)


fig, axs = plt.subplots( 6, 2, figsize = (12,15), gridspec_kw = { "height_ratios": [3,1,3,1,3,1] } ) # figsize = (9,12)
plt.subplots_adjust(wspace=0.04, hspace=0)
#plt.subplots_adjust(left=0.1, right=0.9, bottom=0.1, top=0.9)
#hep.cms.label("Preliminary", lumi=138.0, ax=axs[0][0], loc=0, fontsize=10)
hep.cms.text("", ax=axs[0][0], loc=0, fontsize=22)
hep.cms.lumitext(text="138 fb$^{-1}$ (13 TeV)", ax=axs[0][1], fontsize=22)

for x in range(6):
  for y in range(2):
    if x % 2 == 0:
      plot_hist(
        ax = axs[x,y],
        x = int( x / 2 ), y = y
      )
    else:
      plot_ratio(
        ax = axs[x,y],
        x = int((x-1)/2), y = y
      )
    if(x!=0):
      position_old = axs[x,y].get_position()
      position_new = axs[x-1,y].get_position()
      points_old = position_old.get_points()
      points_new = position_new.get_points()
      points_old[1][1] = points_new[0][1]
      position_old.set_points( points_old )
      axs[x,y].set_position( position_old )

plt.savefig( f"plots/{args.tag}_{variable}.png" )
plt.savefig( f"plots/{args.tag}_{variable}.pdf" )
plt.close()

print(f"{args.tag}_{variable}.png created")
print(f"{args.tag}_{variable}.pdf created")
