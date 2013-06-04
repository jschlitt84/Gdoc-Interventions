import gdata.docs
import gdata.docs.service
import gdata.spreadsheet.service
import sys 
import os

import requests

isPrivate = True

def spreadConnect(userName, __password, fileName):
    client = gdata.spreadsheet.service.SpreadsheetsService()
    client.email = userName
    client.password = __password
    __password = "*"*len(__password)
    client.ssl = False
    client.source = fileName
    try:
        client.ProgrammaticLogin()
        print "Connected to Google Spreadsheet via username %s & password %s" % (userName,__password)
    except:
        print "Error, Google Spreadhseet Login Failed, username %s & password %s" % (userName,__password)
        client.password = None
        quit()
    return client
    
def googConnect(userName, __password, fileName):
    client = gdata.docs.service.DocsService()
    client.email = userName
    client.password = __password
    __password = "*"*len(__password)
#    client.ssl = False
    client.source = fileName
    try:
        client.ProgrammaticLogin()
        print "Connected to Google Docs via username %s & password %s" % (userName,__password)
    except:
        print "Error, Google Docs Login Failed, username %s & password %s" % (userName,__password)
        client.password = None
        quit()
    return client

def getFile(userName, __password, fileName):
    gd_client = googConnect(userName, __password, fileName)
    spreadsheets_client = spreadConnect(userName, __password, fileName)
    __password = None
    
    q = gdata.spreadsheet.service.DocumentQuery()
    q['title'] = fileName
    q['title-exact'] = 'true'
    feed = spreadsheets_client.GetSpreadsheetsFeed(query=q)
    
    spreadsheet_id = feed.entry[0].id.text.rsplit('/',1)[1]
    print "Accessing Spreadsheet ID:", spreadsheet_id
    feed = spreadsheets_client.GetWorksheetsFeed(spreadsheet_id)
    
    tempFile = "googtemp.csv"
    uri = 'http://docs.google.com/feeds/documents/private/full/%s' % spreadsheet_id

    entry = gd_client.GetDocumentListEntry(uri)
    docs_auth_token = gd_client.GetClientLoginToken()
    gd_client.SetClientLoginToken(spreadsheets_client.GetClientLoginToken())
    gd_client.Export(entry, tempFile)
    gd_client.SetClientLoginToken(docs_auth_token)
    
def getPublicFile(userName, fileName):
    fileName = fileName.replace('#gid=0','&output=csv')
    if not '&output=csv' in fileName:
        fileName += '&output=csv'
    print "\nLoading public file", fileName
    
    response = requests.get(fileName)
    assert response.status_code == 200, 'Wrong status code'
    data = response.content.split('\n')
    return data

def getPos (start, stop, script):
    length = len(script)
    pos = 0
    startPos = 0
    stopPos = len(script)
    if isinstance(start, str) and not isinstance(stop, str):
        foundStart = False
        foundStop = True
        stopPos = int(stop)
        while pos < length:
            if start in script[pos]:
                startPos = pos + 1
                foundStart = True
                break
            pos += 1
    if not isinstance(start, str) and isinstance(stop, str):
        foundStart = True
        foundStop = False
        startPos = int(start)
        while pos < length:
            if stop in script[pos]:
                stopPos = pos
                foundStop = True
                break
            pos += 1
    if isinstance(start, str) and isinstance(stop, str):
        foundStart = False
        foundStop = False
        while pos < length:
            if start in script[pos]:
                startPos = pos + 1
                foundStart = True
            if stop in script[pos]:
                stopPos = pos
                foundStop = True
            pos += 1
    if not foundStart:
        print "Error, start string", start, "not found, defaulting to pos 0"
        startPos = 1
    if not foundStop:
        print "Error, stop string", stop, "not found, defaulting to pos", length
        stopPos = length
    return {'start':startPos,'stop':stopPos}
    
def loadNClean(isPrivate,publicData, start, end, cleanType):
    if isPrivate:
        tempFile = open("googtemp.csv")
        script = tempFile.readlines()
        tempFile.close()
        os.remove("googtemp.csv")
    else:
        script = publicData
                    
    if isinstance(start, str) or isinstance(end, str):
        holder = getPos(start, end, script)
        start = int(holder['start'])
        end = int(holder['stop'])
        hasEnd = True
    try:
        if int(end) >= 1 and int(end) > int(start):
            hasEnd= True
        else:
            hasEnd = False
    except:
        start = 0
        hasEnd = False        
                            
    length = len(script)
    
    if length < start:
        print "Error, no values found"
        quit
            
    script = script[start:length+1]
    length -= start
    end -= start
    pos = 0
    print "Google content loaded, parsing to internal format"
    
    if cleanType == "single line":
        hasEnd = True
        end = 1
    
    if hasEnd:
        if end < length:
            del script[end:length+1]
            length = end    
    while pos < length:
        if "#" in script[pos] or len(script[pos].replace(",",''))<1:
            del script[pos]
            pos -= 1
            length -= 1
        if cleanType == "intervention script":
            if "enum" in script[pos]:
                script[pos] = script[pos].replace(',',' ')
                script[pos] = script[pos].replace('enum enum','enum')
                script[pos] = script[pos].replace('enum 0','enum')
                pos += 1
                while "#" in script[pos] or len(script[pos].replace(",",''))<1:
                    del script[pos]
                    pos -= 1
                    length -= 1
                
                
                script[pos] = script[pos].replace('","',' ; ')
                script[pos] = script[pos].replace('"','')
                script[pos] = script[pos].replace(':',' ')
                script[pos] = script[pos].replace('-',' ') 
                
    
            script[pos] = script[pos].replace(',',' ')
            script[pos] = script[pos].replace('  ',' ')
        pos += 1
    
    pos = 0
    print
    while pos < len(script):
        while " \n" in script[pos] or "  " in script[pos]:
            script[pos] = script[pos].replace(' \n','\n')
            script[pos] = script[pos].replace('  ',' ')
        print script[pos].replace('\n','')
        pos += 1
    print
    
    if cleanType == "default":
        listScript = []
        pos = 0
        while pos < len(script):
            listScript.append(script[pos].split(","))
            pos += 1
        return listScript
    
    elif cleanType == "single line":
        return script[0].split(",")
            
    else:
        return script
  
    
    
def getLine(userName, __password, fileName, line):
    if __password == "null" and "https://docs.google.com" in fileName:
        
        publicData = getPublicFile(userName, fileName)
        isPrivate = False
        
    else:
        getFile(userName, __password, fileName)
        isPrivate = True
        publicData = []
           
    __password = None
    
    return loadNClean(isPrivate, publicData, line, 0, "single line")      
    
def getScript(userName, __password, fileName, start, end, loadType):
    if __password == "null" and "https://docs.google.com" in fileName:
        
        publicData = getPublicFile(userName, fileName)
        isPrivate = False
        
    else:
        getFile(userName, __password, fileName)
        isPrivate = True
        publicData = []
        
    __password = None

    return loadNClean(isPrivate, publicData, start, end, loadType)            
    
    
if __name__ == '__main__':
    getScript (sys.argv[1], sys.argv[2], sys.argv[3])
    sys.argv[3]= None
