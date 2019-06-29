#! /bin/bash
#set -x

function rm_dt()
{
  #删除dataloader
  rm -rf /home/noah/dataloader 1>/dev/null 2>&1
  
  #删除守护配置文件
  rm -rf ${FUDE_ROOT}/fude/etc/guard/conf.d/dataloader.xml 1>/dev/null 2>&1
  rm -rf ${FUDE_ROOT}/fude/etc/guard/conf.d/statloader.xml 1>/dev/null 2>&1

  #reloader守护程序
  fudeguardmgr.py --r 1>/dev/null 2>&1
  
  #杀掉进程
  pkill -f dataloader.py 1>/dev/null 2>&1
  pkill -f statloader.py 1>/dev/null 2>&1
}

rm_dt