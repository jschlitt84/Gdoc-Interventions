import gdata.docs
import gdata.docs.service
import gdata.spreadsheet.service
import sys 
import os

def spreadConnect(userName, __password, fileName):
    client = gdata.spreadsheet.service.SpreadsheetsService()
    client.email = userName
    client.password = __password
    client.ssl = False
    client.source = fileName
    try:
        client.ProgrammaticLogin()
        print "Connected to Google Spreadsheet via username %s & password %s" % (userName,"*"*len(__password))
    except:
        print "Error, Google Spreadhseet Login Failed, username %s & password %s" % (userName,"*"*len(__password))
        quit()
    return client
    
def googConnect(userName, __password, fileName):
    client = gdata.docs.service.DocsService()
    client.email = userName
    client.password = __password
#    client.ssl = False
    client.source = fileName
    try:
        client.ProgrammaticLogin()
        print "Connected to Google Docs via username %s & password %s" % (userName,"*"*len(__password))
    except:
        print "Error, Google Docs Login Failed, username %s & password %s" % (userName,"*"*len(__password))
        quit()
    return client

def getFile(userName, __password, fileName):
    gd_client = googConnect(userName, __password, fileName)
    spreadsheets_client = spreadConnect(userName, __password, fileName)
    
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

def loadNClean():
    tempFile = open("googtemp.csv")
    script = tempFile.readlines()
    tempFile.close()
    os.remove("googtemp.csv")
    length = len(script)
    if length < 4:
        print "Error, no interventions found"
        quit
    name = script[1]
    if len(name) == 0:
        print "No name stored, defaulting to 'Intervention'"
        name = "Intervention"
    else:
        name = name.replace(',','')
    script = script[3:length+1]
    length -= 3
    pos = 0
    print "Google temp file loaded, parsing to internal format"
    while pos < length:
        if "enum" in script[pos]:
            
            script[pos] = script[pos].replace(',',' ')
            script[pos] = script[pos].replace('enum enum','enum')
            script[pos] = script[pos].replace('enum 0','enum')
            pos += 1
            script[pos] = script[pos].replace('","',' ; ')
            script[pos] = script[pos].replace('"','') 

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
    
    name = name.replace('\n','')    
    outPut = {'name':name,'script':script}
    return outPut
    

def getScript(userName, __password, fileName):   
    getFile(userName, __password, fileName)
    __password = None
    return loadNClean()            
    
    
if __name__ == '__main__':
    getScript (sys.argv[1], sys.argv[2], sys.argv[3])
    sys.argv[3]= None
