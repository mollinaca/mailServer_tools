#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os
import configparser
import subprocess
import urllib.request
import json

cfg = configparser.ConfigParser()
cfg.read(os.path.dirname(__file__)+"/config.ini")
NACL_ID=cfg["aws"]["naclId"]
WEBHOOK_URL=cfg["slack"]["webhookUrl"]

## functions ##
def usage ():
    message=("Usage: modify_nacl.py [commands] \n"
        "commands: \n"
        "    test : print test message \n"
        "    display_my_rules : get and display my deny rules \n"
        "    create_entry : create entry [RuleNumber] [IPaddress] \n"
        "    delete_entry : delete entry [RuleNumber] \n"
        "    orgnize_entry : make empty rulenumber if number of rules > 30 \n "
    )
    print (message, file=sys.stderr)
    return 0

def slack (message:str):
    url=WEBHOOK_URL
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
    return 0

def get_acls ():
    acls = json.loads(subprocess.check_output(["aws", "ec2", "describe-network-acls"]))
    return acls

def is_my_rule (n: int):
    if 10000 < n <= 10050:
        return True
    else:
        return False

def get_my_rules ():
    my_rules={}
    acls = get_acls()
    for rule in acls['NetworkAcls'][0]['Entries']:
        if is_my_rule(int(rule['RuleNumber'])):
            my_rules[int(rule['RuleNumber'])] = rule['CidrBlock']
    return my_rules

def has_my_rules_empty_number (my_rules: dict):
    """
    my_rules の要素数が30以下ならTrue、そうでなければFalse
    """
    if len(my_rules) <= 30:
        return True
    else:
        return False

def get_next_empty_number ():
    my_rules = get_my_rules()
    for i in range(10001,10050):
            if not i in my_rules:
                return i
    return "null"

def create_entry (rn:str, ip:str):
    target_ip=ip+"/32"
    res = subprocess.check_output(["aws", "ec2", "create-network-acl-entry", "--network-acl-id", NACL_ID, "--ingress", "--rule-number", rn, "--protocol", "-1", "--cidr-block", target_ip, "--rule-action", "deny"]).decode('utf-8')
    return str(res)

def delete_entry (rn:str):
    res = subprocess.check_output(["aws", "ec2", "delete-network-acl-entry", "--network-acl-id", NACL_ID, "--ingress", "--rule-number", rn]).decode('utf-8')
    return str(res)

def has_gap (rules:dict):
    """
    キーの最小と最大を取得し、
    10001 から始まっていない or あるべき要素の数と等しくなければ隙間があると判断する
    """
    count = len (rules)
    min_rn = min (rules)
    max_rn = max (rules)
    if not min_rn == 10001 or not (max_rn - min_rn + 1) == count:
        return True
    return False

def orgnize_entry ():
    """
    ルール数が30を超えていて
    先頭から末尾までの間に隙間があったら、末尾から3つを削除する
    先頭から末尾までの間に隙間がなかったら、先頭から3つを削除する
    """
    my_rules = get_my_rules ()
    if len(my_rules) > 30:
        if has_gap (my_rules):
            for _ in range(3):
                target_rule=max(my_rules)
                delete_entry(target_rule)
                my_rules = get_my_rules ()
        else:
            for _ in range(3):
                target_rule=min(my_rules)
                delete_entry(target_rule)
                my_rules = get_my_rules ()
    else:
        slack ('```' + __file__ + ' ' + command + ' ' + ' → did nothing, number of rules → ' + str(len(my_rules)) + '```')
    return 0

## main function ##
def main (args):
    global command
    command = args[1]
    if command == "test":
        print ("!! test !!")
    elif command == "display_my_rules":
        my_rules = get_my_rules ()
        print (str(json.dumps(my_rules,indent=2)))
        slack ('```' + __file__ + ' ' + command + ' ' + ' → \n' + str(json.dumps(my_rules,indent=2)) + '```')
    elif command == "check_rules_empty": # will remove
        my_rules = get_my_rules ()
        has_my_rules_empty_number (my_rules)
    elif command == "search_next_empty_number": # will remove
        next_empty = get_next_empty_number ()
        print (next_empty)
    elif command == "create_entry":
        ip = args[2]
        next_empty = get_next_empty_number ()
        if not next_empty == "null":
            create_entry (str(next_empty), ip)
            slack ('```' + __file__ + ' ' + command + ' ' + ' → \n' + str(next_empty) + ':' + ip + '```')
        else:
            orgnize_entry ()
            create_entry (str(next_empty), ip)
            slack ('```' + __file__ + ' ' + command + ' ' + ' → \n' + str(next_empty) + ':' + ip + '```')
    elif command == "delete_entry":
        rn = args[2]
        delete_entry (str(rn))
        slack ('```' + __file__ + ' ' + command + ' ' + ' → \n' + str(rn) + ':' + '```')
    elif command == "orgnize_entry":
        orgnize_entry ()

    else:
        usage()

    return 0

## do main ##
if __name__ == "__main__":
    main(sys.argv)
    exit (0)


