import gDocsImport
import sys, os

def writeToFile(directory, runList, refMatrix, valMatrix, xTitles, yTitles, title):
    if not os.path.exists(directory):
        os.mkdir(directory)
    writeOut = open(directory+title,'w')
    xLen = len(xTitles)
    yLen = len(yTitles)
    writeOut.write('EFO6 Length Values' + ', '*(xLen) + '\n, ') 
    pos = 0
    while pos < xLen:
        writeOut.write(xTitles[pos] + ', ')
        pos += 1
    writeOut.write('\n')
    posY =0
    while posY < yLen:
        writeOut.write(yTitles[posY] + ', ')
        posX = 0
        while posX < xLen:
            writeOut.write(str(valMatrix[posX][posY]) + ', ')
            posX += 1
        posY += 1
        writeOut.write('\n')
    writeOut.write('\nQsubList Line References' + ', '*(xLen) + '\n, ')
    pos = 0
    while pos < xLen:
        writeOut.write(xTitles[pos] + ', ')
        pos += 1
    writeOut.write('\n')
    posY =0
    while posY < yLen:
        writeOut.write(yTitles[posY] + ', ')
        posX = 0
        while posX < xLen:
            writeOut.write(str(refMatrix[posX][posY]) + ', ')
            posX += 1
        posY += 1
        writeOut.write('\n')
    pos = 0
    writeOut.write('\nLines Ran' + ', '*(xLen) + '\n')
    while pos < len(runList):
        print runList[pos]
        writeOut.write(runList[pos] + ', '*(xLen) + '\n')
        pos += 1
    writeOut.close()
    

def checkLines(file):
    wholeThing = open(file)
    content = wholeThing.readlines()
    params = content.split(' ')    
    popSize = content[2]
    iterations = content[4]
    numInfected =  popSize/iterations
    trimmed = content[popSize:].split(' ')
    print trimmed
    quit
    max(trimmed)
    return content.count('\n') + 1
    
def prepDir(directory):
    return (directory+'/').replace('//','/')

def main():
    
    if len(sys.argv) > 2:
        if len(sys.argv) == 3:
            sys.argv.insert(2,'null') 
        else:
            print "Ignoring", len(sys.argv) - 2, "excess arguments\n"
    elif len(sys.argv) == 2:
            sys.argv.insert(1,'null')
            sys.argv.insert(1,'null')

    script = gDocsImport.getScript(sys.argv[1], sys.argv[2], sys.argv[3], 0, -1, "default", False, [])
    sys.argv = None
    print script
    
    column = 1
    while column < len(script[0]):
        params = []
        pos = 0
        limit  = len(script)
        while pos < limit:
            params.append(script[pos][column])
            pos += 1
        
        print params
        directoryIn = prepDir(params[0])
        directoryOut = prepDir(params[1])
        studyName = params[2]
        qsubDir = params[3]
        target = params[4]
    
        xID = int(params[7])
        xFind = params[8].split(' ')
        xFLen = len(xFind)
        toFindX = xFLen > 0
        xIgnore = params[9].split(' ')
        xILen = len(xIgnore)
        toIgnoreX = xIgnore != ['']
        
        yID =  int(params[10])
        yFind = params[11].split(' ')
        yFLen =  len(yFind)
        toFindY = yFLen > 0
        yIgnore = params[12].split(' ')
        yILen = len(yIgnore)
        toIgnoreY = yIgnore != ['']
        
        const =  params[13].split(' ')
        cLen = len(const)
        
        
        fileIn = open(directoryIn + qsubDir)
        qsubList = fileIn.readlines()
        fileIn.close()
        
        pos = 0
        
        splitList =[]
        if "chmod -R 775" in qsubList[-1]:
            del qsubList[-1]
        limit = len(qsubList)
        while pos < limit:
            qsubList[pos] = qsubList[pos].replace('qsub ','').replace('qsub','').replace(directoryIn,'').replace('/\n','')
            splitList.append(qsubList[pos].split('/'))
            pos += 1
        width = qsubList[0].count('/') + 1
        
        targetStrings = ['']*width
        tracker = [0] * width
        pos1 = 0
        while pos1 < limit:
            pos2 = 0
            while pos2 < width:
                word = splitList[pos1][pos2]
                keep = True
                isAxis = True
                if pos2 == xID:
                    found = False
                    pos3 = 0
                    while pos3 < xFLen:
                        if xFind[pos3] in word:
                            found = True
                            break
                        pos3 += 1
                    pos3 = 0
                    while pos3 < xILen and toIgnoreX:
                        if xIgnore[pos3] in word:
                            keep = False
                            break
                        pos3 += 1
                    if toFindX and not found:
                        keep = False
                elif pos2 == yID:
                    found = False
                    pos3 = 0
                    while pos3 <yFLen:
                        if yFind[pos3] in word:
                            found = True
                            break
                        pos3 += 1
                    pos3 = 0
                    while pos3 < yILen and toIgnoreY:
                        if yIgnore[pos3] in word:
                            keep = False
                            break
                        pos3 += 1
                    if toFindY and not found:
                        keep = False
                else:
                    isAxis = False
                    if word in const and word not in targetStrings[pos2]:
                        tracker[pos2] += 1
                        targetStrings[pos2] += word + ' ' 
                if isAxis and keep and word not in targetStrings[pos2]:
                    targetStrings[pos2] += word + ' '
                    tracker[pos2] += 1
                pos2 += 1
            pos1 += 1
        
        targetList = [[]]*width
        pos = 0
        while pos < width:
            count = targetStrings[pos].count(' ')
            if pos == xID:
                if count == 0:
                    print "Error: no variables found for X axis"
                    quit()
                elif count == 1:
                    print "Warning: only one variable found for X axis"
            elif pos == yID:
                if count == 0:
                    print "Error: no variables found for Y axis"
                    quit()
                elif count == 1:
                    print "Warning: only one variable found for Y axis"
            else:
                if count > 1:
                    print "Error, multiple variables found for const #%s, operators = %s" % (str(pos), const)
            targetList[pos] = targetStrings[pos].split(' ') [:-1]
            pos += 1
            
        runList = []
        xCols =  len(targetList[xID])
        yRows =  len(targetList[yID])
        refMatrix = [[0 for pos1 in range(yRows)] for pos2 in range(xCols)]
        valMatrix = [[0 for pos1 in range(yRows)] for pos2 in range(xCols)]
        dirMatrix = [[0 for pos1 in range(yRows)] for pos2 in range(xCols)]
        testMatrix = [[0 for pos1 in range(yRows)] for pos2 in range(xCols)]
        
        
        pos1 = 0
        limit = len(splitList)
        while pos1 < limit:
            pos2 = 0
            keepLine = True
            while pos2 <  width:
                if splitList[pos1][pos2] not in targetStrings[pos2]:
                    keepLine = False
                    break
                pos2 += 1
            if keepLine:
                xPos =  targetList[xID].index(splitList[pos1][xID])
                yPos = targetList[yID].index(splitList[pos1][yID])
                print xPos, yPos
                refMatrix[xPos][yPos] = pos1
                testMatrix[xPos][yPos] = xPos
                dirMatrix[xPos][yPos] = directoryIn + qsubList[pos1] + '/' + target
                valMatrix[xPos][yPos] = int(checkLines(dirMatrix[xPos][yPos]))/5            
                print pos1
                print qsubList[pos1]
                runList.append(qsubList[pos1])
                
            pos1 += 1
        print runList
        print refMatrix
        print valMatrix
        
        xTitles = targetList[xID]
        yTitles = targetList[yID]
        print xTitles
        print yTitles
    
        writeToFile(directoryOut, runList, refMatrix, valMatrix, xTitles, yTitles, studyName)
        
        column += 1
        
    print "Finished analyses, quitting now"
    

    
    
                
                    
                
    

    



main()
quit()