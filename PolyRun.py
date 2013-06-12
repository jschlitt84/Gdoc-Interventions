import sys
import os
import shutil
import gDocsImport
import RollVac


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
            shutil.rmtree(flushDirectory)
            print "cleared succesfully"
        else:
            print "not found, skipping"
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
        print "Loading Script for line:", runTracker
        while pos < length:
            if getPoly(script[pos])[0] == 'null' or getPoly(script[pos])[1] in toRun:
                scriptOut.write(filterPoly(script[pos]))
            pos += 1  
            
        scriptOut.close()

                
#SUPPORT ADDED FOR MULTIPLE DIRECTORIES/ RUN         
                
        folder = "polyrun"
        params = gDocsImport.getLine(sys.argv[1], sys.argv[2], sys.argv[3], paramsStart , True)
        if len(params[0]) > 0:
            folder = params[0]
        directory = folder + "/"


#OUT DIRECTORY GENERATED VIA SUFFIX MATRIX
                                
        pos = 0
        while pos < totalVars:
            directory += suffixMatrix[pos][runTracker[pos]] + '/'
            pos += 1   

        RollVac.main('poly', directory, 'null', 'null')
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