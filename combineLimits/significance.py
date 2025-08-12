import os,sys

# construct the distribution of the test statistic
combine -M AsymptoticLimits datacard.txt --LHCmode LHC-significance  --saveToys --fullBToys --saveHybridResult -T toys -i 5 -s 12345

# observed significance
combine -M AsymptoticLimits datacard.txt --LHCmode LHC-significance --readHybridResult --toysFile=input.root
