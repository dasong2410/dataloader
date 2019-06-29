#! /usr/bin/env python
#_*_encoding:utf-8_*_

import sys
import time
import datetime
import random
from Global import *
from noah import StatGather

#检查程序是否正在运行
if toolkit.isRunning("statloader.py") > 1:
  dataLogger.info('statloader正在运行')
  print 'statloader正在运行'
  sys.exit()

#构建StatGather实例
statGather = StatGather.StatGather(protocolBodyDict, statLogger, statLogDir, bcpDir, localDbid, toolkit, statDelay)

#入库代码
while True:
  statLogger.info('statloader开始处理数据')

  #生成统计bcp文件名
  sec = toolkit.date2sec(datetime.datetime.now())
  statBcpFile = '%s/DATANUM_TB_%s_%s'%(statBcpDir, sec, random.randint(100000000,999999999))
  
  statGather.genBcp(statBcpFile)
  statGather.moveFile()
  
  #等待一定时间
  statLogger.info('statloader处理数据结束，等待%d秒\n'%(statInterval))
  time.sleep(statInterval)