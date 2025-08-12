import os,sys,shutil,datetime,time,random
from ROOT import *

exec(open("/uscms_data/d3/jmanagan/EOSSafeUtils.py").read())

start_time = time.time()

#IO directories must be full paths
outputDir='/eos/uscms/store/user/xshen/CombineV10_BpInjection' ## CHANGE MY PATH!
condorDir='/uscms_data/d3/xshen/combinejobs_BpInjection/' ## CHANGE MY PATH!
tarfile = '/uscms_data/d3/jmanagan/combineV10.tar' ## LEAVE ME! -- don't change to your folder

runDir=os.getcwd()
whichjob = sys.argv[1]
limitdir = sys.argv[2]
mass = sys.argv[3]

if whichjob == 'inject':
    rInj = float(sys.argv[4])
    nToys = int(sys.argv[5])
    executable = 'condorToyFitting.sh'
elif whichjob == 'gof':
    rInj = 0
    nToys = int(sys.argv[4])
    executable = 'condorGofFitting.sh'
    outputDir = outputDir.replace('Injection','GOF')
    condorDir = condorDir.replace('Injection','GOF')

if whichjob == 'inject':
    name = limitdir.replace('limits_templatesABCDnn_V2_Jan2025_','').replace('limits_templatesABCDnn_DV2_Jan2025_','')+'InjR'+str(rInj).replace('.','p')+'CDMS0'
else:
    name = limitdir.replace('limits_templatesABCDnn_V2_Jan2025_','').replace('limits_templatesABCDnn_DV2_Jan2025_','')+'GOF'
path = limitdir+'/cmb/'+mass
outDir=outputDir[10:]+'/'+limitdir+'_'+mass
condorDir += limitdir+'_'+mass

isSR = False
#if '_DV2' in limitdir: isSR = True
#if '_D' in limitdir: isSR = True 

#if isSR and '_DV2' in limitdir:
if '_DV2' in limitdir:
    toysperjob = 25
    filename = 'morphedWorkspace.root'
    maskstring = '--setParameters mask_Case1_D=0,mask_Case2_D=0,mask_Case3_D=0,mask_Case4_D=0,mask_Case1_V2=1,mask_Case2_V2=1,mask_Case3_V2=1,mask_Case4_V2=1' # unmask D, remask V after V-only fit
    maskstring += ',signalScale=0.01' # set 10fb after CR-only fit

else:
    toysperjob = 25
    filename = 'initialFitWorkspace.root'
    #maskstring = '--setParameters mask_Case1_D=0,mask_Case2_D=0,mask_Case3_D=1,mask_Case4_D=1' # unblind step2 requested test: gof with case1 and case2
    maskstring = '' # shouldn't need to change anything

if whichjob == 'gof': filename = 'workspace.root' # GOF always just starts from the bare workspace, assuming CR categories only

print('Starting submission')
count=0

os.system('eos root://cmseos.fnal.gov/ mkdir -p '+outDir)
os.system('mkdir -p '+condorDir)

ijob = 0
for i in range(0,nToys,toysperjob):  
    ijob += 1

    seed = random.randrange(100000,999999)
    print('Job',ijob,'using seed',seed)

    count+=1
    dict={'RUNDIR':runDir, 'EXEC':executable, 'CONDORDIR':condorDir, 'OUTPUTDIR':outDir, 'PATH':path, 'WORKSPACE':filename, 'NTOYS':toysperjob, 'RINJ':rInj, 'RMIN':rInj-10, 'RMAX':rInj+10,
          'NAME':name, 'MASKS':maskstring, 'TARBALL':tarfile, 'INDEX':ijob, 'SEED':seed}
    
    if not EOSpathExists(outDir+'/fitDiagnostics'+name+'_'+str(ijob)+'.root'): ## this is a super baseline failure checker -- if there's a file, don't resubmit

        jdfName=condorDir+'/%(NAME)s_%(INDEX)s.job'%dict
        print("jdfname: ",jdfName)
        jdf=open(jdfName,'w')
        jdf.write(
            """use_x509userproxy = true
universe = vanilla
Executable = %(RUNDIR)s/%(EXEC)s
Should_Transfer_Files = YES
WhenToTransferOutput = ON_EXIT
Transfer_Input_Files = %(TARBALL)s, %(RUNDIR)s/%(PATH)s/%(WORKSPACE)s
Output = %(NAME)s_%(INDEX)s.out
Error = %(NAME)s_%(INDEX)s.err
Log = %(NAME)s_%(INDEX)s.log
request_memory = 2000
Notification = Never
Arguments = "%(OUTPUTDIR)s %(WORKSPACE)s %(NTOYS)s %(RINJ)s %(RMIN)s %(RMAX)s %(NAME)s %(SEED)s '%(MASKS)s' %(INDEX)s"

Queue 1"""%dict)
        jdf.close()
        os.chdir('%s/'%(condorDir))
        os.system('condor_submit %(NAME)s_%(INDEX)s.job'%dict)
        os.system('sleep 0.5')                                
        os.chdir('%s'%(runDir))
        print(count, "jobs submitted!!!")
    else:
        print('Found this file, skipping! fitDiagnostics'+name+'_'+str(ijob)+'.root')

print("--- %s minutes ---" % (round(time.time() - start_time, 2)/60))





