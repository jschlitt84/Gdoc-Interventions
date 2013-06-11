import sys
import gDocsImport
import RollVac


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
#        print cmd
        return cmd
        
        
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
        
def main():
    
    vacsRolled = 0
    
    totalVars = 0
    varList = []
    varSets = []
    suffixes = []
    positions = []
    
    if len(sys.argv) > 2:
        if len(sys.argv) == 3:
            sys.argv.insert(2,'null') 
        else:
            print "Ignoring", len(sys.argv) - 2, "excess arguments\n"
    elif len(sys.argv) == 2:
            sys.argv.insert(1,'null')
            sys.argv.insert(1,'null')
    script = gDocsImport.getScript(sys.argv[1], sys.argv[2], sys.argv[3], 0, -1, "default", False)


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
        directory = ""
        
        toRun  =  ''
        while pos < totalVars:
            directory += suffixMatrix[pos][runTracker[pos]] + '/'
            toRun += suffixMatrix[pos][runTracker[pos]].replace(' ','') + ' '
            pos += 1
        print toRun
        
        
        pos = 0
        length = len(script)
        scriptOut = open('polytemp.csv', 'w')
        print "Loading Script for line:", runTracker
        while pos < length:
            print '\n' + str(getPoly(script[pos]))
            if getPoly(script[pos])[0] == 'null' or getPoly(script[pos])[1] in toRun:
                scriptOut.write(filterPoly(script[pos]))
                print "LINE WRITTEN:"
                print script[pos]
                print filterPoly(script[pos])
            pos += 1  
            
        scriptOut.close()

        RollVac.main('poly', directory, 'null', 'null')
        vacsRolled += 1

        pos = 0
        runOut = open("diagLog", 'a+b')
        print >> runOut, directory
        
        justRolled = False
        while runTracker[pos] == ends[pos] and pos < totalVars - 1:
            justRolled = True
            runTracker[pos] = 0
            runTracker[pos+1] += 1
            pos += 1
            
        if pos == totalVars - 1 and runTracker[pos] == ends[pos]:
            print >> runOut, "MADE IT HERE1"
            print >> runOut, "Vacs Rolled=", vacsRolled
            print "Interventions Iterated =", vacsRolled
            runOut.close()
            done = True
            break
         
        if not justRolled:
            runTracker[0] += 1   
            
        runOut.close()
    print "Intervention iteration succesfully complete!"

            
main() 