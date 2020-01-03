#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os, re
import datetime
import modify_nacl

## functions ##
def usage ():
    message=("Usage: logcheck.py [target] \n"
        "discription: \n"
        "    search evil IP address in hour from [target] file. \n"
        " \n"
        "target: \n"
        "    test : print test message \n"
        "    secure : file -> /var/log/secure \n"
        "    mail : file -> /var/log/maillog \n"
    )
    print (message, file=sys.stderr)
    return 0 

def secure ():
    evil_list = {}
    search_target_time = (now+datetime.timedelta(hours=-1)).strftime("%b  %-d %H") 
    ld = open ("/var/log/secure")
    lines = ld.readlines()
    ld.close()

    target_log = []
    for line in lines:
        if line.find(search_target_time) >= 0:
             target_log.append(line[:-1])

    for line in target_log:
        # "Invalid user" | "Bye Bye" となっているIPアドレスを怪しいアクセスとする
        # Todo: secure のセキュリティ的なエラー表示
        if line.find("Invalid user") >= 0:
            m = re.search('\\d+\\.\\d+\\.\\d+\\.\\d+', line)
            evil_ip = str(m.group(0))
            if not evil_ip in evil_list:
                evil_list[evil_ip] = 1
            else:
                evil_list[evil_ip] += 1

    for line in target_log:
        if line.find("Bye Bye") >= 0:
            m = re.search('\\d+\\.\\d+\\.\\d+\\.\\d+', line)
            evil_ip = str(m.group(0))
            if not evil_ip in evil_list:
                evil_list[evil_ip] = 1
            else:
                evil_list[evil_ip] += 1

    # count が 5以上のIPアドレスを evil なものとして、NACLに登録する
    for ip, count in evil_list.items():
        if count >= 5:
            args = ["create_entry",ip]
            modify_nacl.main (args)

    return 0

def mail ():
    evil_list = {}
    search_target_time = (now+datetime.timedelta(hours=-1)).strftime("%b  %-d %H") 
    ld = open ("/var/log/maillog")
    lines = ld.readlines()
    ld.close()

    target_log = []
    for line in lines:
        if line.find(search_target_time) >= 0:
             target_log.append(line[:-1])

    for line in target_log:
        # from unknown となっているIPアドレスを怪しいアクセスとする
        # Todo: maillog のセキュリティ的なエラー表示
        if line.find("unknown") >= 0:
            m = re.search('\\d+\\.\\d+\\.\\d+\\.\\d+', line)
            evil_ip = str(m.group(0))
            if not evil_ip in evil_list:
                evil_list[evil_ip] = 1
            else:
                evil_list[evil_ip] += 1

    # count が 5以上のIPアドレスを evil なものとして、NACLに登録する
    for ip, count in evil_list.items():
        if count >= 5:
            args = ["create_entry",ip]
            modify_nacl.main (args)

    return 0

## main function ##
def main (args):
    global target
    global now
    target = args[1]
    now = datetime.datetime.now()

    if target == "test":
        print ("!! test !!")
    elif target == "secure":
        secure ()
    elif target == "mail":
        mail ()
    else:
        usage()

    return 0

## do main ##
if __name__ == "__main__":
    if len(sys.argv) == 1:
        usage ()
        exit (1)
    main(sys.argv)
    exit (0)

