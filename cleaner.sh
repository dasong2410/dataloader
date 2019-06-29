#! /bin/sh
#set -x
#当前目录
CURR_DIR=$(cd "$(dirname $0)"; pwd)

#保存周期，0：只保留今天，1：保留到昨天，类推
dura=7

#计算文件保存临界点
dura_point=$(date -d "-${dura} days" "+%Y%m%d")

#删除过期的FATAL文件
for f in $(ls ${CURR_DIR}/bad/FATAL); do
  dt=${f:0:8}
  if [ ${dt} -lt ${dura_point} ]; then
    #echo "${CURR_DIR}/bad/FATAL/${f}"
    rm -rf ${CURR_DIR}/bad/FATAL/${f} 1>/dev/null 2>&1
  fi
done

#删除过期的WARN文件
for f in $(ls ${CURR_DIR}/bad/WARN); do
  dt=${f:0:8}
  if [ ${dt} -lt ${dura_point} ]; then
    #echo "${CURR_DIR}/bad/WARN/${f}"
    rm -rf ${CURR_DIR}/bad/WARN/${f} 1>/dev/null 2>&1
  fi
done

#删除过期的坏文件应对的日志（FATAL）
for f in $(ls ${CURR_DIR}/log/bad/FATAL); do
  dt=${f:0:8}
  if [ ${dt} -lt ${dura_point} ]; then
    #echo "${CURR_DIR}/log/bad/FATAL/${f}"
    rm -rf ${CURR_DIR}/log/bad/FATAL/${f} 1>/dev/null 2>&1
  fi
done

#删除过期的坏文件应对的日志（WARN）
for f in $(ls ${CURR_DIR}/log/bad/WARN); do
  dt=${f:0:8}
  if [ ${dt} -lt ${dura_point} ]; then
    #echo "${CURR_DIR}/log/bad/WARN/${f}"
    rm -rf ${CURR_DIR}/log/bad/WARN/${f} 1>/dev/null 2>&1
  fi
done

#删除过期的日志
for f in $(find ${CURR_DIR}/log/stat/log -ctime +${dura}); do
  #echo "${CURR_DIR}/log/stat/log/${f}"
  rm -rf ${CURR_DIR}/log/stat/log/${f} 1>/dev/null 2>&1
done

#删除过期的系统日志文件
for f in $(ls ${CURR_DIR}/log/sys/*.log.????-??-??); do
  suffix=$(echo ${f} | sed "s/.*.log.\(.*\)/\1/g")
  dt=$(echo ${suffix} | sed "s/-//g")
  if [ ${dt} -lt ${dura_point} ]; then
    #echo "${f}"
    rm -rf ${f} 1>/dev/null 2>&1
  fi
done