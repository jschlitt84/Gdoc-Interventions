import sys
import os
import shutil
import gDocsImport
import RollVac
import subprocess
    

def appendSuffix(directory, suffix):
    while directory[-1] == "/":
        directory = directory[:-1]
    directory = directory + suffix + '/'  
    while '//' in directory:
        directory = directory.replace('//','/')
    return directory
    

# ERASES DIRECTORIES FROM GIVEN LIST

def flushDirectories(directoryList):
    pos = 0
    suffix = 2
    limit = len(directoryList)
    usedNum = False
    while pos < limit:    
        flushDirectory= directoryList[pos].replace(' ','')
        if len(flushDirectory) == 0:
            flushDirectory = "polyrun"
        print "Flushing directory %s: %s" % (pos, flushDirectory)
        if os.path.exists(flushDirectory):
            print "*** Warning, preparing to flush path:", flushDirectory, " - continue? (yes/no/num) ***"
            print "-Choosing num will suffix the output directories with a number"
            while True:
                response = str(raw_input(":")).lower()
                if response == "n" or response == "no" or response == "y" or response == "yes" or response == "num":
                    answer = RollVac.isYes(response, "null")
                    break
                else:
                    print "Invalid Response, please enter yes, no, or num"
            if answer == True:
                shutil.rmtree(flushDirectory)
                print " cleared succesfully"             
            elif response == 'num':
                copyNum = 2
                if os.path.exists(flushDirectory):
                    while os.path.exists(flushDirectory + str(copyNum)):
                        copyNum += 1                 
                    suffix = max(copyNum, suffix)   
                    usedNum = True  
                    
        else:
            print "not found, skipping"
        pos += 1
        
    suffix = str(suffix)
    if usedNum:
        print "Duplicate directories found, will append suffix '%s' to output directories" % (suffix)
        return str(suffix)
    else:
        return ""
        
        
# PULLS POLYRUN OPERATOR FROM CSV ROW VIA LIST OF STRINGS FORMAT. RETURNS NULL IF NOT FOUND  

def getPoly(refLine):
    pos = 0
    line = refLine[:]
    length= len(line)
    found = False
    while pos < length:
        if '$' in line[pos]:
            found = True
            break
        pos += 1
    if not found:
        return ['null', 'null']
    else:
        line[pos]= line[pos].replace('\n','')
        while "  " in line[pos]:
            line[pos]= line[pos].replace('  ',' ')
        cmd = line[pos].split(' ')
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
    pos = 0
    limit = len(fileList)
    while pos < limit:
        copyFile = fileList[pos].replace(' ','')
        copyFile2 = copyFile
        print "File %s: %s" % (pos, copyFile)
        if os.path.exists(copyFile):
            shutil.copy2(copyFile, directory + copyFile2)
            print "copied succesfully"
        else:
            print "Error: copyfile not found"
            quit()
        pos += 1
    return True    
    

# REPLACE & RETURN NEW FILES

def findNReplace(fileString, replaceScript, directory, iteration, home, explicit):  
    print "Executing find & replace"
    
    fileList = fileString.split(';')
    print "Loading files:", fileList
    pos = 0
    limit = len(fileList)
    while pos < limit:
        copyFile = fileList[pos].replace(' ','')
        print "File %s: %s" % (pos, copyFile)
        if os.path.exists(copyFile):
            replaceFile = open(copyFile)
            contents = replaceFile.readlines()
            replaceFile.close()
            print "loaded succesfully, replacing target content"
            
            limit3 = len(replaceScript)
            limit2 = len(contents)
            pos2 = 0
            
            while pos2 < limit2:
                
                pos3 = 0
                while pos3 < limit3:
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
                            print contents[pos2]
                    pos3 +=1
                pos2 += 1
                
            replaceFile = open((directory + '/' + copyFile).replace('//','/'), 'w')
            contents = ''.join(contents)
            replaceFile.write(contents)
            replaceFile.close()
            pos += 1

        else:
            print "Error: copyfile not found"
            quit()
        

    print "Find and replace completed succesfully"
        
        
                
    
    
# LOADS REPLACE SCRIPT 

def loadReplaceScript(replaceFile):
    print "Loading find/replace script"
    replaceFile = open(replaceFile)
    script = replaceFile.readlines()
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
    
    pos = 0
    directories = []
    toSetPermissions = []
    while pos  < len(directoryLines):
        dirToFlush =(directoryLines[pos][2] + '/' + directoryLines[pos][0]).replace('//','/')
        if not dirToFlush in directories: 
            directories.append(dirToFlush)
            toSetPermissions.append(RollVac.isYes(directoryLines[pos][7],'set 775 permissions'))
        pos += 1
    
    directorySuffix = flushDirectories(directories)
    
    
# CREATES LISTS OF ALL EXPERIMENTAL VARIABLES ITERATED OVER
            
    pos = 0
    length = len(script)
    
    print "Searching list for experimentally iterated variables"
    
    while pos < length:
        temp = getPoly(script[pos])
        if temp[0] != 'null':
            if temp[0] not in varSets:
                totalVars += 1
                varList.append(temp[0])
            varSets.append(temp[0]) 
            suffixes.append(temp[1])
        pos += 1  
    pos1 = 0

    varList.sort()
    length = len(varSets)
    varMatrix = [[] for x in xrange(totalVars)]
    suffixMatrix = [[] for x in xrange(totalVars)]
#    positionMatrix = [[] for x in xrange(totalVars)]
    
    
# CREATES MATRICES OF SUFFIXES, VARIABLE ID, AND LIST POSITION FOR ITERATION  
    
    pos2 = 0                 
    while pos2 < totalVars:
        pos1 = 0
        while pos1 < length:
            if varSets[pos1] == varList[pos2] and (suffixes[pos1] not in suffixMatrix[pos2]):
                varMatrix[pos2].append(varSets[pos1])
                suffixMatrix[pos2].append(suffixes[pos1])
#                positionMatrix[pos2].append(positions[pos1])
            pos1 += 1
        pos2 += 1
    

# SETS UP RUN BOUNDS
        
    runTracker = [0] * totalVars
    done = False
    totalRuns = 1
    pos = 0
    ends = []
    while pos < totalVars:
        totalRuns *= len(varMatrix[pos])
        ends.append(len(varMatrix[pos])-1)
        if pos >= 1:
            ends[pos] += 1
        pos += 1  
        
    
# ITERATED RUN GENERATION, IF SCRIPT LINE CONTAINS CURRENT ITERATION RUN MARKERS OR NONE, SENT TO RollVac TO PARSE    
    
    while not done:      
        
        pos = 0      
        toRun  =  []
        while pos < totalVars:
            toRun.append(suffixMatrix[pos][runTracker[pos]])
            pos += 1        
        
        pos = 0
        length = len(script)
        rollScript = []
        print "Loading Script for line:", runTracker
        while pos < length:
            if getPoly(script[pos])[0] == 'null' or getPoly(script[pos])[1] in toRun:
                rollScript.append(filterPoly(script[pos]))
            pos += 1  
                
# SUPPORT ADDED FOR MULTIPLE DIRECTORIES/ RUN         
                
        folder = "polyrun"
        params = gDocsImport.getLine('null', 'null','null', paramsStart, True, rollScript)
        if len(params[0]) > 0:
            folder = params[2] + '/' + params[0]
        directory = appendSuffix(folder,directorySuffix)      

# OUT DIRECTORY GENERATED VIA SUFFIX MATRIX
                                
        pos = 0
        while pos < totalVars:
            directory += suffixMatrix[pos][runTracker[pos]] + '/'
            pos += 1
            
        params = gDocsImport.loadNClean(False, rollScript, paramsStart, startWord, "single line")
        print params
        
        homeDir = appendSuffix(params[2] + '/' + params[0], directorySuffix)
        explicit =  appendSuffix(params[2], directorySuffix)
        
        needsReplace = len(params[5]) > 0
        fileString =  params[3]
        filesToCopy = len(fileString) > 0
 #       fileList = fileString.split(';')
 #       homeList = []
        
 #       needsToHome = False 
        
 #       pos = 0
 #       length = len(fileList)
 #       while pos < len(fileList):
 #           if fileList[pos].startswith('@'):
 #               homeList.append(fileList[pos].replace('@',''))
 #               del fileList[pos]
 #               length -=1
 #           pos += 1
            
 #       fileString = ';'.join(fileList)
 #       homeString = ';'.join(homeList)
               
        filteredIDs = RollVac.main('poly', directory, 'null', 'null', rollScript, filteredIDs)
        
        qsubs = open(homeDir + '/qsublist', 'a+b')
        qsubs.write(("qsub " + directory + 'qsub\n').replace('//','/'))   
        qsubs.close()    
               
        if needsReplace:
            replaceFile = params[5]
            replaceScript = loadReplaceScript(replaceFile)
            findNReplace(fileString, replaceScript, directory, vacsRolled, homeDir, explicit)
#            findNReplace(homeString, replaceScript, directory, vacsRolled, homeDir, explicit)
        
        if filesToCopy and not needsReplace:
            print fileString, directory       
            fileCopy(fileString, directory)
 #           fileCopy(homeString, explicit)
            
        vacsRolled += 1


# POLYRUN MULTIDIMENSIONAL LOOP ITERATOR

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
    
    pos = 0
    limit = len(toSetPermissions)
    while pos < limit:
        if toSetPermissions[pos]:
            print "Appending bash set permissions to 775 command to qsub list in directory:", directories[pos]
            qsubs = open(directories[pos] + '/qsublist', 'a+b')
            qsubs.write("chmod -R 775 " + directories[pos])   
            qsubs.close()  
            pos += 1 
 

            
main() 