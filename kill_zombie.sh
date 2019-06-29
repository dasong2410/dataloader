#! /bin/sh
#kill僵掉的sqlldr进程
#set -x
#临界值，默认超过1小时的进程会被杀掉
threshold=3600

mask="000 00 00 00"
#获取进程信息
ps -eo pid,comm,etime | grep sqlldr | while read pinfo; do
  #pid
  pid=$(echo ${pinfo} | awk -F' ' '{print $1}')
  
  #消耗时间
  etime=$(echo ${pinfo} | awk -F' ' '{print $3}')
  etime=${etime//-/ }
  etime=${etime//:/ }
  ((len=12-${#etime}))

  etime=${mask:0:${len}}${etime}
  
  #获取天、小时、分钟、秒
  day=10#$(echo ${etime} | awk -F' ' '{print $1}')
  hour=10#$(echo ${etime} | awk -F' ' '{print $2}')
  minute=10#$(echo ${etime} | awk -F' ' '{print $3}')
  second=10#$(echo ${etime} | awk -F' ' '{print $4}')
  ((dura=86400*day+3600*hour+60*minute+second))
  
  #判断是否超时，超时则kill进程
  if [ ${dura} -gt ${threshold} ]; then
    #echo ${etime} ${dura}
    kill -9 ${pid}
  fi
done