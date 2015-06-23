import sys
import os
import shutil
import gDocsImport
import RollVac
#import subprocess
from time import sleep
    

def appendSuffix(directory, suffix):
    while directory[-1] == "/":
        directory = directory[:-1]
    directory = directory + suffix + '/'  
    while '//' in directory:
        directory = directory.replace('//','/')
    return directory
    

# ERASES DIRECTORIES FROM GIVEN LIST

def flushDirectories(directoryList):
    suffix = 2
    usedNum = False
    for pos in range(len(directoryList)):
        flushDirectory= directoryList[pos].replace(' ','')
        if len(flushDirectory) == 0:
            flushDirectory = "polyrun"
        print "Flushing directory %s: %s" % (pos, flushDirectory)
        if os.path.exists(flushDirectory):
            print "*** Warning, preparing to flush path:", flushDirectory, " - continue? (yes/no/num/quit) ***"
            print "-num will suffix the output directories with a number"
            print "-no will output over the prior directory without cleanup"
            while True:
                response = str(raw_input(":")).lower()
                if response == "n" or response == "no" or response == "y" or response == "yes" or response == "num" or response == "quit":
                    answer = RollVac.isYes(response, "null")
                    break
                else:
                    print "Invalid Response, please enter yes, no, or num"
            if answer == True:
                shutil.rmtree(flushDirectory)
                print " cleared succesfully"             
            elif response == 'quit':
                print "Quitting now....\n\n"
                quit()
            elif response == 'num':
                copyNum = 2
                if os.path.exists(flushDirectory):
                    while os.path.exists(flushDirectory + str(copyNum)):
                        copyNum += 1                 
                    suffix = max(copyNum, suffix)   
                    usedNum = True  
                    
        else:
            print "not found, skipping"
        
    suffix = str(suffix)
    if usedNum:
        print "Duplicate directories found, will append suffix '%s' to output directories" % (suffix)
        return str(suffix)
    else:
        return ""
        
        
# PULLS POLYRUN OPERATOR FROM CSV ROW VIA LIST OF STRINGS FORMAT. RETURNS NULL IF NOT FOUND  

def getPoly(refLine):
    line = refLine[:]
    found = False
    for item in line:
        if '$' in item:
            found = True
            break
    if not found:
        return ['null', 'null']
    else:
        item= item.replace('\n','')
        while "  " in item:
            item= item.replace('  ',' ')
        cmd = item.split(' ')
        del cmd[0]
        return cmd


# RETURNS LIST WITHOUT POLYRUN OPERATORS       
        
def filterPoly(refLine):
    pos = 0
    line = refLine[:]
    length= len(line)
    while pos < length:
        if '$' in line[pos]:
            del line[pos]
            length -= 1
        pos += 1
    lineout = ",".join(line) + '\n'
    return lineout
    
    
# COPIES SELECTED CONFIG/ PERIPHERAL FILES TO DIRECTORY

def fileCopy(fileString, directory):
    if not os.path.exists(directory):
        print "Error: directory not found"
        return False
    fileList = fileString.split(';')
    print "copying files:", fileList

    for copyFile in fileList:
        copyFile = copyFile.replace(' ','')
        print "File %s: %s" % (pos, copyFile)
        if os.path.exists(copyFile):
            shutil.copy2(copyFile, directory + copyFile)
            print "copied succesfully"
        else:
            print "Error: copyfile not found"
            quit()

    return True    
    

# REPLACE & RETURN NEW FILES

def findNReplace(fileString, replaceScript, directory, iteration, home, explicit):  
    print "Executing find & replace"
    
    fileList = fileString.split(';')
    print "Loading files:", fileList
    for pos in range(len(fileList)):
        copyFile = fileList[pos].replace(' ','')
        print "File %s: %s" % (pos, copyFile)
        if os.path.exists(copyFile):
            replaceFile = open(copyFile)
            contents = replaceFile.readlines()
            replaceFile.close()
            print "loaded succesfully, replacing target content"
            
            for pos2 in range(len(contents)):
                for pos3 in range(len(replaceScript)):
                    if replaceScript[pos3]['file'] == copyFile:
                        if replaceScript[pos3]['find'] in contents[pos2]:
                            line = replaceScript[pos3]['replace']                    
                            line = line.replace("$ITER", str(iteration))
                            line = line.replace("$DIR", directory)
                            line = line.replace("$HOME", home)
                            line = line.replace("$EXP", explicit)
                            if "https://" not in line:
                                line =  line.replace("//","/")
                            contents[pos2] = line + '\n'
                            print line
                
            replaceFile = open((directory + '/' + copyFile).replace('//','/'), 'w')
            contents = ''.join(contents)
            replaceFile.write(contents)
            replaceFile.close()

        else:
            print "Error: copyfile not found"
            quit()
        

    print "Find and replace completed succesfully"
        
        
                
    
    
# LOADS REPLACE SCRIPT 

def loadReplaceScript(replaceFile, extraCommands):
    print "Loading find/replace script"
    script = []
    if replaceFile != "null":
        replaceFile = open(replaceFile)
        script += replaceFile.readlines()
    if extraCommands != "null":
        script += extraCommands
    
    replaceFile.close()
    fileName = ""
    replaceScript = []
    
    pos = 0
    length = len(script)
    while pos < length:
        line = script[pos]
        if not line.startswith('#') and len(line.replace(" ",""))>1:     
            if line.startswith('File = '):
                line = line.replace('File = ','').lstrip(' ')
                line = line.replace('  ','')
                fileName =  line.replace('\n','')
                if len(fileName) == 0:
                    print "Error, filename missing"
                    quit()
            elif line.startswith("Find = "):
                if len(fileName) == 0:
                    print "Error, Find & Replace filename not found"
                    quit()
                line = line.replace('Find = ','').lstrip(' ')
                line = line.replace('  ','')
                find =  line.replace('\n','')
                if len(find) == 0:
                    print "Error, find string missing"
                    quit()
                if (pos + 1) == length:
                    print "Error, end of file reached, missing replace line"
                    quit()
                pos += 1
                line = script[pos]
                if line.startswith("Replace = "):
                    line = line.replace('Replace = ','').lstrip(' ')
                    line = line.replace('  ','')
                    replace = line.replace('\n','')
                    if len(find) == 0:
                        print "Error, replace string missing"
                        quit()
                    replaceScript.append({'file':fileName,'find':find,'replace':replace})
                    print "Command appended, file %s, find %s, replace %s" % (fileName, find, replace)
        pos += 1
    print "Script loaded succesfully\n"
    return replaceScript
                
                
        
            
    
        
# MAIN                
                                
def main():
    

# USED TO DEFINE LOADING POSITIONS, MUST BE CONSERVED IN SOURCE AND GDOC
        
    paramsStart = "Study Name Prefix (optional),Diagnosis Based"
    startWord = "Subpopulation,Day/'enum',Length of Spread"
    
    vacsRolled = 0
    
    totalVars = 0
    varList = []
    varSets = []
    suffixes = []
    directorySuffix = ""
    filteredIDs = [{"directory":'null','ids':[]}]
    popSizes = dict()
#    positions = []

# PARSING COMMAND LINE ARGUMENTS FOR PUBLIC/ PRIVATE FILE ACCESS        
    
                    
    if len(sys.argv) > 2:
        if len(sys.argv) == 3:
            sys.argv.insert(2,'null') 
        else:
            print "Ignoring", len(sys.argv) - 2, "excess arguments\n"
    elif len(sys.argv) == 2:
            sys.argv.insert(1,'null')
            sys.argv.insert(1,'null')

    script = gDocsImport.getScript(sys.argv[1], sys.argv[2], sys.argv[3], 0, -1, "default", False, [])
    directoryLines = gDocsImport.getScript(sys.argv[1], sys.argv[2], sys.argv[3], paramsStart, startWord, "default", False,[])
    sys.argv = None
    
# ERASES DIRECTORY NAMES GIVEN BY GDOC
    
    directories = []
    for directory in directoryLines:
        dirToFlush =(directory[2] + '/' + directory[0]).replace('//','/')
        if not dirToFlush in directories: 
            directories.append(dirToFlush)
    
    directorySuffix = flushDirectories(directories)
    
    
# CREATES LISTS OF ALL EXPERIMENTAL VARIABLES ITERATED OVER
            
    length = len(script)
    
    print "Searching list for experimentally iterated variables"
    print 'DEBOOO',script    
    for item in script:
        temp = getPoly(item)
        if temp[0] != 'null':
            if temp[0] not in varSets:
                totalVars += 1
                varList.append(temp[0])
            varSets.append(temp[0]) 
            suffixes.append(temp[1])    
            
    varList.sort()
    length = len(varSets)
    varMatrix = [[] for x in xrange(totalVars)]
    suffixMatrix = [[] for x in xrange(totalVars)]
#    positionMatrix = [[] for x in xrange(totalVars)]
    
    
# CREATES MATRICES OF SUFFIXES, VARIABLE ID, AND LIST POSITION FOR ITERATION  
      
    for pos2 in range(totalVars):              
        for pos1 in range(length):
            if varSets[pos1] == varList[pos2] and (suffixes[pos1] not in suffixMatrix[pos2]):
                varMatrix[pos2].append(varSets[pos1])
                suffixMatrix[pos2].append(suffixes[pos1])
#                positionMatrix[pos2].append(positions[pos1])
    

# SETS UP RUN BOUNDS
        
    runTracker = [0] * totalVars
    done = False
    totalRuns = 1
    ends = []
    for pos in range(totalVars):
        totalRuns *= len(varMatrix[pos])
        ends.append(len(varMatrix[pos])-1)
        if pos >= 1:
            ends[pos] += 1
        
    
# ITERATED RUN GENERATION, IF SCRIPT LINE CONTAINS CURRENT ITERATION RUN MARKERS OR NONE, SENT TO RollVac TO PARSE    
    
    while not done:      
            
        toRun  =  []
        for pos in range(totalVars):
            toRun.append(suffixMatrix[pos][runTracker[pos]])      
        
        length = len(script)
        rollScript = []
        print "Loading Script for line:", runTracker
        for item in script:
            if getPoly(item)[0] == 'null' or getPoly(item)[1] in toRun:
                rollScript.append(filterPoly(item))
                #if len(item.replace('"','').replace(',','').replace('\n','')) != 0:
                    
                
# SUPPORT ADDED FOR MULTIPLE DIRECTORIES/ RUN         
                
        params = gDocsImport.getLine('null', 'null','null', paramsStart, True, rollScript)
        folder = params[2] + '/' + params[0]
        directory = appendSuffix(folder,directorySuffix) 

# OUT DIRECTORY GENERATED VIA SUFFIX MATRIX
                                
        for pos in range(totalVars):
            directory += suffixMatrix[pos][runTracker[pos]] + '/'
            
        params = gDocsImport.loadNClean(False, rollScript, paramsStart, startWord, "single line")
        print params
        
        homeDir = appendSuffix(params[2] + '/' + params[0], directorySuffix)
        explicit =  appendSuffix(params[2], directorySuffix)
        
        needsReplace = len(params[5]) > 0
        noAVDiag = not RollVac.isYes(params[1],'null')
        fileString =  params[3]
        filesToCopy = len(fileString) > 0
            
        filteredIDs = RollVac.main('poly', directory, 'null', 'null', rollScript, filteredIDs, popSizes)
        sleep(0.05)
        
        qsubs = open(homeDir + 'qsublist', 'a+b')
        qsubs.write(("qsub " + directory + 'qsub\n').replace('//','/'))   
        qsubs.close()
        
        if noAVDiag: 
            extraCommands = ["Find = DiagnosisFile =",
                "Replace = ",
                "Find =  AntiviralFile = ",
                "Replace = "]
        else:
            extraCommands = 'null'
                
        if needsReplace:
            replaceFile = params[5]
        else:
            replaceFile = 'null'
               
        if needsReplace or noAVDiag:
            replaceScript = loadReplaceScript(replaceFile, extraCommands)    
            findNReplace(fileString, replaceScript, directory, vacsRolled, homeDir, explicit)
        
        if filesToCopy and not needsReplace:
            print fileString, directory       
            fileCopy(fileString, directory)
            
        vacsRolled += 1


# POLYRUN MULTIDIMENSIONAL LOOP ITERATOR

        if totalVars == 0:
            print "No PolyRun iteration operators found, running in singular mode."
            done = True
            break
            
        pos = 0 
        justRolled = False
 
        while runTracker[pos] == ends[pos] and pos < totalVars - 1:
            justRolled = True
            runTracker[pos] = 0
            runTracker[pos+1] += 1
            pos += 1
            
        if pos == totalVars - 1 and runTracker[pos] == ends[pos]:
            print "Interventions Iterated =", vacsRolled
            done = True
            break
         
        if not justRolled:
            runTracker[0] += 1   
            
    print "Intervention iteration succesfully complete!"
                 
main() 
