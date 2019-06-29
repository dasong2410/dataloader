#! /bin/sh
#手动安装调用脚本，需要根据具体情况设置相应变量
#set -x

#当前目录的绝对路径
CURR_DIR=$(cd "$(dirname $0)"; pwd)

#安装类型
type=${1:-"install"}

#需要修改的变量
export NOAHPFDB_USERNAME=noahpf
export NOAHPFDB_PASSWORD=noahpf
export NOAHPFDB_IP=10.0.2.15
export NOAHPFDB_SID=ora10g

sh ${CURR_DIR}/install.sh install
