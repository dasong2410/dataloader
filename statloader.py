#! /usr/bin/env python
#_*_encoding:utf-8_*_

import sys
import time
import datetime
import random
from Global import *
from noah import StatGather

#当前脚本名
myFullName = sys.argv[0].split(os.sep)[-1]
myPrefixName = myFullName.split(".")[0]

#检查程序是否正在运行
if toolkit.isRunning(myFullName) > 1:
  dataLogger.info('%s正在运行'%(myPrefixName))
  print '%s正在运行'%(myPrefixName)
  sys.exit()

#构建StatGather实例
statGather = StatGather.StatGather(protocolBodyDict, statLogger, statLogDir, bcpDir, localDbid, toolkit, statDelay)

#入库代码
while True:
  statLogger.info('%s开始处理数据'%(myPrefixName))

  #生成统计bcp文件名
  sec = toolkit.date2sec(datetime.datetime.now())
  statBcpFile = '%s/DATANUM_TB_%s_%s'%(statBcpDir, sec, random.randint(100000000,999999999))
  
  statGather.genBcp(statBcpFile)
  statGather.moveFile()
  
  #等待一定时间
  statLogger.info('%s处理数据结束，等待%d秒\n'%(myPrefixName, statInterval))
  time.sleep(statInterval)
