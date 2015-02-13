import sys

try:
  mode = sys.argv[4]
except:
  mode = 'a+b'

file1 = open(sys.argv[1])
file2 = open(sys.argv[2])
fileOut = open(sys.argv[3],mode)
list1 = file1.readlines(); file1.close()
list2 = file2.readlines()[1:]; file2.close()
dir = list1[0][0:list1[0].index(list2[0].split('/')[0])].replace('qsub ','')

print "Mode", mode, "Dir:", dir

for pos in range(len(list2)):
  line = list2[pos]
  list2[pos] = 'qsub ' + dir + line.split(' ')[0] + '/qsub\n'
  print list2[pos][0:-1]
  
for line in list1:
  if line not in list2:
    print "Missing:", line[0:-1]
    fileOut.write(line)
  else:
    print "Found:", line[0:-1]
    
fileOut.close()
