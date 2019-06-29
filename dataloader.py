#! /usr/bin/env python
#_*_encoding:utf-8_*_

import sys
import time
import datetime
import random
from noah import BcpLoader
from Global import *

#当前脚本名
myFullName = sys.argv[0].split(os.sep)[-1]
myPrefixName = myFullName.split(".")[0]

#参数处理
opts = toolkit.getOpts(sys.argv[1:])

for o,a in opts:
  if o in ("-v"):
    versionInfo.info()
    sys.exit()
  if o in ("-h"):
    versionInfo.usage()
    sys.exit()

#检查环境
#检查程序是否正在运行
if toolkit.isRunning(myFullName) > 1:
  dataLogger.info("%s正在运行"%(myPrefixName))
  print "%s正在运行"%(myPrefixName)
  sys.exit()

#配置文件不存在则退出
#if toolkit.checkFileExist(CFG_FILES) != 0:
#  sys.exit()

#数据库状态不正常则退出
#if toolkit.checkDbStatus(userpwd) == 0:
#  sys.exit()

#线程列表
threadList = {}

#入库代码
while True:
  dataLogger.info("%s开始处理数据"%(myPrefixName))

  #主机列表遍历
  for db in dbs:
    dbid = db.get("id")
    dbip = db.text

    #协议线程列表遍历
    for threadName, thdProts in threads.items():
      thdName = dbid + '_' + threadName
    
      #检查线程
      try:
        isAlive = threadList[thdName].isAlive()
      except:
        isAlive = False
    
      #启动新线程
      if not isAlive:
        #bcp文件行数 统计信息文件名
        sec = toolkit.date2sec(datetime.datetime.now())
        statBcpFile = '%s/MASS_%s_%s_BCPSTAT_0001_DTL'%(statBcpDir, sec, random.randint(100000000,999999999))
        
        threadList[thdName] = BcpLoader.BcpLoader(dbid, dbip, thdName, thdProts)
        threadList[thdName].setAll(bcpDir, ctlDir, sqlldrLogDir, badFileRoot, badLogRoot, statLogDir, statBcpFile, localDbid, protocolBodyDict, threadLogList[thdName], toolkit)
        threadList[thdName].start()
        
        dataLogger.debug("%s启动线程：%s\n"%(myPrefixName, thdName))
        dataLogger.debug("线程%s：%s\n"%(thdName, thdProts))
  
  dataLogger.debug("%s线程数：%s\n"%(myPrefixName, len(threadList)))
  
  #等待一定时间
  dataLogger.info("%s处理数据结束，等待%d秒\n"%(myPrefixName, dataInterval))
  time.sleep(dataInterval)
