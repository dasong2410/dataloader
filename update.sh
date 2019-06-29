#! /bin/sh
#set -x

#当前目录
CURR_DIR=$(cd "$(dirname $0)"; pwd)

#安装类型
type=${1:-"update"}

sh ${CURR_DIR}/install.sh ${type}
