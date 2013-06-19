import subprocess
import time
import sys
import select

increment = 10
submitDelay = 3
inputDelay = 10
stopAt = 10

print "Loading qsubs..."
tempFile = open("qsublist")
script = tempFile.readlines()
tempFile.close()

length = len(script)

print "%s qsubs found, running %s per user prompt with a %s second input delay and a %s second submission delay" % (length,increment,inputDelay,submitDelay) 

pos = 0
while pos < length:    
    
    if pos == stopAt:
        quit()
        
    print script[pos]
    subprocess.call(script[pos])    
    
    print "Submitted Qsub", pos, "out of", length-1
    time.sleep(submitDelay)
    
    if pos > 0 and pos%increment == 0:
        print "Interval Reached, please enter 'quit' in next", inputDelay, "seconds to quit"
        i, o, e = select.select([sys.stdin], [], [], inputDelay)
        if (i):
            if sys.stdin.readline().strip().lower() == 'quit':
                print "Quit command recieved, exiting now"
                quit()
            else:
                print "No input recieved, continuing process"
    pos += 1
        
print "Process complete, quitting now"
quit()