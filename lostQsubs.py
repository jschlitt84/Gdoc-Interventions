import sys, os

file1 = open(sys.argv[1])
file2 = open(sys.argv[2])
fileOut = open(sys.argv[3],'a+b')
list1 = file1.readlines(); file1.close()
list2 = file2.readlines(); file2.close()
dir = list1[0].replace('qsub ','')[0:list1[0].index('/'.split(list2[0])[0])]

print "Dir:", dir

list2 =  list2[0:5]

for pos in range(len(list2)):
  line = list2[pos]
  list2[pos] = 'qsub ' + dir + ' '.split(line)[0] + '/qsub\n'
  print list2[pos]
  
for line in list2:
  if line not in list1:
    print "Missing:", line
    fileOut.write(line)
    
fileOut.close()
