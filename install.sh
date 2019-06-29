#! /bin/sh
#set -x

#当前目录
CURR_DIR=$(cd "$(dirname $0)"; pwd)

#安装类型
type=${1:-"install"}

#bcp目录
BCP_DIR="/home/bcpsplit/dam_outpath"

#平台库连接串
pf_usrpwd="${NOAHPFDB_USERNAME}/${NOAHPFDB_PASSWORD}@${NOAHPFDB_IP}:1521/${NOAHPFDB_SID}"

#程序主目录
DL_HOME=/home/noah/dataloader

#DBS
COMMON_CFG=${DL_HOME}/etc/common.xml

#日志文件
er_log=${CURR_DIR}/er.log
inst_log=${CURR_DIR}/dataloader.log

#清空已存在的日志
echo -n "" > ${er_log} 2>/dev/null
echo -n "" > ${inst_log} 2>/dev/null

#帮助信息
function usage()
{
  cat <<EOF
usage: install.sh [install|update|reconfig]
EOF
}

#安装进度
function show_process()
{   
   time=$(date "+%Y-%m-%d %T")
   echo "[$time]：$1" | tee -a ${inst_log}
}

#检查数据库状态
function check_db_status()
{
  #获取数据库状态
  db_mesg=$(sqlplus -S -L ${1} <<EOF
    set head off;
    select lower(status) from v\$instance;
    exit;
EOF
)

  if [ "$(echo ${db_mesg} | tr -d "\n")" = "open" ]; then
    db_status=1
  else
    db_status=0
  fi
}

#kill已存在进程
function kill_processes()
{
  show_process "kill已存在进程"
  pkill -f dataloader.py
  pkill -f statloader.py
  pkill -f dataloaderbcp.py
}

#生成db列表
function gen_dblist()
{
  #生成db列表
  show_process "配置common.xml数据库列表"
  db_info=$(sqlplus -S -L ${pf_usrpwd} <<EOF
    set newp none;
    set feedback off;
    set trimspool on;
    set heading off;
    select positionid || '=' || username || '/' || password || '@' || ipaddress || ':' || port || '/' || sid
      from base_database_position
     where dbtype='ORACLE'
       and dbdesc='DAM'
     union all
    select distinct 'local_dbid=' || a.positionid
      from base_database_position a,
           base_group_position_detail b
     where a.positionid=b.positionid
       and b.groupid=2
     order by 1;
EOF
)
  #清除已存在的机器列表
  sed -i '/<db /'d ${COMMON_CFG} 2>>${er_log}

  for db in ${db_info}; do
    #echo ${db}
    dbid=$(echo ${db} | awk -F'=' '{print $1}')
    dbip=$(echo ${db} | awk -F'=' '{print $2}')
    
    #获取local_dbid
    if [ "${dbid}" = "local_dbid" ]; then
      local_dbid=${dbip}
    else
      mkdir -p ${BCP_DIR}/${dbid} 2>>${er_log}
      
      #添加机器列表
      sed -i "/\/dbs/i\    <db id=\"${dbid}\">${dbip}</db>" ${COMMON_CFG} 2>>${er_log}
    fi
  done
}

#安装dataloader
function install_dataloader()
{
  #安装开始
  show_process "dataloader安装开始"
  
  #备份已存在旧的dataloader入库程序
  if [ ! -e ${DL_HOME}.$(date +%Y%m%d) ]; then
    mv ${DL_HOME} ${DL_HOME}.$(date +%Y%m%d) 1>/dev/null 2>&1
  else
    rm -rf ${DL_HOME} 1>/dev/null 2>&1
  fi
  
  rm -rf /etc/cron.d/noah_dataloader_del 1>/dev/null 2>&1
  rm -rf ${CURR_DIR}/etc/protocols/*.xml 1>/dev/null 2>&1

  #解析现有的协议配置文件
  if [ -e ${DL_HOME}.$(date +%Y%m%d) ]; then
    show_process "旧系统中协议配置文件转化"
    rm -rf ${CURR_DIR}/etc/v1/*.xml 1>/dev/null 2>&1
    rm -rf ${CURR_DIR}/etc/v2/*.xml 1>/dev/null 2>&1
    rm -rf ${CURR_DIR}/etc/v3/*.xml 1>/dev/null 2>&1
    
    cp -f ${DL_HOME}.$(date +%Y%m%d)/etc/dbnbase.conf ${CURR_DIR}/etc/ 1>/dev/null 2>&1
    cp -f ${DL_HOME}.$(date +%Y%m%d)/etc/dbn.cfg ${CURR_DIR}/etc/ 1>/dev/null 2>&1
    cp -f ${DL_HOME}.$(date +%Y%m%d)/etc/protocols/*.xml ${CURR_DIR}/etc/v3/ 1>/dev/null 2>&1
    
    python ${CURR_DIR}/convertor.py 1>/dev/null 2>&1
    
    #copy旧协议配置文件到protocols
    cp -f ${CURR_DIR}/etc/v1/*.xml ${CURR_DIR}/etc/protocols/ 1>/dev/null 2>&1
    cp -f ${CURR_DIR}/etc/v2/*.xml ${CURR_DIR}/etc/protocols/ 1>/dev/null 2>&1
    cp -f ${CURR_DIR}/etc/v3/*.xml ${CURR_DIR}/etc/protocols/ 1>/dev/null 2>&1
  fi
  
  #copy新协议配置文件到protocols
  cp -f ${CURR_DIR}/etc/new/*.xml ${CURR_DIR}/etc/protocols/ 1>/dev/null 2>&1
  
  #创建dataloader目录
  show_process "创建dataloader目录"
  mkdir -p ${DL_HOME} 2>>${er_log}
  
  #copy文件到目标目录
  show_process "copy文件至dataloader目录"
  cp -rf ${CURR_DIR}/* ${DL_HOME} 2>>${er_log}
  
  #转为unix格式并赋执行权限
  show_process "py&sh文件格式转换（dos2unix）"
  find ${DL_HOME} -name "*.py" -exec dos2unix -q {} \;
  find ${DL_HOME} -name "*.py" -exec chmod +x {} \; 2>>${er_log} 1>/dev/null
  
  find ${DL_HOME} -name "*.sh" -exec dos2unix -q {} \;
  find ${DL_HOME} -name "*.sh" -exec chmod +x {} \; 2>>${er_log} 1>/dev/null
  
  #生成db列表
  gen_dblist
  
  #修改common.xml中数据库连接串
  show_process "配置common.xml"
  sed -i "s#\(<pf_usrpwd>\).*\(</pf_usrpwd>\)#\1${pf_usrpwd}\2#g" ${COMMON_CFG} 2>>${er_log}
  sed -i "s#\(<local_dbid>\).*\(</local_dbid>\)#\1${local_dbid}\2#g" ${COMMON_CFG} 2>>${er_log}
  sed -i "s#\(<home_dir>\).*\(</home_dir>\)#\1${DL_HOME}\2#g" ${COMMON_CFG} 2>>${er_log}
  sed -i "s#\(<bcp_dir>\).*\(</bcp_dir>\)#\1${BCP_DIR}\2#g" ${COMMON_CFG} 2>>${er_log}

  #配置dataloader守护程序
  show_process "配置dataloader守护程序"
  sed -i "s#\(<WorkPath>\).*\(</WorkPath>\)#\1${DL_HOME}\2#g" ${DL_HOME}/fude/dataloader.xml 2>>${er_log}
  sed -i "s#\(<WorkPath>\).*\(</WorkPath>\)#\1${DL_HOME}\2#g" ${DL_HOME}/fude/statloader.xml 2>>${er_log}
  cp -f ${DL_HOME}/fude/* ${FUDE_ROOT}/fude/etc/guard/conf.d 2>>${er_log}

  #配置清理程序
  show_process "配置清理程序"
  #cleaner_cron要修改权限为644，否则cron执行可能会出错
  cp -f ${DL_HOME}/cleaner_cron /etc/cron.d 2>>${er_log}
  chmod 644 ${DL_HOME}/cleaner_cron 2>>${er_log}
  
  #重启crond
  service crond restart 1>/dev/null 2>&1
  
  #reload守护进程
  fudeguardmgr.py --r 1>/dev/null 2>&1

  #kill已存在进程
  kill_processes
  
  #安装结束
  show_process "dataloader安装结束"
}

#重新配置dataloader
function reconfig_dataloader()
{
  show_process "dataloader配置开始"
  
  #生成db列表
  gen_dblist
  
  #修改dbn.cfg
  show_process "配置common.xml"
  sed "s#\(<pf_usrpwd>\).*\(</pf_usrpwd>\)#\1${pf_usrpwd}\2#g" ${COMMON_CFG} 2>>${er_log}
  sed "s#\(<local_dbid>\).*\(</local_dbid>\)#\1${local_dbid}\2#g" ${COMMON_CFG} 2>>${er_log}

  #kill已存在进程
  kill_processes
  
  show_process "dataloader配置结束"
}

#检查数据库相关信息
if [ $# -lt 1 ]; then
  usage
  exit
fi

#检查平台库状态
#check_db_status ${pf_usrpwd}

#数据库不是open状态则寻出
#if [ ${db_status} -ne 1 ]; then
#  show_process "平台库连接不成功，退出"
#  exit 1
#fi

#判断安装及重新配置
case "${type}" in
  install|update)
    install_dataloader
    ;;
  reconfig)
    reconfig_dataloader
    ;;
  *)
    usage
    ;;
esac

#判断安装结果
if [ -f ${er_log} -a $(sed '/^\W*$/d' ${er_log} | wc -l) -ne 0 ]; then
  show_process "安装出错"
  exit 1
fi