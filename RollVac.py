import sys
import os
import shutil
import chopper
import gDocsImport



# DENOTES SEPARATION ON GDOCS SPREADSHEET FOR FILE LOADING, MUST MATCH

varFolders = False
paramsStart = "Study Name Prefix (optional),Diagnosis Based"
avStart = "Condition Threshold Subpopulation,Condition Date"
avStop = "Raw Epifast Script Appender"
startWord = "Subpopulation,Day/'enum',Length of Spread"
stopWord = "Diagnosis Model Version,Antiviral Model Version,"

####NEW EPIFAST FORMAT COMMANDS

# GENERATE EMPTY EPIFAST INTERVENTION SCRIPT BLOCKS & CONVERT BLOCKS TO TEXT

def prepNewSubpop():
    temp = dict(subpopulationID = 'null',
    subpopulationName = 'null',
    subpopulationFile = 'null')
    return temp
    
def getSubpopText(subpop):
    pos = 0
    limit = 1
    isList = False
    if isinstance(subpop,list):
        subpops = subpop
        limit = len(subpop)
        isList = True
    while pos < limit:
        if isList:
            subpop = subpops[pos]
    text = makeIfFound(subpop['subpopulationID'],"SubpopulationId = ")
    text += makeIfFound(subpop['subpopulationName'],"SubpopulationName = ")
    text += makeIfFound(subpop['subpopulationFile'],"SubpopulationFile = ") + '\n'
    print "Subpop(s) block\n", text
    return text
    
def prepNewAction():
    temp = dict(actionID = 'null',
    actionDescription = 'null',
    actionDelay = 'null',
    actionDuration = 'null',
    actionConsumption = 'null',
    actionType = 'null',
    actionEfficacy = 'null',
    actionEfficacyIn = 'null',
    actionEfficacyOut = 'null')
    return temp
    
def getActionText(action):
    pos = 0
    limit = 1
    isList = False
    if isinstance(action,list):
        actions = action
        limit = len(action)
        isList = True
    while pos < limit:
        if isList:
            action = actions[pos]
        text = makeIfFound(action['actionID'],"ActionId = ")
        text += makeIfFound(action['actionDescription'],"ActionDescription = ")
        text += makeIfFound(action['actionDelay'],"ActionDelay = ")
        text += makeIfFound(action['actionDuration'],"ActionDuration = ")
        text += makeIfFound(action['actionConsumption'],"ActionConsumption = ")
        text += makeIfFound(action['actionType'],"ActionType = ")
        text += makeIfFound(action['actionEfficacy'],"ActionEfficacy = ")
        text += makeIfFound(action['actionEfficacyIn'],"ActionEfficacyIn = ")
        text += makeIfFound(action['actionEfficacyOut'],"ActionEfficacyOut = ") + '\n'
        pos += 1
    print "Action(s) block\n",text
    return text

def prepNewIntervention():
    temp = dict(interventionID = 'null',
    interventionType = 'null',
    conditionState = 'null',
    conditionDate = 'null',
    conditionTotal = 'null',
    conditionMembership = 'null',
    conditionMutex = 'null',
    conditionCompliance = 'null',
    conditionThresholdValue = 'null',
    conditionThresholdSubpopulation = 'null',
    action = 'null')
    print temp
    return temp
    
def getInterventionText(interv):
    pos = 0
    limit = 1
    isList = False
    if isinstance(interv,list):
        intervs = interv
        limit = len(interv)
        isList = True
    while pos < limit:
        if isList:
            interv = intervs[pos]
        text = makeIfFound(interv['interventionID'],"InterventionId = ")
        text += makeIfFound(interv['interventionType'],"InterventionType = ")
        text += makeIfFound(interv['conditionState'],"ConditionState = ")
        text += makeIfFound(interv['conditionDate'],"ConditionDate = ")
        text += makeIfFound(interv['conditionTotal'],"ConditionTotal = ")
        text += makeIfFound(interv['conditionMemberShip'],"ConditionMemberShip = ")
        text += makeIfFound(interv['conditionMutex'],"ConditionMutex = ")
        text += makeIfFound(interv['conditionCompliance'],"ConditionCompliance = ")
        text += makeIfFound(interv['conditionThresholdValue'],"ConditionThresholdValue = ")
        text += makeIfFound(interv['conditionThresholdSubpopulation'],"ConditionThresholdSubpopulation = ") + '\n'
        pos += 1
    print "Intervention(s) block\n",text
    return text
    
def getTotalText(total):
    text = "TotalId = 9100\n"
    text += "TotalName = Vaccine Supply\n"
    text += "Total Amount = " + str(total['vaccination']) + '\n\n'
    text += "TotalId = 9101\n"
    text += "TotalName = Antiviral Supply\n"
    text += "Total Amount = " + str(total['antiviral']) + '\n\n'
    return text

# GENERATE FINAL OUTPUT    
            
def getOutputNew(subpop, total, action, interv):
    return getSubpopText(subpop) + getTotalText(total) + getActionText(action) + getInterventionText(interv)
    
    
    
#PREPS SCRIPT OUTPUT IF BLOCK HAS CONTENTS

def makeIfFound(argument, markup):
    string = ""
    if argument != 'null':
        string += markup + argument + '\n'
    return string

    
            
# FIND ID REFERENCE TO SUBPOP

def getSubpopID(subpops,name):
    pos = 0
    print "Checking subpops for name", name
    while pos < len(subpops):
        if subpops[pos]['subpopulationName'] == name or subpops[pos]['subpopulationFile'] == name:
            ID = subpops[pos]['subpopulationID'] 
            print name, "found at ID", ID
            return ID
        pos += 1
    print "Subopulation", name, "not in subpops list"
    return 'null'
    
def getActionType(actions,action):
    pos = 0
    print "Checking actions for action", action
    while pos < len(actions):
        if actions[pos]['actionID'] == action:
            return actions[pos]['actionType']
        pos += 1
    print "Action", action, "not in actions list"
    return 'null'
 
# APPENDS SUBPOP IF NOT YET PRESENT      
                
def addSubpop(subpops, name, directory, count):
    if getSubpopID(subpops,name) == 'null':
        tempSubpop = prepNewSubpop()
        tempSubpop['subpopulationName'] = name
        tempSubpop['subpopulationFile'] = directory + name
        tempSubpop['subpopulationID'] = str(count)
        subpops.append(tempSubpop)
        print "Subpop", name, "added"
        return 1
    else:
        return 0
    
# READS AVSCRIPT, APPENDS TO ACTION IDS & INTERVENTION IDS

def prepNewAV(avScript, diagParams, outName, directory, subpopDirectory, totalsNew):
    
    tempDirectory = subpopDirectory + '/' + outName
    tempDirectory = tempDirectory.replace('//','/')
    
    subPopNew = []
    actionNew = []
    intervNew = []
    avCount = 5000
    subCount = 9000
    mutStart = 9300
    
    print "Initiating new format AV scripting"
    probDiag = diagParams[4]
    probHosp = diagParams[3]
    probCoeff = float(probDiag) * float(probHosp)
    print "Diagnoses [%s] and to hospital [%s] joined as compliance coefficient [%s]" % (probDiag,probHosp,probCoeff)
    if len(diagParams[2]) != 0:
        totalsNew['antiviral'] = str(diagParams[2])
        print "Antiviral total loaded from file,",totalsNew['antiviral'],"units available"
    else:
        print "No AV unit count found, using default value of", totalsNew['antiviral'], "antiviral units"
    
    configV = diagParams[1]
    
    print "Prepping AV subpopulation list"
    pos = 0
    length = len(avScript)
    while pos < length:
        if len(avScript[pos][0]) != 0:
            subCount += addSubpop(subPopNew,avScript[pos][0],tempDirectory,subCount)
        if len(avScript[pos][4]) != 0: 
            subCount += addSubpop(subPopNew,avScript[pos][4],tempDirectory,subCount)
        pos += 1
    
    print "Converting AV script to new action & intervention format"
    pos = 0
    length = len(avScript)
    mutex = []
    
    while pos < length:
        tempAction = prepNewAction()
        tempInterv = prepNewIntervention()
        tempAction['actionID'] = tempInterv['action'] = str(avCount+pos)
        tempAction['actionType'] = tempAction['actionDescription'] = "Antiviral"
        tempInterv['interventionType'] = 'Offline'
        tempInterv['interventionID'] = str(mutStart+pos)
        tempInterv['conditionTotal'] = '9101'
        
        if len(avScript[pos][1]) != 0:
            tempInterv['conditionDate'] = avScript[pos][1]
        if len(avScript[pos][2]) != 0:
            if percentFix(avScript[pos][2]) >= 1:
                tempInterv['conditionThresholdValue'] = + avScript[pos][2]
            else:
                tempInterv['conditionThresholdFraction'] = + str(percentFix(avScript[pos][2]))
        if len(avScript[pos][0]) != 0:
            tempInterv['conditionThresholdSubpopulation'] = getSubpopID(subPopNew,avScript[pos][0])
        if isYes(avScript[pos][3], "Condition Diagnosis"):
           tempInterv['conditionState'] = 'Diagnosed'
        if len(avScript[pos][4]) != 0:
            tempInterv['conditionMembership'] = getSubpopID(subPopNew,avScript[pos][4])
        if isYes(avScript[pos][5], "Condition Mutually Exclusive"):
            mutex.append(str(mutStart+pos))
        
        tempInterv['conditionCompliance'] = str(float(avScript[pos][6]) * probCoeff)
        tempAction['actionDelay'] = avScript[pos][7]
        tempAction['actionDuration'] = avScript[pos][8]
        tempAction['actionConsumption'] = str(int(avScript[pos][9])*int(avScript[pos][8]))
        tempAction['actionEfficacyIn'] = avScript[pos][10]
        tempAction['actionEfficacyOut'] = avScript[pos][11]
        
        actionNew.append(tempAction)
        intervNew.append(tempInterv)
        
        pos +=1
    
    pos = 0
    length = len(avScript)
    """while pos < length:
        if str(pos+9300) in mutex:
            intervNew[pos]['conditionMutex'] = ";".join(mutex)
        else:
            intervNew[pos]['conditionMutex'] = str(mutStart+pos)
        pos += 1"""
    
    print "Antiviral treatment scripting complete"
    return {'configV':str(configV),'actions':actionNew,'interventions':intervNew,'subpops':subPopNew}

#RETURNS ENUMERATION AS PERCENTAGES RATHER THAN COUNTS FOR NEW FORMAT

def countEnum(enumerator,size):
    pos1 = 1
    print
    workEnum =  enumerator[:]
    total = 0
    limit =  len(workEnum)    
    while pos1 < limit+1:
        temp = float(workEnum[pos1])
        if temp > 1:
            workEnum[pos1] = float(temp/size)
            print "Count", temp, "of population size", size, "converted to", workEnum[pos1], "percent for new format enumeration" 
        else:
            workEnum[pos1] = int(workEnum[pos1])
        total += workEnum[pos1]*size
        pos1 += 2
    return {'enum':workEnum,"total":total} 
    
#APPEND RAW EPISCRIPT

def appendRaw(script):
    if len(script) == 0:
        print "No script(s) to append"
        return 'null'
    text = '\n# ----- Begin PolyRun Appended Raw Epifast Script -----\n\n'
    print "Appending script:"
    
    for line in script:
        line = line.replace('"','')
        text += line+'\n'
        print line
        
    return text + '\n# ----- End Appended Epi Script -----\n'
    
    
###OLD EPIFAST FORMAT COMMANDS


# ONE TIME LID LOAD & FILTER FROM FILE

def filterIDs(directory):   
    print "Initiating one time ID load/ filter to memory"
    popfile = open(directory)
    #ids = []   
    ids = set()              
    line = 0
    while True:
            testline = popfile.readline()
            if len(testline) == 0:
                break
            if not testline.startswith("#"):
                #ids.append(testline)
                ids.add(testline)
                line += 1
                
    ids =  sorted(list(ids))      
    print str(line), "entries with IDS\n", int(ids[0]), "through", int(ids[line-1]), "loaded,\npreparing to chop\n"
    
    return {"directory":directory,"ids":ids}

# WRITES ANTIVIRAL AND DIAGNOSIS SCRIPTS TO DIRECTORY 
  
def writeAvScript(avScript, diagParams, outName, directory, subpopDirectory):
    
#    if len(explicitDirectory) > 1:
#        tempDirectory = explicitDirectory + '/' + directory + outName
#    else:
    tempDirectory = subpopDirectory + '/' + outName
    tempDirectory = tempDirectory.replace('//','/')

    
    print "\nOutputting antiviral and diagnosis scripts %s and %s to directory %s" % (outName+'Antiviral',outName+'Diagnosis', directory)
    diagFile = open(directory + outName + "Diagnosis", 'w')
    avFile = open(directory + outName + "Antiviral", 'w')
    
    diagFile.write("# ----- RollVac.py Autogenerated Diagnosis File -----\n")
    diagFile.write("\nModelVersion = " + str(diagParams[0]))
    diagFile.write("\nProbSymptomaticToHospital = " + diagParams[3])
    diagFile.write("\nProbDiagnoseSymptomatic = " + diagParams[4])
    diagFile.write("\nDiagnosedDuration = " + diagParams[5])
    diagFile.write("\n\n# ----- End of Generated Diagnosis File -----")
    
    diagFile.close()
    
    avFile.write("# ----- RollVac.py Autogenerated Antiviral File -----\n")
    avFile.write("\n# Global parameters")
    avFile.write("\nAntiviralConfigVersion = " + diagParams[1])
    avFile.write("\nTotalAntiviralSupply = " + diagParams[2])
    
    pos = 0
    length = len(avScript)
    
    while pos < length:
        avFile.write("\n\n# -----------------------\n")
        avFile.write("\nInterventionId = " + str(pos+5000))
        if len(avScript[pos][1]) != 0:
            avFile.write("\nConditionDate = " + avScript[pos][1])
        if len(avScript[pos][2]) != 0:
            if percentFix(avScript[pos][2]) >= 1:
                avFile.write("\nConditionThresholdValue = " + avScript[pos][2])
            else:
                avFile.write("\nConditionThresholdFraction = " + str(percentFix(avScript[pos][2])))
        if len(avScript[pos][0]) != 0:
            avFile.write("\nConditionThresholdSubpopulation = " +tempDirectory + avScript[pos][0])
        if isYes(avScript[pos][3], "Condition Diagnosis"):
            avFile.write("\nConditionDiagnosis = Required")
        if len(avScript[pos][4]) != 0:
            avFile.write("\nConditionMembership = " + tempDirectory + avScript[pos][4])
        if isYes(avScript[pos][5], "Condition Mutually Exclusive"):
            avFile.write("\nConditionMutex = Required")
        
        avFile.write("\n\nCompliance = " + avScript[pos][6])
        avFile.write("\nDelay = " + avScript[pos][7])
        avFile.write("\nDuration = " + avScript[pos][8])
        avFile.write("\nUnitNumberEachDay = " + avScript[pos][9])
        avFile.write("\nEfficacyIn = " + avScript[pos][10])
        avFile.write("\nEfficacyOut = " + avScript[pos][11])
        
        pos +=1
    avFile.write("\n\n# ----- End of Generated Antiviral File ----")
    avFile.close()
    
    print "Antiviral treatment scripting complete"
    return length

    

# USER INTERACTIVE ENUMERATION MODE

def getEnum():
    while True:
        print """\nEnter enumeration day and number list, format: 0 1; 1 5; 2 10; 3 14
per a given intervention, all enumeration must be taken care of in one call
further enumeration may lead to overlap with undesirable results for certain interventions"""
        enumerator =str(raw_input(":"))
        if len(enumerator) == 0:
            print "Nothing entered, defaulting to '0 1; 1 2; 3 5; 4 8'\n"
            enumerator = "0 1; 1 2; 3 5; 4 8"
        enumerator = enumerator.replace(";"," ; ")
        if checkEnum(enumerator):
            break
    return parseEnum(enumerator)
         
         
# RETURNS TRUE IF GIVEN PROPERLY FORMATTED ENUMERATION
     
def checkEnum(enumerator):
    cmds = enumerator.split()
    pos = 0
    lim = len(cmds) 
    if lim%3 != 2:
        print "Error: enumerator missing/ extra terms"
        return False
    while pos < lim:
        if pos%3 ==1:
            if not chopper.isInt(cmds[pos]):
                if '%' in cmds[pos]:
                    cmds[pos] = cmds[pos].replace('%','')
                    try:
                        temp = float(cmds[pos])/ 100
                        if temp > 1 or temp <= 0:
                            print "Error: non integer enumerator outside of 0-100% range"
                            return False
                    except:
                        print "Error: improperly formatted percentage enumerator"
                        return False
                else:
                    try:
                        temp = float(cmds[pos])
                        if temp > 1 or temp <= 0:
                            print "Error: non integer enumerator outside of 0-100% range"
                            return False
                    except:
                        print "Error: improper string value, cannot convert"
                        return False
            else:
                if cmds[pos]<0:
                    print "Error: enumerator must be a positive integer or percentage"
                    return False
        
        if pos%3 == 0:
            if not chopper.isInt(cmds[pos]) or cmds[pos] < 0:
                print "Error: enumeration entry at pos", len, "is not a positive integer"
                return False
        if pos%3 == 2:
            if cmds[pos] != ";":
                print "Error: semicolon seperator not found"
                return False
        pos += 1
    return True
    

# PARSES STRING ENUMERATION COMMANDS TO INTEGER ENUMERATION LIST   
    
def parseEnum(enumerator):
    enums = []
    cmds = enumerator.split()
    pos = 0
    lim = len(cmds) 
    while pos < lim:
        if pos%3 == 0:
            enums.append(int(cmds[pos]))
        if pos%3 == 1:
            enums.append(percentFix(cmds[pos]))
        pos += 1
    print "Valid intervention enumeration recieved:", enums
    return enums
 
       
# SORTS ENUMERATIONS BY DAY AND COMBINES SAME DAY ENUMERATIONS 
 
def cleanEnum(enumerator):
    workEnum = enumerator[:]
    oldEnum = workEnum[:]
    limit = len(workEnum)
    if len(workEnum) == 2:
        return workEnum
    used = False
    pos1 = 0
    while pos1 < limit-2:
        pos2 = pos1 +2
        while pos2 < limit:
            if workEnum[pos1] == workEnum[pos2]:
                workEnum[pos1+1] += workEnum[pos2+1]
                del workEnum[pos2:pos2+2]
                limit -= 2
                pos2 -= 2
                used = True
            if workEnum[pos1] > workEnum[pos2]:
                workEnum[pos1],workEnum[pos1+1], workEnum[pos2], workEnum[pos2+1] = workEnum[pos2], workEnum[pos2+1], workEnum[pos1], workEnum[pos1+1]
                used = True
            pos2 += 2
        pos1 += 2
        
    if used:
        print "Enumeration list cleaned up from original:", oldEnum
        print "to new:", workEnum, '\n'
    return workEnum

    
# FIXES USER INPUT PERCENTAGE DENOTED VALUES BY POPULATION SIZE TO INTERAL INTEGER NOTATION   
         
def percentFix(value):
    if '%' in value :
                value = value.replace('%','')
                return float(value)/100
    else:
        return float(value)

        
# REPLACES PERCENTAGE SPECIFIC ENUMERATIONS WITH ACTUAL INTEGER VALUES   
                                     
def percentEnum(enumerator,size):
    pos1 = 1
    print
    workEnum =  enumerator[:]
    limit =  len(workEnum)    
    while pos1 < limit+1:
        temp = float(workEnum[pos1])
        if temp < 1:
            workEnum[pos1] = int(temp*size+0.5)
            if workEnum[pos1] == 0:
                print "Percentage", temp*100, "% of population size", size, "resulted in", workEnum[pos1], "individuals, entry ignored for enumeration" 
                del workEnum[pos1-1:pos1+1]
                limit -= 2
                pos1 -= 2
            else:
                print "Percentage", temp*100, "% of population size", size, "converted to", workEnum[pos1], "individuals for enumeration" 
        else:
            workEnum[pos1] = int(workEnum[pos1])
        pos1 += 2
    return workEnum


# USER INPUT CHECKER, RETURNS TRUE FOR Y/YES, FALSE FOR N/NO OR ERROR WITH MESSAGE

def isYes(response, use):
    response = response.lower()   
    if response == 'y' or response == 'yes':
        result = True
    elif response == 'n' or response == 'no':
        result = False
    else:
        result = False
        if use != 'null':
            print "Error, please enter 'y' or 'n' for %s, defaulting to 'n'" %(use)  
    return result  
                        


# MAIN

def main(arg1, arg2, arg3, arg4, polyScript, filteredIDs):
        

    print arg1, arg2, arg3, arg4
    
    if __name__ != '__main__':
        sys.argv = ['RollVac.py',arg1,arg2,arg3,arg4]
    
    if arg1 == "poly":
        del sys.argv[3:5]

 
    trigger = 1
    subnum = 0
    path = ""
    population = ""
    useExplicit = False
    explicitDirectory = ""
    subpopDirectory = ""
    useBase = False
    useRaw =  False
    baseFile = "" 
    pos = 0
    iCode = 0
    
    vacTotal =  0
    avTotal = 0
    socialTotal = 0
    workTotal = 0
    schoolTotal = 0
    avTreatments = 0
    toFilterIDs = len(filteredIDs) > 0
    useNew = False
    subpopsNew = []
    actionsNew = []
    totalsNew =  {'vaccination':1000000000,'antiviral':1000000000}
    interventionsNew = []
    

# UNIX PASSED ARGUMENTS DECISION TREE  
    
    if len(sys.argv) <= 1:
        print "Missing arguments, defaulting to user mode with file prefix 'Default'\n"
        arg =  "user"
        outName = "Default"
    elif sys.argv[1] == "help":
        print """\nArguments: chopper.py {filepath/user} {intervention outfile}
        (Filepath): loads vaccination spread commands from an external script at (filepath)
        user: manual mode, enter each vaccination manually, enter (done) to quit\n"""
        quit()
    elif len(sys.argv) == 2:
        print "Missing 2nd argument, defaulting to file prefix 'Default'"
        arg = sys.argv[1]
        outName = "Default"
    elif len(sys.argv) > 3:


# LOADS PUBLIC/ PRIVATE DATA FROM GDOC IF PASSED
   
        if sys.argv[1] == "gdoc" or sys.argv[1] == "poly":
            arg = "gDoc"
            if len(sys.argv) == 4:
                sys.argv.insert(3,'null') 
            else:
                print "Ignoring", len(sys.argv) - 3, "excess arguments\n"
    elif len(sys.argv) == 3:
        if sys.argv[1] == "gdoc" or sys.argv[1] == "poly":
            arg = "gDoc" 
            sys.argv.insert(2,'null')
            sys.argv.insert(2,'null')
        else:
            outName = sys.argv[2]
            arg = sys.argv[1]


# LOADS AND WRITES AV/ DIAG SCRIPT FROM GOOGLE DOC, NOT IMPLEMENTED FOR USER/ LOCAL SCRIPT MODE
                                               
    print sys.argv
    if arg == "gDoc":
        
        if sys.argv[1] == "poly":
            isPoly = True
            sys.argv[3] = 'null'
            path = arg2
            if os.path.exists(path):
                shutil.rmtree(path)
            os.makedirs(path)
            os.makedirs(path + "/output")
        else:
            isPoly = False
        loadType = "intervention script"
        print sys.argv
        script = gDocsImport.getScript(sys.argv[2], sys.argv[3], sys.argv[4], startWord, stopWord, loadType, isPoly, polyScript)
        params = gDocsImport.getLine(sys.argv[2], sys.argv[3], sys.argv[4],paramsStart, isPoly, polyScript)
        
        emptyblock = script == 'null'
        
        explicitDirectory= params[2]
        if len(explicitDirectory) > 0:
            useExplicit  = True
        
        if isPoly:
            outName = ""
            baseFile = params[4]
            subpopDirectory = params[6]
            if len(baseFile) > 0:
                if os.path.exists(baseFile):
                    print "Appending interventions to base file", baseFile
                    useBase = True
                else:
                    print "Error, base file", baseFile, "not found"
                    quit()
                     
            
        else:
            outName = params[0]

        if len(outName) == 0:
            print "No name prefix stored, using default intervention, antiviral, and diagnosis"
            outName = ""
            
        print "Will write to intervention file '%sIntervention'\n" % outName

        diag = params[1]
        diagnosis = isYes(diag, "diagnosis")
        useNew = isYes(params[7], "new style")
        
        try:
            appendScript =  gDocsImport.getScript(sys.argv[2], sys.argv[3], sys.argv[4], avStop, 0, loadType, isPoly, polyScript)
            appendScript = appendRaw(appendScript)
            useRaw = appendScript != 'null'
            if useRaw:
                print "\nRaw script footer loaded succesfully,", appendScript.count('\n') - 3, "lines to append"
        except:
            print "Error, raw script footer not loaded"
        
        if not diagnosis:
            sys.argv[3] = "null"
        else:
            loadType = "default"
            avScript = gDocsImport.getScript(sys.argv[2], sys.argv[3], sys.argv[4], avStart, avStop, loadType, isPoly, polyScript)
            diagParams = gDocsImport.getLine(sys.argv[2], sys.argv[3], sys.argv[4], stopWord, isPoly, polyScript)
            sys.argv[3] = "null"               
            
            if not useNew:
                if avScript == 'null':
                    print "No AV-Script found"
                    avTreatments = 0
                else:
                    avTreatments = writeAvScript(avScript, diagParams, outName, path, subpopDirectory)
                
                
# PREP NEW FORMAT DICTS
 
            else:
                if avScript == 'null':
                    print "No AV-Script found"
                    avTreatments = 0
                else:
                    temp = prepNewAV(avScript, diagParams, outName, path, subpopDirectory, totalsNew)
                    subpopsNew += temp['subpops']
                    actionsNew += temp['actions']
                    interventionsNew += temp['interventions']
                    print subpopsNew
                    print actionsNew
                    print interventionsNew
                    #quit()
                    avTreatments = len(actionsNew)
        
    if arg != "user" and arg != "gDoc" and arg != "gdoc" and (not os.path.isfile(arg)):
        print arg
        print "Error, cannot open file or directory\n"
        quit()     
        
    done = False
    
    
# LOCAL SCRIPT FILE LOADING
      
    if arg != "user" and arg != "gDoc":
        scriptfile = open(arg)    
        script = []    
        line = 0
        gotPath = False
        while True:
                testline = scriptfile.readline()
                if len(testline) == 0:
                    break
                if not testline.startswith("#"):
                    if testline.startswith("Directory"):
                        gotPath =  True
                        temp = testline.split()
                        if len(temp) <2:
                            path = ""
                        else:
                            path = testline.split()[1]
                            if (path == "local" or path == "Local"):
                                path = ""
                    else:
                        script.append(testline)
                        line += 1
        if not gotPath:
            path = ""
        
              
# USER FILE LOADING                  
            
    if arg == "user":
        print """\nEnter desired intervention & subpopulation storage directory
Subpops will be created in local subpops folder, though intervention file will point to said directory
Enter 'local' to use current working directory or 'explicit' for a direct link"""
        path=str(raw_input(":"))
        if path == "explicit":
            path = os.getcwd()
        if (path == "local") or (path == "home") or (len(path) == 0):
            path = ""
            
        print "\nEnter desired intervention start number, default 1, useful for appending interventions to pre-existing files"
        number=raw_input(":")
        try:
            trigger = int(number)
            if trigger <= 0:
                print "Entry must be greater than 0, defaulting to 1\n"
                trigger = 1
        except:
            print "No entry/ invalid entry, defaulting to 1\n"
            trigger = 1


# FLUSH INTERVENTION FILE & COPY POLYRUN BASEFILE IF NEEDED
    
    writePath = path + outName + 'Intervention'
    if useNew:
        writePath += 'New'
    if useBase:
        shutil.copy2(baseFile, writePath)
        outFile = open(writePath)
        temp = outFile.read()
        outFile.close()
        outFile = open(writePath, 'w')
        outFile.write("# ----- PolyRun.Py Appended Intervention File -----\n\n")
        outFile.write(temp)
        outFile.write("\n\n# ----- End of Appended Intervention File -----\n\n")
    else:
        outFile = open(writePath, 'w')
    if useNew:
        outFile.write("# ----- RollVac.Py Autogenerated Intervention File New Version-----\n\n")
    else:
        outFile.write("# ----- RollVac.Py Autogenerated Intervention File Old Version-----\n\n")
    outFile.close()

        
# GENERATING OUTPUT FILE LOOP
       
    while not done and emptyblock == False:
    
        subnum += 1
        enum = False
    

# USER CONTROLLED CHOPPING  
            
        if arg == "user":
            
            while True:
                print "\nEnter source population filename/ directory"
                population=str(raw_input(":"))
                if len(population) == 0:
                    print "Nothing entered, defaulting to 'SUBPOP'\n"
                    population = "SUBPOP"
                if population == "done":
                    print "Data entry complete, quitting now!\n"
                    done = True
                    break
                if len(population) == 0:
                    population = "EFO6"
                try:
                    with open(population): pass
                    break
                except:
                    print "Error: population file", population, "not found\n"
            
            if done:
                break
            
            while True:   
                print "\nEnter desired intervention trigger day/ 'enum' for enumerated intervention"
                number=raw_input(":")
                if str(number) == 'enum' or str(number) == 'e':
                    enum = True
                    enumList = getEnum()
                    break
                else:
                    try:
                        day = int(number)
                        if day <= 0:
                            print "Error: invalid entry, please enter a positive integer or 'enum'\n"
                        else:
                            break
                    except:
                        print "Error: invalid entry, please enter a positive integer\n"
    
            
            while not enum:
                print "\nEnter desired intervention time to completion"
                number=raw_input(":")
                try:
                    length = int(number)
                    if length <= 0:
                        print "Error: invalid entry, please enter a positive integer\n"
                    else:
                        break
                except:
                    print "Error: invalid entry, please enter a positive integer\n"
        
            while True:
                print """\nEnter intervention type with numerical parameters (ex: Vaccination 10 0.5 .7)
Text will be saved to intervention file exactly as entered with generated
action number and subpopulation directory appended"""
                interv=str(raw_input(":"))
                temp =  interv.split()
                if len(temp) == 0:
                    print "Error: please enter intervention command\n"
                else:   
                    method = temp[0]
                    target = 0
                    if method == "Vaccination":
                        target = 4
                        meth = "v"
                        iCode = 0
                    elif method == "Antiviral":
                        target = 5
                        meth = "av"
                        iCode = 1000
                    elif method == "SocialDistancing":
                        target = 3
                        meth = "sd"
                        iCode= 2000
                    elif method == "WorkClosure":
                        target = 3
                        meth = "cw"
                        iCode = 3000
                    elif method == "SchoolClosure":
                        target = 3
                        meth =  "cs"
                        iCode = 4000
                    elif method == "Sequestion":
                        target = 4
                        meth =  "sq"
                        iCode = 6000
                    if (len(temp) != target):
                        print "Error:",  len(temp), "parameters found,", target, "expected for intervention type", method, "\n"
                    elif target == 0:
                        print "Error:", method, "method not recognized\n"
                    else:
                        if not temp[1].isdigit():
                            print "Error: second value must be an integer"
                        else:
                            pos2 = 1
                            allGood = True
                            while pos2 < target:
                                if not chopper.isInt(temp[pos2]):
                                    allGood = False
                                pos2 += 1
                            if not allGood:
                                print temp
                                print "Error: non-numerical parameters found\n"
                            else:
                                break  
  
                                                                              
#  LOCAL SCRIPT/ GDOC CONTROLLED CHOPPING                                                                                                                                                                                           
                                                                                                                                                                                                
        else:
            if pos == len(script):
                done = True
                break
                
            cmd = script[pos]
            items = cmd.split()
            population =  (subpopDirectory + '/' + items[0]).replace('//','/')
            try:
                with open(population): pass
            except:
                print "Error: population file", population, "not found\n"
                quit()
            
            if str(items[1]) == 'enum':
                enum = True
                cmd = cmd.replace("enum","null null")
                items = cmd.split()
                pos += 1
                enumList = script[pos].replace(";"," ; ")
                if checkEnum(enumList):
                    enumList = parseEnum(enumList)
                else:
                    print "Error: misformatted enumeration list", enumList
                    quit()
            
            if not enum:
                try:
                    day = int(items[1])
                    if day <= 0:
                        print "Error, day must be an integer greater than zero\n"
                        quit()
                except:
                    print "Error, day must be an integer greater than zero\n"
                    quit()
                try:
                    length = int(items[2])
                    if length <= 0:
                        print "Error, length must be an integer greater than zero\n"
                        quit()
                except:
                    print "Error, length must be an integer greater than zero\n"
                    quit()
            
            temp = cmd.split()
            print "Generating interventions with parameters:",cmd
            method = temp[3]
            if method == "Vaccination":
                target = 7
                meth = "v"
                iCode = 0
            elif method == "Antiviral":
                target = 8
                meth = "av"
                iCode = 1000
            elif method == "SocialDistancing":
                target = 6
                meth = "sd"
                iCode = 2000
            elif method == "WorkClosure":
                target = 6
                meth = "cw"
                iCode = 3000
            elif method == "SchoolClosure":
                target = 6
                meth = "cs"
                iCode = 4000
            elif method == "Sequestion":
                target = 7
                meth = "sq"
                iCode = 6000
            else:
                print "Error:", method, "method not recognized\n"
                quit()
            if (len(temp) != target):
                print "Error:",  len(temp), "parameters found,", target, "expected for intervention type", method, "\n"
                quit()
            
            
            interv = " ".join(temp[3:target])
            intervNew = temp[3:target]
            pos += 1
    
        suffix = str(subnum) + meth


# ALL MODE CHOPPING EXECUTION

        print population
        if not useNew:
            pos2 = 0
            limit = len(filteredIDs)
            found = False
            while pos2 < limit:
                if population in filteredIDs[pos2]['directory']:
                    found = True
                    runIDs = filteredIDs[pos2]['ids']
                    break
                pos2 += 1
            
            if not found:
                filteredIDs.append(filterIDs(population))
                runIDs = filteredIDs[-1]['ids']
            
            if enum:
                populationSize = chopper.popSize(population)
                enumList = cleanEnum(percentEnum(enumList,populationSize))
                holder = chopper.main(population,'e'," ".join(map(str, enumList)),suffix, path,runIDs)
                returnSize = holder['count']
                enumList = holder['enum']
                length = chopper.getEnumSize(enumList)
            else:
                holder = chopper.main(population,'b',str(length),suffix, path, runIDs)
                returnSize = holder['count']
        else:
            addSubpop(subpopsNew, population.split('/')[-1], population, 9000+ len(subpopsNew))

            if enum:
                populationSize = chopper.popSize(population)
                temp = countEnum(enumList,populationSize)
                enumList = chopper.trimEnum(cleanEnum(temp['enum']))
                length = chopper.getEnumSize(enumList)
                returnSize = min(temp['total'],populationSize)
            else:
                populationSize = returnSize = chopper.popSize(population)


# NON TREATMENT BASED INTERVENTION TRACKING            
    
        if meth == "v":
            vacTotal += returnSize
        elif meth == "av":
            avTotal += returnSize
        elif meth == "sd":
            socialTotal += returnSize
        elif meth == "cw":
            workTotal += returnSize
        elif meth == "cs":
            schoolTotal += returnSize
        
                
# WRITING INTERVENTION FILE (AV TREATMENT & DIAG HANDLED SEPERATELY)

        writePath = path + outName + 'Intervention'
               
        pos2 = 0
        popName = population.split('/')[-1]
        
        if not useNew:
            outFile = open(writePath, 'a+b')
            if enum:
                while pos2 < len(enumList):
                    subPopName = popName + 'd' + str(pos2/2) + 'i' + suffix
                    if ".txt" in subPopName:
                        subPopName = subPopName.replace('.txt','') + '.txt'
                    triggerOut = "* Trigger " + str(trigger+iCode) + " Date " + str(enumList[pos2]) + "\n" 
                    if useExplicit:
                        tempPath = path + "/subpops/" + subPopName
                    else:
                        tempPath = "subpops/" + subPopName
                    intervOut = "* Action " + str(trigger+iCode) + " " + interv + " " + tempPath + "\n"
                    intervOut =  intervOut.replace('//','/')
                    print triggerOut, intervOut.replace('\n','')
                    outFile.write(triggerOut)
                    outFile.write(intervOut)
                    trigger += 1
                    pos2 += 2
                
            else:
                while pos2 < length:
                    subPopName = popName + 'd' + str(pos2) + 'i' + suffix
                    if ".txt" in subPopName:
                        subPopName = subPopName.replace('.txt','') + '.txt'
                    triggerOut = "* Trigger " + str(trigger+iCode) + " Date " + str(day+pos2) + "\n" 
                    if useExplicit:
                        tempPath = path + "/subpops/" + subPopName
                    else:
                        tempPath = "subpops/" + subPopName
                    intervOut = "* Action " + str(trigger+iCode) + " " + interv + " " + tempPath + "\n"
                    intervOut =  intervOut.replace('//','/')
                    print triggerOut, intervOut.replace('\n','')
                    outFile.write(triggerOut)
                    outFile.write(intervOut)
                    trigger += 1
                    pos2 += 1
            
            outFile.close()
            print
        else:
            writePath += 'New'
            tempAction = prepNewAction()
            #tempInterv = [prepNewIntervention()]*len(enumList/2)
            tempAction['actionID'] = actionID = str(trigger + iCode)
            tempAction['actionDescription'] = tempAction['actionType'] = method
            tempAction['actionDelay'] = '0'
            tempAction['actionDuration'] = intervNew[0]
            conditionTotal = -1
            if method == "Vaccination":
                tempAction['actionEfficacy'] = intervNew[2]
                conditionTotal = '9100'
            elif method == "Antiviral":
                tempAction['actionEfficacyIn'] = intervNew[2]
                tempAction['actionEfficacyOut'] = intervNew[3]
                conditionTotal = '9101'
            if enum:    
                tempInterv = [prepNewIntervention()]*len(enumList/2)
                while pos2 < len(enumList):
                    tempInterv[pos2/2]['interventionID'] = str(9300 + len(interventionsNew) + pos/2)
                    tempInterv[pos2/2]['interventionType'] = "Offline"
                    if conditionTotal != -1:
                        tempInterv[pos2/2]['conditionTotal'] = conditionTotal
                    tempInterv[pos2/2]['conditionDate'] = str(enumList[pos2]) + '~' + str(enumList[pos2])
                    tempInterv[pos2/2]['conditionMembership'] = getSubpopID(subpopsNew,popName)
                    tempInterv[pos2/2]['conditionCompliance'] = str(float(intervNew[1]) * enumList[pos2+1])
                    tempInterv[pos2/2]['action'] = actionID
                    pos2 += 2
            else:
                tempInterv = [prepNewIntervention()]*length
                while pos2 < length:
                    tempInterv[pos2]['interventionID'] = str(9300 + len(interventionsNew) + pos/2)
                    tempInterv[pos2]['interventionType'] = "Offline"
                    if conditionTotal != -1:
                        tempInterv[pos2]['conditionTotal'] = conditionTotal
                    tempInterv[pos2]['conditionDate'] = str(day+pos2) + '~' + str(day+pos2)
                    tempInterv[pos2]['conditionMembership'] = getSubpopID(subpopsNew,popName)
                    tempInterv[pos2]['conditionCompliance'] = str(float(intervNew[1]) / length)
                    tempInterv[pos2]['action'] = actionID
                    pos2 +=1
                    subPopName = popName + 'd' + str(pos2) + 'i' + suffix
                    if ".txt" in subPopName:
                        subPopName = subPopName.replace('.txt','') + '.txt'
                    triggerOut = "* Trigger " + str(trigger+iCode) + " Date " + str(day+pos2) + "\n" 
            actionsNew += tempAction
            intervNew += tempInterv


# AUTOGENERATE NEW FORMAT MUTEXES           
                                              
    if useNew:
        vMutex = avMutex = sdMutex = cwMutex = csMutex = sqMutex = []
        pos = 0
        while pos < len(actionsNew):
            print "DEBUG****", actionsNews
            if actionsNew[pos]['actionDescription'] == "Vaccination":
                vMutex.append(str(pos))
            elif actionsNew[pos]['actionDescription'] == "Antiviral":
                avMutex.append(str(pos))
            elif actionsNew[pos]['actionDescription'] == "SocialDistancing":
                sdMutex.append(str(pos))
            elif actionsNew[pos]['actionDescription'] == "CloseWork":
                cwMutex.append(str(pos))
            elif actionsNew[pos]['actionDescription'] == "CloseSchools":
                csMutex.append(str(pos))
            elif actionsNew[pos]['actionDescription'] == "Sequestion":
                sqMutex.append(str(pos))
            pos+=1
        pos = 0
        while pos < length(interventionsNew):
            temp = getActionType(actionsNew,interventionsNew[pos]['action'])
            if temp == "Vaccination":
                interventionsNew[pos]['conditionMutex'] = ';'.join(vMutex)
            elif temp == "Antiviral":
                interventionsNew[pos]['conditionMutex'] = ';'.join(avMutex)
            elif temp == "SocialDistancing":
                interventionsNew[pos]['conditionMutex'] = ';'.join(sdMutex)
            elif temp == "CloseWork":
                interventionsNew[pos]['conditionMutex'] = ';'.join(cwMutex)
            elif temp == "CloseSchools":
                interventionsNew[pos]['conditionMutex'] = ';'.join(csMutex)
            elif temp == "Sequestion":
                interventionsNew[pos]['conditionMutex'] = ';'.join(sqMutex)
            pos+=1

            
# APPENDING NON TREATMENT INTERVENTION TOTALS    
   
    outFile = open(path + outName+'Intervention', 'a+b')
    if useNew:
        outFile.write(getOutputNew(subpopsNew, totalsNew, actionsNew, interventionsNew))
    sumIntervs = vacTotal + avTotal + socialTotal + workTotal + schoolTotal + avTreatments
    if sumIntervs == 0:
        if useRaw:
            print "No scripted interventions found, using iterated manual script"
            outFile.write(appendScript)
        else:
            print "No scripted interventions or raw script found"
    else:
        if useRaw:
            print "Appending manually iterated script"
            outFile.write(appendScript)
    
        outFile.write("""\n#----- End of Generated Intervention File -----\n\n# RollVac.Py Pre Compliance Intervention Totals- calculated per output,
does not account for over-application to a given set of IDs. 
Please apply only one of each type per sub pop, using enumerated
    interventions for complex interventions.""")
        outFile.write("\n# Vaccination: " + str(vacTotal))
        outFile.write("\n# Antiviral Prophylaxis: " + str(avTotal))
        outFile.write("\n# Social Distancing: " + str(socialTotal))
        outFile.write("\n# Close Work: " + str(workTotal))
        outFile.write("\n# Close Schools: " + str(schoolTotal))
        outFile.write("\n# AV Treatment Programs: " + str(avTreatments))
        outFile.close()
        print """RollVac.Py Pre Compliance Intervention Totals- calculated per output,
does not account for over-application to a given set of IDs. 
Please apply only one of each type per sub pop, using enumerated 
interventions for complex interventions."""
        print "\nVaccination: " + str(vacTotal)
        print "Antiviral Prophylaxis: " + str(avTotal)
        print "Social Distancing: " + str(socialTotal)
        print "Close Work: " + str(workTotal)
        print "Close Schools:" + str(schoolTotal)
        print "AV Treatment Programs: " + str(avTreatments)
        print
        if toFilterIDs:
            return filteredIDs
    
if __name__ == '__main__':    
    main(0,0,0,0,[],[])
    print "Intervention scripting succesfully completed, exiting now.\n"
    quit
