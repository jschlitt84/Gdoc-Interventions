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
    toFindX = len(xFind) > 0
    xIgnore = params[9].split(' ')
    yID =  int(params[10])
    yFind = params[11].split(' ')
    yIgnore = params[12].split(' ')
    toFindY = len(yFind) > 0
    const =  params[14].split(' ')
    
    
    fileIn = open(directoryIn + target)
    qsubList = fileIn.readlines()
    fileIn.close()
    
    pos = 0
    
    splitList =[]
    width = qsubList[0].count('/') + 1
    if "chmod -R 775" in qsubList[-1]:
        del qsubList[-1]
    limit = len(qsubList)
    while pos < limit:
        qsubList[pos] = qsubList[pos].replace('qsub ','').replace('qsub','').replace(directoryIn,'').replace('/\n','')
        splitList.append(qsubList[pos].split('/'))
        print splitList[pos]
        pos += 1
    
    targetStrings = ['']*width
    pos1 = 0
    while pos1 < limit:
        pos2 = 0
        while pos2 < width:
            word = splitList[pos1][pos2]
            if pos2 == xID:
                keep = True
                if 
                
                if word
    

    



main()
quit()