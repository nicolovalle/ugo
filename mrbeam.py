import os
import requests
import json
import smtplib, ssl
import time
import re
from datetime import datetime
import sys
import inspect


INFO = 'INFO'
WARNING = 'WARNING'
ERROR = 'ERROR'
FATAL = 'FATAL'
DEBUG = 'DEBUG'

VERSION = 'v1.0.0'

target_channel = 'ugo-qc'




def LOG(severity, *message):
    filename = str(inspect.stack()[1][1])
    filename = filename.split('/')[-1]
    funcname = str(inspect.stack()[1][3])

    tt = datetime.now()
    tstamp = "%s-%d-%d-%d:%d:%d"%(str(tt.year)[-2:],tt.month,tt.day,tt.hour,tt.minute,tt.second)
    print("[%s][%s][%s]"%(severity,tstamp,filename+':'+funcname),*message)

    

def SendAnUgo(message, username='MrBeam', channel=target_channel):

    if username != "MrBeam":
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
    response = requests.post('https://mattermost.web.cern.ch/hooks/kk9cwkqoe7d7fqt3rbpe91uwwy',headers=headers,data=str(values))
    LOG(INFO,response)  


        

def GetDataJson(fname):
    
    vfile = open(fname)
    data = json.load(vfile)

    filln = data['fill'] #int
    fills = data['fillscheme'] #str
    accmode = data['accmode']
    beammode = data['beammode']
    pagetime_source = data['time']['page1']
    comment = data['comments']['text']
    commenttime_source = data['comments']['time']

    pagetime = pagetime_source[2:10]+' '+pagetime_source[11:19]
    commenttime = commenttime_source[2:10]+' '+commenttime_source[11:19]

    LOG(INFO,'Read',fname,'. Page time:',pagetime_source)
    return filln, fills, accmode, beammode, pagetime, comment, commenttime

def SendAnUgoBeamMode(timestamp, accmode, beammode, username='MrBeam', channel=target_channel):

    web_url = 'https://mattermost.web.cern.ch/hooks/kk9cwkqoe7d7fqt3rbpe91uwwy'
    boxcolor = '#61D5FF'
   
    tags = []

    if 'PHYSICS' in accmode:
        if 'SETUP' in beammode:
            tags.append('LHBSTP')
        if 'PROBE BEAM' in beammode:
            tags.append('LHBIPR')
        if 'PHYSICS' in beammode:
            tags.append('LHBIPH')
        if beammode == 'RAMP':
            tags.append('LHBRMP')
        if 'SQUEEZE' in beammode or 'ADJUST' in beammode:
            tags.append('LHBADJ')
        if 'STABLE BEAM' in beammode:
            tags.append('LHBSBB')


    pretext = 'tags:'
    for t in tags:
        pretext += ' '+t

    if len(tags) == 0:
        pretext = ''
    
    payload = {
        'icon_url': "https://nvalle.web.cern.ch/teddy_animated.png",
        'channel': channel,
        'username': username,
        'text': pretext,
        'attachments': [
            {
                'title': 'New beam mode',
                'text': accmode+': '+beammode+'\n*'+timestamp+'*'
            }
        ]
    }

    if username != "MrBeam":
        LOG(INFO,"I will not send anything with the name",username)
        return
    # https://mattermost.com/blog/mattermost-integrations-incoming-webhooks/
    # https://developers.mattermost.com/integrate/webhooks/incoming/
    logmessage = "I'm sending an UGO as for %s: %s. Page1 time: %s"%(accmode,beammode,timestamp)

    LOG(INFO,logmessage)
        
    response = requests.post(web_url, json=payload, headers={'Content-Type': 'application/json'})
    LOG(INFO,response)  

def SendAnUgoFill(timestamp, filln, fills, accmode, beammode, username='MrBeam', channel=target_channel):

    web_url = 'https://mattermost.web.cern.ch/hooks/kk9cwkqoe7d7fqt3rbpe91uwwy'
    boxcolor = '#61D5FF'
   
    
    payload = {
        'icon_url': "https://nvalle.web.cern.ch/teddy_animated.png",
        'channel': channel,
        'username': username,
        'attachments': [
            {
                'title': 'New fill n.'+str(filln),
                'text': fills,
                'fields': [
                    {
                        'short': True,
                        'title': 'Beam mode',
                        'value': accmode+': '+beammode
                    },
                    {
                        'short': True,
                        'title': 'Page1 time',
                        'value': '*'+timestamp+'*'
                    }
                ]
            }
            
        ]
    }

    if username != "MrBeam":
        LOG(INFO,"I will not send anything with the name",username)
        return
    # https://mattermost.com/blog/mattermost-integrations-incoming-webhooks/
    # https://developers.mattermost.com/integrate/webhooks/incoming/
    logmessage = "I'm sending an UGO as for fill %s: Page1 time: %s"%(str(filln),timestamp)

    LOG(INFO,logmessage)
        
    response = requests.post(web_url, json=payload, headers={'Content-Type': 'application/json'})
    LOG(INFO,response)  
    

def SendAnUgoLHCMessage(pagetime, msgtime, accmode, beammode, message, username='MrBeam', channel=target_channel):

    web_url = 'https://mattermost.web.cern.ch/hooks/kk9cwkqoe7d7fqt3rbpe91uwwy'
    boxcolor = '#61D5FF'
   
    tags = ['LHMNWC']


    pretext = 'tags:'
    for t in tags:
        pretext += ' '+t

    if len(tags) == 0:
        pretext = ''
    
    payload = {
        'icon_url': "https://nvalle.web.cern.ch/teddy_animated.png",
        'channel': channel,
        'username': username,
        'text': pretext,
        'attachments': [
            {
                'title': 'New message from LHC, '+msgtime,
                'text': message,
                'fields': [
                    {
                        'short': True,
                        'title': 'Beam mode',
                        'value': accmode+': '+beammode
                    },
                    {
                        'short': True,
                        'title': 'Page1 time',
                        'value': '*'+pagetime+'*'
                    }
                ]
            }
            
        ]
    }

    if username != "MrBeam":
        LOG(INFO,"I will not send anything with the name",username)
        return
    # https://mattermost.com/blog/mattermost-integrations-incoming-webhooks/
    # https://developers.mattermost.com/integrate/webhooks/incoming/
    logmessage = "I'm sending an UGO as for new LHC message at %s. Page1 time: %s"%(msgtime, pagetime)

    LOG(INFO,logmessage)
        
    response = requests.post(web_url, json=payload, headers={'Content-Type': 'application/json'})
    LOG(INFO,response)  
    

    
#________________________ MAIN ______________________-

if __name__ == "__main__":

    try:

       fn0, fs0, a0, b0, t0, m0, tm0 = GetDataJson('vistars-last.json')
       fn1, fs1, a1, b1, t1, m1, tm1 = GetDataJson('vistars.json')
       
       if t0 == t1:
           LOG(WARNING,'LHC PAGE 1 TIMESTAMP DID NOT CHANGE')
           SendAnUgo(':warning: LHC PAGE 1 TIMESTAMP DID NOT CHANGE')
           
       
       if b0 != b1 or a0 != a1:
           SendAnUgoBeamMode(t1, a1, b1)
       else:
           LOG(INFO,'Beam mode not changed')
       
       if fn0 != fn1 or fs0 != fs1:
           SendAnUgoFill(t1, fn1, fs1, a1, b1)
       else:
           LOG(INFO,'Fill number/scheme not changed')
       
       if m0 != m1 or tm0 != tm1:
           SendAnUgoLHCMessage(t1, tm1, a1, b1, m1)
       else:
           LOG(INFO,'LHC comment not changed')

    except:
        SendAnUgo(':warning: Errors in procesing vistar information')
    


  
