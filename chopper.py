import sys
import os


# CHECKS THE SIZE OF A POPULATION, IGNORES DUPLICATE IDS

def popSize(subPop):
    line = pos1 = 0
    tempList = []
    popfile = open(subPop)
    while True:
            testline = popfile.readline()
            if len(testline) == 0:
                break
            if not testline.startswith("#"):
                ID = testline
                tempList.append(ID)
                line += 1
                
    while pos1 < line-1:             
        while (tempList[pos1] in tempList[pos1+1:line]):
            del tempList[pos1]
            line -= 1
        pos1 += 1
    return line
    

# SUMS THE SIZE OF AN ENUMERATION LIST  
    
def getEnumSize(enumList):
    size = pos = 0
    while pos < len(enumList):
        size += enumList[pos+1]
        pos += 2
    return size
    

# TRIMS ENUMERATION IF OVERLARGE ENUMERATION REQUESTED FOR A GIVEN POPULATION
# REFLECTED IN INTERVENTION TOTALS

def trimEnum(enumList, target):
    total = pos = 0
    newEnum = []
    while total <= target:
        newEnum.append(enumList[pos])
        total += enumList[pos+1]
        if total > target:
            newEnum.append(enumList[pos+1] - total + target)
        else:
            newEnum.append(enumList[pos+1])
        pos += 2
    print "Trimming excess enumurated interventions, original:", enumList
    print "to new:", newEnum
    print "to meet size", target, "\n"
    return newEnum
        

# RETURNS TRUE IF STRING CARIES INTEGER VALUE

def isInt(number):
    try:
         return (number.replace(".", "", 1).isdigit())
    except:
        return False


# GENERATES FILE BASED ON ARGUMENTS GIVEN, RETURNS POSITION IN LIST OF IDS AND FILE/CHUNK NUMBER

def runChunk (IDS, outfile, index, limit, filenum, size, suffix, path):  
    while index < limit:
        fileName = outfile.split('/')[-1]
        log = open(path + 'subpops/chop.log', 'a+b')
        writefile = open((path + '/subpops/' + fileName).replace('//','/') + str(filenum) + suffix, 'w')
        log.write("Generating file " + (path + '/subpops/' + fileName).replace('//','/') + str(filenum) + suffix)
        log.write("\tID " + str(index+1) + " -" + str(int(IDS[index])))
        writefile.write("".join(IDS[index:index+size]))
        index += size
        last = min(index, len(IDS))
        log.write("\tID " + str(last) + "-" + IDS[last-1]+ '\n')
        filenum += 1
    log.close()
    writefile.close()
    return {'pos':index,'file':filenum}



def main(arg1, arg2, arg3, arg4, arg5):
    
    path = arg5    
    if not (os.path.isdir(path + "subpops")):
        os.makedirs(path + "subpops")

    log = open(path +'subpops/chop.log', 'a+b')

    if __name__ != '__main__':
        sys.argv = ['chopper.py',arg1,arg2,arg3,arg4]
        print "Preparing to chop, parameters:", sys.argv

    from datetime import datetime
    log.write("*************************\n" + str(datetime.now()) + '\n')
    
    if len(sys.argv) < 4 or len(sys.argv) > 5:
        print "Error,", len(sys.argv)-1, "arguments found, 3-4 expected\n"
        log.write("Termination due missing/ excess arguments\n")
        quit()
    
    filepath = sys.argv[1]
    print "****===", filepath
        
    if filepath == "help":
        print """\nArguments: chopper.py {filename} A{count or blocks} B{number} C{optional suffix}
        A: enter a letter 'c' for count to chop ID's to group size B, or the letter 'b' to chop ID's to B equal sized blocks
        B: enter the number for argument A
        C: optional, chopped file suffix\n\n"""
        quit() 
          
    A = sys.argv[2].lower()
    if A == 'c' or A == 'count':
        chopStyle = 'count'
    elif A == 'b' or A == 'blocks':
        chopStyle = 'block'
    elif A == 'e' or A == 'enum':
        chopStyle = 'enum'
    else:
        print "Error: invalid chop type, enter c for count or b for blocks\n\n"
        log.write("Termination due to invalid chop type\n")
        quit()

    if chopStyle != "enum":
        enumList = []
        if not sys.argv[3].isdigit():
            print "Error: must enter an integer value for 3rd argument\n"
            log.write("Termination due to non integer 3rd argument\n")
            quit()
        num = int(sys.argv[3])
        if num < 1:
            print "Error: invalid count, enter a number between 1 and the total population number\n\n"
            log.write("Termination due to invalid count, value too small: " + str(sys.argv[3]) + "\n\n")
            quit()
    else:
        enumList = map(int,sys.argv[3].split())
        num = getEnumSize(enumList)
        
        
    if len(sys.argv)==5:    
        suff=sys.argv[4]
        
            
    print "\nOpening file name", filepath
    popfile = open(filepath)
    ids = []
        
    print filepath,"succesfully opened\n"
    log.write("File " + filepath + " opened succesfully\n\n")


# LOAD IDS FROM FILE    
                      
    line = 0
    while True:
            testline = popfile.readline()
            if len(testline) == 0:
                break
            if not testline.startswith("#"):
                ID = testline
                ids.append(ID)
                line += 1
          
    print str(line), "entries with IDS\n", int(ids[0]), "through", int(ids[line-1]), "loaded,\npreparing to chop\n"
    log.write(str(line) + " entries with IDS\n" + str(int(ids[0])) + " through " + ids[line-1] + " loaded,\npreparing to chop\n")  
    
    print "(sub)Population loaded succesfully, checking for duplicate IDs...\n"
    duplicates = pos1 = 0
    
    while pos1 < line-1:             
        while (ids[pos1] in ids[pos1+1:line]):
            print "Ignoring duplicate instance of ID", ids[pos1].replace('\n','')
            del ids[pos1]
            line -= 1
            duplicates += 1
        pos1 += 1
 
    if num >= line:
        print "Error: block size and number must be less than population size, applying correction\n"
        log.write("Termination due to invalid count, value too large: " + str(num) + "\n")
        if chopStyle == 'enum':
            enumList = trimEnum(enumList, line)
        else:    
            num = line      

# ENUMERATED CHOP
        
          
    if chopStyle == 'enum':
        pos1 = pos2 = chunk = returnCount = 0
        tracker = 0
        limit = len(enumList)
        print "\nChopping into", limit/2, "blocks via enumeration"
        log.write("Chopping population into " + str(limit/2) + " blocks via enumeration")
        while pos1 < limit:
            b = enumList[pos1+1]
            print "Block", pos1/2, "set to size", enumList[pos1+1]
            tracker = runChunk(ids, filepath, pos2, pos2+b, chunk, b, suff, path)
            pos2 = tracker['pos']
            chunk = tracker['file']
            pos1 += 2
        returnCount = tracker['pos']
        if returnCount > line:
            print (returnCount-line), "excess interventions administered"
            returnCount = line
 
 
 # CHOP BY COUNT
                       
                                  
    elif chopStyle == 'count':
        a = line
        b = int(a/num)
        c = a-b*num
        print "Chopping population into", b, "blocks of size", num
        log.write("Chopping population into " + str(b) + " blocks of size " + str(num) + "\n")        
        if c != 0:
            print "with 1 block of size", c, "\n"
            log.write("with 1 block of size " + str(c) + "\n\n")
        
        runChunk(ids, filepath, 0, line, 0, num, suff, path)
        returnCount = b*num + c

    
# CHOP BY BLOCK (ROLLED INTERVENTIONS)                  
    
    elif chopStyle == 'block':
        a = line
        b = int(a/num)
        c = a-b*num
        small = num
        if c == 0:
            print "Chopping population into", num, "blocks of size", b
            log.write("Chopping population into " + str(num) + " blocks of size " + str(b) + "\n")  
            returnCount = b*num 
        else:
            print "Chopping population into", c, "blocks of size", b+1, "with", num-c, "blocks of size", b
            log.write("Chopping population into " + str(c) + " blocks of size " + str(b+1) + " with " + str(num-c) + " blocks of size " + str(b) +"\n")
            small = num-c
            returnCount = c*(b+1) + (num-c)*b
                
                                    
        chunk = pos1 = 0
        tracker = runChunk(ids, filepath, pos1, small*b, chunk, b, suff, path)
        if c!= 0:
            pos1 = tracker['pos']
            chunk = tracker['file']
            runChunk(ids, filepath, pos1, line, chunk, b+1, suff, path)
                
    print "Chopping complete!\n"
    log.write("\nChopping succesfully completed\n\n")
    log.close()

    
# For later implementation of start here/ subpop finished. 
# Current implementation runs each from start of subpop to end of intervention/ subpop 
# Workaround is to use each intervention only once per populaton                   
 
    subpop = {'name':'null','size':0,'v':0,'av':0,'sd':0,'cw':0,'cs':0} 

    return {'count':returnCount,'enum':enumList, 'subpop': subpop}

if __name__ == '__main__':
    main(0,0,0,0,'')