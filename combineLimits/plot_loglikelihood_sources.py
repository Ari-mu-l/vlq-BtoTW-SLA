#!/usr/bin/env python
from argparse import ArgumentParser
import json

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from dataclasses import dataclass, field
import scipy.stats as st
import numpy as np

import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.PyConfig.IgnoreCommandLineOptions = True

####Classes for handling the fit models
@dataclass
class Model:
    
    obs:  list
    exp: list
    pulls: dict 
    prefit_pulls: dict
    data_labels: list

    def __post_init__(self):
        self._check_obs_exp_lengths()
        self._check_pull_types()
    
    class DataAndExpectationHaveDifferentNumberOfEntriesError(Exception):
        pass

    def _check_obs_exp_lengths(self):
        same_length = ( len(self.obs) == len(self.exp) )
        if not same_length:
            raise self.DataAndExpectationHaveDifferentNumberOfEntriesError()
    
    class PullNameIsNotAStringException(Exception):
        pass

    class NoMatchingPrefitPullException(Exception):
        pass

    def _check_pull_types(self):
        for k, v in self.pulls.items():
            if not isinstance(k, str):
                raise self.PullNameIsNotAStringException(f'Pull key is {k}, of type {type(k)}, but all keys but be string instances')
            if not k in self.prefit_pulls:
                raise self.NoMatchingPrefitPullException(f'Pull key {k}, is in the post-fit pulls but not found in the pre-fit pulls.')
    
    def poisson_likelihoods(self):
        return np.array([ st.poisson(n_exp).pmf(n_obs) for n_exp, n_obs in zip(self.exp, self.obs) ])

    def poisson_nll(self):
        return -sum( np.log( self.poisson_likelihoods()) )

    def pull_likelihoods(self):
        return { name :st.norm().pdf( pull -self.prefit_pulls[name] )  for name, pull in self.pulls.items() }

    def pull_nll(self):
        logs = np.log( np.array([ pval for _, pval in self.pull_likelihoods().items() ]) )
        return -sum(logs) 

    def single_pull_nll(self, pull):
        return -np.log(st.norm().pdf( self.pulls[pull] ) )

    def full_nll(self):
        return self.pull_nll() + self.poisson_nll()
        

@dataclass
class FitResult:

    signal_model: Model
    bkg_model: Model

    def  __post_init__(self):
        self._check_same_nuisances()
        self._check_same_observations()

    class SignalBkgModelDifferentObsError(Exception):
        pass

    def _check_same_observations(self):
        for idx, (val_sig, val_bkg) in enumerate(zip(self.signal_model.obs, self.bkg_model.obs)):
            if not val_sig == val_bkg:
                raise self.SignalBkgModelDifferentObsError(f'Signal And Background Model must share observations but found observation values {val_sig} and {val_bkg}, for the {idx}th observation, which are not equal')

    class DifferentPullsException(Exception):
        pass

    def _check_same_nuisances(self):
        names_sig = set(self.signal_model.pulls.keys())
        names_bkg = set(self.bkg_model.pulls.keys())
        if not  ( set(names_bkg) == set(names_sig) ):
            raise self.DifferentPullsException(f'Signal and Background must share pulls, but found {names_bkg.difference(names_sig)} only in the backgorund model and {names_sig.difference(names_bkg)} only in the signal model')

    def get_neg_log_likelihood_ratio(self):
        nll1 = self.signal_model.full_nll()
        nll2 = self.bkg_model.full_nll()
        return nll2 - nll1
    
    def get_wilks_value( self):
        return 2*self.get_neg_log_likelihood_ratio()
    
    def get_significance(self,ndf=1,verbose=True):
        chi_val = self.get_wilks_value( )
        pvalue = 1-st.chi2(ndf).cdf( chi_val)
        sigma = -st.norm().ppf( pvalue/2 )
        return np.sign(0.5-pvalue)*sigma



### Convenience functions for data manipulation
def get_cumulativeDeltaLL_df( df ):
    df['log-likelihood'] = df['value'].apply( lambda x : np.log( st.norm().pdf( x ) ) )
    dfcomb = df.pivot( index='name', columns='type', values='log-likelihood')
    dfcomb['DeltaLL'] = dfcomb['sbfit'] - dfcomb['bfit']
    dfcomb[r'$\Delta$ Log-Likelihood'] = dfcomb['DeltaLL']
    dfcomb.sort_values('DeltaLL', inplace=True, ascending=False)
    dfcomb['SumDeltaLL'] = dfcomb['DeltaLL'].cumsum()
    
    return dfcomb.reset_index()

def get_data_df( bkg_model, sig_model):
    data_log_likelihoods = []
    for idx, (b_ll, sb_ll, region) in enumerate(zip(bkg_model.poisson_likelihoods(), sig_model.poisson_likelihoods(), bkg_model.data_labels)):
        dct = {'name': idx, 'bin': idx, 'b-only likelihood':b_ll, 'signal+bkg likelihood':sb_ll, r'$\Delta$ Log-Likelihood': np.log(sb_ll) - np.log(b_ll), 'region':region }
        data_log_likelihoods += [ dct ]
    data_df = pd.DataFrame(data_log_likelihoods)
    data_df['SumDeltaLL'] = data_df[r'$\Delta$ Log-Likelihood'].cumsum()
    return data_df

def get_pulls( fpf_s, fpf_b, prefit):
    # loop over all fitted parameters
    all_values = []
    for i in range(fpf_s.getSize()):
    
        nuis_s = fpf_s.at(i)
        name   = nuis_s.GetName();
        nuis_b = fpf_b.find(name)
        nuis_p = prefit.find(name)
    
        if name.startswith('yield'):
            continue
        elif name == 'r':
            continue
        for fit_name, nuis_x in [('prefit', nuis_p), ('bfit', nuis_b), ('sbfit',nuis_s)]:
            values = {}
            values['name'] = name
            values['type'] = fit_name
            if nuis_x == None:
                values['value'] = None
            else:
                values['value'] = nuis_x.getVal()
            all_values += [ values ]

    return all_values

def group_minor_nuisances( df, min_diff, new_name=None ):

    if new_name is None:
        new_name = f'Other Nuisances [ abs(DLL) < {min_diff} ]'

    missing_entries = df[ abs(df[r'$\Delta$ Log-Likelihood']) < min_diff ]
    if len(missing_entries) > 0:
        df = df[ abs(df[r'$\Delta$ Log-Likelihood']) > min_diff ]
        missing_entry_sum = missing_entries[r'$\Delta$ Log-Likelihood'].sum()
        missing_entry_cum_sum = missing_entries['SumDeltaLL'].iloc[-1]
        last_index = missing_entries.index[-1]
        new_entry = { 'name': new_name, r'$\Delta$ Log-Likelihood': missing_entry_sum, 'SumDeltaLL': missing_entry_cum_sum, 'index':last_index }
        missing_entry_summary = pd.DataFrame( [new_entry] )
        missing_entry_summary.set_index( 'index', inplace=True )
        df = pd.concat( [df, missing_entry_summary], sort=True )
        df = df.sort_index() #not sure why the above sort=True isnt enough
    return df

def get_region_names_from_fit_file( fit_file, shapes_dir='shapes_fit_b' ):
    shapes_dir = fit_file.Get(shapes_dir)
    key_names = [ key.GetName() for key in shapes_dir.GetListOfKeys() ]
    region_names = []
    for name in key_names:
        obj = shapes_dir.Get( name )
        if isinstance(obj,ROOT.TDirectory):
            region_names += [ name ]
    return region_names

def read_expectations_and_data( fit_file, alt_file=None,  regions=[None]):
    obs=[]
    b_exp=[]
    s_exp=[]
    region_labels = []
    for this_region in regions:
        region_dir = "" if this_region is None else f"{this_region}/"
        h_b_exp = fit_file.Get(f"shapes_fit_b/{region_dir}total_background")
        
        add_total= "total_" if this_region is None else ""
        h_data = fit_file.Get(f"shapes_fit_b/{region_dir}{add_total}data")
        add_overall = "_overall" if this_region is None else ""
        if alt_file is None:
            h_s_exp = fit_file.Get(f"shapes_fit_s/{region_dir}total{add_overall}")
        else:
            h_s_exp = alt_file.Get(f"shapes_fit_b/{region_dir}total_background")
        
        region_name = region_names.get(this_region, this_region)
        n_bins = h_b_exp.GetNbinsX()
        for binno in range(1, n_bins+1):
            data = h_data.GetPointY( binno-1 )
            bkg = h_b_exp.GetBinContent(binno)
            bkgsig = h_s_exp.GetBinContent( binno )
            if (data == 0 ) and (bkg ==0) and (bkgsig) ==0:
                continue
            obs +=  [ data ]
            b_exp += [ bkg ]
            s_exp += [ bkgsig ]
            region_labels += [ region_name ]

    return (obs, b_exp, s_exp, region_labels)

def translate_nuisance_names( df, name_dict ):
    df['name'] = df['name'].apply( lambda nuis_name : name_dict.get( nuis_name, nuis_name)  )
    return df

#### Plotting functions
def get_region_boundaries(df):
    boundaries = []
    for region, r_df in df.groupby(['region']):
        max_val = r_df['bin'].max()
        boundaries += [ max_val + 0.5 ]
    return boundaries

def draw_region_boundaries(df, ax ):
        lines_coords = get_region_boundaries(df)
        lines_coords.sort()
        for boundary in lines_coords[:-1]:
            ax.axvline( boundary, dashes=[5,5,5,5], color='black' )

def get_region_centers(df):
    centers = {}
    for region, r_df in df.groupby(['region']):
        max_val = r_df['bin'].max()
        min_val = r_df['bin'].min()
        center = (max_val + min_val)/2
        centers[region] = center
    return centers

def draw_region_names(df, ax):
    regions = get_region_centers(df)
    y_lims = ax.get_ylim()
    y_coord = y_lims[1] - (y_lims[1] - y_lims[0])*0.1
    for name, center in regions.items():
        ax.annotate( name, # this is the text
                     (center,y_coord), # these are the coordinates to position the label
                     #textcoords="offset points", # how to position the text
                     #xytext=(0,0), # distance from text to points (x,y)
                     ha='center',
                     color='black') 

   
def annotate_cumulative(df, ax, color='lightsteelblue'):
    
    median = np.floor( len(df)/2)
    y_coord = df.loc[median]['SumDeltaLL']
    
    ax.annotate('Cumulative Difference', # this is the text
                 (median,y_coord), # these are the coordinates to position the label
                 textcoords="offset points", # how to position the text
                 xytext=(0,10), # distance from text to points (x,y)
                 ha='center',
                 color=color) 
   
def add_cumulative_plot(df, ax, color='lightsteelblue'):
    sns.pointplot(x='name',y=r'SumDeltaLL', data=df, ax=ax, color=sum_colour) #, s=1 ) # got an error with s. param not recognized
    annotate_cumulative( df, ax, color=sum_colour )
    ax.set_ylabel( r'$\Delta$ Log-Likelihood' )

def plot_data_delta_nll(df, plot_cumulative=True, draw_regions=True, bar_colour='salmon', sum_colour='lightsteelblue' ):
    col_arg=None
    the_aspect =len(df)/20.
    #height_arg, aspect_arg = None, None
    if (not draw_regions) and len(df['region'].unique()) > 1:
        col_arg='region'
        bar_colour=None
    elif draw_regions:
        boundaries = [0] + get_region_boundaries( df )
        boundaries.sort()
        sizes = [ boundaries[idx+1] - val for idx, val in enumerate(boundaries[:-1]) ]
        #the_aspect = 0.2/(min(sizes)/len(df))
        the_aspect =len(df)/45
        
    fg = sns.catplot(x='bin', y=r'$\Delta$ Log-Likelihood', data=df, kind='bar', color=bar_colour, hue=col_arg, aspect=the_aspect )    

    if plot_cumulative:
        add_cumulative_plot( df, fg.axes[0][0], color=sum_colour)
    if draw_regions:
        draw_region_boundaries(df, fg.axes[0][0])
        draw_region_names(df, fg.axes[0][0])
    fg.axes[0][0].set_xlabel( 'Bin' )
    fg.set_xticklabels(labels=fg.axes[-1][-1].get_xticklabels(), rotation=45, horizontalalignment='right', fontsize=5)
    return fg

def plot_pull_delta_nlls( df, plot_cumulative=True, bar_colour='salmon', sum_colour='lighsteelblue', min_pull_dll=None):

    if not min_pull_dll is None:
        df = group_minor_nuisances(df, min_pull_dll)

    fg = sns.catplot(x='name', y=r'$\Delta$ Log-Likelihood', data=df, kind='bar', color=bar_colour, aspect=len(df)/45. )    
    if plot_cumulative:
        add_cumulative_plot(df, fg.axes[0][0], color=sum_colour)
    fg.axes[0][0].set_xlabel( 'Nuisance' )
    fg.set_xticklabels(labels=fg.axes[-1][-1].get_xticklabels(), rotation=45, horizontalalignment='right', fontsize=5)
    return fg

def plot_summary_delta_nll( data_df, pull_df, bar_colour='salmon', sum_colour='lightsteelblue', min_pull_dll=None):
    
    data_df['source'] = 'Stats'
    if not min_pull_dll is None:    
        pull_df = group_minor_nuisances( pull_df, min_pull_dll)
    pull_df['source'] = 'Pulls'

    new_df = pd.concat([pull_df,data_df], sort=True)
    fg = sns.FacetGrid(new_df, row="source",sharex=False, height=7.5, aspect=len(df)/60, row_order=['Stats','Pulls']) #aspect=2.3, row_order=['Stats','Pulls']) #gridspec_kws={"width_ratios":[3,1]})
    nuis_ax = fg.axes[1][0]
    data_ax = fg.axes[0][0]
    sns.pointplot(x='name',y=r'SumDeltaLL', data=pull_df, ax=nuis_ax, color=sum_colour) #, s=1 )
    sns.pointplot(x='name',y=r'SumDeltaLL', data=data_df, ax=data_ax, color=sum_colour) #, s=1 )
    fg.map( sns.barplot, 'name', r'$\Delta$ Log-Likelihood', color=bar_colour )
    data_ax.set_xticklabels(labels=nuis_ax.get_xticklabels(), rotation=45, horizontalalignment='right', fontsize=5)
    nuis_ax.set_xticklabels(labels=nuis_ax.get_xticklabels(), rotation=45, horizontalalignment='right', fontsize=5)
    #plt.subplots_adjust(hspace=1)
    annotate_cumulative( pull_df, nuis_ax, color=sum_colour)
    annotate_cumulative( data_df, data_ax, color=sum_colour)

    draw_region_boundaries(data_df, data_ax)
    draw_region_names(data_df, data_ax)

    data_ax.set_xlabel('Bin', fontsize=15)
    nuis_ax.set_xlabel('Nuisance',fontsize=15)
    for ax in fg.axes[:,0]:
        ax.set_ylabel(r'$\Delta$ Log-Likelihood', fontsize=20)
    fg.set_titles(row_template='', col_template='')
    return fg


parser = ArgumentParser(usage="usage: %(prog)s <fit_file> [options]. \n The <fit_file> is expected to follow the format of running the CMS combine tool fitDiagnostics. Specifically, it should have RooFit results named 'nuisances_prefit', 'fit_b' and 'fit_s', and the output shapes of the expectation and data should be stores in the subfolders 'shapes_prefit/', 'shapes_fit_b', and 'shapes_fit_s'.   \nrun with --help to get list of options")
parser.add_argument("-f", "--fitfile", type=str, help="Fit diagnostics file containing the fits and shapes.", required=True)
parser.add_argument("-p", "--plotfile", dest="plotfile", default=None, type=str, help="If true, plot the pulls of the nuisances to files using this name prefix (can include a path). [default %(default)s]")
parser.add_argument("-s", "--show-plots",  action="store_true", default=False, help="show plots interactively [default %(default)s].")
parser.add_argument("-r", "--regions", nargs='+',default=[None], type=str, help="For data likelihoods, only plot these regions (space separated list) [default: %(default)s]")
parser.add_argument("-d", "--drop-regions", nargs='+',default=[], type=str, help="For data likelihoods, exclude these regions (space separated list) [default: %(default)s]")
parser.add_argument("-c", "--config", default=None, type=str, help="json file with 'region_names' and/or 'nuisance_names' dictionaries that translate from the name in the code to the human readable one. [default: %(default)s]")
parser.add_argument("--compare",default=None, help="Compare two alternative background fits rather than the signal to a background, must give the name of the fitDiagnostic file with the other bakground fit, which is then treated as signal fit. [default %(default)s].")
parser.add_argument("--min-pull-dll",type=float,default=None, help="Combine nuisances where the absolute log-likeihood difference is smaller than this value into one source for plotting purposes. [default %(default)s].")

args = parser.parse_args()

fit_file = ROOT.TFile.Open(args.fitfile,"READ")
if fit_file == None: raise RuntimeError(f"Cannot open file {args.fitfile}")

alternate_file = None
if not args.compare is None:
    alternate_file = ROOT.TFile(args.compare)
    if alternate_file == None: raise RuntimeError(f"Cannot open file {args.compare}")

fit_s  = fit_file.Get("fit_s") if args.compare is None else alternate_file.Get("fit_b")
fit_b  = fit_file.Get("fit_b")
prefit = fit_file.Get("nuisances_prefit")
if fit_s == None or fit_s.ClassName()   != "RooFitResult": raise RuntimeError( "File %s does not contain the output of the signal fit 'fit_s'"     % args[0])
if fit_b == None or fit_b.ClassName()   != "RooFitResult": raise RuntimeError( "File %s does not contain the output of the background fit 'fit_b'" % args[0])
if prefit == None or prefit.ClassName() != "RooArgSet":    raise RuntimeError( "File %s does not contain the prefit nuisances 'nuisances_prefit'"  % args[0])
fpf_b = fit_b.floatParsFinal()
fpf_s = fit_s.floatParsFinal()


regions = args.regions
if regions == [None]: #Take the regions from the files
    regions = get_region_names_from_fit_file( fit_file )
    if len(regions) == 0: #revert back to no regions default if no subdirectories found
        regions = [None]
    
for to_drop in args.drop_regions:
    regions.remove(to_drop)

region_names = {}
nuisance_names = {}
if not args.config is None:
    with open(args.config, 'r') as f:
        name_translations = json.load(f)
    region_names = name_translations.get('region_names',{})
    nuisance_names = name_translations.get('nuisance_names',{})


#get the data and expectations
obs, b_exp, s_exp, region_labels = read_expectations_and_data( fit_file, alt_file=alternate_file, regions=regions)

# get the fitted parameters
all_values = get_pulls( fpf_s, fpf_b, prefit)
df = pd.DataFrame(  all_values )
s_pulls = { row['name'] : row['value'] for _, row in df[ df['type'] == 'sbfit' ].iterrows() }
b_pulls = { row['name'] : row['value'] for _, row in df[ df['type'] == 'bfit' ].iterrows() }
prefit_pulls = { row['name'] : row['value'] for _, row in df[ df['type'] == 'prefit'].iterrows() }

b_model = Model( obs, b_exp, b_pulls, prefit_pulls, data_labels=region_labels)
s_model = Model( obs, s_exp, s_pulls, prefit_pulls, data_labels=region_labels)

pull_df = get_cumulativeDeltaLL_df( df )
pull_df = translate_nuisance_names( pull_df, nuisance_names)

data_df = get_data_df( b_model, s_model )
    
bar_colour='salmon'
sum_colour='lightsteelblue'

fg = plot_pull_delta_nlls(pull_df, bar_colour=bar_colour, sum_colour=sum_colour, min_pull_dll=args.min_pull_dll)
if not args.plotfile is None:
    plt.savefig(f'{args.plotfile}_nuisance.pdf', bbox_inches='tight')
elif args.show_plots:
    plt.show()
    
draw_regions = not (regions == [None])
fg = plot_data_delta_nll(data_df, draw_regions=draw_regions, bar_colour=bar_colour, sum_colour=sum_colour)
if not args.plotfile is None:
    plt.savefig(f'{args.plotfile}_data.pdf', bbox_inches='tight')
elif args.show_plots:
    plt.show()

fg = plot_summary_delta_nll(data_df, pull_df, bar_colour=bar_colour, sum_colour=sum_colour, min_pull_dll=args.min_pull_dll)
if not args.plotfile is None:
    plt.savefig(f'{args.plotfile}_summary.pdf', bbox_inches='tight')
elif args.show_plots:
    plt.show()

fr = FitResult(s_model, b_model)
nll = fr.get_neg_log_likelihood_ratio()
print( f'The significance in these regions is: {fr.get_significance()}' )

