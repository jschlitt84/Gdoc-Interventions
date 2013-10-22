import sys, os

directory = sys.argv[1]
fileIn = directory.open()
qsublist = fileIn.readlines
cwd = os.getcwd()

def runFix(qsublist, commands, words, fix):
    
    
    print "*** RUNNING FIX", "'" + fix + "'"
    for line in qsublist:
        actualDir = line.replace('qsub ','').replace('qsub\n','')
        print "\nchecking directory", actualDir
        useCommands = True
        for word in words:
            if word not in actualDir:
                useCommands = False
                break
        if useCommands:
            for command in commands:
                print "\tRunning Command:", command
                os.system("cd " + actualDir)
                os.system(command)
        else:
            print "\tNo commands run"
    print "\tfix complete"
    os.system("cd " + cwd)

commands = [
    "sed -e 's/#.*$//' -e '/^$/d' -e 's/  //' Intervention > temp",
    "mv temp Intervention"]
words = [
    "nowhiteINT"]
runFix(qsublist, commands, words, "No WhiteSpace Interventions")

commands = [
    "sed -e 's/#.*$//' -e '/^$/d' -e 's/  //' Antiviral > temp",
    "mv temp Antiviral,
    "sed -e 's/#.*$//' -e '/^$/d' -e 's/  //' Diagnosis > temp",
    "mv temp Diagnosis"]
words = [
    "nowhiteAV"]

