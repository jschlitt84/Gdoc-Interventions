import sys
from glob import glob




def prepFiles(wildcards,lineIn,lineOut):
   files = glob(wildcards)
   print "Prepping file: ",
   for ref in files:
      print '%s, ' % ref,
      readNWrite(ref,lineIn,lineOut)
   print complete


def changer(line,lineIn,lineOut):
   if lineIn in line:
      line = lineOut
   return line


def readNWrite(ref,lineIn,lineOut = 'null',x='x'):
   fileIn = open(ref)
   contents = fileIn.readLines()
   fileIn.close()

   if lineOut == 'null':
      lineOut = lineIn.split('=')[0]+'= %s.txt\n' % x
   newLine = lineOut.replace(x,ref.split('/')[-1])

   contents = [changer(line,lineIn,lineOut) for line in contents]
 
   fileOut = open(ref,'w')
   fileOut.write('\n'.join(contents))
   fileOut.close()


def main():
   wildCards =  sys.argv[1]
   try:
       lineIn =  sys.argv[2]
   except:
       lineIn = 'null'
   try:
       lineOut = sys.argv[3]
   except:
       lineOut = 'null'
   prepFiles(wildcards,lineIn,lineOut)


main()
