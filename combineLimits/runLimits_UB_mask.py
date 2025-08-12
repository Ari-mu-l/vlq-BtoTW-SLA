import os,sys
from ROOT import TFile, TObject, RooArgSet

## Arguments: limit directory name; mass point; signal amount to inject; number of toys

## Make a datacard first with datacard.py!

limitdir = sys.argv[1]
path = limitdir+'/'
os.chdir(path)
blind = False # unblind
morph = True

print('====================================================================')
print('==   Launching limits for in',limitdir)
print('==   ...')

masks = 'mask_Case1_D=0,mask_Case2_D=0,mask_Case3_D=1,mask_Case4_D=1'

print('***** Running Asymptotic CLs limits for all masses in'+os.getcwd()+' *****')
print('Running Asymptotic CLs limits for all masses')
print('Command = combineTool.py -M AsymptoticLimits -d cmb/*/workspace.root --there -n .limitUB')
#os.system('combineTool.py -M AsymptoticLimits -d cmb/*/workspace.root --there -n .limitUB')
os.system(f'combineTool.py -M AsymptoticLimits -d cmb/*/workspace.root --there -n .limitUB --setParameters {masks}')

print('Making a JSON file')
print('Command = combineTool.py -M CollectLimits cmb/*/*.limitUB.* --use-dirs -o limitsUB_cmb.json')
#os.system('combineTool.py -M CollectLimits cmb/*/*.limitUB.* --use-dirs -o limitsUB_cmb.json')
os.system(f'combineTool.py -M CollectLimits cmb/*/*.limitUB.* --use-dirs -o limitsUB_cmb.json --setParameters {masks}')

print('Done!')
print('====================================================================')

