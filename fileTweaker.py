import sys, os

directory = sys.argv[1]
fileIn = open(directory)
qsublist = fileIn.readlines()
cwd = os.getcwd()

def runFix(qsublist, commands, words, fix):

    print "*** RUNNING UNIX FIX", "'" + fix + "'"
    for line in qsublist:
        actualDir = line.replace('qsub ','').replace('qsub\n','')
        print "\nchecking directory", actualDir
        useCommands = True
        for word in words:
            if word not in actualDir:
                useCommands = False
                break
        if useCommands:
            os.chdir(actualDir)
            for command in commands:
                print "\tRunning Command:", command
                os.system(command)
        else:
            print "\tNo commands run"
    print "\tfix complete"
    os.chdir(cwd)

# Loop 1 Intervention Tweaks
commands = [
    "sed -e 's/#.*$//' -e '/^$/d' -e 's/  //' Intervention > temp",
    "mv temp Intervention"]
words = [
    "nowhiteINT"]
runFix(qsublist, commands, words, "No WhiteSpace Interventions")

# Loop 2 AV/Diag Tweaks
commands = [
    "sed -e 's/#.*$//' -e '/^$/d' -e 's/  //' Antiviral > temp",
    "mv temp Antiviral",
    "sed -e 's/#.*$//' -e '/^$/d' -e 's/  //' Diagnosis > temp",
    "mv temp Diagnosis"]
words = [
    "nowhiteAV"]
runFix(qsublist, commands, words, "No WhiteSpace AV/Diag")
    
# Loop 3 Config Tweaks
commands = [
    "sed -e 's/#.*$//' -e '/^$/d' -e 's/  / /' config > temp",
    "mv temp config"]
words = [
    "nowhiteCFG"]
runFix(qsublist, commands, words, "No WhiteSpace Congig")
    
# Loop 4.1 Config Tweaks
commands = [
    "sed -e '/^DiagnosisFile =/ d' -e '/^AntiviralFile =/ d' config > temp",
    "mv temp config",
    "rm Diagnosis",
    "rm Antiviral"]
words = [
    "noAV"]
runFix(qsublist, commands, words, "No AV/Diag File or References")

# Loop 4.2 Config Tweaks
commands = [
    "echo > Antiviral",
    "echo > Diagnosis"]
words = [
    "emptyAV"]
runFix(qsublist, commands, words, "Empty AV/Diag Files")

print "****Operations complete!****"
quit()

