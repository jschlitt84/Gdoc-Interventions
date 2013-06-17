import subprocess
import time
import sys
import select

increment = 5
submitDelay = 1
inputDelay = 10

print "Loading qsubs..."
tempFile = open("qsublist")
script = tempFile.readlines()
tempFile.close()

length = len(script)

print "%s qsubs found, running %s per user prompt with a %s second input delay and a %s second submission delay" % (length,increment,inputDelay,submitDelay) 

pos1 = 0
while pos1 < length:    

    print script[pos1]
#    subprocess.call(script[pos1])    
    
    print "Submitted Qsub", pos1, "out of", length
    time.sleep(submitDelay)
    
    if pos1 > 0 and pos1%increment == 0:
        print "Interval Reached, please enter 'quit' in next", inputDelay, "seconds to quit"
        i, o, e = select.select([sys.stdin], [], [], inputDelay)
        if (i):
            if sys.stdin.readline().strip().lower() == 'quit':
                print "Quit command recieved, exiting now"
                quit()
            else:
                print "No input recieved, continuing process"
    pos1 += 1
        
print "Process complete, quitting now"
quit()