import gDocsImport
import sys, os
from multiprocessing import Process, Queue, cpu_count

from math import ceil
try:
    from collections import OrderedDict
    print "\n*** Python 2.7+, loading OrderedDict from Collections ***"
except:
    from OrderedDict import OrderedDict
    print "\n*** OrderedDict not found in collections, using drop in version ***"


#From Rollvac, loads IDS as set for fast search
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
                ids.add(testline.strip())
                line += 1
                
    idstemp =  sorted(list(ids))      
    print str(line), "entries with IDS\n", int(idstemp[0]), "through", int(idstemp[line-1]), "loaded,\npreparing to analyze\n"
    
    return ids

#Returns first instance of substring in list of strings or false if not found

def checkList(text, textList):
    pos = 0
    index = -1
    while pos < len(textList):
        if text in textList[pos]:
            if index == -1:
                index = pos
            else:
                print "Warning, second instance of string %s found in list %s" % (text, str(textList))
        pos += 1
    return index
    
#For qsub list parsing, removes variable abbreviation and adjacent numbers from passed list of strings

def removeDescriptor(text, descriptors):
    print text, descriptors
    pos2 = 0
    while pos2 < len(descriptors):
        descriptor = descriptors[pos2]
        if descriptor in text:
            pos = text.index(descriptor) + 1
            text = text.replace(descriptor,' ')
            if pos < len(text) -1:
                while isDigit(text[pos]) and pos != len(text) -1:
                    text =  text[:pos] + text[pos+1:]
        pos2 += 1
    while text[0] == ' ':
        text = text[1:]
    return text
        
def isDigit(character):
    try:
        int(character)
        return True
    except:
        return False
        
        
def filterDict(paramDict,isKeys,hide):
    tempDict = paramDict.copy()
    hideThese = hide.split(' ')
    pos = 0
    while pos < len(hideThese):
        if hideThese[pos].replace(' ','') != '':
            try:
                del tempDict[hideThese[pos]]
                print "Column", hideThese[pos], "deleted"
            except:
                print "Warning, key '", hideThese[pos], "' not found"
        pos += 1 
    if isKeys:
        string = str(paramDict.keys())
    else:
        string = str(paramDict.values())
    return string.replace('[','').replace(']','').replace("'",'')
    
    
def getSpreadSheet(data, line, hide, justGetKeys):
    paramDict = OrderedDict((('ve',-1),('v',-1),('vti',-1),('vtd',-1),('sd',-1),('sdti',-1),('sdtd',-1),('sdl',-1),('cw',-1),('cwti',-1),('cwtd',-1),('cwl',-1),('cs',-1),('csti',-1),('cstd',-1),('csl',-1),('ate',-1),('at',-1),('atdr',-1),('atti',-1),('attd',-1),('atl',-1),('ape',-1),('ap',-1),('apti',-1),('aptd',-1),('apl',-1),('sq',-1),('sqg',-1),('sqtd',-1),('sql',-1),('other','')))
    dataDict = OrderedDict((('attackRate',0),('peakDay',0),('peakNumber',0),('isEpidemic',0),('leftBound',0),('rightBound',0),('secondaryMaxima','')))
    if justGetKeys:
        return "directory, iteration, " + filterDict(paramDict, True, hide) + ', ' + filterDict(dataDict, True, hide) + '\n'
    words = []
    numbers = []
    extra = ''
    pos = 0
    tempString = ''
    while '//' in line:
        line =  line.replace('//','/')
    line = line.replace(' ','').replace('\n','')
    while pos < len(line):
        if not isDigit(line[pos]) and line[pos] != '/':
            tempString += line[pos]
        else:
            if pos == len(line) -1 or line[pos] ==  '/':
                if isDigit(line[pos]):
                    if tempString not in paramDict.keys():
                        extra += tempString + str(line[pos]) + '_'
                    else:
                        words.append(tempString)
                        numbers.append(line[pos])
                else:
                    extra += tempString + '_'
                    tempString = ''
            else:
                isValid = True
                if tempString not in paramDict.keys():
                    extra += tempString
                    isValid = False
                else:
                    words.append(tempString)
                tempString = ''
                while pos < len(line) and isDigit(line[pos]) :
                    tempString += line[pos]
                    pos += 1
                if isValid:
                    numbers.append(tempString)
                else:
                    extra += tempString + '_'
                if pos < len(line):
                    if line[pos] != '/':
                        tempString = line[pos]
                    else:
                        tempString = ''
        pos += 1
    pos = 0
    
    if len(extra)!= 0:
        if extra[-1]=='_':
            extra = extra[0:-1]
    
    if len(words) != len(numbers):
        print "Data output error, word & number list lengths do not match"
        quit()
        
    while pos < len(words):
        word = words[pos]
        if word not in hide:
            try:
                paramDict[word] =  numbers[pos]
            except:
                print "Warning: word", word, "with value", numbers[pos], "not found"
        pos += 1
    paramDict['other'] = extra
    
    pos = 0
    outString = ''
    while pos < data['iterations']:
        dataDict['attackRate'] = data['attackRates'][pos]
        dataDict['peakDay'] = data['peakDay'][pos]
        dataDict['peakNumber'] = data['peakNumber'][pos]
	dataDict['isEpidemic'] = not data['ignored'][pos]
        dataDict['leftBound'] = data['leftBound'][pos]
        dataDict['rightBound'] = data['rightBound'][pos]
        try:
            dataDict['secondaryMaxima'] = data['secondaryMaxima'][pos][0:-1].replace(' ','-')
        except:
            dataDict['secondaryMaxima'] = 'NaN'
        lineOut = line + ', ' + str(pos) + ', ' + filterDict(paramDict, False, hide) + ', ' + filterDict(dataDict, False, hide) + '\n'
        outString += lineOut
        pos += 1
    dataDict['attackRate'] = data['epiMean']
    dataDict['peakDay'] = data['epiPeak']
    dataDict['peakNumber'] = data['epiNumber']
    dataDict['isEpidemic'] = '-1'
    dataDict['leftBound'] = data['epiLeft']
    dataDict['rightBound'] = data['epiRight']
    try:
        dataDict['secondaryMaxima'] = data['epiSecondary'][0:-1].replace(' ','-')
    except:
        dataDict['secondaryMaxima'] = 'NaN'
    outString += line + ', Mean, ' + filterDict(paramDict, False, hide) + ', ' + filterDict(dataDict, False, hide) + '\n'
    return outString

def writeTSVcells(directory, runList, refMatrix, valMatrix, xTitles, yTitles, title):
    print "refMatrix", refMatrix
    print "valMatrix", valMatrix
    print "xTitles", xTitles
    print "yTitles", yTitles,
    print "title", title
    
    if not os.path.exists(directory):
        os.mkdir(directory)
        
    dirTemp = directory+'/'+title
    titlesOut =  open(dirTemp+'Titles.txt','w')
    xTitlesTemp = '["' + '", "'.join(xTitles) + '"],'
    yTitlesTemp = '["' + '", "'.join(yTitles) + '"],'
    titlesOut.write("xAxisLables = " + xTitlesTemp + '\n')
    titlesOut.write("yAxisLables = " + yTitlesTemp)
    titlesOut.close()
    
    chartsOut = open(dirTemp+'Chart.tsv','w')
    refsOut =  open(dirTemp+'Refs.tsv','w')
    chartsOut.write('y\tx\tattackRate\n')
    refsOut.write('y\tx\tcellReference\n')
    
    
    xLen = len(xTitles)
    yLen = len(yTitles)
    posY =0
    while posY < yLen:
        #chartsOut.write(yTitles[posY] + ', ')
        posX = 0
        while posX < xLen:
            chartsOut.write(str(posY+1) + '\t' + str(posX+1) + '\t' + str(valMatrix[posX][posY]) + '\n')
            refsOut.write(str(posY+1) + '\t' + str(posX+1) + '\t' + str(refMatrix[posX][posY]) + '\n')
            posX += 1
        posY += 1
    
    chartsOut.close()
    refsOut.close()
        

def writeToFiles(directory, runList, refMatrix, valMatrix, xTitles, yTitles, title):
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

def writeAll(directory,title,data):
    if not os.path.exists(directory):
        os.mkdir(directory)
    summaryOut = open(directory+title+'Summary.txt','w')
    chartsOut = open(directory+title+'Charts.csv','w')
    summaryOut.write("Directory:\t" + str(data['directory']))
    summaryOut.write("\nPopsize:\t" + str(data['popsize']))
    summaryOut.write("\nIterations:\t" + str(data['iterations']))
    summaryOut.write("\nAttack Rates:\t" + str(data['attackRates']))
    summaryOut.write("\nPeak Day:\t" + str(data['peakDay']))
    summaryOut.write("\nPeak Number:\t" + str(data['peakNumber']))
    summaryOut.write("\nIgnored:\t" + str(data['ignored']))
    summaryOut.write("\nPercent Reaching Epidemic:\t" + str(data['epiPercent']))
    summaryOut.write("\nEpidemic Mean Attack Rate:\t" + str(data['epiMean']))
    summaryOut.write("\nEpidemic Mean Peak Day:\t" + str(data['epiPeak']))
    summaryOut.write("\nEpidemic Mean Peak Number:\t" + str(data['epiNumber']))
    summaryOut.write("\nSecondary Maxima:\t" + str(data['secondaryMaxima']))
    summaryOut.write("\nEpicurve Left Bounds:\t" + str(data['leftBound']))
    summaryOut.write("\nEpicurve Right Bounds:\t" + str(data['rightBound']))
    
    summaryOut.close()
    chartsOut.write('DAY')
    for pos in range(data['iterations']):
        chartsOut.write(', ' + str(pos) + ' ')
    chartsOut.write(', MEAN\n')
    for pos1 in range(data['days']):
        chartsOut.write(str(pos1) + ', ')
        for pos2 in range(data['iterations']):
            chartsOut.write(str(data['iterationsByDay'][pos2][pos1]) + ', ')
        try:
            chartsOut.write(str(data['meanCurve'][pos1]) + '\n')
        except:
            chartsOut.write('[0]\n')
    chartsOut.close()
    
def getMeanPlots(directory,data,duration):
    entries =  len(data['meanCurve'])
    text = directory + ', '
    for i in range(entries):
        text += str(data['meanCurve'][i]) + ', '
    text +='0, '*(duration - entries)
    return text + '\n'
    
def getDuration(directory):
    fileIn = open(directory + '/config')
    cue = "SimulationDuration = "
    config = fileIn.readlines()
    for line in config:
        if cue in line:
            return int(line.replace(cue,''))
    print "Error: Simulation duration not found in", directory + '/config'
    quit()

    
#Worker function for EFO6 sorting & parallelization
    
def sortEFO6(trimmed, subpopLoaded, useSubpop, out_q, core, iterations, disjoint):
    length = length0 =  len(trimmed)
    days = comments = filtered = pos = 0
    notifyEvery = 50000
    print "Core", core, "preparing to filter population, size:", length0
    outdict = {}
    content = {}
    
    #debug vars
    #useSubpop = False
    
    while pos < length:
        adjusted = pos + disjoint
        if '#' in trimmed[pos]:
		print "Ignoring comment:", trimmed[pos]
		disjoint -= 1
		comments += 1
        elif useSubpop:
	   temp = trimmed[pos].split()[0]
	   if temp not in subpopLoaded:
	           disjoint -=1
	   else:
    	       content[adjusted] = map(int,trimmed[pos].split(' '))	      
        else:
    	  content[adjusted] = map(int,trimmed[pos].split(' '))
    	
    	pos += 1
        if (pos+filtered)%notifyEvery == 0:
            print "Core", core, "filtering", pos+filtered, "out of", length0, "entries"
    
    print "Core", core, "filtering complete, beginning sort by day"
    for key, entry in content.iteritems():
        days =  max(days, entry[2])
        
    iterXDay = [[0 for pos1 in range(days+1)] for pos2 in range(iterations)]
    for key, entry in content.iteritems():
	iterXDay[entry[1]][entry[2]] += 1
    
    print "Core", core, "task complete"
    
    filtered = length - comments - len(outdict)
    outdict['comments'+str(core)] = comments
    outdict['filtered'+str(core)] = filtered
    outdict['byDay' + str(core)] = iterXDay
    outdict['days' + str(core)] = days
    out_q.put(outdict)
        
#Main Stat Generation Function

def checkLines(fileName, subpopLoaded, useSubpop, multiThreaded,):
    print "Reading file:", fileName
    wholeThing = open(fileName)
    content = wholeThing.readlines()
    params = content[0].split(' ')    
    popSize = int(params[1])
    iterations = int(params[3])
    trimmed = content[popSize+2:]
    length0 = len(trimmed)
    days =comments = filtered = pos = 0
    lengths = []
    isEmpty = False
    
    #debug var
    #trimmed = trimmed[:2000]
    
    if not multiThreaded:
        cores = 1
    else:
        cores = cpu_count()
    out_q = Queue()
    block =  int(ceil(len(trimmed)/float(cores)))
    processes = []
    
    for i in range(cores):
        p = Process(target = sortEFO6, args = (trimmed[block*i:block*(i+1)], subpopLoaded, useSubpop, out_q, i, iterations, block*i))
        processes.append(p)
        p.start() 
    trimmed = None
    merged = {}
    for i in range(cores):
        merged.update(out_q.get())
    for p in processes:
        p.join()
    
    for i in range(cores):
        lengths.append(merged["days" + str(i)])
        comments += merged["comments" + str(i)]
        filtered += merged["filtered" + str(i)]
        
    days = max(lengths)
    #print "%s entries remaining of %s entries: %s entries commented out, %s filtered via subpop membership" % (str(filtered),str(length0),str(comments),str(filtered))
   
    print "Subproccesses complete, merging results" 
    iterXDay = [[0 for pos1 in range(days+1)] for pos2 in range(iterations)]
    for i in range(days):
        for j in range(iterations):
            summed = 0
            for k in range(cores):
                if i <= lengths[k]:
                    summed += merged['byDay' + str(k)][j][i]
            iterXDay[j][i] += summed
            
    print "Results merge complete, beginning analysis"
    
    attackRates = []
    ignore = [False]*iterations
    empty = [False]*(iterations+1)
    ignored = 0
    maxDay = []
    maxNumber = []
    for pos in range(iterations):
        attackRates.append(sum(iterXDay[pos]))
        maxima = max(iterXDay[pos])
        maxNumber.append(max(iterXDay[pos]))
        maxDay.append(iterXDay[pos].index(maxima))
    meanAttack = sum(attackRates)/iterations
    print "Attack Rates:", attackRates
    print "Mean:", meanAttack
    print "Peak Days:", maxDay
    print "Peak Infected:", maxNumber
    
    epiAttack = 0
    for pos in range(iterations):
        if attackRates[pos] < meanAttack/10 or attackRates[pos] == 0:
            ignore[pos] =  True
            ignored += 1
            print "Iteration",pos,"did not reach epidemic status"
	if attackRates[pos] == 0:
	   print "Iteration",pos,"no infections found"
	   empty[pos] = True
        else:
            epiAttack += attackRates[pos]
    print "Ignored:", ignored
    if ignored != iterations:
        epiMean = epiAttack/(iterations-ignored)
    else:
        epiMean = 0
    epiPercent = ((iterations-ignored)/iterations)*100
    print "Percent Reaching Epidemic:", epiPercent
    print "Mean epdidemic attack rate:", epiMean
    
    meanCurve = []
    for pos1 in range(days):
        temp = 0
        for pos2 in range(iterations):
            if not ignore[pos2]:
                temp += iterXDay[pos2][pos1]   
        if iterations != ignored:
            meanCurve.append(int((float(temp)/(iterations-ignored))+.5))
    
    if sum(meanCurve) == 0:
        empty[iterations] = True    
        
    if not empty[iterations]:
        epiNumber = max(meanCurve)
        epiPeak =  meanCurve.index(epiNumber)
    else:
        epiNumber = 0
        epiPeak = 0
    
    leftBounds = []
    rightBounds = []
    lengths = []
    secondaryMaxima = [""]*(iterations + 1)
    curveWidth = .95
    searchWidth = .20
    peakToLocal = 10
    localSNR = 2
    secondaryThreshold = 10
    pos1 = 0
            
    while pos1 < iterations + 1:
        if empty[pos1]:
            leftBounds.append(-1)
            rightBounds.append(-1)
            lengths.append(-1)
            pos1 += 1
        else:
            isMean = pos1 == iterations
            pos2 = temp = 0
            if isMean:
                outside = (1-curveWidth)*epiMean*0.5
            else:
                outside = (1-curveWidth)*attackRates[pos1]*0.5
            while pos2 < days:
                if isMean:
                    temp += meanCurve[pos2]
                else:
                    temp += iterXDay[pos1][pos2]
                if temp > outside:
                    leftBounds.append(pos2)
                    print "left bound:",pos2
                    break
                pos2 += 1
            pos2 = days-1
            temp = 0

            while pos2 > 0:
                if isMean:
                    temp += meanCurve[pos2]
                else:
                    temp += iterXDay[pos1][pos2]
                if temp > outside:
                    print "right bound:",pos2
                    rightBounds.append(pos2)
                    break
                pos2 -= 1
                                        
            try:	
		lengths.append(rightBounds[pos1]-leftBounds[pos1])
            except:
                print "Error: out of bounds analysis on iteration", pos1
		print "Please review attack rate by day by iteration for unusual output:\n", iterXDay
		quit()
		
            sliceWidth = int(lengths[pos1]*searchWidth)
            pos2 = leftBounds[pos1]
            while pos2 + sliceWidth < rightBounds[pos1]:
                if isMean:
                    tempMax =  epiNumber
                else:
                    tempMax = maxNumber[pos1]
                if isMean:
                    tempSlice = meanCurve[pos2:min(pos2+sliceWidth+1,days)]
                else:
                    tempSlice = iterXDay[pos1][pos2:min(pos2+sliceWidth+1,days)]
                localPeak = max(tempSlice)
           	print tempSlice, localPeak
                localMaxima = tempSlice.index(localPeak)
            
           	if localMaxima == 0:
		      pos2 += 1
                elif localMaxima > sliceWidth/2:
                    pos2 += localMaxima - sliceWidth/2
                elif localPeak*peakToLocal >= tempMax and localPeak != tempMax and localPeak > secondaryThreshold and str(localMaxima + pos2) not in secondaryMaxima[pos1]:
                    leftSlice = tempSlice[0:localMaxima]
                    rightSlice = tempSlice[localMaxima:len(tempSlice)+1]
                    leftMin = min(leftSlice)
                    rightMin = min(rightSlice)
                    if localPeak>(leftMin+rightMin)*0.5*localSNR:
                        secondaryMaxima[pos1] += str(localMaxima+pos2) + ' '
                        pos2 += localMaxima
                        print "Secondary Maxima found in iteration %s on day %s" % (str(pos1),str(pos2+localMaxima))   
                    else:
			pos2 += 1
                else:
                    pos2 += 1
            pos1 += 1
    
    epiLeft = leftBounds[-1]
    epiRight = rightBounds[-1]    
    epiSecondary = secondaryMaxima[-1]
    del leftBounds[-1]
    del rightBounds[-1]
    del secondaryMaxima[-1]
    
    return {'directory':fileName,'days':days,'meanCurve':meanCurve,'epiPeak':epiPeak,'epiNumber':epiNumber,'epiLeft':epiLeft,'epiRight':epiRight,'epiSecondary':epiSecondary,'popsize':popSize,'iterations':iterations,'attackRates':attackRates,"ignored":ignore,'epiMean':epiMean,'epiPercent':epiPercent,'peakDay':maxDay,'peakNumber':maxNumber,'secondaryMaxima':secondaryMaxima,'leftBound':leftBounds,'rightBound':rightBounds,"iterationsByDay":iterXDay}
    
def prepDir(directory):
    while '//' in directory:
        directory = directory.replace('//','/')
    if directory[-1] != '/':
        directory += '/'
    return directory
        
def prepSingle(params,qsubList,splitList,passedX,passedY,passedC,lineIndex, subpopLoaded, useSubpop, multiCore):
    print splitList
    directoryIn = prepDir(params[0])
    directoryOut = prepDir(params[1])
    qsubTemp =  qsubList[lineIndex].replace(directoryIn,'').replace('/',' ').split(' ')
    print 'x/y', passedX, passedY
    if passedX != '':
        xID = checkList(passedX,qsubTemp)
        xFind = passedX.split(' ')
        xIgnore = ['']
    else:
        xID = int(params[7])
        xFind = params[8].split(' ')
        xIgnore = params[9].split(' ')
    xILen = len(xIgnore)
    xFLen = len(xFind)
    toFindX = xFLen > 0
    toIgnoreX = xIgnore != ['']
    
    if passedY != '':
        yID = checkList(passedY,qsubTemp)
        yFind = passedY.split(' ')
        yIgnore = ['']
    else:
        yID =  int(params[10])
        yFind = params[11].split(' ')
        yIgnore = params[12].split(' ')
    yILen = len(yIgnore)
    yFLen =  len(yFind)
    toFindY = yFLen > 0
    toIgnoreY = yIgnore != ['']
    print 'ids(x,y)', xID, yID
    if passedC != '':
        const = passedC
    else:
        const =  params[13]
    hasConst = len(const)>0
    const =  const.split()
    cLen = len(const)
    
    #width = qsubList[0].count('/') + 1
    print const
    width = len(splitList[0]) 
    limit = len(splitList)
    targetStrings = ['']*width
    studyName = params[2]
    target = params[4]
    print 'Flen',xFLen, yFLen
 
    tracker = [0] * width
    pos1 = 0
    while pos1 < limit:
        pos2 = pos3 = 0
	word = qsubList[pos1].replace(directoryIn,'')
	allFound = True
	while pos3 < cLen:
	    if const[pos3] not in word:
		allFound = False
		break
	    pos3 += 1
        while pos2 < width and allFound:
            word = splitList[pos1][pos2]
            keep = True
            isAxis = True
            if pos2 == xID:
                found = False
                pos3 = 0
                while pos3 < xFLen:
                    print word, xFind[pos3]
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
                    print word, yFind[pos3]
                    if yFind[pos3] in word:
                        found = True
			#print "huzzah!"
                        break
                    pos3 += 1
                pos3 = 0
                #print pos3, yILen, toIgnoreY
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
                    #tracker[pos2] += 1
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
            dirMatrix[xPos][yPos] = directoryIn + qsubList[pos1].replace(directoryIn,'') + '/' + target
            temp = checkLines(dirMatrix[xPos][yPos], subpopLoaded, useSubpop, multiCore)
            valMatrix[xPos][yPos] = temp['epiMean']          
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
    writeParams = {'directoryOut':directoryOut,'runList':runList,'refMatrix':refMatrix,'valMatrix':valMatrix,'xTitles':xTitles,'yTitles':yTitles,'studyName':studyName}
    return writeParams

def curveToTSV(epiMean):
    text = "day\tinfected\n"
    for pos in range(len(epiMean)):
        text += str(pos+1) + '\t' + str(epiMean[pos]) + '\n'
    return text

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
    #script = [entry.replace('\r','') for entry in script]
    sys.argv = None
    print script
    
    column = 1
    parseAll = False
    while column < len(script[0]):
        limit  = len(script)
        hasContent = False
        while not hasContent and column < len(script[0]):  
            params = []
            for pos in range(len(script)):
                params.append(script[pos][column])
            column +=1
            hasContent = len(''.join(params).replace(' ','') ) != 0
        if column == len(script[0]) and not hasContent:
            break
        
        params = [entry.replace('\r','') for entry in params]
        print params
        directoryIn = prepDir(params[0])
        directoryOut = prepDir(params[1])
        subpopDir = params[5]
        multiCore = params[14].lower()[0] == 'y'
        useSubpop = len(subpopDir) > 1
        subpopLoaded = []
        if useSubpop:
            try:
                print "Attempting analysis by subpop directory, loading file"
                subpopLoaded = filterIDs(subpopDir)
            except:
                print "Subpop load failed, quiting now."
                quit()
        studyName = params[2]
        qsubDir = params[3]
        target = params[4]
        runAll = params[14].lower()[0] == 'y'
        #makeAll =  params[15].lower()[0] == 'y'
        makeAll = False
	hideThese = params[16]
        
        fileIn = open(directoryIn + qsubDir)
        qsubList = fileIn.readlines()
        fileIn.close()
        pos = 0
        splitList =[]
        if "chmod -R 775" in qsubList:
            del qsubList[qsubList.index("chmod -R 775")]
        limit = len(qsubList)
        while pos < limit:
            if runAll:
                qsubList[pos] = qsubList[pos].replace('qsub ','').replace('qsub','').replace('/\n','')
                temp = qsubList[pos].replace(directoryIn,'').split('/')
            else:
                qsubList[pos] = qsubList[pos].replace('qsub ','').replace('qsub','').replace(directoryIn,'').replace('/\n','')
                temp = qsubList[pos].split('/')
            if temp not in splitList:
  		splitList.append(temp)
  		pos += 1
	    else:
		print "Duplicate entry on line %s ignored" % (pos)
		del qsubList[pos]
		limit -= 1
		
        duration = getDuration(qsubList[0])
        
        if not runAll:
            prepped = prepSingle(params,qsubList,splitList,'','','','', multiCore)
            writeToFiles(prepped['directoryOut'],prepped['runList'],prepped['refMatrix'],prepped['valMatrix'],prepped['xTitles'],prepped['yTitles'],prepped['studyName'])
        
        if runAll:
            temp = ''
            if useSubpop:
                temp = subpopDir.split('/')[-1].replace('.txt','') + '_'
            studyPrefix = prepDir(directoryOut + '/' + studyName) + temp
            VAVPrefix = prepDir(studyPrefix + 'Vacc_Vs_Av_Charts') 
            meansPrefix = prepDir(studyPrefix + 'Individual_Mean_Stats')
            print studyPrefix
            print VAVPrefix
            print meansPrefix
            if not os.path.exists(VAVPrefix):
                os.makedirs(VAVPrefix)
            if not os.path.exists(meansPrefix):
                os.makedirs(meansPrefix)
            
            #uniqueInterventions = []
            #uniqueIndex = []
            
            pos =  0
            for item in qsubList:
                print '\033[1m' + "\nAnalyzing cell #" + str(pos) + '\033[0m'
                data = checkLines(item+'/'+target, subpopLoaded, useSubpop, multiCore)
                qsubTemp = item.replace(directoryIn,'')
                #filteredName = removeDescriptor(qsubTemp,['ve','ate','ape']).replace('/',' ')
                qsubTemp = qsubTemp.replace('/','_')
                #if filteredName not in uniqueInterventions:
                  #  uniqueInterventions.append(filteredName)
                  #  uniqueIndex.append(pos)"""
                if pos == 0:
                    attackOut = open(studyPrefix + 'AttackList.txt','w')
                    attackOut.write("# Attack Rate List\n")
                    attackOut.close()
                    statsOut = open(studyPrefix + 'DetailStats.csv','w')
                    statsOut.write(getSpreadSheet(data, '', hideThese, True))
                    statsOut.close()
                    plotsOut = open(studyPrefix + 'MeanPlots.csv','w')
                    plotsOut.write('index, '+ str(range(duration)).replace('[','').replace(']',', \n'))
                    plotsOut.close()
                attackOut = open(studyPrefix + 'AttackList.txt','a+b')            
                statsOut = open(studyPrefix + 'DetailStats.csv','a+b')
                plotsOut = open(studyPrefix + 'MeanPlots.csv','a+b') 
                #qsubLine = meansPrefix + '/' + qsubTemp
                #meansOut = open(qsubLine + 'Means.tsv','w')
                if makeAll:
                    writeAll(item+'/', studyName, data)
                    writeAll(meansPrefix, qsubTemp, data)        
                attackOut.write(item.replace(directoryIn,'') + ' ' + str(data['epiMean']) + '\n')
                statsOut.write(getSpreadSheet(data, item.replace(directoryIn,''),hideThese, False))
                plotsOut.write(getMeanPlots(item.replace(directoryIn,''),data,duration))
                #meansOut.write(curveToTSV(data['meanCurve']))
                attackOut.close()
	        statsOut.close()
	        #meansOut.close()
	        pos += 1
	        
            """print "Finished generation of cell summaries & detail stats, starting mass chart generation"
            uniqueLimit = len(uniqueInterventions)
            cells =  qsubLimit/uniqueLimit
            print "%s unique interventions found with %s antiviral & vaccine effectiveness cells per graph" % (str(uniqueLimit),str(cells))
	    pos = 0
	    while pos < uniqueLimit:
	        qsubTemp = qsubList[uniqueIndex[pos]].replace(directoryIn,'')
	        print "SPLIT LIST:", splitList
	        if 've' in qsubTemp and ('ate' in qsubTemp or 'ape' in qsubTemp):
	           if 'ate' not in qsubTemp:
	                prepped = prepSingle(params,qsubList,splitList,'ape','ve',uniqueInterventions[pos],uniqueIndex[pos])
	           else:
	               prepped = prepSingle(params,qsubList,splitList,'ate','ve',uniqueInterventions[pos],uniqueIndex[pos])
	           print uniqueInterventions, uniqueLimit
	           writeTSVcells(directoryOut+'/Vacc_Vs_Av_Charts',prepped['runList'],prepped['refMatrix'],prepped['valMatrix'],prepped['xTitles'],prepped['yTitles'],uniqueInterventions[pos].replace(' ',''))
	        pos += 1"""
	        
        
    print "Finished analyses, quitting now"
        
    
main()
quit()
