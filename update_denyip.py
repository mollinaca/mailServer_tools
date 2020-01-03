#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os
import subprocess

denyip_file = os.path.dirname(__file__) + "/docs/denyip.txt"
previous_denyip_number_file = os.path.dirname(__file__) + "/docs/number_of_denyip.txt"
with open(denyip_file, 'r+') as f:
    l = subprocess.check_output(["sort","-n", denyip_file]).decode('utf-8').split()
    sorted_uniq_list = sorted(l,key=l.index)
    with open(previous_denyip_number_file, 'r+') as n:
        previous_lines = n.read().strip()
    if int(len(sorted_uniq_list)) > int(previous_lines):
        for ip in sorted_uniq_list:
            f.write(str(ip)+"\n")
            n.write(str(len(sorted_uniq_list)))

        # git
        commit_message="auto update, add & sort"
        git_add = subprocess.check_output(["/usr/bin/git", "add", denyip_file, previous_denyip_number_file]).decode('utf-8')
        print (str(git_add), file=sys.stderr)
        git_commit = subprocess.check_output(["/usr/bin/git", "commit","-m",commit_message]).decode('utf-8')
        print (str(git_commit), file=sys.stderr)
        git_push = subprocess.check_output(["/usr/bin/git", "push","origin","master"]).decode('utf-8')
        print (str(git_push), file=sys.stderr)
    else:
        print ("did nothing",file=sys.stderr)

exit (0)

