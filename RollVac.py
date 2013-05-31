import sys
import os
import chopper
import gDocsImport    

def getEnum():
    while True:
        print """\nEnter enumeration day and number list, format: 0 1; 1 5; 2 10; 3 14
per a given intervention, all enumeration must be taken care of in one call
further enumeration may lead to overlap with undesirable results for certain interventions"""
        enumerator =str(raw_input(":"))
        if len(enumerator) == 0:
            print "Nothing entered, defaulting to '0 1; 1 2; 3 5; 4 8'\n"
            enumerator = "0 1; 1 2; 3 5; 4 8"
        enumerator = enumerator.replace(";"," ; ")
        if checkEnum(enumerator):
            break
    return parseEnum(enumerator)
         
def checkEnum(enumerator):
    cmds = enumerator.split()
    pos = 0
    lim = len(cmds) 
    if lim%3 != 2:
        print "Error: enumerator missing/ extra terms"
        return False
    while pos < lim:
        if pos%3 == 0 or pos%3 ==1:
            if not chopper.isInt(cmds[pos]) or cmds[pos] < 0:
                print "Error: enumeration entry at pos", len, "is not a positive integer"
                return False
            if pos%3 == 1 and cmds[pos] < 1:
                print "Error: enumeration size must be greater than or equal to 1"
                return False
        if pos%3 == 2:
            if cmds[pos] != ";":
                print "Error: semicolon seperator not found"
                return False
        pos += 1
    return True
    
def parseEnum(enumerator):
    enums = []
    cmds = enumerator.split()
    pos = 0
    lim = len(cmds) 
    while pos < lim:
        if pos%3 == 0 or pos%3 ==1:
            enums.append(int(cmds[pos]))
        pos += 1
    print "Valid intervention enumeration recieved:", enums
    return enums
    
def cleanEnum(enumerator):
    workEnum = enumerator[:]
    oldEnum = workEnum[:]
    limit = len(workEnum)
    if len(workEnum) == 2:
        return workEnum
    used = False
    pos1 = 0
    while pos1 < limit-2:
        pos2 = pos1 +2
        while pos2 < limit:
            if workEnum[pos1] == workEnum[pos2]:
                workEnum[pos1+1] += workEnum[pos2+1]
                del workEnum[pos2:pos2+2]
                limit -= 2
                pos2 -= 2
                used = True
            if workEnum[pos1] > workEnum[pos2]:
                workEnum[pos1],workEnum[pos1+1], workEnum[pos2], workEnum[pos2+1] = workEnum[pos2], workEnum[pos2+1], workEnum[pos1], workEnum[pos1+1]
                used = True
            pos2 += 2
        pos1 += 2
        
    if used:
        print "Enumeration list cleaned up from original:", oldEnum
        print "to new:", workEnum, '\n'
    return workEnum
        
    

def main():
 
    trigger = 1
    subnum = 0
    path = ""
    population = "" 
    pos = 0
    iCode = 0
    
    vacTotal =  0
    avTotal = 0
    socialTotal = 0
    workTotal = 0
    schoolTotal = 0
    
#    vacEnum = False
#    avEnum = False
#    socialEnum = False
#    workEnum = False
#    schoolEnum = False
    
    if len(sys.argv) <= 1:
        print "Missing arguments, defaulting to user mode with filename 'Intervention'\n"
        arg =  "user"
        outName = "Intervention"
    elif sys.argv[1] == "help":
        print """\nArguments: chopper.py {filepath/user} {intervention outfile}
        (Filepath): loads vaccination spread commands from an external script at (filepath)
        User: manual mode, enter each vaccination manually, enter (done) to quit\n"""
        quit()
    elif len(sys.argv) == 2:
        print "Missing 2nd argument, defaulting to filename 'Intervention'"
        arg = sys.argv[1]
        outName = "Intervention"
    elif len(sys.argv) > 3:
        if sys.argv[1] == "gdoc" or sys.argv[1] == "google":
            if len(sys.argv) == 4:
                googData = gDocsImport.getScript(sys.argv[2], 'null', sys.argv[3])
            else:
                googData = gDocsImport.getScript(sys.argv[2], sys.argv[3], sys.argv[4])
                sys.argv[3] = None
            outName = googData['name']
            print "Will write to intervention file '%s'\n" % outName
            script =  googData['script']    
            arg = "gDoc"  
        else:
            print "Ignoring", len(sys.argv) - 3, "excess arguments\n"
    elif len(sys.argv) == 3:
        if sys.argv[1] == "gdoc" or sys.argv[1] == "google":
            googData = gDocsImport.getScript('null', 'null', sys.argv[2])
            outName = googData['name']
            print "Will write to intervention file '%s'\n" % outName
            script =  googData['script']    
            arg = "gDoc"  
        else:
            outName = sys.argv[2]
            arg = sys.argv[1]
        
    if arg != "user" and arg != "gDoc" and (not os.path.isfile(arg)):
        print "Error, cannot open file or directory\n"
        quit()     
        
    done = False
    
    #print os.path.isfile(arg)
    #print arg
    
    #SCRIPT FILE LOADING
    
    
    if arg != "user" and arg != "gDoc":
        scriptfile = open(arg)    
        script = []    
        line = 0
        gotPath = False
        while True:
                testline = scriptfile.readline()
                if len(testline) == 0:
                    break
                if not testline.startswith("#"):
                    if testline.startswith("Directory"):
                        gotPath =  True
                        temp = testline.split()
                        if len(temp) <2:
                            path = ""
                        else:
                            path = testline.split()[1]
                            if (path == "local" or path == "Local"):
                                path = ""
                    else:
                        script.append(testline)
                        line += 1
        if not gotPath:
            path = ""
           
    #USER FILE LOADING       
            
            
    if arg == "user":
        print """\nEnter desired intervention & subpopulation storage directory
Subpops will be created in local subpops folder, though intervention file will point to said directory
Enter 'local' to use current working directory or 'explicit' for a direct link"""
        path=str(raw_input(":"))
        if path == "explicit":
            path = os.getcwd()
        if (path == "local") or (path == "home") or (len(path) == 0):
            path = ""
            
        print "\nEnter desired intervention start number, default 1, useful for appending interventions to pre-existing files"
        number=raw_input(":")
        try:
            trigger = int(number)
            if trigger <= 0:
                print "Entry must be greater than 0, defaulting to 1\n"
                trigger = 1
        except:
            print "No entry/ invalid entry, defaulting to 1\n"
            trigger = 1
    
    outFile = open(outName, 'w')
    outFile.close()
    
    ## GENERATING OUTPUT FILE LOOP
    
    
    while not done:
    
        subnum += 1
        enum = False
    
    # USER CONTROLLED 
    
            
        if arg == "user":
            
            while True:
                print "\nEnter source population filename/ directory"
                population=str(raw_input(":"))
                if len(population) == 0:
                    print "Nothing entered, defaulting to 'SUBPOP'\n"
                    population = "SUBPOP"
                if population == "done":
                    print "Data entry complete, quitting now!\n"
                    done = True
                    break
                if len(population) == 0:
                    population = "EFO6"
                try:
                    with open(population): pass
                    break
                except:
                    print "Error: population file", population, "not found\n"
            
            if done:
                break
            
            while True:   
                print "\nEnter desired intervention trigger day/ 'enum' for enumerated intervention"
                number=raw_input(":")
                if str(number) == 'enum' or str(number) == 'e':
                    enum = True
                    enumList = getEnum()
                    break
                else:
                    try:
                        day = int(number)
                        if day <= 0:
                            print "Error: invalid entry, please enter a positive integer or 'enum'\n"
                        else:
                            break
                    except:
                        print "Error: invalid entry, please enter a positive integer\n"
    
            
            while not enum:
                print "\nEnter desired intervention time to completion"
                number=raw_input(":")
                try:
                    length = int(number)
                    if length <= 0:
                        print "Error: invalid entry, please enter a positive integer\n"
                    else:
                        break
                except:
                    print "Error: invalid entry, please enter a positive integer\n"
        
            while True:
                print """\nEnter intervention type with numerical parameters (ex: Vaccination 10 0.5 .7)
Text will be saved to intervention file exactly as entered with generated
action number and subpopulation directory appended"""
                interv=str(raw_input(":"))
                temp =  interv.split()
                if len(temp) == 0:
                    print "Error: please enter intervention command\n"
                else:   
                    method = temp[0]
                    target = 0
                    if method == "Vaccination":
                        target = 4
                        meth = "v"
                        iCode = 0
                    elif method == "Antiviral":
                        target = 5
                        meth = "av"
                        iCode = 1000
                    elif method == "SocialDistancing":
                        target = 3
                        meth = "sd"
                        iCode= 2000
                    elif method == "WorkClosure":
                        target = 3
                        meth = "cw"
                        iCode = 3000
                    elif method == "SchoolClosure":
                        target = 3
                        meth =  "cs"
                        iCode = 4000
                    if (len(temp) != target):
                        print "Error:",  len(temp), "parameters found,", target, "expected for intervention type", method, "\n"
                    elif target == 0:
                        print "Error:", method, "method not recognized\n"
                    else:
                        if not temp[1].isdigit():
                            print "Error: second value must be an integer"
                        else:
                            pos2 = 1
                            allGood = True
                            while pos2 < target:
                                if not chopper.isInt(temp[pos2]):
                                    allGood = False
                                pos2 += 1
                            if not allGood:
                                print temp
                                print "Error: non-numerical parameters found\n"
                            else:
                                break  
                                        
    #  SCRIPT CONTROLLED                                                                          
                                                                                                                    
                                                                                                                                                                                                
        else:
            if pos == len(script):
                done = True
                break
                
            cmd = script[pos]
            items = cmd.split()
            population =  items[0]
            try:
                with open(population): pass
            except:
                print "Error: population file", population, "not found\n"
                quit()
            
            if str(items[1]) == 'enum':
                enum = True
                cmd = cmd.replace("enum","null null")
                items = cmd.split()
                pos += 1
                enumList = script[pos].replace(";"," ; ")
                if checkEnum(enumList):
                    enumList = parseEnum(enumList)
                else:
                    print "Error: misformatted enumeration list", enumList
                    quit()
            
            if not enum:
                try:
                    day = int(items[1])
                    if day <= 0:
                        print "Error, day must be an integer greater than zero\n"
                        quit()
                except:
                    print "Error, day must be an integer greater than zero\n"
                    quit()
                try:
                    length = int(items[2])
                    if length <= 0:
                        print "Error, length must be an integer greater than zero\n"
                        quit()
                except:
                    print "Error, length must be an integer greater than zero\n"
                    quit()
            
            temp = cmd.split()
            print "Generating interventions with parameters:",cmd
            method = temp[3]
            if method == "Vaccination":
                target = 7
                meth = "v"
                iCode = 0
            elif method == "Antiviral":
                target = 8
                meth = "av"
                iCode = 1000
            elif method == "SocialDistancing":
                target = 6
                meth = "sd"
                iCode = 2000
            elif method == "WorkClosure":
                target = 6
                meth = "cw"
                iCode = 3000
            elif method == "SchoolClosure":
                target = 6
                meth = "cs"
                iCode = 4000
            else:
                print "Error:", method, "method not recognized\n"
                quit()
            if (len(temp) != target):
                print "Error:",  len(temp), "parameters found,", target, "expected for intervention type", method, "\n"
                quit()
            
            
            interv = " ".join(temp[3:target])
            pos += 1
    
        suffix = str(subnum) + meth

        if enum:
            enumList = cleanEnum(enumList)
            holder = chopper.main(population,'e'," ".join(map(str, enumList)),suffix)
            returnSize = holder['count']
            enumList = holder['enum']
            length = chopper.getEnumSize(enumList)
        else:
            holder = chopper.main(population,'b',str(length),suffix)
            returnSize = holder['count']
            
    
        if meth == "v":
            vacTotal += returnSize
        elif meth == "av":
            avTotal += returnSize
        elif meth == "sd":
            socialTotal += returnSize
        elif meth == "cw":
            workTotal += returnSize
        elif meth == "cs":
            schoolTotal += returnSize
        
        
    # WRITING INTERVENTION FILE 
        
        if enum:
            pos2 = 0
            outFile = open(outName, 'a+b')
            while pos2 < len(enumList):
                subPopName = population + str(pos2/2) + suffix
                triggerOut = "Trigger " + str(trigger+iCode) + " Day " + str(enumList[pos2]) + "\n" 
                intervOut = "Action " + str(trigger+iCode) + " " + interv + " " + path + "/subpops/" + subPopName + "\n"
                print triggerOut, intervOut.replace('\n','')
                outFile.write(triggerOut)
                outFile.write(intervOut)
                trigger += 1
                pos2 += 2
            outFile.close()
            print
            
        else:
            pos2 = 0
            outFile = open(outName, 'a+b')
            while pos2 < length:
                subPopName = population + str(pos2) + suffix
                triggerOut = "Trigger " + str(trigger+iCode) + " Day " + str(day+pos2) + "\n" 
                intervOut = "Action " + str(trigger+iCode) + " " + interv + " " + path + "/subpops/" + subPopName + "\n"
                print triggerOut, intervOut.replace('\n','')
                outFile.write(triggerOut)
                outFile.write(intervOut)
                trigger += 1
                pos2 += 1
            outFile.close()
            print

    # APPENDING INTERVENTION TOTALS        
                         
    outFile = open(outName, 'a+b')
    outFile.write("\n# Pre Compliance Intervention Totals- calculated per output, does not account for over-application to a given set of IDs. Please apply only one of each type per sub pop, using enumerated interventions for complex interventions.")
    outFile.write("\n# Vaccination: " + str(vacTotal))
    outFile.write("\n# Antiviral: " + str(avTotal))
    outFile.write("\n# Social Distancing: " + str(socialTotal))
    outFile.write("\n# Close Work: " + str(workTotal))
    outFile.write("\n# Close Schools: " + str(schoolTotal))
    outFile.close()
    print """Pre Compliance Intervention Totals- calculated per output,
does not account for over-application to a given set of IDs. 
Please apply only one of each type per sub pop, using enumerated 
interventions for complex interventions."""
    print "\nVaccination: " + str(vacTotal)
    print "Antiviral: " + str(avTotal)
    print "Social Distancing: " + str(socialTotal)
    print "Close Work: " + str(workTotal)
    print "Close Schools:" + str(schoolTotal)
    
    
main()
print "Intervention scripting succesfully completed, exiting now.\n"
quit