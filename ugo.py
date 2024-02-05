import os
import requests
import json
import smtplib, ssl
import time
import re
from datetime import datetime
import sys
import inspect


# Reference for mattermost webhooks:
# https://mattermost.com/blog/mattermost-integrations-incoming-webhooks/
# https://developers.mattermost.com/integrate/webhooks/incoming/

# Implemented tags:
# ITQNKX --> quality Not good for any kind of run
# ITQBAD --> quality BAD for any kind of run
# ITQW01 --> :warning: present in QC message, e.g. when run number does not match
# ITRPHY --> New physics run

INFO =    ' INFO'
WARNING = ' WARN'
ERROR =   'ERROR'
FATAL =   'FATAL'
DEBUG =   'DEBUG'

VERSION = 'v1.0.0'

target_channel = 'ugo-qc'

#_________________________________________________________________________________
def LOG(severity, *message):
    filename = str(inspect.stack()[1][1])
    filename = filename.split('/')[-1]
    funcname = str(inspect.stack()[1][3])

    tt = datetime.now()
    tstamp = "%s-%s-%s-%s:%s:%s"%(str(tt.year)[-2:],str(tt.month).zfill(2),str(tt.day).zfill(2),str(tt.hour).zfill(2),str(tt.minute).zfill(2),str(tt.second).zfill(2))
    print("[%s][%s][%s]"%(tstamp,severity,filename+':'+funcname),*message)

    
#______________________ Default, not formatted. Use only for emergencies___________
def SendAnUgo(message, username='Ugo', channel=target_channel):

    if username != "Ugo":
        LOG(INFO,"I will not send anything with the name",username)
        return
    # https://mattermost.com/blog/mattermost-integrations-incoming-webhooks/
    # https://developers.mattermost.com/integrate/webhooks/incoming/
    logmessage = """I'm sending an UGO
%s
    """%(message)
    LOG(INFO,logmessage)
    headers = {}
    values = {"channel": channel, "username": username, "text": message}
    values = str(values).replace("'","|").replace('"',"'").replace("|",'"')
    print('AAAA',str(values))
    response = requests.post('https://mattermost.web.cern.ch/hooks/kk9cwkqoe7d7fqt3rbpe91uwwy',headers=headers,data=str(values))
    LOG(INFO,response)  

#_________________________________________________________________________________
def SendAnUgoNewRun(run, rtype, o2start, trgstart, ndet, nepns, ongoing, message, username='Ugo', channel=target_channel):

    web_url = 'https://mattermost.web.cern.ch/hooks/kk9cwkqoe7d7fqt3rbpe91uwwy'

    tags = []

    if 'PHYSICS' in rtype:
        tags.append('ITRPHY')

    pretext = 'tags:'
    for t in tags:
        pretext += ' '+t

    if len(tags) == 0:
        pretext = ''

    def formattedstart(o2, trg):
        if o2 == 'none':
            return 'not found'
        elif trg == 'none':
            return str(o2)[:10]+'\n*O2*: '+str(o2)[11:]
        else:
            return str(o2)[:10]+'\n*O2*: '+str(o2)[11:]+'\n*Trg*: '+str(trg)[11:]
    
    payload = {
        'channel': channel,
        'username': username,
        'text': pretext,
        'attachments': [
            {
                'title': 'New run '+str(run),
                'color':  '#384E6B',
                'fields': [
                    {
                        'short': True,
                        'title': 'Start',
                        'value': formattedstart(o2start, trgstart)
                    },
                    {
                        'short': True,
                        'title': 'Is ongoing',
                        'value': 'Yes :runner:' if ongoing else 'No'
                    },
                    {
                        'short': True,
                        'title': 'Detectors',
                        'value': str(ndet)
                    },
                    {
                        'short': True,
                        'title': 'EPNs',
                        'value': str(nepns)
                    },
                    {
                        'short': False,
                        'title': 'Type',
                        'value': rtype
                    },
                    {
                        'short': False,
                        'title': '---',
                        'value': "\n\n"+message
                    }            
                ]
            }
        ]
    }

    if username != "Ugo":
        LOG(INFO,"I will not send anything with the name",username)
        return
    # https://mattermost.com/blog/mattermost-integrations-incoming-webhooks/
    # https://developers.mattermost.com/integrate/webhooks/incoming/
    logmessage = """I'm sending an UGO as %s on channel %s:
run: %s
type: %s
o2start: %s
trgstart: %s
ongoing: %s
message: %s
    """%(username,channel,str(run),str(rtype),str(o2start),str(trgstart),str(ongoing),str(message))
    LOG(INFO,logmessage)

    response = requests.post(web_url, json=payload, headers={'Content-Type': 'application/json'})
    LOG(INFO,response)  


#_________________________________________________________________________________
def SendAnUgoQC(run, quality, details, timesmp, message, username='Ugo', channel=target_channel):

    web_url = 'https://mattermost.web.cern.ch/hooks/kk9cwkqoe7d7fqt3rbpe91uwwy'
    boxcolor = '#384E6B'
    if quality == 'GOOD':
        boxcolor = '#3ED138'
    elif quality == 'MEDIUM':
        boxcolor = '#CF5E0E'
    elif quality != 'NONE':
        boxcolor = '#CF0E0E'
    
    tags = []

    if quality != 'GOOD':
        tags.append('ITQNKX')
    if quality == 'BAD':
        tags.append('ITQBAD')
    if ':warning:' in message:
        tags.append('ITQW01')

    pretext = 'tags:'
    for t in tags:
        pretext += ' '+t

    if len(tags) == 0:
        pretext = ''
    
    payload = {
        'channel': channel,
        'username': username,
        'text': pretext,
        'attachments': [
            {
                'title': 'QC found for run '+str(run),
                'color':  boxcolor,
                'fields': [
                    {
                        'short': False,
                        'title': 'Quality: '+str(quality),
                        'value': details
                    },
                    {
                        'short': False,
                        'title': 'Uploaded at',
                        'value': str(timesmp)
                    },
                    {
                        'short': False,
                        'title': '---',
                        'value': "\n\n"+message+"\n[ali-qcg.cern.ch](https://ali-qcg.cern.ch/?page=layoutShow&layoutId=62f641c5175bbd6a6629bf38)"
                    }            
                ]
            }
        ]
    }

    if username != "Ugo":
        LOG(INFO,"I will not send anything with the name",username)
        return
    logmessage = """I'm sending an UGO as %s on channel %s:
run: %s
quality: %s
uploaded at: %s
message: %s
    """%(username,channel,str(run),str(quality),str(timesmp),str(message))
    LOG(INFO,logmessage)
        
    response = requests.post(web_url, json=payload, headers={'Content-Type': 'application/json'})
    LOG(INFO,response)  
      

#________communication between one cycle and the other happens through these 3 files________________________________
def ReadLastRun():
    f = open("lastrun.txt","r")
    r = int(f.read())
    f.close()
    LOG(INFO,"Read last run",r)
    return r

def WriteLastRun(n):
    f = open("lastrun.txt","w")
    f.write(str(n))
    LOG(INFO,"Written last run",str(n))
    f.close()

def ReadQCNeeded(): # 0 (false) or 1 (true)
    f = open("qcneeded.txt","r")
    r = bool(int(f.read()))
    f.close()
    LOG(INFO,"Read QC needed",r)
    return r

def WriteQCNeeded(n):
    f = open("qcneeded.txt","w")
    f.write(str(int(n)))
    LOG(INFO,"Written QC needed:",str(int(n)))
    f.close()

def ReadLastQuality():
    f = open("lastquality.txt","r")
    r = str(f.read())
    f.close()
    LOG(INFO,"Read last quality",r)
    return r

def WriteLastQuality(n):
    f = open("lastquality.txt","w")
    f.write(str(n))
    LOG(INFO,"Written last quality",str(n))
    f.close()

#_________________________________________________________________________________
def tconvert(timestamp):
    if timestamp < 0:
        return "none"
    dt = datetime.fromtimestamp(timestamp)
    return "%s-%s-%s %s:%s:%s"%(str(dt.year),str(dt.month).zfill(2),str(dt.day).zfill(2),str(dt.hour).zfill(2),str(dt.minute).zfill(2),str(dt.second).zfill(2))

#_________________________________________________________________________________
def MakeObjectReport(outfile="objectreport.txt"):
    os.system('root getObject2.C\\(\\"'+outfile+'\\"\\) 1>>getobject_stdout.out')
    print()
    LOG(INFO,"Gloab QC dumped on",outfile)

#_________________________________________________________________________________
def ParseObjectReport(infile="objectreport.txt"):

    LOG(INFO,"Parsing",infile)
    RunNumber = 999999999
    GloQual = ''

    log = open(infile,'r')
    line = '0'
    detailsstart = False
    detailstring = '```\nITS DETAILS'
    while line:
        line = log.readline().replace('\n','')
        if 'Object creation time' in line:
            creation_utc = re.findall('[0-9]+',line)[0]
        if 'RunNumber:' in line:
            RunNumber = re.search('RunNumber: [0-9]{6}',line).group(0)[-6:]
        if 'ITS Quality' in line:
            qstring = re.search('ITS Quality : (Good|Bad|Medium)',line).group(0)
            if 'Good' in qstring:
                GloQual = 'GOOD'
            elif 'Bad' in qstring:
                GloQual = 'BAD'
            elif 'Medium' in qstring:
                GloQual = 'MEDIUM'
        if 'ITS DETAILS' in line:
            detailsstart = True
        if detailsstart:
            detl = re.findall('\{.*\}',line)
            if len(detl)>0:
                detail = detl[0].replace('{','').replace('}','').replace('#rightarrow','   ')
                detailstring += '\n'+detail
    detailstring += '\n```'

    LOG(INFO,"Run:",RunNumber," Created",creation_utc," GloQual",GloQual)
    return RunNumber,creation_utc,GloQual,detailstring
        
#_________________________________________________________________________________
def QueryLogbook():  # return last_run_number, False
    LOG(INFO,"Querying last 50 bookkeeping entries")
    req = requests.get('https://ali-bookkeeping.cern.ch/api/runs?page[limit]=50',verify=False)
    data = json.loads(req.text)['data']
    with open('logquery.json','w') as f:
        json.dump(data,f,indent=2)
        LOG(INFO,"json dumped on logquery.json")
    for run in data:
        ndet = run['nDetectors']
        if 'ITS' in run['detectors']:
            runnumber = int(run['runNumber'])
            IsSynthetic = run['runType']['name'] == 'SYNTHETIC'
            IsCalibration = run['definition'] == 'CALIBRATION'
            RunType = 'PHYSICS/COSMICS'
            if IsSynthetic:
                RunType = 'SYNTHETIC'
            if IsCalibration:
                RunType = 'CALIBRATION'
            try:
                o2end = int(run['timeO2End'])
                isongoing = False
            except:
                isongoing = True
            nEpns = 0
            if bool(run['epn']):
                nEpns = int(run['nEpns'])
            try:
                O2startime = int(run['timeO2Start'])
            except:
                O2startime = -1
            try:
                Trgstartime = int(run['timeTrgStart'])
            except:
                Trgstartime = -1
            LOG(INFO,"Returning",run['runNumber'],", O2start",O2startime," Trgstart ",Trgstartime," type",RunType," ndet",ndet," nEpns",nEpns," ongoing",isongoing)
            return int(run['runNumber']),O2startime,Trgstartime,RunType,ndet,nEpns,isongoing

            
    LOG(ERROR,"Run not found, returning dummy values")
    return -1,-1,-1,"unknown",-1,-1,False
        

    
#________________________ MAIN ______________________-

if __name__ == "__main__":


    #______ opening __________-
    if len(sys.argv) > 1:
        #exit()
        if str(sys.argv[1]) == "start":
            SendAnUgo("#### You go! :black_cat_dj:\nNew instance created - %s\nReading bookkeeping every: 5 minutes.\nChecking QC every: 5 minutes.\nThe first cycle may be run on an old run, then I will wait for new runs."%(VERSION))
            WriteLastRun(189076289293640)
            WriteLastQuality("NONE")
            WriteQCNeeded(True)
            exit()
    
    
    lastrunlogbook,timestart,trgstart,runtype,ndet,nepns,isongoing = QueryLogbook()
    if (runtype != "SYNTHETIC" and int(trgstart)<0) or int(timestart)<0:
        LOG(INFO,'Probably querying logbook while run was starting? Waiting 1 minute and doing again')
        time.sleep(60)
        lastrunlogbook,timestart,trgstart,runtype,ndet,nepns,isongoing = QueryLogbook()
    lastruncache = ReadLastRun()
    qcneeded = bool(ReadQCNeeded())
    lastquality = ReadLastQuality()
    
    
    
    if lastrunlogbook != lastruncache:

        LOG(INFO,"Entering the new run condition for run",lastrunlogbook,"started on ",timestart,"/",trgstart)
    
        runnumber = lastrunlogbook

        if isongoing:
            UgoText = "The run is ongoing. Waiting 5 minutes after O2 start, then looking into QC."
        else:
            UgoText = "The run is NOT ongoing. Looking into QC."
        if runtype == "CALIBRATION":
            UgoText = "I will not check QC for calibration runs"
        if nepns == 0:
            UgoText = "No EPN workflows for this run. QC will not be checked."
            
    
       
        SendAnUgoNewRun(runnumber, str(runtype), tconvert(timestart/1000), tconvert(trgstart/1000), ndet, nepns, isongoing, UgoText)
       
    
        secondsaftersor = (datetime.now()-datetime.fromtimestamp(timestart/1000)).total_seconds()
    
        waiting_time = max(1, 5*60 - secondsaftersor)
        if not isongoing or runtype == "CALIBRATION":
            waiting_time = 1
        
    
        LOG(INFO,"Waiting",waiting_time,"seconds")
        time.sleep(waiting_time)

        if runtype == "CALIBRATION" or nepns == 0:
            LOG(INFO,"Skipping QC check for run type",runtype," nEPNs=",nepns)

            WriteLastRun(runnumber)
            WriteLastQuality("NONE")
            WriteQCNeeded(False)

        else:
    
            #___ First QC check____
            LOG(INFO,'QUERYING THE QCDB')
            MakeObjectReport()
            LOG(INFO,'OBJECT REPORT CREATED')
            time.sleep(1)
            RunNumberQC,Creation_utc,GloQual,DetailsQC = ParseObjectReport()
            CreatedOn = tconvert(int(Creation_utc)/1000)
           
            RunNotMatching = False

            DetailsText = DetailsQC
    
            NotificationText = ""
            if str(RunNumberQC) != str(runnumber):
                NotificationText += "\n:warning: The run number does not match!\nMaybe the run is too short?"
                RunNotMatching = True
            if GloQual == "GOOD":
                NotificationText += "\nYou will be notified if the quality changes."
                DetailsText = ""
            elif not isongoing:
                NotificationText += "\nMy job is done. Waiting for new run..."
            else:
                NotificationText += "\nI will keep checking every 5 minutes unless a new run arrives, up to 10 minutes after the start."


            if RunNotMatching:
                SendAnUgoQC(str(RunNumberQC)+' (old)', str(GloQual)+' (old)', '', CreatedOn, NotificationText)
            else:
                SendAnUgoQC(str(RunNumberQC), str(GloQual), DetailsText, CreatedOn, NotificationText)
    
            WriteLastRun(runnumber)
            WriteLastQuality(GloQual)

            NewQCneeded = isongoing 
            WriteQCNeeded(NewQCneeded)
    
        
    elif qcneeded:
        LOG(INFO,'Entering condition of not a new run but checking QC, for run',lastrunlogbook)
        runnumber = lastrunlogbook
    
        #___ QC check____
        LOG(INFO,'QUERYING THE QCDB')    
        MakeObjectReport()
        LOG(INFO,'OBJECT REPORT CREATED')
        time.sleep(1)
        RunNumberQC,Creation_utc,GloQual,DetailsQC = ParseObjectReport()
        CreatedOn = tconvert(int(Creation_utc)/1000)
    
        NewUgoNeeded = True
        secafterstart = (datetime.now()-datetime.fromtimestamp(timestart/1000)).total_seconds() 
        thermalizedTime = secafterstart > 10*60
        
        if int(trgstart) > 0:
            secbetweentrgandqc = (datetime.fromtimestamp(int(Creation_utc)/1000) - datetime.fromtimestamp(int(trgstart)/1000)).total_seconds() 
            thermalizedQC = secbetweentrgandqc > 10*60
        else:
            thermalizedQC = True

        thermalized = thermalizedTime and thermalizedQC

        NewQCNeeded = (isongoing and GloQual == 'GOOD') or (isongoing and not thermalized)
       
    
        NotificationText = ""
        DetailsText = ""
        if str(RunNumberQC) != str(runnumber):
            NotificationText += "\n:warning: The run number does not match! At this stage, this should not happen. Check qcdb."
            LOG(WARNING,"Not matching run number after first QC cycle! Check QCDB")
        
        if GloQual == "GOOD" and str(lastquality) == "GOOD":
            NewUgoNeeded = False
            LOG(INFO,"No need to send UGO for this cycle")
        elif GloQual != "GOOD" and str(lastquality) == "GOOD":
            NotificationText += "\n :exclamation: The quality changed!"
            DetailsText = DetailsQC
            if thermalized:
                NotificationText += "\n10 mins have passed. The run is not good. I will not check this run anymore :exclamation:"
        elif GloQual == "GOOD" and str(lastquality) != "GOOD":
            NotificationText += "\n :grinning: All good now. You will be notified if quality changes."
        else:
            NotificationText += "\n Still not good."
            if thermalized:
                NotificationText += "10 mins have passed. I will not check this run anymore :exclamation:"
    
        if not isongoing:
            NotificationText += "\nThe run is NOT ongoing anymore. My job is done. Waiting for new run..."
    
        if NewUgoNeeded:
            SendAnUgoQC(str(RunNumberQC), str(GloQual), DetailsText, CreatedOn, NotificationText)

    
        WriteLastRun(runnumber)
        WriteQCNeeded(NewQCNeeded)
        WriteLastQuality(GloQual)
    
    
    else:
        LOG(INFO,"Entering condition of not a new run and QC not needed. Doing nothing for run",lastrunlogbook)
    
    

    




    

    
