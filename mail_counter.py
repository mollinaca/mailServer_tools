#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os
import configparser
import datetime
import urllib.request
import json

cfg = configparser.ConfigParser()
cfg.read(os.path.dirname(__file__)+"/config.ini")
webhookUrl=cfg["slack"]["webhookUrl"]

now = datetime.datetime.now()
target_time = (now+datetime.timedelta(hours=-1)).strftime("%Y/%m/%d %H")
search_target_time = (now+datetime.timedelta(hours=-1)).strftime("%b  %-d %H") 

ld = open ("/var/log/maillog")
lines = ld.readlines()
ld.close()

target_log = []
for line in lines:
    if line.find(search_target_time) >= 0:
         target_log.append(line[:-1])

log_count=len(target_log)
sent_count=0
reject_count=0

for line in target_log:
    if line.find("sent") >= 0:
        sent_count+=1

for line in target_log:
    if line.find("reject") >= 0:
        reject_count+=1

url=webhookUrl
message = ("```number of mails around " + target_time + ":xx:xx \n"
                "log count : " + str(log_count) + "\n" 
                "sent      : " + str(sent_count) + "\n"
                "rejected  : " + str(reject_count) + "```"
                )

data = {
    'text': message
}

headers = {
    'Content-Type': 'application/json',
}

req = urllib.request.Request(url, json.dumps(data).encode(), headers)
with urllib.request.urlopen(req) as res:
    body = res.read()

print('ResponseBody:'+str(body), file=sys.stderr)
exit (0)

