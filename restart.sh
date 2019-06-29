#! /bin/bash
#set -x
#重启dataloader，kill掉dataloader进程，fude重启进程
pkill -f dataloader.py 1>/dev/null 2>&1
pkill -f statloader.py 1>/dev/null 2>&1
