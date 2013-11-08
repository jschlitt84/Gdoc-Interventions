import gDocsImport as gd
import sys, os

from GetSlice import filterIDs, prepDir
from multiprocessing import Process, Queue, cpu_count

from math import ceil
try:
    from collections import OrderedDict
    print "\n*** Python 2.7+, loading OrderedDict from Collections ***"
except:
    from OrderedDict import OrderedDict
    print "\n*** OrderedDict not found in collections, using drop in version ***"
    
paramsLine = "Analysis Name,Output Folder"
toFromLine = "To Subpopulation,From Subpopulation"
EFO6Line = "EFO6 Files To Analyze"
    
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
    
    
def checkLines(fileName, subpopLoaded, useSubpop, multiThreaded, crossTalk):
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
    
    return {'directory':fileName,'days':days,'meanCurve':meanCurve,"iterationsByDay":iterXDay}
    
def main():
    if len(sys.argv) > 2:
        if len(sys.argv) == 3:
            sys.argv.insert(2,'null') 
        else:
            print "Ignoring", len(sys.argv) - 2, "excess arguments\n"
    elif len(sys.argv) == 2:
            sys.argv.insert(1,'null')
            sys.argv.insert(1,'null')

    #script = gDocsImport.getScript(sys.argv[1], sys.argv[2], sys.argv[3], 0, -1, "default", False, [])
    params = gd.getLine(sys.argv[1], sys.argv[2], sys.argv[3], paramsLine, False, []):
    script = gd.getScript(sys.argv[1], sys.argv[2], sys.argv[3], toFromLine, EFO6Line, "default", False, [])
    directories = gd.getScript(sys.argv[1], sys.argv[2], sys.argv[3], EFO6Line, -1, "default", False, [])
    sys.argv = None
    print "PARAMS:", params
    print "SCRIPT:", script
    print "DIRECTORIES:", directories

    
main()
quit()
