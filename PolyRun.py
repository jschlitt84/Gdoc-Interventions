import sys
import os
import chopper
import gDocsImport
import csv
import RollVac.py

totalVars = 0
varList = []
varSets = []
suffixes = []
positions = []
#startWord = "Study Name Prefix (optional),Diagnosis Based"


def getPoly(refline):
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
        return ['null']
    else:
        line[pos]= line[pos].replace('\n','')
        while "  " in line[pos]:
            line[pos]= line[pos].replace('  ',' ')
        cmd = line[pos].split(' ')
        del cmd[0]
        print cmd
        return cmd
        
        
def filterPoly(refLine)
    pos = 0
    line = refLine[:]
    length= len(line)
    while pos < length:
        if '$' in line[pos]:
            del line[pos]
            length -= 1
        pos += 1
    lineout = ",".join(line) + '\n'
    return line
        
def main():
    if len(sys.argv) > 2:
        if len(sys.argv) == 3:
            sys.argv.insert(2,'null') 
        else:
            print "Ignoring", len(sys.argv) - 2, "excess arguments\n"
    elif len(sys.argv) == 2:
            sys.argv.insert(1,'null')
            sys.argv.insert(1,'null')
            
    script = gDocsImport.getScript(sys.argv[1], sys.argv[2], sys.argv[3], 0, 0, "default")
    
    pos = 0
    length = len(script)
    while pos < length:
        temp = getPoly(script)
        if temp[0] != 'null':
            if temp[0] not in varSets:
                totalVars += 1
                varList.append(temp[0])
            varSets.append(temp[0]) 
            suffixes.append(temp[1])
            positions.append(pos)
        pos += 1
        
    pos1 = 0
    length = len(varSets)
    varMatrix = [[] for x in xrange(totalVars)]
    suffixMatrix = varMatrix
    positionMatrix = varMatrix
    
    while pos1 < length:
        pos2 = 0
        while pos2 < totalVars:
            if varSets[pos1] == varList[pos2] and suffixes[pos1] not in suffixMatrix[pos2]:
                varMatrix[pos2].append(varList[pos1])
                suffixMatrix[pos2].append(suffixes[pos1])
                positionMatrix[pos2].append(positions[pos1])
                break
            pos2 += 1
        pos1 += 1
    
    runTracker = [0] * totalVars
    done = False
    
    totalRuns = 1
    pos = 0
    ends = []
    while pos < totalVars:
        totalRuns *= len(varMatrix[pos]))
        ends.append(len(varMatrix[pos])-1)
        pos += 1  
    
    pos = 0
    
    
    while not done:
        
        pos = 0
        directory = ""
        
        while pos < totalVars:
            directory += suffixMatrix[pos][runtracker[pos]] + '/'
        
        pos = 0
        length = len(script)
        scriptOut = open('googTemp.csv', 'w')
        while pos < length:
            if getPolyCommands == 'null' or getPolyCommands in varList
                scriptOut.write(filterPoly(script))
            pos += 1
            
        scriptOut.close()
        
        chopper.main(poly, directory)
        
        pos = 0
        while pos < toTalVars
            if runTracker[pos] == ends[pos]:
                if pos == totalVars - 1:
                    done = True
                    break
                else:
                    runTracker[pos] = 0
                    runTracker[pos+1] += 1
            else: 
                break
            pos += 1
            
        runTracker[0] += 1
            
            
            

    
        
            