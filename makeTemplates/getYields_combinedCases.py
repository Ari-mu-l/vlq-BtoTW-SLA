import numpy as np

case = "case23"
procList = ["BpM1400", "ttbar", "qcd", "wjets", "singletop", "ewk", "ttx"]
nameMap = {"BpM1400": "1.4 TeV",
           "ttbar": "ttbar",
           "qcd": "QCD",
           "wjets": "W jets",
           "singletop": "ST",
           "ewk": "EWK",
           "ttx": "ttbar+X",
           }

for proc in procList:
    table = f'{nameMap[proc]} '
    for region in ["A", "B", "C", "X", "Y"]:
        try:
            inFile = open(f'templates{region}_Oct2024StatsOnly/yields_BpMass_138fbfb_rebinned_stat0p2.txt')
            #inFile = open(f'/uscms/home/jmanagan/nobackup/BtoTW/CMSSW_13_0_18/src/vlq-BtoTW-SLA/makeTemplates/templates{region}_Oct2024/yields_BpMass_138fbfb_rebinned_stat0p2.txt', 'r')
        except:
            print(f'text file does not exist for {region}')
            continue
        topTable = (inFile.read().split('isL_untag_yields')[0]).split('isL_tag_yields')[1]
        tableLines = topTable.split('\n')[3:]
        for line in tableLines:
            if proc in line:
                yieldContent = (line.split(' \\\\ ')[0]).split(' & ')[1:]
                if case=="case14":
                    caseYield = float(yieldContent[0].split(' $\pm$ ')[0]) + float(yieldContent[3].split(' $\pm$ ')[0])
                    caseUncer = np.sqrt((float(yieldContent[0].split(' $\pm$ ')[1]))**2 + (float(yieldContent[3].split(' $\pm$ ')[1]))**2)
                elif case=="case23":
                    caseYield = float(yieldContent[1].split(' $\pm$ ')[0]) + float(yieldContent[2].split(' $\pm$ ')[0])
                    caseUncer = np.sqrt((float(yieldContent[1].split(' $\pm$ ')[1]))**2 + (float(yieldContent[2].split(' $\pm$ ')[1]))**2)
                else:
                    print("Unrecognized case")
                    exit()
        table += f'& {round(caseYield,2)} $\pm$ {round(caseUncer,2)} '
        if region=="Y":
            table += '\\\\'
    #print(f'{proc} yield table for {case}: ')
    print(table, '\n')
    
    
