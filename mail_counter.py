#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os
import configparser
import datetime
import urllib.request
import json

cfg = configparser.ConfigParser()
cfg.read(os.path.dirname(__file__)+"/config.ini")
WEBHOOK_URL=cfg["slack"]["webhookUrl"]

now = datetime.datetime.now()
target_time = (now+datetime.timedelta(hours=-1)).strftime("%Y/%m/%d %H")
today_date = (now+datetime.timedelta(hours=-1)).strftime("%d")

if 1 < int(today_date) < 9:
    search_target_time = (now+datetime.timedelta(hours=-1)).strftime("%b  %-d %H")
else:
    search_target_time = (now+datetime.timedelta(hours=-1)).strftime("%b %-d %H")

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
deferred_count=0

for line in target_log:
    if line.find("status=sent (250 2.0.0 OK") >= 0:
        sent_count+=1
    elif line.find("NOQUEUE: reject") >= 0:
        reject_count+=1
    elif line.find("status=deferred") >= 0:
        deferred_count+=1

url=WEBHOOK_URL
message = ("```[" + os.uname()[1] + "] \n"
		"number of mails around " + target_time + ":xx:xx \n"
                "log count : " + str(log_count) + "\n"
                "sent      : " + str(sent_count) + "\n"
                "rejected  : " + str(reject_count) + "\n"
                "deferred  : " + str(deferred_count) + "```"
                )

data = {
    'text': message
}

headers = {
    'Content-Type': 'application/json',
}

req = urllib.request.Request(url, json.dumps(data).encode(), headers)
with urllib.request.urlopen(req) as res:
    body = res.read().decode('utf-8')

print('ResponseBody:'+str(body), file=sys.stderr)
exit (0)
