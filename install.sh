#! /bin/sh
#set -x

#当前目录
CURR_DIR=$(cd "$(dirname $0)"; pwd)

#载入函数库
. ${CURR_DIR}/../mslib.s

#帮助信息
function usage()
{
  cat <<EOF
usage: install.sh module tns ftp_usr ftp_pwd
  module  : 模块名
  tns     : 数据库联接串
  ftp_usr ：FTP用户名
  ftp_pwd ：FTP密码
EOF
}

#参数不是两个则退出
if [ $# -ne 4 ]; then
  usage
  exit 1
fi

#模块名
module="${1}"

#数据库连接串
#noahpf/noahpf@127.0.0.1:1521/ora11g
usrpwd="${2}"

#ftp用户名密码
#fenghuo
ftp_usr="${3}"
#123456
ftp_pwd="${4}"

#dbid
local_dbid="1000"

#模块目录
MODULE_HOME=/home/${module}

#bcp目录
BCP_DIR=${MODULE_HOME}/bcp

#程序主目录
DL_HOME=${MODULE_HOME}/dataloader

#DBS
COMMON_CFG=${DL_HOME}/etc/common.xml

#日志文件
er_log=${CURR_DIR}/../dl_er.log
inst_log=${CURR_DIR}/../dl_inst.log

#清空已存在的日志
echo -n "" > ${er_log} 2>/dev/null
echo -n "" > ${inst_log} 2>/dev/null

#kill已存在进程
function kill_processes()
{
  #show_process "kill已存在进程"
  pkill -f dataloader_${module}.py
  pkill -f statloader_${module}.py
}

#生成db列表
function gen_dblist()
{
  #清除已存在的机器列表
  sed -i '/<db /'d ${COMMON_CFG} 2>>${er_log}
  
  #添加机器列表
  sed -i "/\/dbs/i\    <db id=\"${local_dbid}\">${usrpwd}</db>" ${COMMON_CFG} 2>>${er_log}
}

#安装dataloader
function install_dataloader()
{
  #安装开始
  show_process "start install dataloader_${module}..."
  
  #创建dataloader目录
  #show_process "创建dataloader_${module}目录"
  mkdir -p ${DL_HOME} 2>>${er_log}
  
  #copy文件到目标目录
  #show_process "copy文件至dataloader_${module}目录"
  cp -rf ${CURR_DIR}/* ${DL_HOME} 2>>${er_log}
  mv ${DL_HOME}/dataloader.py ${DL_HOME}/dataloader_${module}.py 2>>${er_log}
  mv ${DL_HOME}/statloader.py ${DL_HOME}/statloader_${module}.py 2>>${er_log}
  
  #转为unix格式并赋执行权限
  #show_process "py&sh文件格式转换（dos2unix）"
  find ${DL_HOME} -name "*.py" -exec dos2unix -q {} \;
  find ${DL_HOME} -name "*.py" -exec chmod +x {} \; 2>>${er_log} 1>/dev/null
  
  find ${DL_HOME} -name "*.sh" -exec dos2unix -q {} \;
  find ${DL_HOME} -name "*.sh" -exec chmod +x {} \; 2>>${er_log} 1>/dev/null
  
  #生成db列表
  gen_dblist
  
  #修改common.xml中数据库连接串
  #show_process "配置common.xml"
  sed -i "s#\(<home_dir>\).*\(</home_dir>\)#\1${DL_HOME}\2#g" ${COMMON_CFG} 2>>${er_log}
  sed -i "s#\(<local_dbid>\).*\(</local_dbid>\)#\1${local_dbid}\2#g" ${COMMON_CFG} 2>>${er_log}
  sed -i "s#\(<bcp_dir>\).*\(</bcp_dir>\)#\1${BCP_DIR}\2#g" ${COMMON_CFG} 2>>${er_log}

  #配置dataloader守护程序
  #show_process "配置dataloader_${module}守护程序"
  sed "s#\[module\]#${module}#g" ${DL_HOME}/fude/dataloader.xml 1> ${FUDE_ROOT}/fude/etc/guard/conf.d/dataloader_${module}.xml 2>>${er_log}
  sed "s#\[module\]#${module}#g" ${DL_HOME}/fude/statloader.xml 1> ${FUDE_ROOT}/fude/etc/guard/conf.d/statloader_${module}.xml 2>>${er_log}
  
  #配置清理程序
  #show_process "配置清理程序"
  #cleaner_cron要修改权限为644，否则cron执行可能会出错
  sed "s#\[module\]#${module}#g" ${DL_HOME}/cleaner_cron 1> /etc/cron.d/cleaner_cron_${module} 2>>${er_log}
  chmod 644 /etc/cron.d/cleaner_cron_${module} 2>>${er_log}
  
  #show_process "创建ftp用户开始"
  useradd ${ftp_usr} 1>/dev/null 2>&1
  echo ${ftp_pwd} | passwd ${ftp_usr} --stdin 2>>${er_log} 1>/dev/null
  
  #修改rc.local，开机创建bcp接收目录
  #show_process "创建bcp接收目录"
  mkdir -p ${DL_HOME} 2>>${er_log}
  mkdir -p ${BCP_DIR}/${local_dbid}/tmp 2>>${er_log}
  chmod 777 ${MODULE_HOME} 2>>${er_log}
  chmod -R 777 ${BCP_DIR} 2>>${er_log}
  
  #重启crond
  service crond restart 1>/dev/null 2>&1
  
  #reload守护进程
  fudeguardmgr.py --r 1>/dev/null 2>&1

  #kill已存在进程
  kill_processes
}

#安装
install_dataloader

#判断安装结果
if [ -f ${er_log} -a $(sed '/^\W*$/d' ${er_log} | wc -l) -ne 0 ]; then
  show_error "install dataloader_${module} failed."
  exit 1
else
  show_success "install dataloader_rtk successfully."
fi
