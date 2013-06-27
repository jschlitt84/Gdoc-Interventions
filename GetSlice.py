import gDocsImport
import sys


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
    target = params[3]
   
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
    
    
    fileIn = open(directoryIn + target)
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
    
    print
    print tracker
    print targetStrings
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
        
    toRun = []
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
            toRun.append(pos1)
        pos1 += 1
    print toRun
    
    
                
                    
                
    

    



main()
quit()