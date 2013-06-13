import sys
import os
import shutil
import gDocsImport
import RollVac

#import time


# ERASES DIRECTORIES FROM GIVEN LIST

def flushDirectories(directoryList):
    pos = 0
    limit = len(directoryList)
    while pos < limit:
        flushDirectory= directoryList[pos].replace(' ','')
        if len(flushDirectory) == 0:
            flushDirectory = "polyrun"
        print "Flushing directory %s: %s" % (pos, flushDirectory)
        if os.path.exists(flushDirectory):
            print "HUZZAH"
            shutil.rmtree(flushDirectory)
            print "cleared succesfully"
        else:
            print "not found, skipping"
#        qsub = open(flushDirectory, 'w')
#        qsub.close()
        pos += 1
        
        
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

def fileCopy(fileString, directory, findAndReplace):
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
        if findAndReplace:
            copyFile2 = copyFile2.replace('findAndReplace/','')
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
    
    if os.path.exists("findAndReplace"):
        shutil.rmtree("findAndReplace")
    os.makedirs("findAndReplace")

    fileList = fileString.split(';')
    print "Copying files:", fileList
    pos = 0
    limit = len(fileList)
    while pos < limit:
        copyFile = fileList[pos].replace(' ','')
        print "File %s: %s" % (pos, copyFile)
        if os.path.exists(copyFile):
            shutil.copy2(copyFile, "findAndReplace/" + copyFile)
            print "copied succesfully"
        else:
            print "Error: copyfile not found"
            quit()
        pos += 1
    print "Replacing content"
    pos1 = 0
    limit3 = len(replaceScript)
    while pos1 < limit:
        copyFile = fileList[pos1].replace(' ','')
        replaceFile = open("findAndReplace/" + copyFile)
        contents = replaceFile.readlines()
        replaceFile.close()
        limit2 = len(contents)
        
        pos2 = 0
        while pos2 < limit2:
            
            pos3 = 0
            while pos3 < limit3:
                if replaceScript[pos3]['file'] == fileList[pos1]:
                    if replaceScript[pos3]['find'] in contents[pos2]:
                        line = replaceScript[pos3]['replace'] 
                                    
#                        print "***",line, "***"
#                        print pos1, pos2, pos3, "CHECK IT"
#                        time.sleep(4)
                        
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
            
        replaceFile = open("findAndReplace/" + copyFile, 'w')

        contents = ''.join(contents)
        replaceFile.write(contents)
        replaceFile.close()
        pos1 += 1
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
    positions = []


# PARSING COMMAND LINE ARGUMENTS FOR PUBLIC/ PRIVATE FILE ACCESS        
            
    if len(sys.argv) > 2:
        if len(sys.argv) == 3:
            sys.argv.insert(2,'null') 
        else:
            print "Ignoring", len(sys.argv) - 2, "excess arguments\n"
    elif len(sys.argv) == 2:
            sys.argv.insert(1,'null')
            sys.argv.insert(1,'null')
    script = gDocsImport.getScript(sys.argv[1], sys.argv[2], sys.argv[3], 0, -1, "default", False)
    directoryLines = gDocsImport.getScript(sys.argv[1], sys.argv[2], sys.argv[3], paramsStart, startWord, "default", False)
    

# ERASES DIRECTORY NAMES GIVEN BY GDOC
    
    pos = 0
    directories = []
    while pos  < len(directoryLines):
        directories.append(directoryLines[pos][0])
        pos += 1
    flushDirectories(directories)
    
    
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
            positions.append(pos)
        pos += 1  
    pos1 = 0

    varList.sort()
    length = len(varSets)
    varMatrix = [[] for x in xrange(totalVars)]
    suffixMatrix = [[] for x in xrange(totalVars)]
    positionMatrix = [[] for x in xrange(totalVars)]
    
    
# CREATES MATRICES OF SUFFIXES, VARIABLE ID, AND LIST POSITION FOR ITERATION  
    
    pos2 = 0                 
    while pos2 < totalVars:
        pos1 = 0
        while pos1 < length:
            if varSets[pos1] == varList[pos2] and (suffixes[pos1] not in suffixMatrix[pos2]):
                varMatrix[pos2].append(varSets[pos1])
                suffixMatrix[pos2].append(suffixes[pos1])
                positionMatrix[pos2].append(positions[pos1])
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
        scriptOut = open('polytemp.csv', 'w')
        tempScript = []
        print "Loading Script for line:", runTracker
        while pos < length:
            if getPoly(script[pos])[0] == 'null' or getPoly(script[pos])[1] in toRun:
                scriptOut.write(filterPoly(script[pos]))
                tempScript.append(filterPoly(script[pos]))
            pos += 1  
            
        scriptOut.close()

                
# SUPPORT ADDED FOR MULTIPLE DIRECTORIES/ RUN         
                
        folder = "polyrun"
        params = gDocsImport.getLine(sys.argv[1], sys.argv[2], sys.argv[3], paramsStart , True)
        if len(params[0]) > 0:
            folder = params[0]
        directory = folder + "/"


# OUT DIRECTORY GENERATED VIA SUFFIX MATRIX
                                
        pos = 0
        while pos < totalVars:
            directory += suffixMatrix[pos][runTracker[pos]] + '/'
            pos += 1
            
        params = gDocsImport.loadNClean(False, tempScript, paramsStart, startWord, "single line", False)
        print params
        
        homeDir = params[0]
        explicit =  params[2]
        needsReplace = len(params[5]) > 0
        fileString =  params[3]
        filesToCopy = len(fileString) > 0
                
        RollVac.main('poly', directory, 'null', 'null')
        
        qsubs = open(homeDir + '/qsublist', 'a+b')
        qsubs.write(explicit + directory + 'qsub\n')   
        qsubs.close()    
               
        if needsReplace:
            replaceFile = params[5]
            replaceScript = loadReplaceScript(replaceFile)
            findNReplace(fileString, replaceScript, directory, vacsRolled, homeDir, explicit)
            pos = 0
            fileString = "findAndReplace/"+ fileString.replace(';',';findAndReplace/')
        
        if filesToCopy:
            print fileString, directory       
            fileCopy(fileString, directory,needsReplace)
            
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
    os.remove("polytemp.csv")

            
main() 